from abc import ABC, abstractmethod
from typing import Any


class S3IRepository(ABC):
    @abstractmethod
    def get_docx_file(self, key: str, bucket_name: str) -> Any:
        pass
