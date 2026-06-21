from __future__ import annotations

from unittest.mock import Mock

from utils.karma_calculator import (
    KarmaResult,
    calculate_karma,
    formatted_karma,
)


class TestCalculateKarma:
    def test_returns_none_when_api_fails(self) -> None:
        user = Mock()
        user.name = "error_user"
        user.submissions.new.side_effect = Exception("Reddit API down")
        result = calculate_karma(user)
        assert result is None


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
