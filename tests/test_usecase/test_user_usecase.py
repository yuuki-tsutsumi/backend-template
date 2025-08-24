from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time
from sqlalchemy.orm import Session

from app.config import settings
from app.domain.i_repository.organization import OrganizationIRepository
from app.domain.i_repository.user import UserIRepository
from app.domain.i_repository.user_organization import UserOrganizationIRepository
from app.infra.models.user import User
from app.infra.repository.organization import OrganizationRepository
from app.infra.repository.user import UserRepository
from app.infra.repository.user_organization import UserOrganizationRepository
from app.usecase.error import EntityNotFoundError
from app.usecase.user import UserUsecase
from tests.common import fixed_time_freezgun
from tests.factories.user import create_user


@pytest.fixture
def user_organization_repository() -> UserOrganizationIRepository:
    """UserOrganizationRepositoryのfixture"""
    return UserOrganizationRepository()


@pytest.fixture
def user_repository(
    db: Session, user_organization_repository: UserOrganizationIRepository
) -> UserIRepository:
    """UserRepositoryのfixture"""
    return UserRepository(user_organization_repository=user_organization_repository)


@pytest.fixture
def organization_repository() -> OrganizationIRepository:
    """OrganizationRepository の fixture"""
    return OrganizationRepository()


@pytest.fixture
def user_usecase(
    db: Session,
    user_repository: UserIRepository,
    organization_repository: OrganizationIRepository,
) -> UserUsecase:
    """UserUsecaseのfixture"""
    return UserUsecase(
        user_repository=user_repository,
        organization_repository=organization_repository,
    )


@freeze_time(fixed_time_freezgun)
def test_get_user_by_email(db: Session, user_usecase: UserUsecase) -> None:
    """メールアドレスからユーザーを取得できることを確認する"""
    # テストデータの作成
    email = "test@org.com"
    user = create_user(
        id=1, cognito_user_id="test", email=email, display_name="test_user"
    )

    # ユースケースの実行
    result = user_usecase.get_user_by_email(email=email)

    # 検証
    assert result.id == user.id
    assert result.cognito_user_id == user.cognito_user_id
    assert result.email == email
    assert result.display_name == user.display_name


@freeze_time(fixed_time_freezgun)
def test_get_user_by_email_not_found(db: Session, user_usecase: UserUsecase) -> None:
    """存在しないメールアドレスの場合にEntityNotFoundErrorが発生することを確認する"""
    # 存在しないメールアドレスで検索
    with pytest.raises(EntityNotFoundError) as excinfo:
        user_usecase.get_user_by_email(email="org@org.com")

    assert (
        str(excinfo.value)
        == "指定されたメールアドレスのユーザーは存在しません。 email: org@org.com"
    )


@freeze_time(fixed_time_freezgun)
def test_delete_user_by_cognito_user_id(db: Session, user_usecase: UserUsecase) -> None:
    """cognito_user_idからユーザーを削除できることを確認する"""
    # テストデータ作成
    cognito_user_id = "test"
    create_user(
        id=1,
        cognito_user_id=cognito_user_id,
        email="test1234@org.com",
        display_name="test_user",
    )

    with patch(
        "app.infra.repository.cognito.create_cognito_client"
    ) as mock_create_client:
        # 2. モッククライアント作成
        mock_cognito_client = MagicMock()
        mock_create_client.return_value = mock_cognito_client

        # 3. ユーザー削除実行
        user_usecase.delete_user(cognito_user_id=cognito_user_id)

        # 4. DB論理削除確認
        deleted_user = (
            db.query(User).filter(User.cognito_user_id == cognito_user_id).first()
        )
        assert deleted_user is not None
        assert deleted_user.deleted is True

        # 5. Cognito クライアントメソッドが呼ばれたことを検証
        mock_cognito_client.admin_disable_user.assert_called_once_with(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=cognito_user_id,
        )
        mock_cognito_client.admin_delete_user.assert_called_once_with(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=cognito_user_id,
        )


@freeze_time(fixed_time_freezgun)
def test_delete_user_not_found(db: Session, user_usecase: UserUsecase) -> None:
    """存在しないユーザーを削除しようとしたときにEntityNotFoundErrorが発生することを確認"""
    with pytest.raises(EntityNotFoundError):
        user_usecase.delete_user(cognito_user_id="test")


def test_delete_user_db_failure_triggers_cognito_reenable(
    user_usecase: UserUsecase,
) -> None:
    cognito_user_id = "test-user-id"

    with patch.object(
        user_usecase.user_repository, "disable_user_on_cognito"
    ) as mock_disable, patch.object(
        user_usecase.user_repository,
        "soft_delete_user",
        side_effect=Exception("DB失敗"),
    ) as mock_delete_db, patch.object(
        user_usecase.user_repository, "enable_user_on_cognito"
    ) as mock_enable, patch.object(
        user_usecase.user_repository, "delete_user_on_cognito"
    ) as mock_delete_cognito:

        with pytest.raises(Exception) as excinfo:
            user_usecase.delete_user(cognito_user_id=cognito_user_id)

        assert "DB失敗" in str(excinfo.value)
        mock_disable.assert_called_once_with(cognito_user_id)
        mock_delete_db.assert_called_once()
        mock_enable.assert_called_once_with(cognito_user_id)
        mock_delete_cognito.assert_not_called()


def test_delete_user_cognito_final_delete_fails(user_usecase: UserUsecase) -> None:
    cognito_user_id = "test-user-id"

    with patch.object(
        user_usecase.user_repository, "disable_user_on_cognito"
    ) as mock_disable, patch.object(
        user_usecase.user_repository, "soft_delete_user"
    ) as mock_delete_db, patch.object(
        user_usecase.user_repository,
        "delete_user_on_cognito",
        side_effect=Exception("Cognito削除失敗"),
    ) as mock_delete_cognito:

        with pytest.raises(Exception) as excinfo:
            user_usecase.delete_user(cognito_user_id=cognito_user_id)

        assert "Cognito削除失敗" in str(excinfo.value)
        mock_disable.assert_called_once_with(cognito_user_id)
        mock_delete_db.assert_called_once()
        mock_delete_cognito.assert_called_once_with(cognito_user_id)
