from dataclasses import dataclass
from typing import Any, Optional, Self

from injector import inject
from pydantic import BaseModel, Field, model_validator

from app.domain.entity.organization import Organization

# from app.domain.entity.user_organization import UserRole
from app.domain.i_repository.organization import OrganizationIRepository
from app.usecase.error import (
    ValidationParamError,
)


class CreateOrganizationParams(BaseModel):
    name: Any = Field(
        ...,
    )
    deleted: Optional[bool] = Field(default=None)

    @model_validator(mode="after")
    def check_fields(self: Self) -> Self:
        name = self.name

        if not isinstance(name, str):
            raise TypeError("名前はstr型である必要があります")

        if not self.name.strip():
            raise ValidationParamError("名前は有効な文字列である必要があります")

        return self


@inject
@dataclass
class OrganizationUsecase:
    organization_repository: OrganizationIRepository

    def create_organization(self, params: CreateOrganizationParams) -> Organization:
        organization = Organization(**params.model_dump())
        return self.organization_repository.save_organization(organization)

    def get_organization(self, organization_id: int) -> Organization:
        return self.organization_repository.get_organization(organization_id)

    def get_all_organizations(self) -> list[Organization]:
        return self.organization_repository.get_all_organizations()
