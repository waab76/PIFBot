from __future__ import annotations

from unittest.mock import Mock

import pytest
from freezegun import freeze_time

from utils.karma_calculator import (
    formatted_karma,
    KarmaResult,
)


class TestFormattedKarma:
    def test_good_karma(self) -> None:
        result: KarmaResult = (100, 5, 20, 0, 0)
        user = Mock()
        user.name = "good_user"
        output = formatted_karma(user, result)
        assert "good_user" in output
        assert "5 Submissions" in output
        assert "20 Comments" in output
        assert "100 Karma" in output

    def test_bad_karma(self) -> None:
        result: KarmaResult = (100, 10, 20, 50, 25)
        user = Mock()
        user.name = "pif_farmer"
        output = formatted_karma(user, result)
        assert "More than 25%" in output

    def test_new_user_karma(self) -> None:
        result: KarmaResult = (5, 1, 3, 0, 0)
        user = Mock()
        user.name = "new_user"
        output = formatted_karma(user, result)
        assert "brand new" in output.lower()
