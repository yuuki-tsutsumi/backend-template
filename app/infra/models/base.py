from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.orm import Mapped, declarative_base, declared_attr
from sqlalchemy.sql import func

from app.config import settings

Engine = create_engine(
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
    echo=False,
)  # noqa E501
ModelBase = declarative_base()


class Base(ModelBase):
    __abstract__ = True

    @declared_attr
    # NOTE: Column[DateTime]としたいが、Mappedにしないと、マイグレーションファイル生成時にエラーが出てしまうため、仕方なくこうしている。
    def created_at(cls) -> Mapped[DateTime]:
        return Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )

    @declared_attr
    def updated_at(cls) -> Mapped[DateTime]:
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
