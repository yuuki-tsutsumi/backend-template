import logging
from dataclasses import dataclass
from typing import List, Optional

from injector import inject
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from app.domain.entity.user import User as UserEntity
from app.domain.entity.user_organization import UserRole
from app.domain.i_repository.organization import OrganizationIRepository
from app.domain.i_repository.user import UserIRepository
from app.infra.repository.db import transaction_scope
from app.usecase.error import (
    EntityNotFoundError,
    MemberAccessDeniedError,
    OrgMemberAccessDeniedError,
    ValidationParamError,
)

logger = logging.getLogger(__name__)


class UserCreateParams(BaseModel):
    cognito_user_id: str = Field(..., min_length=1, description="cognitoのユーザID")
    email: EmailStr = Field(..., description="メールアドレス")
    display_name: str = Field(..., min_length=1, max_length=100, description="名前")
    role: str = Field(..., description="役割")
    organization_id: int = Field(..., gt=0, description="組織ID")
    password: str = Field(..., description="パスワード")

    @field_validator("cognito_user_id")
    @classmethod
    def cognito_user_id_must_be_str(cls, v: str) -> str:
        if not v.strip():
            raise ValidationParamError("cognitoのユーザIDは必須です")
        return v

    @field_validator("email")
    @classmethod
    def email_must_be_str(cls, v: EmailStr) -> EmailStr:
        if not v.strip():
            raise ValidationParamError("メールアドレスは必須です")
        return v

    @field_validator("display_name")
    @classmethod
    def display_name_must_be_str(cls, v: str) -> str:
        if not v.strip():
            raise ValidationParamError("名前は必須です")
        return v

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        try:
            UserRole(v)
            return v
        except ValueError:
            raise ValidationParamError("無効な役割が指定されています")

    @field_validator("organization_id")
    @classmethod
    def organization_id_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValidationParamError("組織IDは1以上の整数である必要があります")
        return v


class UserUpdateParams(BaseModel):
    # TODO: バリデーションの見直しが必要。一旦全項目必須とする
    email: EmailStr = Field(..., description="メールアドレス")
    name: str = Field(..., min_length=1, description="名前")
    role: int = Field(..., description="役割")


@inject
@dataclass
class UserUsecase:
    user_repository: UserIRepository
    organization_repository: OrganizationIRepository

    def create_user(self, role: UserRole, params: UserCreateParams) -> UserEntity:

        # ユーザーを作成
        user_params = params.model_dump()

        if role is UserRole.MEMBER:
            raise MemberAccessDeniedError()
        if role is UserRole.ORG_ADMIN and user_params["role"] == UserRole.APP_ADMIN:
            raise OrgMemberAccessDeniedError()
        if not self.organization_repository.is_organization_exist(
            user_params["organization_id"]
        ):
            raise EntityNotFoundError(
                entity_name="Organization",
                entity_id=user_params["organization_id"],
                message=f"指定された組織が存在しません。organization_id: {user_params['organization_id']}",
            )

        # 必要なフィールドのみでUserEntityを作成
        user = UserEntity(
            cognito_user_id=params.cognito_user_id,
            email=params.email,
            display_name=params.display_name,
        )
        # ユーザーとユーザー組織を作成
        return self.user_repository.create_user_with_user_organization(
            user=user,
            organization_id=user_params["organization_id"],
            role=UserRole(user_params["role"]),
            password=user_params["password"],
        )

    def get_users(self, db: Session) -> List[UserEntity]:
        return self.user_repository.get_users(db)

    def update_user(
        self, db: Session, params: UserUpdateParams
    ) -> Optional[UserEntity]:
        user = UserEntity(**params.model_dump())
        return self.user_repository.update_user(db, user)

    def delete_user(self, cognito_user_id: str) -> None:
        """
        ユーザーを段階的に削除する

        1. Cognito 上のユーザーを一時的に無効化する
        2. DB 上のユーザーを論理削除する
        3. 上記 DB 論理削除が成功した場合、Cognito 上のユーザーを完全に削除する
        """
        with transaction_scope() as db:
            try:
                # cognito user disable
                self.user_repository.disable_user_on_cognito(cognito_user_id)
                try:
                    # DB論理削除
                    self.user_repository.soft_delete_user(db, cognito_user_id)

                except Exception as db_err:
                    # 論理削除失敗時、cognito userをenable
                    try:
                        self.user_repository.enable_user_on_cognito(cognito_user_id)
                        logger.info(
                            "DBの削除に失敗したため、Cognitoユーザーを再有効化しました"
                        )
                    except Exception as e:
                        logger.error(f"Cognitoユーザーの再有効化にも失敗しました: {e}")
                    raise db_err

                # Cognito完全削除
                self.user_repository.delete_user_on_cognito(cognito_user_id)
            except Exception as e:
                logger.error(f"ユーザー削除処理に失敗しました: {e}")
                raise

    def get_user_by_email(self, email: str) -> UserEntity:
        try:
            return self.user_repository.get_user_by_email(email=email)
        except EntityNotFoundError as e:
            raise EntityNotFoundError(
                entity_name=e.entity_name,
                entity_id=e.entity_id,
                message=e.message,
            )
