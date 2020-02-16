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

import praw

from praw.models import Submission

bot_name="PIFBot"
user_agent="script:PIFBot:0.1 (by u/BourbonInExile and u/MrSabuhudo)"

# Create the connection to Reddit.
# This assumes a properly formatted praw.ini file exists:
#   https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html
reddit = praw.Reddit(bot_name, user_agent=user_agent)

# Get a handle on our preferred subreddit
subreddit = reddit.subreddit("TrueWetShaving")

def getSubmission(postId):
    return Submission(reddit, postId)