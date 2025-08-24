import pytest
from freezegun import freeze_time
from sqlalchemy.orm import Session

from app.domain.entity.user_organization import UserRole
from app.infra.repository.user_organization import UserOrganizationRepository
from app.usecase.error import EntityNotFoundError
from app.usecase.user_organization import UserOrganizationUsecase
from tests.common import fixed_time_freezgun
from tests.factories.organization import create_organization
from tests.factories.user import create_user
from tests.factories.user_organization import create_user_organization


@pytest.fixture
def user_organization_repository(db: Session) -> UserOrganizationRepository:
    """UserOrganizationRepositoryのfixture"""
    return UserOrganizationRepository()


@pytest.fixture
def user_organization_usecase(
    db: Session, user_organization_repository: UserOrganizationRepository
) -> UserOrganizationUsecase:
    """UserOrganizationUsecaseのfixture"""
    return UserOrganizationUsecase(
        user_organization_repository=user_organization_repository
    )


@freeze_time(fixed_time_freezgun)
def test_get_role_by_user_id_and_organization_id(
    user_organization_usecase: UserOrganizationUsecase,
) -> None:
    """ユーザーIDと組織IDからロールを取得できることを確認する"""
    # テストデータの作成
    create_user(
        id=1, cognito_user_id="test", email="test@example.com", display_name="test_user"
    )
    create_organization(id=1, name="test_organization")
    create_user_organization(user_id=1, organization_id=1, role=UserRole.APP_ADMIN)

    # ユースケースの実行
    result = user_organization_usecase.get_role_by_user_id_and_organization_id(
        user_id=1, organization_id=1
    )

    # 検証
    assert result == UserRole.APP_ADMIN.value


@freeze_time(fixed_time_freezgun)
def test_get_role_by_user_id_and_organization_not_found(
    db: Session, user_organization_usecase: UserOrganizationUsecase
) -> None:
    """存在しないユーザーIDと組織IDの組み合わせの場合にEntityNotFoundErrorが発生することを確認する"""
    # 存在しない組み合わせで検索
    with pytest.raises(EntityNotFoundError) as excinfo:
        user_organization_usecase.get_role_by_user_id_and_organization_id(
            user_id=999, organization_id=999
        )

    assert (
        str(excinfo.value)
        == "指定された組織が存在しないか、組織にユーザーが所属していません。 user_id: 999, organization_id: 999"
    )


@freeze_time(fixed_time_freezgun)
def test_get_role_by_user_id_and_organization_id_roles(
    db: Session, user_organization_usecase: UserOrganizationUsecase
) -> None:
    """同一ユーザーが複数の組織に所属している場合に、指定した組織のロールが取得できることを確認する"""
    # テストデータの作成
    create_user(
        id=1, cognito_user_id="test", email="test@example.com", display_name="test_user"
    )
    create_organization(id=1, name="test_organization1")
    create_organization(id=2, name="test_organization2")

    # 複数の組織に異なるロールで所属
    create_user_organization(user_id=1, organization_id=1, role=UserRole.APP_ADMIN)
    create_user_organization(user_id=1, organization_id=2, role=UserRole.MEMBER)

    # ユースケースの実行（organization1のロールを取得）
    result1 = user_organization_usecase.get_role_by_user_id_and_organization_id(
        user_id=1, organization_id=1
    )

    # ユースケースの実行（organization2のロールを取得）
    result2 = user_organization_usecase.get_role_by_user_id_and_organization_id(
        user_id=1, organization_id=2
    )

    # 検証
    assert result1 == UserRole.APP_ADMIN.value
    assert result2 == UserRole.MEMBER.value
