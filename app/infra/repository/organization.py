import logging
from datetime import datetime
from typing import cast

import pytz
from sqlalchemy import Column
from sqlalchemy.exc import NoResultFound

from app.domain.constants import NOT_SPECIFIED_ID
from app.domain.entity.organization import Organization as OrganizationEntity
from app.domain.i_repository.organization import OrganizationIRepository
from app.infra.models.organization import Organization
from app.infra.repository.db import readonly_transaction_scope, transaction_scope
from app.usecase.error import ConflictError, EntityNotFoundError

japan_tz = pytz.timezone("Asia/Tokyo")

logger = logging.getLogger(__name__)


class OrganizationRepository(OrganizationIRepository):
    def save_organization(self, org: OrganizationEntity) -> OrganizationEntity:
        now_utc = datetime.now(pytz.utc)
        now = now_utc.astimezone(japan_tz)

        with transaction_scope() as db:
            if org.id == NOT_SPECIFIED_ID:
                # 新しいレコードを作成
                org_rec = Organization(
                    name=org.name,
                    created_at=now,
                    updated_at=now,
                )
                db.add(org_rec)
            else:
                # 既存のレコードを更新
                try:
                    existing_org = (
                        db.query(Organization).filter(Organization.id == org.id).one()
                    )

                    if org.updated_at and (
                        cast(datetime, existing_org.updated_at) != org.updated_at
                    ):
                        logger.error(
                            f"他のユーザが先に更新したため、{existing_org.name}の更新に失敗しました。"
                        )
                        raise ConflictError(entity_name=cast(str, existing_org.name))
                    existing_org.billing_phone = cast(Column[str], org.billing_phone)
                    if org.deleted is not None:
                        existing_org.deleted = cast(Column[bool], org.deleted)
                    existing_org.updated_at = now

                    org_rec = existing_org
                except NoResultFound:
                    logger.error(
                        f"指定された組織が見つかりません organization_id: {org.id}"
                    )
                    raise EntityNotFoundError(
                        entity_name="OrganizationEntity",
                        entity_id=org.id if org.id is not None else NOT_SPECIFIED_ID,
                        message=f"指定された組織が見つかりません organization_id: {org.id}",
                    )
            db.flush()
            db.refresh(org_rec)
            return self.convert_organization_model_to_entity(org_rec)

    def get_organization(
        self, organization_id: int, exclude_deleted: bool = False
    ) -> OrganizationEntity:
        with readonly_transaction_scope() as db:
            try:
                query = db.query(Organization).filter(
                    Organization.id == organization_id
                )
                if exclude_deleted:
                    query = query.filter(Organization.deleted.is_(False))
                db_organization = query.one()
                return OrganizationEntity.model_validate(db_organization)
            except NoResultFound:
                logger.error(
                    f"指定された組織が見つかりません organization_id: {organization_id}"
                )
                raise EntityNotFoundError(
                    entity_name="OrganizationEntity",
                    entity_id=organization_id,
                    message=f"指定された組織が見つかりません organization_id: {organization_id}",
                )

    def get_all_organizations(
        self, exclude_deleted: bool = False
    ) -> list[OrganizationEntity]:
        with readonly_transaction_scope() as db:
            query = db.query(Organization)
            if exclude_deleted:
                query = query.filter(Organization.deleted.is_(False))
            db_organizations = query.all()
            organization_list: list[OrganizationEntity] = [
                self.convert_organization_model_to_entity(db_org)
                for db_org in db_organizations
            ]
            return organization_list

    def is_organization_exist(self, organization_id: int) -> bool:
        with readonly_transaction_scope() as db:
            db_organization = (
                db.query(Organization)
                .filter(Organization.id == organization_id)
                .first()
            )

            return db_organization is not None

    def convert_organization_model_to_entity(
        self, db_org: Organization
    ) -> OrganizationEntity:
        org_entity = OrganizationEntity(
            id=cast(int, db_org.id),
            name=cast(str, db_org.name),
            deleted=cast(bool, db_org.deleted),
            created_at=cast(datetime, db_org.created_at),
            updated_at=cast(datetime, db_org.updated_at),
        )

        return OrganizationEntity.model_validate(org_entity)
