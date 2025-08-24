from datetime import datetime

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.domain.entity.user_organization import UserRole
from app.infra.models.organization import Organization
from app.infra.models.user import User
from app.infra.models.user_organization import UserOrganization

DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_USER}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"  # noqa E501

engine = create_engine(DATABASE_URL, echo=True)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def insert_initial_users() -> None:
    """初期ユーザーをデータベースに追加する"""
    session = session_local()
    now = datetime.utcnow()
    try:
        users_data = [
            {
                "cognito_user_id": "tsutsumi0106",
                "display_name": "堤 友希",
                "email": "tsutsumi.develop@gmail.com",
                "deleted": False,
                "created_at": now,
                "updated_at": now,
            },
        ]
        session.bulk_insert_mappings(inspect(User).mapper, users_data)
        session.commit()
        user_instance = (
            session.query(User).filter_by(email="tsutsumi.develop@gmail.com").first()
        )
        if not user_instance:
            raise Exception("初期ユーザの作成に失敗しました。")

    except Exception as e:
        session.rollback()
        print(f"Error inserting initial data: {e}")
    finally:
        session.close()


def insert_initial_organizations() -> None:
    """初期組織をデータベースに追加する"""
    session = session_local()
    now = datetime.utcnow()
    try:
        organizations_data = [
            {
                "name": "test",
                "deleted": False,
                "created_at": now,
                "updated_at": now,
            },
        ]
        session.bulk_insert_mappings(inspect(Organization).mapper, organizations_data)
        session.commit()
        organization_instance = (
            session.query(Organization).filter_by(name="test").first()
        )
        if not organization_instance:
            raise Exception("初期組織の作成に失敗しました。")

        print("Initial organization data inserted successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting initial data: {e}")
    finally:
        session.close()


def insert_initial_user_organizations() -> None:
    """初期ユーザ-組織をデータベースに追加する"""
    session = session_local()
    now = datetime.utcnow()
    try:
        user_org_data = [
            {
                "user_id": 1,
                "organization_id": 1,
                "role": UserRole.APP_ADMIN.value,
                "created_at": now,
                "updated_at": now,
            },
        ]
        session.bulk_insert_mappings(inspect(UserOrganization).mapper, user_org_data)
        session.commit()
        user_organization_instance = (
            session.query(UserOrganization).filter_by(user_id=1).first()
        )
        if not user_organization_instance:
            raise Exception("初期ユーザ-組織の作成に失敗しました。")
        print("Initial organization and user data inserted successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting initial data: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    insert_initial_users()
    insert_initial_organizations()
    insert_initial_user_organizations()
