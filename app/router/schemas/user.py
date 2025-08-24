from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    cognito_user_id: str
    email: EmailStr
    display_name: str
    deleted: bool
    created_at: datetime
    updated_at: datetime


class UserCreateParams(BaseModel):
    cognito_user_id: str
    email: EmailStr
    name: str
    role: str
    organization_id: int
    password: str


class UserUpdateParams(UserCreateParams):
    pass
