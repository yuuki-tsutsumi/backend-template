from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str = Field("")
    DB_PASSWORD: str = Field("")
    DB_HOST: str = Field("")
    DB_PORT: str = Field("")
    DB_NAME: str = Field("")
    TEST_DB_NAME: str = Field("")
    LOCALSTACK_HOST: str = Field("")
    CORS_ORIGINS: str = Field("")
    SERVICE_ENV: str = Field("")
    BASIC_USERNAME: str = Field("")
    BASIC_PASSWORD: str = Field("")
    AWS_ACCOUNT_ID: str = Field("")
    AWS_REGION: str = Field("")
    COGNITO_USER_POOL_ID: str = Field("")
    COGNITO_CLIENT_ID: str = Field("")
    COGNITO_DOMAIN: str = Field("")
    OPENAI_API_KEY: str = Field("")
    AWS_ACCESS_KEY_ID: str = Field("")
    AWS_SECRET_ACCESS_KEY: str = Field("")
    AWS_SESSION_TOKEN: str = Field("")
    AI_ENV: str = Field("")
    AZURE_OPENAI_API_KEY: str = Field("")
    AZURE_OPENAI_ENDPOINT: str = Field("")
    AZURE_OPENAI_MODEL: str = Field("")
    AZURE_OPENAI_API_VERSION: str = Field("")

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )


# NOTE: 引数を指定しなくてもpydanticが割り当てているので、対応不要のため、無視。
settings = Settings()  # type: ignore
