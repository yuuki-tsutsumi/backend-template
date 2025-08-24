import io
from typing import Any, Dict, Generator, Tuple

import boto3
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from mypy_boto3_s3 import S3Client
from pytest_mock import MockerFixture
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.config import settings
from app.dependencies.auth import verify_token_and_get_email
from app.dependencies.db import get_db
from app.infra.models.base import Base
from app.infra.repository.s3 import create_s3_client
from app.router.main import app
from app.util import setup_logger

logger = setup_logger(__name__)

TEST_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_USER}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.TEST_DB_NAME}"  # noqa E501

test_engine = create_engine(TEST_DATABASE_URL, echo=True)
testing_session_local = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)
test_db = testing_session_local()


@pytest.fixture(scope="session", autouse=True)
def create_and_delete_database() -> Generator[None, None, None]:
    # setup
    # テスト用データベースの作成
    if database_exists(TEST_DATABASE_URL):
        drop_database(TEST_DATABASE_URL)

    create_database(TEST_DATABASE_URL)

    # テスト用データベースのテーブル作成
    try:
        alembic_cfg = Config(
            file_="alembic.ini",
        )
        alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
        command.upgrade(alembic_cfg, "head")
        Base.metadata.create_all(test_engine)
    except Exception as e:
        logger.debug(f"Database migration failed: {e}")
        raise

    yield

    # teardown
    # テスト終了後にデータベースを削除
    try:
        logger.debug("Dropping database...")
        drop_database(TEST_DATABASE_URL)
    except Exception as e:
        logger.debug(f"Database deletion failed: {e}")
        raise


@pytest.fixture(scope="function", autouse=True)
def delete_data() -> Generator[None, None, None]:
    yield

    # teardown
    # 各テスト関数終了後にデータベースのデータを削除
    # NOTE: 各テーブルの主キーのシーケンスはリセットしないので、idは検証しない方向にするとかやり方を検討する
    try:
        logger.debug("Deleting tables after test function...")

        # 既存のトランザクションをロールバック
        test_db.rollback()

        # 新しいトランザクションでデータを削除
        for table in reversed(Base.metadata.sorted_tables):
            test_db.execute(table.delete())
        test_db.execute(text("SELECT setval('user_id_seq', 1, false)"))
        test_db.commit()

    except Exception as e:
        logger.debug(f"Error while deleting tables or resetting sequence: {e}")
        test_db.rollback()
        raise
    finally:
        test_db.close()


@pytest.fixture(scope="function", autouse=True)
def mock_testdb(mocker: MockerFixture) -> None:
    mocker.patch("app.infra.repository.db.SessionLocal", return_value=test_db)


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    def get_test_db() -> Generator[Session, None, None]:
        try:
            logger.debug("Session opened")
            yield test_db
        finally:
            test_db.close()
            logger.debug("Session closed")

    # NOTE: 現時点では認証のモックとして単一のメールアドレスでテストする。実際の処理はroleを元に行うため
    # 必要になった際、パラメータ化などで複数アドレスに対応する
    async def mock_email() -> str:
        return "org@org.com"

    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[verify_token_and_get_email] = mock_email
    client = TestClient(app)

    yield client


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    yield test_db


def create_s3_test_data(
    bucket_name: str, files: Dict[str, str]
) -> Tuple[S3Client, str]:
    endpoint_url = f"http://{settings.LOCALSTACK_HOST}:4566"

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
        region_name="ap-northeast-1",
    )

    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": "ap-northeast-1"},
    )

    for key, content in files.items():
        s3.put_object(Bucket=bucket_name, Key=key, Body=content.encode())

    return s3, bucket_name


def create_s3_test_data_for_docx(
    bucket_name: str, files: Dict[str, Any]
) -> Tuple[S3Client, str]:
    s3 = create_s3_client()

    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": "ap-northeast-1"},
    )

    for key, doc in files.items():
        docx_io = document_to_bytesio(doc)
        s3.put_object(Bucket=bucket_name, Key=key, Body=docx_io.getvalue())

    return s3, bucket_name


def document_to_bytesio(doc: Any) -> io.BytesIO:
    docx_io = io.BytesIO()
    doc.save(docx_io)
    return docx_io
