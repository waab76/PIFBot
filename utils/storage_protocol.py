import abc
from typing import Any

from pifs.models import PifStorageDict


class StorageProtocol(abc.ABC):
    @abc.abstractmethod
    def save_pif(self, pif_obj: Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_open_pifs(self) -> list[PifStorageDict]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_pif(self, post_id: str) -> PifStorageDict | None:
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_all_pifs(self) -> list[PifStorageDict]:
        raise NotImplementedError

    @abc.abstractmethod
    def open_pif_exists(self, post_id: str) -> bool:
        raise NotImplementedError
