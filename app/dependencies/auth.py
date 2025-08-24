from typing import Any, Dict

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import exceptions, jwt

from app.config import settings

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{settings.COGNITO_DOMAIN}/oauth2/authorize",
    tokenUrl=f"https://{settings.COGNITO_DOMAIN}/oauth2/token",
)


def get_cognito_public_keys() -> dict[str, dict[str, Any]]:
    jwks_url = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"  # noqa: E501
    jwks = requests.get(jwks_url).json()
    return {key["kid"]: key for key in jwks["keys"]}


def verify_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]

    public_keys = get_cognito_public_keys()
    key = public_keys.get(kid)

    if key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    try:
        decoded_token = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.COGNITO_CLIENT_ID,
            issuer=f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}",
        )
        return decoded_token
    except exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except exceptions.JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid issuer or audience",
        )
    except exceptions.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token verification failed"
        )


async def verify_token_and_get_email(
    token: str = Depends(oauth2_scheme),
) -> str:
    decoded_token = verify_token(token)
    email: str = decoded_token["email"]
    return email
