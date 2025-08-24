from typing import Tuple

from injector import Injector

from app.domain.entity.user import User
from app.domain.entity.user_organization import UserRole
from app.usecase.user import UserUsecase
from app.usecase.user_organization import UserOrganizationUsecase


def get_user_and_role(
    injector: Injector, email: str, organization_id: int
) -> Tuple[UserRole, User]:
    user_usecase = injector.get(UserUsecase)
    user_org_usecase = injector.get(UserOrganizationUsecase)

    # user_id取得のためemailからユーザー詳細取得
    user: User = user_usecase.get_user_by_email(email=email)

    role: UserRole = user_org_usecase.get_role_by_user_id_and_organization_id(
        user_id=user.id, organization_id=organization_id
    )

    return role, user


def is_user_role_app_admin(injector: Injector, email: str) -> Tuple[bool, User]:
    user_usecase = injector.get(UserUsecase)
    user_org_usecase = injector.get(UserOrganizationUsecase)
    user: User = user_usecase.get_user_by_email(email=email)

    user_orgs = user_org_usecase.get_user_organizations_by_user_id(user_id=user.id)

    is_app_admin = any(user_org.role == UserRole.APP_ADMIN for user_org in user_orgs)
    return is_app_admin, user


def is_user_role_app_admin_or_org_admin(
    injector: Injector, email: str
) -> Tuple[bool, User]:
    user_usecase = injector.get(UserUsecase)
    user_org_usecase = injector.get(UserOrganizationUsecase)
    user: User = user_usecase.get_user_by_email(email=email)

    user_orgs = user_org_usecase.get_user_organizations_by_user_id(user_id=user.id)

    is_app_admin_or_org_admin = any(
        user_org.role == UserRole.ORG_ADMIN or user_org.role == UserRole.APP_ADMIN
        for user_org in user_orgs
    )
    return is_app_admin_or_org_admin, user
