# TODO: 必ずしも使う必要があるかどうか微妙なところなのでコメントアウト

# from typing import List

# from fastapi import APIRouter, Depends, status
# from injector import Injector

# from app.dependencies import dependency_injector
# from app.dependencies.auth import verify_token_and_get_email
# from app.domain.entity.user import User
# from app.domain.entity.user_organization import (
#     UserOrganization as UserOrganizationEntity,
# )
# from app.router.schemas.user_organization import UserOrganizationResponse
# from app.usecase.user import UserUsecase
# from app.usecase.user_organization import UserOrganizationUsecase

# router = APIRouter()


# @router.get(
#     "",
#     summary="ユーザ-組織情報一覧取得",
#     status_code=status.HTTP_200_OK,
#     response_model=List[UserOrganizationResponse],
# )
# async def get_user_organizations(
#     email: str = Depends(verify_token_and_get_email),
#     injector: Injector = Depends(dependency_injector.get_injector),
# ) -> List[UserOrganizationEntity]:
#     user_usecase = injector.get(UserUsecase)
#     user_organization_usecase = injector.get(UserOrganizationUsecase)

#     user: User = user_usecase.get_user_by_email(email=email)

#     user_organizations = user_organization_usecase.get_user_organizations_by_user_id(
#         user_id=user.id
#     )

#     return [
#         UserOrganizationEntity.model_validate(user_organization)
#         for user_organization in user_organizations
#     ]
