from typing import List

from ..api.api_manager import YepCodeApiManager
from ..api.types import CreateStorageObjectInput, StorageObject, YepCodeApiConfig


class YepCodeStorage:
    def __init__(self, config: YepCodeApiConfig = None):
        """
        Initialize YepCodeStorage with optional configuration.

        Args:
            config: YepCodeApiConfig instance for API configuration
        """
        self._api = YepCodeApiManager.get_instance(config)

    def download(self, name: str) -> bytes:
        return self._api.get_object(name).content

    def upload(self, name: str, file: bytes) -> StorageObject:
        return self._api.create_object(
            CreateStorageObjectInput(name=name, file=file)
        )

    def delete(self, name: str) -> None:
        return self._api.delete_object(name)

    def list(self) -> List[StorageObject]:
        return self._api.get_objects()
