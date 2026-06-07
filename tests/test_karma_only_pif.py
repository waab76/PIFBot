from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from pifs.karma_only_pif import KarmaOnly


@pytest.fixture
def karma_only(base_pif_kwargs: dict[str, Any]) -> KarmaOnly:
    return KarmaOnly(**base_pif_kwargs)


def test_is_already_entered_always_false(karma_only: KarmaOnly) -> None:
    user = Mock()
    user.name = "p1"
    comment = Mock()
    assert not karma_only.is_already_entered(user, comment)


def test_handle_entry_noop(karma_only: KarmaOnly) -> None:
    comment = Mock()
    user = Mock()
    comment.id = "c1"
    user.name = "p1"
    karma_only.handle_entry(comment, user, ["latherbot", "in"])
    assert "p1" not in karma_only.pifEntries


def test_determine_winner_noop(karma_only: KarmaOnly) -> None:
    karma_only.determine_winner()
    assert karma_only.pifWinner == "TBD"


def test_generate_winner_comment_empty(karma_only: KarmaOnly) -> None:
    assert karma_only.generate_winner_comment() == ""


def test_handle_comment_top_level_pass(karma_only: KarmaOnly, mocker: Any) -> None:
    comment = Mock()
    comment.author.name = "good_user"
    comment.parent_id = "t3_abc"
    mocker.patch(
        "pifs.karma_only_pif.calculate_karma",
        return_value=(100, 5, 20, 0, 0),
    )
    mocker.patch(
        "pifs.karma_only_pif.formatted_karma",
        return_value="Good karma stats",
    )
    karma_only.handle_comment(comment)
    comment.reply.assert_called_once_with(
        "Congratulations, you have the karma for this PIF\n\nGood karma stats"
    )


def test_handle_comment_top_level_fail(karma_only: KarmaOnly, mocker: Any) -> None:
    comment = Mock()
    comment.author.name = "poor_user"
    comment.parent_id = "t3_abc"
    mocker.patch(
        "pifs.karma_only_pif.calculate_karma",
        return_value=(10, 1, 3, 0, 0),
    )
    mocker.patch(
        "pifs.karma_only_pif.formatted_karma",
        return_value="Low karma stats",
    )
    karma_only.handle_comment(comment)
    comment.reply.assert_called_once()
    assert "afraid" in comment.reply.call_args[0][0]


def test_handle_comment_reply_does_nothing(karma_only: KarmaOnly) -> None:
    comment = Mock()
    comment.author.name = "testuser"
    comment.parent_id = "t1_xyz"
    karma_only.handle_comment(comment)
    comment.reply.assert_not_called()
