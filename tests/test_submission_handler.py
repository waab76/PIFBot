from __future__ import annotations

from unittest.mock import Mock

from handlers.submission_handler import handle_submission


def test_handle_submission_deleted_post_does_not_crash() -> None:
    submission = Mock()
    submission.author = None
    submission.title = "Deleted PIF"
    submission.link_flair_text = "PIF - Winner"
    handle_submission(submission)
