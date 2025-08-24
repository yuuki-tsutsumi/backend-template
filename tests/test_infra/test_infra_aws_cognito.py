from unittest.mock import MagicMock, patch

import pytest
from pytest import MonkeyPatch

from app.infra.repository.cognito import (
    create_cognito_client,
    delete_user,
    disable_user,
    enable_user,
)


@pytest.fixture
def mock_settings(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("app.infra.repository.cognito.settings.SERVICE_ENV", "local")
    monkeypatch.setattr(
        "app.infra.repository.cognito.settings.COGNITO_USER_POOL_ID", "mock-pool-id"
    )


def test_create_mock_cognito_user_pool(mock_settings: MonkeyPatch) -> None:
    client = create_cognito_client()
    response = client.create_user_pool(PoolName="Mock")
    assert response["UserPool"]["Id"] == "mock-user-pool-id"
    assert response["UserPool"]["Name"] == "mock-user-pool"


def test_disable_user_calls_admin_disable_user(mock_settings: MonkeyPatch) -> None:
    with patch(
        "app.infra.repository.cognito.create_cognito_client"
    ) as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        disable_user("mock-user-id")

        mock_client.admin_disable_user.assert_called_once_with(
            UserPoolId="mock-pool-id",
            Username="mock-user-id",
        )


def test_enable_user_calls_admin_enable_user(mock_settings: MonkeyPatch) -> None:
    with patch(
        "app.infra.repository.cognito.create_cognito_client"
    ) as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        enable_user("mock-user-id")

        mock_client.admin_enable_user.assert_called_once_with(
            UserPoolId="mock-pool-id",
            Username="mock-user-id",
        )


def test_delete_user_calls_admin_delete_user(mock_settings: MonkeyPatch) -> None:
    with patch(
        "app.infra.repository.cognito.create_cognito_client"
    ) as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        delete_user("mock-user-id")

        mock_client.admin_delete_user.assert_called_once_with(
            UserPoolId="mock-pool-id",
            Username="mock-user-id",
        )
