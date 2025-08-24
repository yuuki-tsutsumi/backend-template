from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.infra.models.base import Base
from app.infra.models.user_organization import UserOrganization


class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True)
    deleted = Column(Boolean, default=False, nullable=False)

    users = relationship(UserOrganization, backref="organization")
