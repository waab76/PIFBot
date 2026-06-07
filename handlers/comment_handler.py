#!/usr/bin/env python3
#
#   File = comment_handler.py
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

from praw.models import Comment  # type: ignore[import-untyped]

from utils.pif_storage import get_pif, pif_exists, save_pif
from utils.pif_storage import lock as pif_storage_lock


def handle_comment(comment: Comment) -> None:
    if not comment.author:
        logging.debug("Comment [%s] is deleted, skipping", comment.id)
        return

    logging.info(
        'Handling comment [%s] by %s on post "%s"',
        comment.id,
        comment.author.name,
        comment.submission.title,
    )

    if comment.author.name == "LatherBot":
        logging.debug("I am the author of comment [%s], skipping", comment.id)
        return

    if comment.saved:
        logging.info(
            'Already handled comment [%s] by %s on post "%s"',
            comment.id,
            comment.author.name,
            comment.submission.title,
        )
        return

    if pif_exists(comment.submission.id):
        with pif_storage_lock:
            pif_obj = get_pif(comment.submission.id)
            if pif_obj is not None and pif_obj.handle_comment(comment):
                save_pif(pif_obj)
        return

    logging.debug("Non-PIF comment")
