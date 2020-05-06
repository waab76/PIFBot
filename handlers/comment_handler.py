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

from utils.pif_storage import get_pif, pif_exists

def handle_comment(comment):
    logging.debug('Handling comment [%s] on post [%s]', comment.id, comment.submission.id)

    # LatherBot shouldn't process its own comments
    if not comment.author:
        logging.debug('Comment [%s] is deleted, skipping', comment.id)
        return
    elif comment.author.name == 'LatherBot':
        logging.debug('I am the author of comment [%s], skipping', comment.id)
        return
    elif skip_comment(comment):
        logging.debug('Already replied to comment [%s] on post [%s]', comment.id, comment.submission.id)
        return
    elif comment.submission.link_flair_text == "PIF - Open" and pif_exists(comment.submission.id):
        pif_obj = get_pif(comment.submission.id)
        pif_obj.handle_comment(comment)
        return

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
