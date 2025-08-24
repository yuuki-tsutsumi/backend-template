from datetime import datetime

from pydantic import BaseModel


class UserOrganizationResponse(BaseModel):
    user_id: int
    organization_id: int
    role: str
    created_at: datetime
    updated_at: datetime
