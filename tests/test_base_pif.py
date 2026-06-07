from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from pifs.base_pif import BasePIF


class ConcretePIF(BasePIF):
    pif_type = "test"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            postId=kwargs["postId"],
            authorName=kwargs["authorName"],
            pifType=self.pif_type,
            minKarma=kwargs["minKarma"],
            durationHours=kwargs["durationHours"],
            endTime=kwargs["endTime"],
        )

    def pif_instructions(self) -> str:
        return "Test instructions"

    def handle_entry(self, comment: Any, user: Any, command_parts: Any) -> None:
        pass

    def determine_winner(self) -> None:
        pass

    def generate_winner_comment(self) -> str:
        return "Test winner comment"


@pytest.fixture
def pif(base_pif_kwargs: dict[str, Any]) -> ConcretePIF:
    return ConcretePIF(**base_pif_kwargs)


def test_to_storage_dict(pif: ConcretePIF) -> None:
    d = pif.to_storage_dict()
    assert d["SubmissionId"] == "post_1"
    assert d["Author"] == "author_user"
    assert d["PifType"] == "test"
    assert d["PifState"] == "open"
    assert d["PifWinner"] == "TBD"


def test_is_already_entered_true(pif: ConcretePIF) -> None:
    user = Mock()
    user.name = "player1"
    comment = Mock()
    comment.id = "c1"
    pif.pifEntries = {"player1": {"CommentId": "c1"}}
    assert pif.is_already_entered(user, comment)


def test_is_already_entered_false(pif: ConcretePIF) -> None:
    user = Mock()
    user.name = "player1"
    comment = Mock()
    pif.pifEntries = {}
    assert not pif.is_already_entered(user, comment)


def test_handle_comment_no_latherbot_returns_none(pif: ConcretePIF) -> None:
    comment = Mock()
    comment.body = "Just a regular comment"
    comment.author.name = "someone"
    result = pif.handle_comment(comment)
    assert result is None


def test_handle_comment_karma_command(pif: ConcretePIF, mocker: Any) -> None:
    comment = Mock()
    comment.body = "LatherBot karma"
    comment.author.name = "someone"
    comment.author.created_utc = 1000000
    comment.submission.id = "post_1"
    comment.submission.title = "Test"
    comment.submission.created_utc = 900000
    mocker.patch(
        "pifs.base_pif.check_karma",
        return_value=Mock(
            passed=True,
            reason="",
            karma=(100, 5, 20, 0, 0),
            formatted_karma="Good karma stats",
        ),
    )
    pif.handle_comment(comment)
    comment.reply.assert_called_once_with("Good karma stats")
    comment.downvote.assert_called_once()


def test_handle_comment_invalid_command(pif: ConcretePIF, mocker: Any) -> None:
    comment = Mock()
    comment.body = "LatherBot bogus"
    comment.author.name = "someone"
    comment.author.created_utc = 1000000
    comment.submission.id = "post_1"
    comment.submission.title = "Test"
    comment.submission.created_utc = 900000
    comment.id = "c1"
    mocker.patch(
        "pifs.base_pif.check_karma",
        return_value=Mock(
            passed=True,
            reason="",
            karma=(100, 5, 20, 0, 0),
            formatted_karma="",
        ),
    )
    pif.handle_comment(comment)
    comment.reply.assert_called_once()
    assert "not a valid" in comment.reply.call_args[0][0]
