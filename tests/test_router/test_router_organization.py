import json
from typing import Any

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.domain.entity.user_organization import UserRole
from tests.common import fixed_time, fixed_time_freezgun
from tests.factories.organization import create_organization
from tests.factories.user import create_user
from tests.factories.user_organization import create_user_organization


@freeze_time(fixed_time_freezgun)
def test_create_organization(client: TestClient) -> None:
    response = client.post(
        "/api/organization",
        json={
            "name": "org",
        },
    )
    response_data = response.json()
    expected = {
        "created_at": fixed_time,
        "id": response_data["id"],
        "name": "org",
        "updated_at": fixed_time,
        "deleted": False,
    }
    assert response.status_code == status.HTTP_201_CREATED
    assert response_data == expected


@pytest.mark.parametrize(
    "invalid_name", [None, [], {}, 123, True, False, {"name": "valid"}]
)
@freeze_time(fixed_time_freezgun)
def test_fail_organization_creation_with_empty_string(
    client: TestClient, invalid_name: Any
) -> None:
    response = client.post(
        "/api/organization",
        json={
            "name": invalid_name,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_content_text = response.content.decode("utf-8")
    response_content_json = json.loads(response_content_text)
    assert response_content_json["message"] == "名前はstr型である必要があります"


@pytest.mark.parametrize(
    "invalid_name",
    [
        " ",
        "\t",
        "\n",
        " \t ",
        "\n\t\n",
    ],
)
@freeze_time(fixed_time_freezgun)
def test_fail_organization_creation_with_whitespace_only(
    client: TestClient, invalid_name: str
) -> None:
    response = client.post(
        "/api/organization",
        json={
            "name": invalid_name,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_content_text = response.content.decode("utf-8")
    response_content_json = json.loads(response_content_text)
    assert response_content_json["message"] == "名前は有効な文字列である必要があります"


@freeze_time(fixed_time_freezgun)
def test_get_organization(client: TestClient) -> None:
    # データ作成
    org = create_organization(id=1, name="org")
    response = client.get(f"/api/organization/{org.id}")
    expected = {
        "created_at": fixed_time,
        "id": org.id,
        "name": "org",
        "updated_at": fixed_time,
        "deleted": False,
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@freeze_time(fixed_time_freezgun)
def test_get_organization_not_found(client: TestClient) -> None:
    response = client.get("/api/organization/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response_content_text = response.content.decode("utf-8")
    response_content_json = json.loads(response_content_text)
    assert (
        response_content_json["message"]
        == "指定された組織が見つかりません organization_id: 9999"
    )


@freeze_time(fixed_time_freezgun)
def test_get_all_organizations_success(client: TestClient) -> None:
    # 初期データ作成: 組織、ユーザー、ユーザー組織（アプリ管理者として設定）
    create_organization(id=1, name="org1")
    create_organization(id=2, name="org2")
    create_user(
        id=1,
        cognito_user_id="test",
        email="org@org.com",
        display_name="test_app_admin",
    )
    create_user_organization(
        user_id=1, organization_id=1, role=UserRole.APP_ADMIN  # アプリ管理者として設定
    )

    response = client.get("/api/organization")
    assert response.status_code == status.HTTP_200_OK
    expected = [
        {
            "id": 1,
            "name": "org1",
            "created_at": fixed_time,
            "updated_at": fixed_time,
            "deleted": False,
        },
        {
            "id": 2,
            "name": "org2",
            "created_at": fixed_time,
            "updated_at": fixed_time,
            "deleted": False,
        },
    ]
    assert response.json() == expected


# NOTE: 以降は認可処理前提のテスト

# @freeze_time(fixed_time_freezgun)
# def test_get_all_organizations_access_denied_for_org_admin(client: TestClient) -> None:
#     # 初期データ作成: 組織、ユーザー、ユーザー組織（組織管理者として設定）
#     create_organization(id=1, name="org")
#     create_user(
#         id=1,
#         cognito_user_id="test",
#         email="org@org.com",
#         display_name="test_org_admin",
#     )
#     create_user_organization(
#         user_id=1,
#         organization_id=1,
#         role=UserRole.ORG_ADMIN,  # 組織管理者として設定
#     )
#     response = client.get("/api/organization")

#     assert response.status_code == status.HTTP_403_FORBIDDEN
#     response_content_json = response.json()
#     assert (
#         response_content_json["message"]
#         == "アクセス権がありません。アプリ管理者のみ操作可能です。"
#     )


# @freeze_time(fixed_time_freezgun)
# def test_get_all_organizations_access_denied_for_org_user(client: TestClient) -> None:
#     # 初期データ作成: 組織、ユーザー、ユーザー組織（組織ユーザーとして設定）
#     create_organization(id=1, name="org")
#     create_user(
#         id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
#     )
#     create_user_organization(
#         user_id=1,
#         organization_id=1,
#         role=UserRole.MEMBER,  # 一般ユーザとして設定
#     )
#     response = client.get("/api/organization")

#     assert response.status_code == status.HTTP_403_FORBIDDEN
#     response_content_json = response.json()
#     assert (
#         response_content_json["message"]
#         == "アクセス権がありません。アプリ管理者のみ操作可能です。"
#     )
