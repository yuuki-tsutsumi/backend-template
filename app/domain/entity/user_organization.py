import enum

from pydantic import ConfigDict, Field

from app.domain.constants import NOT_SPECIFIED_ID
from app.domain.entity.common import CommonEntity


class UserRole(str, enum.Enum):
    APP_ADMIN = "app_admin"
    ORG_ADMIN = "org_admin"
    MEMBER = "member"


class UserOrganization(CommonEntity):
    id: int = Field(default=NOT_SPECIFIED_ID)
    user_id: int = Field(default=NOT_SPECIFIED_ID)
    organization_id: int = Field(default=NOT_SPECIFIED_ID)
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
