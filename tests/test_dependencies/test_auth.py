from datetime import datetime, timedelta
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import HTTPException
from jose import jwt
from jose.utils import base64url_encode
from pytest import MonkeyPatch

from app.config import settings
from app.dependencies.auth import verify_token

# ファイルから鍵を読み込み
PRIVATE_KEY_PEM = Path("tests/keys/private_test_key.pem").read_text()
PUBLIC_KEY_OBJ = serialization.load_pem_public_key(
    Path("tests/keys/public_test_key.pem").read_bytes()
)
if not isinstance(PUBLIC_KEY_OBJ, RSAPublicKey):
    raise TypeError("Only RSA public keys are supported in this test.")

# 公開鍵をJOSEのJWK形式に変換
public_numbers = PUBLIC_KEY_OBJ.public_numbers()
n: str = base64url_encode(
    public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, "big")
).decode()
e: str = base64url_encode(
    public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, "big")
).decode()

TEST_KID = "test-kid"
TEST_PUBLIC_KEYS = {
    TEST_KID: {
        "kty": "RSA",
        "kid": TEST_KID,
        "use": "sig",
        "alg": "RS256",
        "n": n,
        "e": e,
    }
}


def create_jwt_token(
    iss: str | None = None,
    aud: str | None = None,
    exp: datetime | None = None,
    kid: str = TEST_KID,
) -> str:
    payload = {
        "email": "test@example.com",
        "iss": iss
        or f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}",
        "aud": aud or settings.COGNITO_CLIENT_ID,
        "exp": exp or (datetime.utcnow() + timedelta(minutes=5)),
    }
    headers = {"kid": kid}
    return jwt.encode(payload, PRIVATE_KEY_PEM, algorithm="RS256", headers=headers)


def test_verify_token_valid(monkeypatch: MonkeyPatch) -> None:
    """正常なJWTトークンが検証に成功し、ペイロードが正しく取得できることを確認するテスト"""
    monkeypatch.setattr(
        "app.dependencies.auth.get_cognito_public_keys", lambda: TEST_PUBLIC_KEYS
    )
    token = create_jwt_token()
    result = verify_token(token)
    assert result["email"] == "test@example.com"


def test_verify_token_expired(monkeypatch: MonkeyPatch) -> None:
    """期限切れのJWTトークンが 'Token has expired' の例外を返すことを確認するテスト"""
    monkeypatch.setattr(
        "app.dependencies.auth.get_cognito_public_keys", lambda: TEST_PUBLIC_KEYS
    )
    token = create_jwt_token(exp=datetime.utcnow() - timedelta(minutes=1))
    with pytest.raises(HTTPException) as exc_info:
        verify_token(token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has expired"


def test_verify_token_invalid_issuer(monkeypatch: MonkeyPatch) -> None:
    """不正なissuerを持つJWTトークンが 'Invalid issuer or audience' の例外を返すことを確認するテスト"""
    monkeypatch.setattr(
        "app.dependencies.auth.get_cognito_public_keys", lambda: TEST_PUBLIC_KEYS
    )

    invalid_iss = "https://invalid-issuer.com"
    token = create_jwt_token(iss=invalid_iss)

    with pytest.raises(HTTPException) as exc_info:
        verify_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid issuer or audience"
