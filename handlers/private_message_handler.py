#!/usr/bin/env python3
# coding: utf-8
#
#   File = private_message_handler.py
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
from utils.karma_calculator import formatted_karma_check


def handle_private_message(message):
    if message.author.name not in ['ModNewsletter', 'reddit']:
        logging.info('PM karma check for %s' % message.author.name)
        message.reply(formatted_karma_check(message.author))
    message.delete()
