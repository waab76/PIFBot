#!/usr/bin/env python3
#
#   File = submission_handler.py
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

from praw.models import Comment, Submission  # type: ignore[import-untyped]

from config import bot_name
from handlers.comment_handler import handle_comment
from pifs import pif_builder
from pifs.registry import known_pif_types
from utils.pif_storage import pif_exists, save_pif


def handle_submission(submission: Submission) -> None:
    author_name = submission.author.name if submission.author else "[deleted]"
    logging.debug('Handling post "%s" by %s', submission.title, author_name)
    if submission.link_flair_text == "PIF - Open":
        logging.debug('Post "%s" has open PIF flair', submission.title)
        handle_pif(submission)
    elif submission.link_flair_text == "PIF - Closed":
        logging.info('Post "%s" appears to be a closed PIF', submission.title)
        if not submission.locked:
            submission.mod.lock()
    elif (
        submission.link_flair_text == "PIF - Winner"
        or "Weekly Sidebar Contest Results" in submission.title
    ):
        pass
    else:
        logging.info('Looking for %s command in post "%s"', bot_name, submission.title)
        if has_latherbot_pif_command(submission):
            handle_pif(submission)


def handle_pif(submission: Submission) -> None:
    logging.info('Handling open PIF "%s"', submission.title)

    if pif_exists(submission.id):
        logging.info('Processing all comments on PIF "%s"', submission.title)
        submission.comment_sort = "new"
        submission.comments.replace_more(limit=0)
        comments: list[Comment] = submission.comments.list()
        for comment in comments:
            handle_comment(comment)
    else:
        logging.info('PIF "%s" is not yet tracked', submission.title)
        pif = pif_builder.build_and_init_pif(submission)
        if pif is not None:
            logging.info('Storing PIF "%s"', submission.title)
            save_pif(pif)


def has_latherbot_pif_command(submission: Submission) -> bool:
    known_types = known_pif_types()
    for line in submission.selftext.lower().split("\n"):
        if line.strip().startswith(bot_name.lower()):
            parts = line.split()
            if len(parts) > 1 and parts[1] in known_types:
                logging.info('Submission "%s" is a PIF!', submission.title)
                return True
    return False
