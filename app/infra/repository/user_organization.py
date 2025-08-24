import logging
from datetime import datetime
from typing import List

import pytz
from psycopg2 import errors as psycopg2_errors
from sqlalchemy import desc, exc
from sqlalchemy.orm import Session

from app.domain.entity.user_organization import (
    UserOrganization as UserOrganizationEntity,
)
from app.domain.entity.user_organization import (
    UserRole,
)
from app.domain.i_repository.user_organization import UserOrganizationIRepository
from app.infra.models.user_organization import UserOrganization
from app.infra.models.user_organization import UserOrganization as UserOrganizationModel
from app.infra.repository.db import readonly_transaction_scope
from app.usecase.error import (
    DuplicateError,
    EntityNotFoundError,
    GetListUserOrganizationByUserIdEmptyError,
)

logger = logging.getLogger(__name__)
japan_tz = pytz.timezone("Asia/Tokyo")


class UserOrganizationRepository(UserOrganizationIRepository):
    def get_role_by_user_id_and_organization_id(
        self, user_id: int, organization_id: int
    ) -> UserRole:
        with readonly_transaction_scope() as db:
            try:
                db_user_org = (
                    db.query(UserOrganizationModel)
                    .filter(UserOrganizationModel.user_id == user_id)
                    .filter(UserOrganizationModel.organization_id == organization_id)
                    .one()
                )
                return UserRole(db_user_org.role)
            except exc.NoResultFound:
                logger.error(
                    f"指定された組織が存在しないか、組織にユーザーが所属していません。 user_id: {user_id}, organization_id: {organization_id}"
                )
                raise EntityNotFoundError(
                    entity_name="UserOrganization",
                    entity_id=organization_id,
                    message=f"指定された組織が存在しないか、組織にユーザーが所属していません。 user_id: {user_id}, organization_id: {organization_id}",
                )

    def create_user_organization(
        self, user_id: int, organization_id: int, role: UserRole, db: Session
    ) -> UserOrganizationEntity:
        # NOTE: 呼び出し元でトランザクションを管理しているため、ここではトランザクションを管理しない
        try:
            now_utc = datetime.now(pytz.utc)
            now = now_utc.astimezone(japan_tz)
            db_user_organization = UserOrganizationModel(
                user_id=user_id,
                organization_id=organization_id,
                role=role.value,
                created_at=now,
                updated_at=now,
            )
            db.add(db_user_organization)
            db.flush()
            db.refresh(db_user_organization)
            return UserOrganizationEntity.model_validate(db_user_organization)
        except exc.IntegrityError as e:
            if isinstance(e.orig, psycopg2_errors.ForeignKeyViolation):
                # 外部キー制約違反の場合
                logger.error(f"外部キー制約違反が発生しました: {str(e)}")
                raise EntityNotFoundError(
                    entity_name="UserOrganization",
                    entity_id=organization_id,
                    message=f"指定された組織が存在しないか、組織にユーザーが所属していません。 user_id: {user_id}, organization_id: {organization_id}",
                )
            elif isinstance(e.orig, psycopg2_errors.UniqueViolation):
                # 一意性制約違反の場合
                logger.error(f"一意性制約違反が発生しました: {str(e)}")
                raise DuplicateError(
                    message=f"指定されたユーザーは既に組織に所属しています。 user_id: {user_id}, organization_id: {organization_id}"
                )
            else:
                # その他のIntegrityErrorの場合
                logger.error(f"予期せぬエラーが発生しました: {str(e)}")
                raise e

    def get_user_organizations_by_user_id(
        self, user_id: int
    ) -> List[UserOrganizationEntity]:
        with readonly_transaction_scope() as db:
            # TODO: updated_at列の値でソートしているが暫定的な処理である。対応方針を検討する必要あり。
            db_user_organizations = (
                db.query(UserOrganization)
                .filter(UserOrganization.user_id == user_id)
                .order_by(desc(UserOrganization.updated_at))
                .all()
            )
            if db_user_organizations == []:
                raise GetListUserOrganizationByUserIdEmptyError(user_id=user_id)
            else:
                return [
                    UserOrganizationEntity.model_validate(user_organization)
                    for user_organization in db_user_organizations
                ]

    def is_user_in_organization_exist(self, user_id: int, organization_id: int) -> bool:
        with readonly_transaction_scope() as db:
            db_user_org = (
                db.query(UserOrganization)
                .filter(UserOrganization.user_id == user_id)
                .filter(UserOrganization.organization_id == organization_id)
                .first()
            )

            return db_user_org is not None
