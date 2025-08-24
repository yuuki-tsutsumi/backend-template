from io import BytesIO
from typing import Any

import boto3
from docx import Document
from mypy_boto3_s3 import S3Client

from app.config import settings
from app.domain.i_repository.s3 import S3IRepository


def create_s3_client() -> S3Client:
    try:
        if settings.SERVICE_ENV == "local":
            s3 = boto3.client(
                "s3",
                endpoint_url=f"http://{settings.LOCALSTACK_HOST}:4566",
                aws_access_key_id="dummy",
                aws_secret_access_key="dummy",
                region_name="dummy",
            )
        else:
            s3 = boto3.client(
                "s3",
                endpoint_url=None,
            )
        return s3
    except Exception as e:
        raise RuntimeError(f"Failed to create an S3 client: {e}")


class S3Repository(S3IRepository):
    def __init__(self) -> None:
        self.s3_client = create_s3_client()

    def get_docx_file(self, key: str, bucket_name: str) -> Any:
        s3 = self.s3_client
        response = s3.get_object(Bucket=bucket_name, Key=key)
        docx_data = response["Body"].read()
        docx_io = BytesIO(docx_data)
        return Document(docx_io)
