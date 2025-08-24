from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entity.user import User
from app.domain.entity.user_organization import UserRole


class UserIRepository(ABC):
    @abstractmethod
    def create_user(self, db: Session, user: User) -> User:
        pass

    @abstractmethod
    def get_users(self, db: Session) -> List[User]:
        pass

    @abstractmethod
    def update_user(self, db: Session, user: User) -> Optional[User]:
        pass

    @abstractmethod
    def soft_delete_user(self, db: Session, cognito_user_id: str) -> None:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> User:
        pass

    @abstractmethod
    def create_user_with_user_organization(
        self, user: User, organization_id: int, role: UserRole, password: str
    ) -> User:
        pass

    @abstractmethod
    def disable_user_on_cognito(self, cognito_user_id: str) -> None:
        pass

    @abstractmethod
    def enable_user_on_cognito(self, cognito_user_id: str) -> None:
        pass

    @abstractmethod
    def delete_user_on_cognito(self, cognito_user_id: str) -> None:
        pass
