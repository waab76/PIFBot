#!/usr/bin/env python3
#
#   File = reddit_helper.py
#
#      Copyright 2020 Rob Curtis
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
############################################################################

from __future__ import annotations

import logging
from typing import Any

import praw  # type: ignore[import-untyped]
from praw.models import Comment, Submission, Subreddit  # type: ignore[import-untyped]

from config import karma_subreddits, monitored_subreddits

bot_name: str = "PIFBot"
user_agent: str = "script:PIFBot:0.1 (by u/BourbonInExile and u/MrSabuhudo)"

# Create the connection to Reddit.
# This assumes a properly formatted praw.ini file exists:
#   https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html
reddit: praw.Reddit = praw.Reddit(bot_name, user_agent=user_agent)

# Build the monitored multi-reddit from the configured list
monitored_sub: Subreddit = reddit.subreddit("+".join(monitored_subreddits))

# Build karma subreddit lookup set and display label
_karma_subs: list[Subreddit] = [reddit.subreddit(s) for s in karma_subreddits]
karma_subreddit_ids: set[str] = {s.id for s in _karma_subs}
karma_subreddit_label: str = ", ".join(f"/r/{s}" for s in karma_subreddits)


def get_submission(post_id: str) -> Submission:
    return Submission(reddit, post_id)


def get_comment(comment_id: str) -> Comment:
    return Comment(reddit, comment_id)


def skip_comment(comment: Comment) -> bool:
    if comment.saved:
        logging.debug(
            "Already replied to comment [%s] on post [%s] (saved)",
            comment.id,
            comment.submission.id,
        )
        return True
    try:
        comment.reply_sort = "old"
        comment.refresh()
        replies = comment.replies
        for reply in replies:
            if reply.author.name == "LatherBot":
                logging.debug(
                    "Already replied to comment [%s] on post [%s]",
                    comment.id,
                    comment.submission.id,
                )
                return True
    except Exception:
        logging.error("Error processing comment: [%s]", comment.id, exc_info=True)
        return True
    return False
