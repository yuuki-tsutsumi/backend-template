from typing import cast

from app.domain.entity.user_organization import UserRole
from app.infra.models import user_organization
from app.infra.models.user_organization import UserOrganization
from tests.common import fixed_time
from tests.factories.base import DBModelFactory


class UserOrganizationFactory(DBModelFactory[UserOrganization]):
    class Meta:
        model = user_organization.UserOrganization


def create_user_organization(
    user_id: int, organization_id: int, role: UserRole
) -> user_organization.UserOrganization:
    return cast(
        UserOrganization,
        UserOrganizationFactory.create(
            user_id=user_id,
            organization_id=organization_id,
            role=role.value,
            created_at=fixed_time,
            updated_at=fixed_time,
        ),
    )
