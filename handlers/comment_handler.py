#!/usr/bin/env python3
# coding: utf-8
#
#   File = comment_handler.py
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

from utils.pif_storage import get_pif, pif_exists, save_pif

def handle_comment(comment):
    logging.info('Handling comment %s by %s on post %s "%s"', comment.id, comment.author.name, comment.submission.id, comment.submission.title)

    # LatherBot shouldn't process its own comments
    if not comment.author:
        logging.debug('Comment %s is deleted, skipping', comment.id)
        return
    elif comment.author.name == 'LatherBot':
        logging.debug('I am the author of comment %s, skipping', comment.id)
        return
    elif skip_comment(comment):
        logging.info('Already replied to comment %s on post %s', comment.id, comment.submission.id)
        return
    elif pif_exists(comment.submission.id):
        pif_obj = get_pif(comment.submission.id)
        if pif_obj.handle_comment(comment):
            save_pif(pif_obj)
        return
    else:
        logging.info('Non-PIF comment')

def skip_comment(comment):
    if comment.saved:
        logging.debug('Already replied to comment %s on post %s (saved)', comment.id, comment.submission.id)
        return True
    return False
