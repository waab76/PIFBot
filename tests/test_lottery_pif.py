from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import pytest

from pifs.lottery_pif import Lottery


@pytest.fixture
def lottery(base_pif_kwargs: dict[str, Any]) -> Lottery:
    return Lottery(**base_pif_kwargs)


def test_pif_type(lottery: Lottery) -> None:
    assert lottery.pif_type == "lottery"


def test_handle_entry_adds_comment_id(lottery: Lottery) -> None:
    comment = Mock()
    comment.id = "comm_1"
    user = Mock()
    user.name = "player1"
    lottery.handle_entry(comment, user, ["latherbot", "in"])
    assert lottery.pifEntries["player1"] == "comm_1"
    comment.reply.assert_called_once()
    comment.save.assert_called_once()


def test_determine_winner_picks_from_entries(lottery: Lottery) -> None:
    lottery.pifEntries = {"p1": "c1", "p2": "c2", "p3": "c3"}
    mock_comment = Mock()
    mock_comment.submission.id = "post_1"
    with (
        patch("random.choice", side_effect=lambda x: x[0]),
        patch("pifs.lottery_pif.get_comment", return_value=mock_comment),
    ):
        lottery.determine_winner()
    assert lottery.pifWinner == "p1"


def test_generate_winner_comment(lottery: Lottery) -> None:
    lottery.pifEntries = {"p1": "c1", "p2": "c2"}
    lottery.pifWinner = "p1"
    comment = lottery.generate_winner_comment()
    assert "p1" in comment
    assert "2" in comment
