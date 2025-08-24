from fastapi import status
from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.domain.entity.user_organization import UserRole
from tests.common import fixed_time_freezgun
from tests.factories.organization import create_organization
from tests.factories.user import create_user
from tests.factories.user_organization import create_user_organization


@freeze_time(fixed_time_freezgun)
def test_create_user_success(client: TestClient) -> None:
    """ユーザーが正しく作成されることを確認"""
    # テストデータの作成
    create_organization(id=1, name="test_org")

    # 認証用のモックユーザー
    create_user(
        id=999,
        cognito_user_id="test999",
        email="org@org.com",
        display_name="mock_user",
    )
    create_user_organization(user_id=999, organization_id=1, role=UserRole.APP_ADMIN)

    user_request = {
        "cognito_user_id": "test",
        "email": "test@example.com",
        "display_name": "test_user",
        "role": UserRole.APP_ADMIN.value,
        "organization_id": 1,
        "password": "Samplepassword_123",
    }

    response = client.post("/api/user", json=user_request)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["cognito_user_id"] == user_request["cognito_user_id"]
    assert response_data["email"] == user_request["email"]
    assert response_data["display_name"] == user_request["display_name"]


# TODO: 権限毎にサインアップのテストケースを作成する


@freeze_time(fixed_time_freezgun)
def test_create_user_duplicate_email(client: TestClient) -> None:
    """既存のメールアドレスで作成を試みた場合にエラーになることを確認"""
    # テストデータの作成
    create_organization(id=1, name="test_org")
    # 認証用のモックユーザー
    create_user(cognito_user_id="test", email="org@org.com", display_name="mock_user")
    create_user_organization(user_id=1, organization_id=1, role=UserRole.APP_ADMIN)
    # 重複チェック用のユーザー
    create_user(
        cognito_user_id="test2",
        email="test@example.com",
        display_name="test_user",
    )
    create_user_organization(user_id=2, organization_id=1, role=UserRole.APP_ADMIN)
    # user.idの調整

    user_request = {
        "cognito_user_id": "test3",
        "email": "test@example.com",
        "display_name": "test_user",
        "role": UserRole.APP_ADMIN.value,
        "organization_id": 1,
        "password": "Samplepassword_123",
    }
    response = client.post("/api/user", json=user_request)

    assert response.status_code == status.HTTP_409_CONFLICT
    response_data = response.json()
    assert (
        response_data["message"]
        == "このメールアドレスは既に登録されています。 email: test@example.com"
    )


@freeze_time(fixed_time_freezgun)
def test_create_user_duplicate_cognito_user_id(client: TestClient) -> None:
    """既存のCognitoユーザーIDで作成を試みた場合にエラーになることを確認"""

    # テストデータの作成
    create_organization(id=1, name="test_org")
    create_user(
        cognito_user_id="test",
        email="org@org.com",
        display_name="test_user",
    )
    create_user_organization(user_id=1, organization_id=1, role=UserRole.APP_ADMIN)
    # 重複チェック用のユーザー
    create_user(
        cognito_user_id="test2",
        email="test2@example.com",
        display_name="test_user",
    )
    create_user_organization(user_id=2, organization_id=1, role=UserRole.APP_ADMIN)

    # 実行リクエスト（cognito_user_id が重複）
    user_request = {
        "cognito_user_id": "test2",
        "email": "test3@example.com",
        "display_name": "test_user",
        "role": UserRole.APP_ADMIN.value,
        "organization_id": 1,
        "password": "Samplepassword_123",
    }
    response = client.post("/api/user", json=user_request)

    # 検証
    assert response.status_code == status.HTTP_409_CONFLICT
    response_data = response.json()
    assert response_data["message"] == "ユーザーは既に存在します: test2"


@freeze_time(fixed_time_freezgun)
def test_create_user_duplicate_user_id(client: TestClient) -> None:
    """既存のユーザーIDで作成を試みた場合にエラーになることを確認"""

    # テストデータの作成
    create_organization(id=1, name="test_org")
    # idを指定することで、あえてシーケンス番号を進めない。
    create_user(
        cognito_user_id="test",
        email="org@org.com",
        display_name="test_user",
        id=1,
    )
    create_user_organization(user_id=1, organization_id=1, role=UserRole.APP_ADMIN)

    # 実行リクエスト（id=0で作成しようとする。）
    user_request = {
        "cognito_user_id": "test2",
        "email": "test2@example.com",
        "display_name": "test_user",
        "role": UserRole.APP_ADMIN.value,
        "organization_id": 1,
        "password": "Samplepassword_123",
    }
    response = client.post("/api/user", json=user_request)

    # 検証
    assert response.status_code == status.HTTP_409_CONFLICT
    response_data = response.json()
    assert response_data["message"] == "ユーザーIDが重複しています。 id: 1"


