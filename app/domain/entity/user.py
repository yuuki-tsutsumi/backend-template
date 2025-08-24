from typing import Optional

from pydantic import ConfigDict, EmailStr, Field

from app.domain.constants import NOT_SPECIFIED_ID
from app.domain.entity.common import CommonEntity


class User(CommonEntity):
    id: int = Field(default=NOT_SPECIFIED_ID)
    cognito_user_id: Optional[str] = Field(default=None)
    display_name: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    deleted: Optional[bool] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)
