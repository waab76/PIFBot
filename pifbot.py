#!/usr/bin/env python
# coding: utf-8
#
#   File = pifbot.py
#
#      Copyright 2019 [name of copyright owner]
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

import threading
import time

from praw.models.reddit import comment
from praw.models.reddit import submission
from praw.models.util import stream_generator

from handlers.periodic_check_handler import check_and_update_pifs
from handlers.comment_handler import handle_comment
from handlers.submission_handler import handle_submission
from handlers.private_message_handler import handle_private_message
from utils.reddit_helper import reddit, subreddit

# Prove we're connected
print(reddit.user.me())

def monitor_submissions():
    for submission in subreddit.stream.submissions():
        handle_submission(submission)


def monitor_comments():
    for comment in subreddit.stream.comments():
        handle_comment(comment)
        
def monitor_edits():
    edited_stream = stream_generator(subreddit.mod.edited, pause_after=0)
    for item in edited_stream:
        if type(item) == comment:
            print("Found edited comment")
            # handle_comment(item)
        elif type(item) == submission:
            print("Found edited submission")
            # handle_submission(item)
        else:
            pass


def monitor_private_messages():
    for inbox_item in reddit.inbox.stream():
        if inbox_item.name.startswith("t4"):
            handle_private_message(inbox_item)
        # TODO in case of a mention, maybe refer to a documentation of this bot's functionality

def periodic_pif_updates():
    while True:
        check_and_update_pifs()
        time.sleep(600)

threading.Thread(target=periodic_pif_updates, name='Updater').start()
threading.Thread(target=monitor_submissions, name='Submissions').start()
threading.Thread(target=monitor_comments, name='Comments').start()
threading.Thread(target=monitor_edits, name='Edits').start()
# threading.Thread(target=monitor_private_messages, name='PMs').start()

