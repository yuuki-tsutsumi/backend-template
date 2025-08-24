from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommonEntity(BaseModel):
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
