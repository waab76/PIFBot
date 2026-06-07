from __future__ import annotations

from unittest.mock import Mock

from handlers.comment_handler import skip_comment


def test_skip_comment_saved_returns_true() -> None:
    comment = Mock()
    comment.saved = True
    assert skip_comment(comment)


def test_skip_comment_not_saved_returns_false() -> None:
    comment = Mock()
    comment.saved = False
    assert not skip_comment(comment)
