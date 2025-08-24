import logging
from typing import cast
from unittest.mock import MagicMock

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_cognito_idp import CognitoIdentityProviderClient

from app.config import settings
from app.infra.repository.error_codes import CognitoErrorCode
from app.usecase.error import EntityNotFoundError

logger = logging.getLogger(__name__)


def create_cognito_client() -> CognitoIdentityProviderClient:
    try:
        if settings.SERVICE_ENV == "local":
            # LocalStackでは Cognito IDPがPro限定のため、モックを使用
            mock_client = MagicMock()

            # create_user_pool のモックレスポンスを定義
            mock_client.create_user_pool.return_value = {
                "UserPool": {
                    "Id": "mock-user-pool-id",
                    "Name": "mock-user-pool",
                }
            }

            return cast(CognitoIdentityProviderClient, mock_client)

        else:
            return boto3.client(
                "cognito-idp",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                aws_session_token=settings.AWS_SESSION_TOKEN,
            )
    except Exception as e:
        raise RuntimeError(f"Failed to create a Cognito client: {e}")


def disable_user(cognito_user_id: str) -> None:
    """Cognito上のユーザーを無効化する"""
    try:
        cognito_client = create_cognito_client()
        cognito_client.admin_disable_user(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=cognito_user_id,
        )
        logger.info(f"Cognitoユーザーを無効化しました: {cognito_user_id}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == CognitoErrorCode.USER_NOT_FOUND_EXCEPTION:
            logger.error(
                f"指定されたIDのユーザーはCognito User Poolに存在しません。 user_id: {cognito_user_id}"
            )
            raise EntityNotFoundError(
                entity_name="User",
                entity_id=0,
                message="指定されたIDのユーザーは存在しません。",
            )
        else:
            logger.error(f"Cognitoユーザー無効化中にエラーが発生しました: {e}")
            raise Exception("Cognitoユーザーの無効化に失敗しました") from e
    except Exception as e:
        logger.error(f"エラーが発生しました（Cognito無効化）: {e}")
        raise


def enable_user(cognito_user_id: str) -> None:
    """Cognito上のユーザーを再有効化する"""
    try:
        cognito_client = create_cognito_client()
        cognito_client.admin_enable_user(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=cognito_user_id,
        )
        logger.info(f"Cognitoユーザーを再有効化しました: {cognito_user_id}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == CognitoErrorCode.USER_NOT_FOUND_EXCEPTION:
            logger.error(f"Cognito上に存在しないユーザー: {cognito_user_id}")
            raise EntityNotFoundError(
                entity_name="User",
                entity_id=0,
                message="指定されたIDのユーザーは存在しません。",
            )
        else:
            logger.error(f"Cognitoユーザー再有効化中にエラーが発生しました: {e}")
            raise Exception("Cognitoユーザーの再有効化に失敗しました") from e
    except Exception as e:
        logger.error(f"エラーが発生しました（Cognito再有効化）: {e}")
        raise


def delete_user(cognito_user_id: str) -> None:
    """Cognito上のユーザーを完全に削除する"""
    try:
        cognito_client = create_cognito_client()
        cognito_client.admin_delete_user(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=cognito_user_id,
        )
        logger.info(f"Cognitoユーザーを削除しました: {cognito_user_id}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == CognitoErrorCode.USER_NOT_FOUND_EXCEPTION:
            logger.warning(f"Cognito上に既に存在しないユーザー: {cognito_user_id}")
        else:
            logger.error(f"Cognitoユーザー削除中にエラーが発生しました: {e}")
            raise Exception("Cognitoユーザーの削除に失敗しました") from e
    except Exception as e:
        logger.error(f"エラーが発生しました（Cognito削除）: {e}")
        raise
