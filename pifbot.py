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

from utils.reddit_helper import reddit, subreddit
from handlers.comment_handler import handle_comment
from handlers.submission_handler import handle_submission
from handlers.private_message_handler import handle_private_message

# Prove we're connected
print(reddit.user.me())

def monitor_submissions():
    for submission in subreddit.stream.submissions():
        handle_submission(submission)


def monitor_comments():
    for comment in subreddit.stream.comments():
        handle_comment(comment)


def monitor_private_messages():
    for inbox_item in reddit.inbox.stream():
        if inbox_item.name.startswith("t4"):
            handle_private_message(inbox_item)
        # TODO in case of a mention, maybe refer to a documentation of this bot's functionality


threading.Thread(target=monitor_submissions).start()
# threading.Thread(target=monitor_comments).start()
# threading.Thread(target=monitor_private_messages).start()

