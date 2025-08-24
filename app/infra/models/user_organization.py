from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, Integer

from app.domain.entity.user_organization import UserRole
from app.infra.models.base import Base

if TYPE_CHECKING:
    from app.infra.models.organization import Organization  # noqa F401
    from app.infra.models.user import User  # noqa F401


class UserOrganization(Base):
    __tablename__ = "user_organization"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), primary_key=True)
    role = Column(
        Enum(UserRole, name="role", native_enum=False, length=255),
        nullable=False,
        server_default=None,
    )
