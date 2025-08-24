# TODO: ロジック側の方に合わせコメントアウト

# import json

# from fastapi import status
# from fastapi.testclient import TestClient
# from freezegun import freeze_time

# from app.domain.entity.user_organization import UserRole
# from tests.common import fixed_time, fixed_time_freezgun
# from tests.factories.organization import create_organization
# from tests.factories.user import create_user
# from tests.factories.user_organization import create_user_organization


# @freeze_time(fixed_time_freezgun)
# def test_get_user_organizations(client: TestClient) -> None:
#     create_organization(id=1, name="test_organization")
#     create_user(
#         id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
#     )
#     create_user_organization(
#         user_id=1,
#         organization_id=1,
#         role=UserRole.MEMBER,
#     )

#     response = client.get("/api/user_organization")
#     response_data = response.json()

#     expected = [
#         {
#             "user_id": 1,
#             "organization_id": 1,
#             "role": UserRole.MEMBER.value,
#             "created_at": fixed_time,
#             "updated_at": fixed_time,
#         }
#     ]

#     assert response.status_code == status.HTTP_200_OK
#     assert response_data == expected


# @freeze_time(fixed_time_freezgun)
# def test_get_user_organizations_empty(client: TestClient) -> None:
#     create_user(
#         id=1, cognito_user_id="test", email="org@org.com", display_name="test_user"
#     )

#     response = client.get("/api/user_organization")

#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     response_content_text = response.content.decode("utf-8")
#     response_content_json = json.loads(response_content_text)
#     assert (
#         response_content_json["message"]
#         == "ユーザが組織に所属していません。 user_id: 1"
#     )
