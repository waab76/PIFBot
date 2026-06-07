from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import pytest

from pifs.range_pif import Range


@pytest.fixture
def range_pif(base_pif_kwargs: dict[str, Any]) -> Range:
    kwargs = {**base_pif_kwargs, "pifOptions": {"RangeMin": 1, "RangeMax": 100}}
    return Range(**kwargs)


def test_handle_entry_valid_guess(range_pif: Range) -> None:
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    range_pif.handle_entry(comment, user, ["latherbot", "in", "42"])
    assert range_pif.pifEntries["p1"]["Guess"] == 42  # type: ignore[index]


def test_handle_entry_missing_guess(range_pif: Range) -> None:
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    range_pif.handle_entry(comment, user, ["latherbot", "in"])
    comment.reply.assert_called_once()
    assert "try again" in comment.reply.call_args[0][0].lower()


def test_handle_entry_non_integer_guess(range_pif: Range) -> None:
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    range_pif.handle_entry(comment, user, ["latherbot", "in", "abc"])
    comment.reply.assert_called_once()
    assert "number" in comment.reply.call_args[0][0]


def test_handle_entry_guess_above_max(range_pif: Range) -> None:
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    range_pif.handle_entry(comment, user, ["latherbot", "in", "200"])
    comment.reply.assert_called_once()
    assert "above" in comment.reply.call_args[0][0]


def test_handle_entry_guess_below_min(range_pif: Range) -> None:
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    range_pif.handle_entry(comment, user, ["latherbot", "in", "0"])
    comment.reply.assert_called_once()
    assert "below" in comment.reply.call_args[0][0]


def test_handle_entry_duplicate_guess(range_pif: Range) -> None:
    comment1 = Mock()
    comment1.id = "c1"
    comment2 = Mock()
    comment2.id = "c2"
    user1 = Mock()
    user1.name = "p1"
    user2 = Mock()
    user2.name = "p2"
    range_pif.handle_entry(comment1, user1, ["latherbot", "in", "50"])
    range_pif.handle_entry(comment2, user2, ["latherbot", "in", "50"])
    comment2.reply.assert_called_once()
    assert "already taken" in comment2.reply.call_args[0][0]


def test_user_already_guessed(range_pif: Range) -> None:
    range_pif.pifEntries = {
        "p1": {"CommentId": "c1", "Guess": 50},
    }
    assert range_pif.userAlreadyGuessed(50) == "p1"
    assert range_pif.userAlreadyGuessed(51) is None


def test_determine_winner_closest_guess(range_pif: Range) -> None:
    range_pif.pifEntries = {
        "p1": {"CommentId": "c1", "Guess": 10},
        "p2": {"CommentId": "c2", "Guess": 50},
        "p3": {"CommentId": "c3", "Guess": 90},
    }
    mock_comment = Mock()
    mock_comment.submission.id = "post_1"
    with (
        patch("pifs.range_pif.randrange", return_value=45),
        patch("pifs.range_pif.get_comment", return_value=mock_comment),
    ):
        range_pif.determine_winner()
    assert range_pif.pifWinner == "p2"


def test_determine_winner_price_is_right_tiebreaker(range_pif: Range) -> None:
    range_pif.pifEntries = {
        "p1": {"CommentId": "c1", "Guess": 40},
        "p2": {"CommentId": "c2", "Guess": 60},
    }
    mock_comment = Mock()
    mock_comment.submission.id = "post_1"
    with (
        patch("pifs.range_pif.randrange", return_value=50),
        patch("pifs.range_pif.get_comment", return_value=mock_comment),
    ):
        range_pif.determine_winner()
    assert range_pif.pifWinner == "p1"
