from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, Mock

import pytest

from config import bot_name


@pytest.fixture(autouse=True)
def mock_reddit_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_reddit = MagicMock()
    mock_sub = MagicMock()
    mock_sub.display_name = "test_sub"
    mock_reddit.user.me.return_value = Mock(name=bot_name)
    mock_reddit.subreddit.return_value = mock_sub

    monkeypatch.setattr("praw.Reddit", lambda *a, **kw: mock_reddit)
    monkeypatch.setattr("utils.reddit_helper.reddit", mock_reddit, raising=False)
    monkeypatch.setattr("utils.reddit_helper.monitored_sub", mock_sub, raising=False)


@pytest.fixture(autouse=True)
def mock_config_blacklist(monkeypatch: pytest.MonkeyPatch) -> None:
    blacklist = {"bad_user": "Known scammer"}
    monkeypatch.setattr("config.blacklist", blacklist, raising=False)


@pytest.fixture
def mock_comment() -> Mock:
    comment = MagicMock()
    comment.author.name = "testuser"
    comment.author.created_utc = 1000000
    comment.body = f"{bot_name} in"
    comment.id = "abc123"
    comment.created_utc = 2000000
    comment.submission.id = "post_1"
    comment.submission.title = "Test PIF"
    comment.submission.created_utc = 1500000
    comment.parent_id = "t3_abc"
    comment.parent.return_value = Mock(
        author=Mock(name=bot_name),
        parent=Mock(
            author=Mock(name="testuser"),
            body=f"{bot_name} in",
        ),
    )
    return comment


@pytest.fixture
def mock_submission() -> Mock:
    submission = MagicMock()
    submission.id = "post_1"
    submission.author.name = "author_user"
    submission.created_utc = 1500000
    submission.selftext = f"{bot_name} lottery 50 24"
    submission.title = "Test PIF"
    return submission


@pytest.fixture
def base_pif_kwargs() -> dict[str, Any]:
    return {
        "postId": "post_1",
        "authorName": "author_user",
        "minKarma": 50,
        "durationHours": 24,
        "endTime": 9999999999,
    }
