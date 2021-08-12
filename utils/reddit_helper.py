#!/usr/bin/env python3
# coding: utf-8
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

import logging
import praw

from praw.models import Comment, Submission

bot_name="PIFBot"
user_agent="script:PIFBot:0.1 (by u/BourbonInExile and u/MrSabuhudo)"

# Create the connection to Reddit.
# This assumes a properly formatted praw.ini file exists:
#   https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html
reddit = praw.Reddit(bot_name, user_agent=user_agent)

# Get a handle on our preferred subreddit
subreddit = reddit.subreddit("WetShaving+ircbst")
rwetshaving = reddit.subreddit("WetShaving")

def get_submission(post_id):
    return Submission(reddit, post_id)

def get_comment(comment_id):
    return Comment(reddit, comment_id)

def skip_comment(comment):
    if comment.saved:
        logging.debug('Already replied to comment [%s] on post [%s] (saved)', comment.id, comment.submission.id)
        return True
    try:
        comment.reply_sort = 'old'
        comment.refresh()
        replies = comment.replies
        for reply in replies:
            if reply.author.name == 'LatherBot':
                logging.debug('Already replied to comment [%s] on post [%s]', comment.id, comment.submission.id)
                return True
    except Exception:
        logging.error('Error processing comment: %s', comment.id, exc_info=True)
        return True
    return False

def submission_link(post_id):
    return "https://redd.it/{}".format(post_id)

def comment_link(comment_id):
    return "http://redd.it/{}".format(comment_id)