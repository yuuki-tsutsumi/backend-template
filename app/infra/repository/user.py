import logging
import re
from datetime import datetime
from typing import Any, List, Optional

import pytz
from botocore.exceptions import ClientError
from injector import inject
from sqlalchemy import exc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.domain.entity.user import User as UserEntity
from app.domain.entity.user_organization import UserRole
from app.domain.i_repository.user import UserIRepository
from app.domain.i_repository.user_organization import UserOrganizationIRepository
from app.infra.models.user import User
from app.infra.repository.cognito import (
    create_cognito_client,
    delete_user,
    disable_user,
    enable_user,
)
from app.infra.repository.db import readonly_transaction_scope, transaction_scope
from app.usecase.error import DuplicateError, EntityNotFoundError

logger = logging.getLogger(__name__)
japan_tz = pytz.timezone("Asia/Tokyo")


@inject
class UserRepository(UserIRepository):
    def __init__(self, user_organization_repository: UserOrganizationIRepository):
        self.user_organization_repository = user_organization_repository
        self.cognito_client = create_cognito_client()

    def create_user(self, db: Session, user: UserEntity) -> UserEntity:
        # NOTE: 呼び出し元でトランザクションを管理しているため、ここではトランザクションを管理しない
        try:
            now_utc = datetime.now(pytz.utc)
            now = now_utc.astimezone(japan_tz)
            db_user = User(
                cognito_user_id=user.cognito_user_id,
                email=user.email,
                display_name=user.display_name,
                deleted=user.deleted,
                created_at=now,
                updated_at=now,
            )
            db.add(db_user)
            db.flush()
            db.refresh(db_user)
            return UserEntity.model_validate(db_user)
        except exc.IntegrityError as e:
            constraint_name = getattr(
                getattr(e.orig, "diag", None), "constraint_name", ""
            )
            if constraint_name == "ix_user_email":
                logger.error(
                    f"このメールアドレスは既に登録されています。 email: {user.email}"
                )
                raise DuplicateError(
                    message=f"このメールアドレスは既に登録されています。 email: {user.email}"
                )
            elif constraint_name == "ix_user_cognito_user_id":
                logger.error(f"ユーザーは既に存在します: {user.cognito_user_id}")
                raise DuplicateError(
                    message=f"ユーザーは既に存在します: {user.cognito_user_id}"
                )
            elif constraint_name == "user_pkey":
                match = re.search(r"Key \(id\)=\((\d+)\)", str(e.orig))
                conflicting_id = match.group(1) if match else "不明"
                logger.error(f"ユーザーIDが重複しています。 id: {conflicting_id}")
                raise DuplicateError(
                    message=f"ユーザーIDが重複しています。 id: {conflicting_id}"
                )
            else:
                logger.error(
                    f"ユーザー作成中にデータベースのエラーが発生しました。: {e.orig}"
                )
                raise Exception(
                    f"ユーザー作成中にデータベースのエラーが発生しました。: {e.orig}"
                )

    def get_users(self, db: Session) -> List[UserEntity]:
        try:
            db_users = db.query(User).all()
            return [UserEntity.model_validate(user) for user in db_users]
        except SQLAlchemyError as e:
            logger.error(f"ユーザの取得中にエラーが発生しました: {e}")
            raise Exception("ユーザの取得に失敗しました") from e
        except Exception as e:
            logger.error(
                f"予期しないエラーが発生しました。管理者にお問い合わせください。: {e}"
            )
            raise

    def update_user(self, db: Session, user: UserEntity) -> Optional[UserEntity]:
        # TODO: mypyに引っかかるため、一旦Anyにする、処理の見直し必要あり
        db_user: Any = db.query(User).filter(User.email == user.email).first()
        if not db_user:
            return None
        db_user.display_name = user.display_name
        db.commit()
        db.refresh(db_user)
        return UserEntity.model_validate(db_user)

    def soft_delete_user(self, db: Session, cognito_user_id: str) -> None:
        # TODO: mypyに引っかかるため、一旦Anyにする、処理の見直し必要あり
        try:
            db_user: Any = (
                db.query(User)
                .filter(
                    User.cognito_user_id == cognito_user_id, User.deleted.is_(False)
                )
                .first()
            )
            if db_user:
                db_user.deleted = True
                db.commit()
            else:
                logger.error(
                    f"指定されたIDのユーザーは存在しません。 user_id: {cognito_user_id}"
                )
                raise EntityNotFoundError(
                    entity_name="User",
                    entity_id=0,
                    message="指定されたIDのユーザーは存在しません。",
                )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"ユーザー削除中にエラーが発生しました: {e}")
            raise Exception("ユーザーの削除に失敗しました") from e
        except Exception as e:
            db.rollback()
            logger.error(
                f"予期しないエラーが発生しました。管理者にお問い合わせください。: {e}"
            )
            raise

    def get_user_by_email(self, email: str) -> UserEntity:
        with readonly_transaction_scope() as db:
            try:
                db_user = (
                    db.query(User)
                    .filter(User.email == email, User.deleted.is_(False))
                    .one()
                )
            except exc.NoResultFound:
                logger.error(
                    f"指定されたメールアドレスのユーザーは存在しません。 email: {email}"
                )
                raise EntityNotFoundError(
                    entity_name="User",
                    entity_id=0,
                    message=f"指定されたメールアドレスのユーザーは存在しません。 email: {email}",
                )
            return UserEntity.model_validate(db_user)

    def create_cognito_user(self, user: UserEntity, password: str) -> None:
        if user.cognito_user_id is None:
            raise ValueError("cognito_user_id is required")
        if user.email is None:
            raise ValueError("email is required")

        try:
            self.cognito_client.sign_up(
                ClientId=settings.COGNITO_CLIENT_ID,  # App Client ID
                Username=user.cognito_user_id,
                Password=password,
                UserAttributes=[
                    {"Name": "email", "Value": user.email},
                ],
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "UsernameExistsException":
                logger.error(f"ユーザーは既に存在します: {user.cognito_user_id}")
                raise DuplicateError(
                    message=f"ユーザーは既に存在します: {user.cognito_user_id}"
                )
            else:
                logger.error(f"サインアップに失敗しました。: {e}")
                raise
        except Exception as e:
            logger.error(
                f"予期しないエラーが発生しました。管理者にお問い合わせください。: {e}"
            )
            raise

    def create_user_with_user_organization(
        self,
        user: UserEntity,
        organization_id: int,
        role: UserRole,
        password: str,
    ) -> UserEntity:
        with transaction_scope() as db:
            try:
                # ユーザ作成
                created_user = self.create_user(db=db, user=user)
                if created_user.id is None:
                    raise ValueError("ユーザーIDが生成されませんでした。")
                # ユーザ組織作成
                self.user_organization_repository.create_user_organization(
                    user_id=created_user.id,
                    organization_id=organization_id,
                    role=role,
                    db=db,  # ユーザ作成と同じセッションを渡す
                )
                # cognitoにユーザを登録
                self.create_cognito_user(user=user, password=password)
                return created_user
            except DuplicateError as e:
                raise DuplicateError(message=e.message)
            except EntityNotFoundError as e:
                raise EntityNotFoundError(
                    entity_name=e.entity_name,
                    entity_id=e.entity_id,
                    message=e.message,
                )

    def disable_user_on_cognito(self, cognito_user_id: str) -> None:
        disable_user(cognito_user_id)

    def enable_user_on_cognito(self, cognito_user_id: str) -> None:
        enable_user(cognito_user_id)

    def delete_user_on_cognito(self, cognito_user_id: str) -> None:
        delete_user(cognito_user_id)
