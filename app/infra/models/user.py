from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.infra.models.base import Base
from app.infra.models.user_organization import UserOrganization


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cognito_user_id = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)

    organizations = relationship(UserOrganization, backref="user")