@freeze_time(fixed_time_freezgun)
def test_create_user_invalid_organization(client: TestClient) -> None:
    """存在しない組織IDを指定した場合にエラーになることを確認"""
    # テストデータの作成
    create_user(
        id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
    )
    create_organization(id=1, name="test_org")
    create_user_organization(user_id=1, organization_id=1, role=UserRole.APP_ADMIN)

    # 存在しない組織IDでユーザー作成を行う
    user_data = {
        "cognito_user_id": "test2",
        "email": "test@example.com",
        "display_name": "test_user",
        "role": UserRole.APP_ADMIN.value,
        "organization_id": 999,
        "password": "Samplepassword_123",
    }

    response = client.post("/api/user", json=user_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    response_data = response.json()
    assert (
        response_data["message"] == "指定された組織が存在しません。organization_id: 999"
    )


@freeze_time(fixed_time_freezgun)
def test_create_user_validation_error(client: TestClient) -> None:
    """不正なJSONが送信された場合にエラーになることを確認"""
    response = client.post("/api/user", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# NOTE: 認可処理前提のテストは一旦コメントアウト。

# @freeze_time(fixed_time_freezgun)
# def test_create_user_member_access_denied(client: TestClient) -> None:
#     """MEMBERロールのユーザーがユーザー作成を試みた場合にエラーになることを確認"""
#     # テストデータの作成
#     create_organization(id=1, name="test_org")
#     # 認証用のモックユーザー
#     create_user(
#         id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
#     )
#     create_user_organization(user_id=1, organization_id=1, role=UserRole.MEMBER)

#     user_request = {
#         "cognito_user_id": "test2",
#         "email": "new_user@example.com",
#         "display_name": "new_user",
#         "role": UserRole.APP_ADMIN.value,
#         "organization_id": 1,
#         "password": "Samplepassword_123",
#     }
#     response = client.post("/api/user", json=user_request)

#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     response_data = response.json()
#     assert response_data["message"] == "メンバーはこの操作を実行する権限がありません"


# def test_create_user_org_admin_add_other_org_denied(client: TestClient) -> None:
#     """ORG_ADMINロールのユーザーが異なる組織のユーザー作成を試みた場合にエラーになることを確認"""
#     # テストデータの作成
#     create_organization(id=1, name="test_org1")
#     create_organization(id=2, name="test_org2")
#     # 認証用のモックユーザー
#     create_user(
#         id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
#     )
#     create_user_organization(user_id=1, organization_id=1, role=UserRole.ORG_ADMIN)

#     user_request = {
#         "cognito_user_id": "test2",
#         "email": "new_user@example.com",
#         "display_name": "new_user",
#         "role": UserRole.ORG_ADMIN.value,
#         "organization_id": 2,
#         "password": "Samplepassword_123",
#     }
#     response = client.post("/api/user", json=user_request)

#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     response_data = response.json()
#     assert (
#         response_data["message"]
#         == "指定された組織が存在しないか、組織にユーザーが所属していません。 user_id: 1, organization_id: 2"
#     )


# @freeze_time(fixed_time_freezgun)
# def test_create_user_org_admin_add_app_admin_denied(client: TestClient) -> None:
#     """ORG_ADMINロールのユーザーがAPP_ADMIN権限のユーザーの作成を試みた場合にエラーになることを確認"""
#     # テストデータの作成
#     create_organization(id=1, name="test_org")
#     # 認証用のモックユーザー
#     create_user(
#         id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
#     )
#     create_user_organization(user_id=1, organization_id=1, role=UserRole.ORG_ADMIN)

#     user_request = {
#         "cognito_user_id": "test2",
#         "email": "new_user@example.com",
#         "display_name": "new_user",
#         "role": UserRole.APP_ADMIN.value,
#         "organization_id": 1,
#         "password": "Samplepassword_123",
#     }
#     response = client.post("/api/user", json=user_request)

#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     response_data = response.json()
#     assert (
#         response_data["message"] == "組織のユーザはこの操作を実行する権限がありません"
#     )


@freeze_time(fixed_time_freezgun)
def test_delete_user_success_with_app_admin(client: TestClient) -> None:
    """app admin権限を持ったユーザー削除を実行を実行できることを確認"""
    # テストデータの作成
    create_organization(id=1, name="test_org")
    create_user(
        id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
    )
    create_user_organization(user_id=1, organization_id=1, role=UserRole.APP_ADMIN)
    create_user(
        id=2,
        cognito_user_id="target",
        email="target@org.com",
        display_name="target_user",
    )

    response = client.delete("/api/user/target")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@freeze_time(fixed_time_freezgun)
def test_delete_user_success_with_org_admin(client: TestClient) -> None:
    """org admin権限を持ったユーザー削除を実行を実行できることを確認"""
    # テストデータの作成
    create_organization(id=1, name="test_org")
    create_user(
        id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
    )
    create_user_organization(user_id=1, organization_id=1, role=UserRole.ORG_ADMIN)
    create_user(
        id=2,
        cognito_user_id="target",
        email="target@org.com",
        display_name="target_user",
    )

    response = client.delete("/api/user/target")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@freeze_time(fixed_time_freezgun)
def test_delete_user_not_found(client: TestClient) -> None:
    """存在しないユーザーIDを削除しようとすると404が返ること"""
    # テストデータの作成
    create_organization(id=1, name="test_org")
    create_user(
        id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
    )
    create_user_organization(user_id=1, organization_id=1, role=UserRole.APP_ADMIN)
    create_user(
        id=2,
        cognito_user_id="admin",
        email="admin@org.com",
        display_name="admin_user",
    )

    response = client.delete("/api/user/nonexistId")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "message" in response.json()
    assert "指定されたIDのユーザーは存在しません。" in response.json()["message"]


# NOTE: 認可処理前提のテストは一旦コメントアウト。

# @freeze_time(fixed_time_freezgun)
# def test_delete_user_member_access_denied(client: TestClient) -> None:
#     """MEMBERロールのユーザーがユーザー削除を試みた場合にエラーになることを確認"""
#     # テストデータの作成
#     create_organization(id=1, name="test_org")
#     create_user(
#         id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
#     )
#     create_user_organization(user_id=1, organization_id=1, role=UserRole.MEMBER)

#     response = client.delete("/api/user/test")

#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     response_data = response.json()
#     assert response_data["message"] == "メンバーはこの操作を実行する権限がありません"
