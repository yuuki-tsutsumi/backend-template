from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.orm import Session

from app.domain.entity.user_organization import (
    UserOrganization as UserOrganizationEntity,
)
from app.domain.entity.user_organization import (
    UserRole,
)


class UserOrganizationIRepository(ABC):
    @abstractmethod
    def get_role_by_user_id_and_organization_id(
        self, user_id: int, organization_id: int
    ) -> UserRole:
        pass

    @abstractmethod
    def create_user_organization(
        self, user_id: int, organization_id: int, role: UserRole, db: Session
    ) -> UserOrganizationEntity:
        pass

    @abstractmethod
    def get_user_organizations_by_user_id(
        self, user_id: int
    ) -> List[UserOrganizationEntity]:
        pass

    @abstractmethod
    def is_user_in_organization_exist(self, user_id: int, organization_id: int) -> bool:
        pass
