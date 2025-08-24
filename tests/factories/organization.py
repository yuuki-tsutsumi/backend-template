from typing import Optional, cast

from app.infra.models import organization
from app.infra.models.organization import Organization
from tests.common import fixed_time
from tests.factories.base import DBModelFactory


class OrganizationFactory(DBModelFactory[Organization]):
    class Meta:
        model = organization.Organization


def create_organization(id: int, name: Optional[str] = "") -> organization.Organization:
    return cast(
        Organization,
        OrganizationFactory.create(
            id=id,
            name=name,
            created_at=fixed_time,
            updated_at=fixed_time,
            deleted=False,
        ),
    )
