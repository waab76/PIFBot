#!/usr/bin/env python3
# coding: utf-8
#
#   File = karma_calculator.py
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
import time

from utils.reddit_helper import rwetshaving

good_karma_template = '''
/r/{} overview for /u/{} for the last 90 days:

{} Submissions

{} Comments

{} Karma

I am a bot. If you'd like to know more about me and what I can do for you, please refer to [my documentation](https://www.reddit.com/r/Wetshaving/wiki/latherbot)
'''

bad_karma_template = '''
/r/{} overview for /u/{} for the last 90 days:

{} Submissions

{} Comments (and {} comments on PIFs)

{} Karma (and {} karma from PIF comments)

More than 25% of your karma is from commenting on PIFs.

I am a bot. If you'd like to know more about me and what I can do for you, please refer to [my documentation](https://www.reddit.com/r/Wetshaving/wiki/latherbot)
'''

new_karma_template = '''
/r/{} overview for /u/{} for the last 90 days:

{} Submissions

{} Comments

{} Karma

It looks like you're brand new to to r/wetshaving. You should try asking a question on our [Daily Questions thread](https://www.reddit.com/r/Wetshaving/?f=flair_name%3A%22Daily%20Q.%22) or posting your Shave of the Day on our [SOTD thread](https://www.reddit.com/r/Wetshaving/?f=flair_name%3A%22SOTD%22).

I am a bot. If you'd like to know more about me and what I can do for you, please refer to [my documentation](https://www.reddit.com/r/Wetshaving/wiki/latherbot)
'''

def calculate_karma(user):
    logging.info('Calculating karma for user %s', user.name)
    """
    Calculate the subreddit-specific karma of the last 90 days for a specific user.
    :param user: The user whose karma is calculated.
    :return: A five-tuple with the elements being the non-pif karma score, number of submissions number of non-pif comments, pif comment karma score, and number of pif comments
    of the last 90 days.
    """
    karma = 0
    num_submissions = 0
    num_comments = 0
    pif_comment_karma = 0
    num_pif_comments = 0
    ninety_days_ago = time.time() - 90 * 86400
    
    try:
        # Calculate the karma of all submissions.
        for submission in user.submissions.new(limit=1000):
            try:
                if submission.created_utc < ninety_days_ago:
                    continue
                elif submission.subreddit_id[3:] == rwetshaving.id:
                    num_submissions += 1
                    karma += submission.score
            except:
                logging.error('Failed to get karma for submision: [%s]', submission.id, exc_info=True)
                continue

        # Calculate the karma of all comments.
        for comment in user.comments.new(limit=1000):
            try:
                if comment.created_utc < ninety_days_ago:
                    continue
                elif comment.subreddit_id[3:] == rwetshaving.id:
                    if comment.saved:
                        num_pif_comments += 1
                        pif_comment_karma += comment.score
                    else: 
                        num_comments += 1
                        karma += comment.score
            except:
                logging.error('Failed to get karma for comment: [%s]', comment.id, exc_info=True)
                continue
    except:
        logging.error('Failed to get karma for user %s', user.name, exc_info=True)
        
    logging.info('User %s has %s karma', user.name, karma)
    
    return karma, num_submissions, num_comments, pif_comment_karma, num_pif_comments

def formatted_karma(user, activity):
    """
    Performs a karma check for the user and returns a String that's already formatted exactly like the usual response of the bot.
    :param user: The user the karma check will be performed for.
    :return: A conveniently formatted karma
    check response.
    """
    response = good_karma_template.format(rwetshaving.display_name, user.name, activity[1], activity[2], activity[0])
    if activity[3] > activity[0]/3:
        response = bad_karma_template.format(rwetshaving.display_name, user.name, activity[1], activity[2], activity[4], activity[0], activity[3])
    elif activity[1] < 2 and activity[2] < 5:
        response = new_karma_template.format(rwetshaving.display_name, user.name, activity[1], activity[2], activity[0])

    return response

def formatted_karma_check(user):
    """
    Performs a karma check for the user and returns a String that's already formatted exactly like the usual response of the bot.
    :param user: The user the karma check will be performed for.
    :return: A conveniently formatted karma
    check response.
    """
    return formatted_karma(user, calculate_karma(user))

