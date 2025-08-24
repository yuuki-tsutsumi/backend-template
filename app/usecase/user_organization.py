from dataclasses import dataclass
from typing import List

from injector import inject

from app.domain.entity.user_organization import (
    UserOrganization as UserOrganizationEntity,
)
from app.domain.entity.user_organization import (
    UserRole,
)
from app.domain.i_repository.user_organization import UserOrganizationIRepository
from app.usecase.error import EntityNotFoundError


@inject
@dataclass
class UserOrganizationUsecase:
    user_organization_repository: UserOrganizationIRepository

    def get_role_by_user_id_and_organization_id(
        self, user_id: int, organization_id: int
    ) -> UserRole:
        try:
            return self.user_organization_repository.get_role_by_user_id_and_organization_id(
                user_id=user_id, organization_id=organization_id
            )
        except EntityNotFoundError as e:
            raise EntityNotFoundError(
                entity_name=e.entity_name,
                entity_id=e.entity_id,
                message=e.message,
            )

    def get_user_organizations_by_user_id(
        self, user_id: int
    ) -> List[UserOrganizationEntity]:
        return self.user_organization_repository.get_user_organizations_by_user_id(
            user_id=user_id,
        )

    def is_user_in_organization_exist(self, user_id: int, organization_id: int) -> bool:
        return self.user_organization_repository.is_user_in_organization_exist(
            user_id=user_id, organization_id=organization_id
        )
