from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, status
from fastapi.openapi.models import Example
from injector import Injector
from sqlalchemy.orm import Session

from app.dependencies import dependency_injector

# from app.dependencies.auth import verify_token_and_get_email
from app.dependencies.db import get_db
from app.domain.constants import NOT_SPECIFIED_ID
from app.domain.entity.user import User as UserEntity
from app.domain.entity.user_organization import UserRole
from app.router.schemas.user import UserResponse

# from app.router.util import (
#     get_user_and_role,
#     is_user_role_app_admin,
#     is_user_role_app_admin_or_org_admin,
# )
# from app.usecase.error import MemberAccessDeniedError
from app.usecase.user import UserCreateParams, UserUsecase

router = APIRouter()

create_user_params_example: Dict[str, Example] = {
    "ユーザ作成": {
        "summary": "ユーザ作成リクエストの例",
        "description": "必要な情報を指定してユーザを作成します。",
        "value": {
            "cognito_user_id": "org",
            "email": "org@example.com",
            "display_name": "org",
            "role": UserRole.ORG_ADMIN,
            "organization_id": 1,
            "password": "Samplepassword_123",
        },
    }
}


@router.post(
    "",
    summary="ユーザ作成",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_user(
    params: UserCreateParams = Body(..., openapi_examples=create_user_params_example),
    # email: str = Depends(verify_token_and_get_email),
    injector: Injector = Depends(dependency_injector.get_injector),
) -> UserResponse:
    user_usecase = injector.get(UserUsecase)
    # role = None
    # is_app_admin, _ = is_user_role_app_admin(injector, email)
    # if is_app_admin:
    #     role = UserRole.APP_ADMIN
    # else:
    #     role, _ = get_user_and_role(injector, email, params.organization_id)

    # TODO: 認可処理をする。
    role = UserRole.APP_ADMIN

    user = user_usecase.create_user(role=role, params=params)
    return UserResponse.model_validate(user.model_dump())


@router.get(
    "",
    summary="ユーザ一覧取得",
    status_code=status.HTTP_200_OK,
    response_model=List[UserResponse],
)
async def get_users(
    organization_id: Optional[int] = NOT_SPECIFIED_ID,
    # _: Dict[str, Any] = Depends(verify_token_and_get_email),
    db: Session = Depends(get_db),
    injector: Injector = Depends(dependency_injector.get_injector),
) -> List[UserEntity]:
    user_usecase = injector.get(UserUsecase)
    # TODO: 組織IDでの絞り込み処理を実装
    users = user_usecase.get_users(db)
    return [UserEntity.model_validate(user) for user in users]


update_user_params_example: Dict[str, Example] = {
    "ユーザ編集": {
        "summary": "ユーザ編集リクエストの例",
        "description": "更新したい情報を設定します。",
        "value": {"email": "org@example.com", "name": "org", "role": "org_member"},
    }
}


@router.delete(
    "/{cognito_user_id}", summary="ユーザ削除", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    cognito_user_id: str,
    # email: str = Depends(verify_token_and_get_email),
    injector: Injector = Depends(dependency_injector.get_injector),
) -> None:
    # is_app_admin_or_org_admin, _ = is_user_role_app_admin_or_org_admin(injector, email)

    # if is_app_admin_or_org_admin is False:
    #     raise MemberAccessDeniedError()

    user_usecase = injector.get(UserUsecase)
    user_usecase.delete_user(cognito_user_id=cognito_user_id)
    return
