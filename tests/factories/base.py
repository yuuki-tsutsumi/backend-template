from typing import Generic, TypeVar

import factory
from sqlalchemy.orm import Session

from tests.conftest import testing_session_local

T = TypeVar("T")


class DBModelFactory(factory.alchemy.SQLAlchemyModelFactory, Generic[T]):
    class Meta:
        abstract = True
        sqlalchemy_session: Session = testing_session_local()
        sqlalchemy_session_persistence = "commit"
