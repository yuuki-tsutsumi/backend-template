from abc import ABC, abstractmethod

from app.domain.entity.organization import Organization


class OrganizationIRepository(ABC):
    @abstractmethod
    def save_organization(self, organization: Organization) -> Organization:
        pass

    @abstractmethod
    def get_organization(
        self, organization_id: int, exclude_deleted: bool = False
    ) -> Organization:
        pass

    @abstractmethod
    def is_organization_exist(self, organization_id: int) -> bool:
        pass

    @abstractmethod
    def get_all_organizations(
        self, exclude_deleted: bool = False
    ) -> list[Organization]:
        pass
