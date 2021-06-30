#!/usr/local/bin/python3
# coding: utf-8
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

import logging
import sys
import threading
import time
from logging.handlers import TimedRotatingFileHandler

handlers = set()
handlers.add(TimedRotatingFileHandler('LatherBot.log',
                                      when='W3',
                                      interval=1,
                                      backupCount=4))

logging.basicConfig(level=logging.INFO, handlers=handlers,
                    format='%(asctime)s :: %(levelname)s :: %(threadName)s :: %(module)s:%(funcName)s :: %(message)s ', 
                    datefmt='%m/%d/%Y %I:%M:%S %p')

from prawcore import ServerError
from praw.models.reddit import comment
from praw.models.reddit import submission
from praw.models.util import stream_generator

from handlers.periodic_check_handler import check_and_update_pifs
from handlers.comment_handler import handle_comment
from handlers.submission_handler import handle_submission
from handlers.private_message_handler import handle_private_message
from utils.reddit_helper import reddit, subreddit

logging.info('Connected to Reddit instance as [%s]', reddit.user.me())

def monitor_submissions():
    logging.info('Monitoring submissions for [r/%s]', subreddit.display_name)
    while True:
        submission_stream = subreddit.stream.submissions()
        try:
            for submission in submission_stream:
                handle_submission(submission)
        except ServerError:
            logging.error('Reddit server is down: %s', sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error('Error processing submission: %s', sys.exc_info()[0], exc_info=True)

def monitor_comments():
    while True:
        logging.info('Monitoring comments for [r/%s]', subreddit.display_name)
        comment_stream = subreddit.stream.comments()
        try:
            for comment in comment_stream:
                handle_comment(comment)
        except ServerError:
            logging.error('Reddit server is down: %s', sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error('Error processing comment: %s', sys.exc_info()[0], exc_info=True)
        
def monitor_edits():
    while True:
        logging.info('Monitoring [r/%s] submission and comment edits', subreddit.display_name)
        edited_stream = stream_generator(subreddit.mod.edited, pause_after=0)
        try:
            for item in edited_stream:
                if isinstance(item, comment.Comment):
                    logging.info('Comment [%s] on submission [%s] was edited', item.id, item.submission.id)
                    handle_comment(item)
                elif isinstance(item, submission.Submission):
                    logging.info('Submission [%s] was edited', item.id)
                    handle_submission(item)
                elif item is not None:
                    logging.warn('Unknown edited item type: [%s]', type(item))
        except ServerError:
            logging.error('Reddit server is down: %s', sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error('Caught exception: %s', sys.exc_info()[0], exc_info=True)

def monitor_private_messages():
    while True:
        logging.info('Monitoring inbox')
        inbox_stream = reddit.inbox.stream(pause_after = -1)
        try:
            for inbox_item in reddit.inbox.stream():
                if inbox_item.name.startswith("t4"):
                    handle_private_message(inbox_item)
        except ServerError:
            logging.error('Reddit server is down: %s', sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error('Caught exception: %s', sys.exc_info()[0], exc_info=True)
        # TODO in case of a mention, maybe refer to a documentation of this bot's functionality

def periodic_pif_updates():
    while True:
        logging.info('Beginning periodic PIF update thread')
        try:
            while True:
                check_and_update_pifs()
                time.sleep(600)
        except Exception:
            logging.error('Caught exception: %s', sys.exc_info()[0], exc_info=True)

logging.debug('Starting child threads')
threading.Thread(target=periodic_pif_updates, name='updater').start()
threading.Thread(target=monitor_submissions, name='submissions').start()
threading.Thread(target=monitor_comments, name='comments').start()
threading.Thread(target=monitor_edits, name='edits').start()
threading.Thread(target=monitor_private_messages, name='pms').start()

