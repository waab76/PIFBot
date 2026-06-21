from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import finalize as finalize_module


def test_finalize_calls_save_pif_after_finalizing(mocker: Any) -> None:
    mock_pif = Mock()
    mocker.patch("finalize.get_pif", return_value=mock_pif)
    mock_save = mocker.patch("finalize.save_pif")
    finalize_module.finalize("post_1")
    mock_save.assert_called_once_with(mock_pif)
