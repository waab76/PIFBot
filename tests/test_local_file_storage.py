from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from utils.local_file_storage import LocalFileStorage
from pifs.models import PifStorageDict


def _mock_pif(post_id: str, storage_dict: PifStorageDict) -> Mock:
    """Build a mock with the interface LocalFileStorage.save_pif expects."""
    m = Mock()
    m.postId = post_id
    m.to_storage_dict.return_value = storage_dict
    return m


def _open_storage_dict(post_id: str) -> PifStorageDict:
    return {
        "SubmissionId": post_id,
        "Author": "author",
        "PifType": "lottery",
        "MinKarma": 50,
        "DurationHours": 24,
        "ExpireTime": 9999999999,
        "PifState": "open",
        "PifWinner": "TBD",
        "PifOptions": {},
        "PifEntries": {},
        "KarmaFail": {},
    }


def test_save_and_get_pif(tmp_path: Path) -> None:
    storage = LocalFileStorage(str(tmp_path / "pifs.json"))
    data = _open_storage_dict("post_1")
    pif = _mock_pif("post_1", data)
    storage.save_pif(pif)
    result = storage.get_pif("post_1")
    assert result is not None
    assert result["SubmissionId"] == "post_1"


def test_get_open_pifs(tmp_path: Path) -> None:
    storage = LocalFileStorage(str(tmp_path / "pifs.json"))
    open_dict = _open_storage_dict("post_1")
    closed_dict = _open_storage_dict("post_2")
    closed_dict["PifState"] = "closed"
    storage.save_pif(_mock_pif("post_1", open_dict))
    storage.save_pif(_mock_pif("post_2", closed_dict))
    open_pifs = storage.get_open_pifs()
    assert len(open_pifs) == 1
    assert open_pifs[0]["SubmissionId"] == "post_1"


def test_open_pif_exists(tmp_path: Path) -> None:
    storage = LocalFileStorage(str(tmp_path / "pifs.json"))
    data = _open_storage_dict("post_1")
    storage.save_pif(_mock_pif("post_1", data))
    assert storage.open_pif_exists("post_1")
    assert not storage.open_pif_exists("nonexistent")


def test_fetch_all_pifs(tmp_path: Path) -> None:
    storage = LocalFileStorage(str(tmp_path / "pifs.json"))
    d1 = _open_storage_dict("post_1")
    d2 = _open_storage_dict("post_2")
    storage.save_pif(_mock_pif("post_1", d1))
    storage.save_pif(_mock_pif("post_2", d2))
    all_pifs = storage.fetch_all_pifs()
    assert len(all_pifs) == 2


def test_load_handles_missing_file(tmp_path: Path) -> None:
    storage = LocalFileStorage(str(tmp_path / "nonexistent.json"))
    assert storage.fetch_all_pifs() == []


def test_load_handles_corrupt_file(tmp_path: Path) -> None:
    p = tmp_path / "corrupt.json"
    p.write_text("not valid json")
    storage = LocalFileStorage(str(p))
    assert storage.fetch_all_pifs() == []
