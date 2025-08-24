from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)  # noqa E501
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# NOTE: yieldの返り値は複雑なため、mypyの指摘を一旦無視する。
def get_db():  # type: ignore
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
