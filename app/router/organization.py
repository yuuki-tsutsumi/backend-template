from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Body, Depends, status
from fastapi.openapi.models import Example
from injector import Injector

from app.dependencies import dependency_injector

# from app.dependencies.auth import verify_token_and_get_email
from app.domain.constants import NOT_SPECIFIED_ID
from app.domain.entity.organization import Organization
from app.router.schemas.organization import OrganizationResponse

# from app.router.util import is_user_role_app_admin
# from app.usecase.error import AppAdminOnlyAccessError
from app.usecase.organization import (
    CreateOrganizationParams,
    OrganizationUsecase,
)

router = APIRouter()


create_organization_params_example: Dict[str, Example] = {
    "組織作成": {
        "summary": "組織作成リクエストの例",
        "description": "名前を指定する。",
        "value": {
            "name": "test",
        },
    }
}


@router.post(
    "",
    summary="組織を作成",
    status_code=status.HTTP_201_CREATED,
    response_model=OrganizationResponse,
)
async def create_organization(
    params: CreateOrganizationParams = Body(
        ..., openapi_examples=create_organization_params_example
    ),
    # _: Dict[str, Any] = Depends(verify_token_and_get_email),
    injector: Injector = Depends(dependency_injector.get_injector),
) -> OrganizationResponse:
    # TODO: 認可処理を入れる。アプリ管理者のみが操作できる。
    organization_usecase = injector.get(OrganizationUsecase)
    organization_entity = organization_usecase.create_organization(params=params)
    # TODO: Entity-Responseの型変換を関数化する。
    return OrganizationResponse(
        id=(
            organization_entity.id
            if organization_entity.id is not None
            else NOT_SPECIFIED_ID
        ),
        name=organization_entity.name if organization_entity.name is not None else "",
        deleted=(
            organization_entity.deleted
            if organization_entity.deleted is not None
            else False
        ),
        created_at=(
            organization_entity.created_at
            if organization_entity.created_at is not None
            else datetime.min
        ),
        updated_at=(
            organization_entity.updated_at
            if organization_entity.updated_at is not None
            else datetime.min
        ),
    )


@router.get(
    "/{organization_id}",
    summary="組織の詳細取得",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationResponse,
)
async def get_organization(
    organization_id: int,
    # _: Dict[str, Any] = Depends(verify_token_and_get_email),
    injector: Injector = Depends(dependency_injector.get_injector),
) -> Organization:
    organization_usecase = injector.get(OrganizationUsecase)
    return organization_usecase.get_organization(organization_id)


@router.get(
    "",
    summary="組織の一覧取得",
    status_code=status.HTTP_200_OK,
    response_model=list[OrganizationResponse],
)
async def get_all_organizations(
    # email: str = Depends(verify_token_and_get_email),
    injector: Injector = Depends(dependency_injector.get_injector),
) -> list[Organization]:

    # 認可処理。アプリの管理者（AA role=app_admin) が操作できる。
    # is_app_admin, _ = is_user_role_app_admin(injector, email)
    # if not is_app_admin:
    #     raise AppAdminOnlyAccessError()

    organization_usecase = injector.get(OrganizationUsecase)
    organizations = organization_usecase.get_all_organizations()
    return organizations
