#!/usr/bin/env python
# coding: utf-8
#
#   File = private_message_handler.py
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

from config import subreddit
from karma_calculator import calculate_karma


def handle_private_message(message):
    '''
    Disregard actual message and respond with a karma check and a reference to the bot's documentation.
    :param message: the message being handled
    :return: nothing
    '''
    author = message.author
    activity = calculate_karma(author)
    author.message('/r/' + subreddit + ' overview for /u/' + author.name + ' for the last 90 days',
                   activity[0] + ' karma\n\n' +
                   activity[1] + ' submissions\n\n' +
                   activity[2] + ' comments\n\n' +
                   'I am a bot. If you\'d like to know more about me and what I can do for you,' +
                   'please refer to my documentation: [this doesn\'t work yet]') # TODO link to documentation
