from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

engine = create_engine(
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Session:
    """
    新しいセッションオブジェクトを取得する。

    Returns:
        Session: SQLAlchemyのセッションオブジェクト
    """
    try:
        db = SessionLocal()
        return db
    except Exception as e:
        raise RuntimeError(f"Failed to create a database session: {e}")


@contextmanager
def transaction_scope() -> Generator[Session, None, None]:
    """
    トランザクションスコープを管理するコンテキストマネージャ。
    トランザクションを開始し、エラー時にロールバック、正常終了時にコミットする。

    Yields:
        Session: トランザクション中のセッションオブジェクト
    """
    db = get_db_session()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@contextmanager
def readonly_transaction_scope() -> Generator[Session, None, None]:
    """
    読み取り専用のトランザクションスコープを管理するコンテキストマネージャ。
    トランザクションを開始するが、commit や rollback を行わない。

    Yields:
        Session: トランザクション中のセッションオブジェクト
    """
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()
