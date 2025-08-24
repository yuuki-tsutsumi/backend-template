from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrganizationResponse(BaseModel):
    id: int
    name: str
    deleted: Optional[bool]
    created_at: datetime
    updated_at: datetime
