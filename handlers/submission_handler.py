#!/usr/bin/env python
# coding: utf-8
#
#   File = submission_handler.py
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

from pifs import pif_builder

from handlers.comment_handler import handle_comment
from utils.pif_storage import pif_exists, save_pif

def handle_submission(submission):
    logging.debug('Handling submission [%s] - %s', submission.id, submission.title)
    # Decide what kind of post this is and proceed appropriately.  Maybe check
    # the flair to see if it's "PIF - Open" and then kick it over to a PIF
    # handler?
    if submission.link_flair_text == "PIF - Open":
        logging.debug('Submission [%s] has open PIF flair', submission.id)
        handle_pif(submission)
    elif submission.link_flair_text == 'PIF - Closed':
        logging.info('Locking closed PIF [%s] - %s', submission.id, submission.title)
        submission.mod.lock()
    elif submission.link_flair_text == 'PIF - Winner':
        pass
    else:
        logging.info('Looking for LatherBot command in submission [%s] - %s', submission.id, submission.title)
        if has_latherbot_pif_command(submission):
            handle_pif(submission)

def handle_pif(submission):
    logging.info('Handling open PIF [%s]', submission.id)
    if pif_exists(submission.id):
        logging.debug('PIF [%s] is already tracked', submission.id)
        pass
    else:
        logging.debug('PIF [%s] is not yet tracked', submission.id)
        pif = pif_builder.build_and_init_pif(submission)
        if pif is not None:
            logging.debug('Storing LatherBot PIF [%s]', submission.id)
            save_pif(pif)
            
    if pif_exists(submission.id):
        logging.info('Processing all comments on PIF [%s]', submission.id)
        submission.comment_sort = 'new'
        submission.comments.replace_more(limit=0)
        comments = submission.comments.list()
        for comment in comments:
            handle_comment(comment)

def has_latherbot_pif_command(submission):
    lines = submission.selftext.lower().split("\n")
    for line in lines:
        if line.strip().startswith("latherbot"):
            logging.info('Submission [%s] MIGHT have a LatherBot command', submission.id)
            parts = line.split()
            if parts[1] in pif_builder.known_pif_types:
                logging.info('Submission [%s] is a PIF!', submission.id)
                return True

    return False