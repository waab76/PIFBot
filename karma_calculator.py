#!/usr/bin/env python
# coding: utf-8
#
#   File = karma_calculator.py
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

import time
from config import subreddit


def calculate_karma(user):
    """
    Calculate the subreddit-specific karma of the last 90 days for a specific user.
    :param user: The user whose karma is calculated.
    :return: A three-tuple with the elements being the karma score, number of submissions and number of comments
    of the last 90 days.
    """
    karma = 0
    num_submissions = 0
    num_comments = 0
    ninety_days_ago = time.time() - 90 * 86400

    # Calculate the karma of all submissions.
    for submission in user.submissions.new():
        if submission.created_utc < ninety_days_ago:
            break
        elif submission.subreddit_id[3:] == subreddit.id:
            num_submissions += 1
            karma += submission.score

    # Calculate the karma of all comments.
    for comment in user.comments.new():
        if comment.created_utc < ninety_days_ago:
            break
        elif comment.subreddit_id[3:] == subreddit.id:
            num_comments += 1
            karma += comment.score

    return karma, num_submissions, num_comments


def formatted_karma_check(user):
    """
    Performs a karma check for the user and returns a String that's already formatted exactly like the usual response of the bot.
    :param user: The user the karma check will be performed for.
    :return: A conveniently formatted karma
    check response.
    """
    activity = calculate_karma(user)
    response = ("/r/" + subreddit.display_name + " overview for /u/" + user.name + " for the last 90 days:\n\n" +
                str(activity[0]) + " karma\n\n" +
                str(activity[1]) + " submissions\n\n" +
                str(activity[2]) + " comments\n\n" +
                "I am a bot. If you'd like to know more about me and what I can do for you, " +
                "please refer to my documentation: [this doesn't work yet]")  # TODO link to documentation
    return response

