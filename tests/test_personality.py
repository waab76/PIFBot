from __future__ import annotations

from unittest.mock import patch

from utils.personality import get_bad_command_response


def test_get_bad_command_response_returns_a_string() -> None:
    result = get_bad_command_response()
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_bad_command_response_from_list() -> None:
    with patch("random.choice", return_value="Go home, you're drunk."):
        assert get_bad_command_response() == "Go home, you're drunk."
