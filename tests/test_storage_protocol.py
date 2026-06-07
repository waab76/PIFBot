from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from utils.storage_protocol import StorageProtocol


def test_storage_protocol_has_all_methods() -> None:
    """Verify StorageProtocol defines the expected interface."""
    methods = [
        "save_pif",
        "get_open_pifs",
        "get_pif",
        "fetch_all_pifs",
        "open_pif_exists",
    ]
    for method in methods:
        assert hasattr(StorageProtocol, method)


def test_mock_can_satisfy_protocol() -> None:
    mock = MagicMock(spec=StorageProtocol)
    mock.save_pif.return_value = None
    mock.get_open_pifs.return_value = []
    mock.get_pif.return_value = None
    mock.fetch_all_pifs.return_value = []
    mock.open_pif_exists.return_value = False
