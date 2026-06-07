from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from pifs.karma_checker import KarmaCheckResult, check_karma


def test_check_karma_blacklisted_user(mocker: Any) -> None:
    user = Mock()
    user.name = "bad_user"
    result = check_karma(user, 50, "post_1")
    assert not result.passed
    assert result.reason == "blacklisted"


def test_check_karma_passes(mocker: Any) -> None:
    user = Mock()
    user.name = "good_user"
    mocker.patch(
        "pifs.karma_checker.calculate_karma",
        return_value=(100, 5, 20, 0, 0),
    )
    mocker.patch(
        "pifs.karma_checker.formatted_karma",
        return_value="Good karma info",
    )
    result = check_karma(user, 50, "post_1")
    assert result.passed
    assert result.reason == ""
    assert result.karma == (100, 5, 20, 0, 0)


def test_check_karma_fails(mocker: Any) -> None:
    user = Mock()
    user.name = "low_karma_user"
    mocker.patch(
        "pifs.karma_checker.calculate_karma",
        return_value=(10, 1, 3, 0, 0),
    )
    mocker.patch(
        "pifs.karma_checker.formatted_karma",
        return_value="Low karma info",
    )
    result = check_karma(user, 50, "post_1")
    assert not result.passed
    assert result.reason == "karma_failed"
    assert result.karma == (10, 1, 3, 0, 0)
    assert result.formatted_karma is not None


def test_check_karma_calculation_error(mocker: Any) -> None:
    user = Mock()
    user.name = "error_user"
    mocker.patch(
        "pifs.karma_checker.calculate_karma",
        return_value=None,
    )
    result = check_karma(user, 50, "post_1")
    assert not result.passed
    assert result.reason == "calculation_error"
