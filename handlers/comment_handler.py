#!/usr/bin/env python
# coding: utf-8
#
#   File = comment_handler.py
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

import logging

from utils.karma_calculator import calculate_karma, formatted_karma
from utils.personality import get_bad_command_response
from utils.pif_storage import get_pif, pif_exists, save_pif
from utils.reddit_helper import already_replied

def handle_comment(comment):
    logging.info('Handling comment [%s] on post [%s]', comment.id, comment.submission.id)

    # LatherBot shouldn't process its own comments
    if comment is None or comment.author is None:
        logging.debug('Comment [%s] is deleted, skipping', comment.id)
        return
    elif comment.author.name == 'LatherBot':
        logging.debug('I am the author of comment [%s], skipping', comment.id)
        return
    elif already_replied(comment):
        logging.debug('Already replied to comment [%s] on post [%s]', comment.id, comment.submission.id)
        return
    
    # Look for a LatherBot command
    for line in comment.body.lower().split('\n'):
        if line.startswith('latherbot'):
            parts = line.split()
            if len(parts) < 2:
                continue
            logging.info('Handling command [%s] for post [%s] comment [%s]', 
                         line, comment.submission.id, comment.id)
            handle_command(comment, parts)
        elif line.startswith('remove'):
            # Possible MOD Action
            logging.info("Possible mod action by [%s]: %s", comment.author.name, line)
    
def handle_command(comment, command_parts):
    user = comment.author
    karma = calculate_karma(user)
    formattedKarma = formatted_karma(user, karma)

    if command_parts[1].startswith('in'):
        handle_pif_entry(comment.submission.id, user, command_parts)
    elif command_parts[1].startswith('karma'):
        logging.info('User [%s] requested karma check', user.name)
        comment.reply(formattedKarma)
    else:
        logging.warning('Invalid command on comment [%s] for post [%s]', comment.id, comment.submission.id)
        comment.reply(get_bad_command_response())
    
def handle_pif_entry(pif_id, comment, karma, command_parts):
    if pif_exists(pif_id):
        logging.debug('Submission [%s] is a tracked PIF', pif_id)
        pif_obj = get_pif(pif_id)
        pif_obj.handle_entry_request(comment, karma, command_parts)
        save_pif(pif_obj)
    else:
        logging.debug('Comment not related to a tracked PIF')
