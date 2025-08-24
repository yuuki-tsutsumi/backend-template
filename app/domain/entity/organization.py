from typing import Optional

from pydantic import ConfigDict, Field

from app.domain.constants import NOT_SPECIFIED_ID
from app.domain.entity.common import CommonEntity


class Organization(CommonEntity):
    id: int = Field(default=NOT_SPECIFIED_ID)
    name: Optional[str] = Field(default=None)
    deleted: Optional[bool] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)
