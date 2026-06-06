import json
import logging
import os
import threading
from typing import Any

from pifs.models import PifStorageDict
from utils.storage_protocol import StorageProtocol


class LocalFileStorage(StorageProtocol):
    def __init__(self, path: str = "/tmp/pifbot_storage/pifs.json") -> None:
        self.path = path
        self._lock = threading.Lock()
        self._cache: dict[str, PifStorageDict] | None = None
        self._load()

    def _load(self) -> None:
        try:
            with open(self.path) as f:
                self._cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._cache = {}

    def _flush(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w") as f:
                json.dump(self._cache, f, indent=2)
        except OSError as e:
            logging.error("Failed to write PIF storage to %s: %s", self.path, e)

    def save_pif(self, pif_obj: Any) -> None:
        logging.debug("Storing PIF [%s] to local file", pif_obj.postId)
        with self._lock:
            assert self._cache is not None
            self._cache[pif_obj.postId] = pif_obj.to_storage_dict()
            self._flush()

    def get_open_pifs(self) -> list[PifStorageDict]:
        with self._lock:
            assert self._cache is not None
            return [v for v in self._cache.values() if v["PifState"] == "open"]

    def get_pif(self, post_id: str) -> PifStorageDict | None:
        with self._lock:
            assert self._cache is not None
            return self._cache.get(post_id)

    def fetch_all_pifs(self) -> list[PifStorageDict]:
        with self._lock:
            assert self._cache is not None
            return list(self._cache.values())

    def open_pif_exists(self, post_id: str) -> bool:
        with self._lock:
            assert self._cache is not None
            pif = self._cache.get(post_id)
        return pif is not None and pif["PifState"] == "open"
