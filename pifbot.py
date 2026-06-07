#!/usr/local/bin/python3
#
#   File = pifbot.py
#
#      Copyright 2019 Rob Curtis
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

import datetime
import logging
import sys
import threading
import time
from logging.handlers import TimedRotatingFileHandler

from config import log_path

handlers: list[TimedRotatingFileHandler] = [
    TimedRotatingFileHandler(log_path, when="W3", interval=1, backupCount=4)
]

logging.basicConfig(
    level=logging.INFO,
    handlers=handlers,
    format="%(asctime)s %(levelname)s %(threadName)s %(module)s:%(funcName)s %(message)s ",
)
logging.Formatter.formatTime = lambda self, record, datefmt=None: (  # type: ignore[method-assign]
    datetime.datetime.fromtimestamp(record.created, datetime.UTC)
    .astimezone()
    .isoformat(sep="T", timespec="milliseconds")
)

from praw.models import Comment, Submission  # type: ignore[import-untyped]
from praw.models.util import stream_generator  # type: ignore[import-untyped]
from prawcore import ServerError  # type: ignore[import-untyped]

from handlers.comment_handler import handle_comment
from handlers.periodic_check_handler import check_and_update_pifs
from handlers.private_message_handler import handle_private_message
from handlers.submission_handler import handle_submission
from utils.reddit_helper import monitored_sub, reddit

logging.info("Connected to Reddit instance as %s", reddit.user.me())


def monitor_submissions() -> None:
    logging.info("Monitoring submissions for r/%s", monitored_sub.display_name)
    while True:
        submission_stream = monitored_sub.stream.submissions()
        try:
            for submission in submission_stream:
                handle_submission(submission)
        except ServerError:
            logging.error("Reddit server is down: %s", sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error(
                "Error processing submission: %s", sys.exc_info()[0], exc_info=True
            )


def monitor_comments() -> None:
    while True:
        logging.info("Monitoring comments for r/%s", monitored_sub.display_name)
        comment_stream = monitored_sub.stream.comments()
        try:
            for comment in comment_stream:
                handle_comment(comment)
        except ServerError:
            logging.error("Reddit server is down: %s", sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error(
                "Error processing comment: %s", sys.exc_info()[0], exc_info=True
            )


def monitor_edits() -> None:
    while True:
        logging.info("Monitoring r/%s edits", monitored_sub.display_name)
        edited_stream = stream_generator(monitored_sub.mod.edited, pause_after=0)
        try:
            for item in edited_stream:
                if isinstance(item, Comment):
                    logging.info(
                        'Comment [%s] on submission "%s" was edited by %s',
                        item.id,
                        item.submission.title,
                        item.author.name,
                    )
                    handle_comment(item)
                elif isinstance(item, Submission):
                    logging.info(
                        'Submission "%s" was edited by %s', item.title, item.author.name
                    )
                    handle_submission(item)
                elif item is not None:
                    logging.error("Unknown edited item type: %s", type(item))
        except ServerError:
            logging.error("Reddit server is down: %s", sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error("Caught exception: %s", sys.exc_info()[0], exc_info=True)


def monitor_private_messages() -> None:
    while True:
        logging.info("Monitoring inbox")
        reddit.inbox.stream(pause_after=-1)
        try:
            for inbox_item in reddit.inbox.stream():
                if hasattr(inbox_item, "name") and str(inbox_item.name).startswith(
                    "t4"
                ):
                    handle_private_message(inbox_item)
        except ServerError:
            logging.error("Reddit server is down: %s", sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error("Caught exception: %s", sys.exc_info()[0], exc_info=True)


def periodic_pif_updates() -> None:
    while True:
        logging.info("Beginning periodic PIF update thread")
        try:
            while True:
                check_and_update_pifs()
                time.sleep(600)
        except Exception:
            logging.error("Caught exception: %s", sys.exc_info()[0], exc_info=True)


logging.debug("Starting child threads")
threading.Thread(target=periodic_pif_updates, name="updater").start()
threading.Thread(target=monitor_submissions, name="submissions").start()
threading.Thread(target=monitor_comments, name="comments").start()
threading.Thread(target=monitor_edits, name="edits").start()
threading.Thread(target=monitor_private_messages, name="pms").start()
