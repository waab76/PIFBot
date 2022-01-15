#!/usr/bin/env python3
# coding: utf-8
#
#   File = submission_hanlder.py
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

from pifs import pif_builder

from handlers.comment_handler import handle_comment
from utils.pif_storage import pif_exists, save_pif

def handle_submission(submission):
    logging.debug('Handling post "%s" by %s', submission.title, submission.author.name)
    # Decide what kind of post this is and proceed appropriately.  Maybe check
    # the flair to see if it's "PIF - Open" and then kick it over to a PIF
    # handler?
    if submission.link_flair_text == "PIF - Open":
        logging.debug('Post "%s" has open PIF flair', submission.title)
        handle_pif(submission)
    elif submission.link_flair_text == 'PIF - Closed':
        logging.info('Post "%s" appears to be a closed PIF', submission.title)
        if not submission.locked:
            submission.mod.lock()
    elif submission.link_flair_text == 'PIF - Winner':
        pass
    elif 'Weekly Sidebar Contest Results' in submission.title:
        pass
        # banner_update()
    else:
        logging.info('Looking for LatherBot command in post "%s"', submission.title)
        if has_latherbot_pif_command(submission):
            handle_pif(submission)
        
def handle_pif(submission):
    logging.info('Handling open PIF "%s"', submission.title)
            
    if pif_exists(submission.id):
        logging.info('Processing all comments on PIF "%s"', submission.title)
        submission.comment_sort = 'new'
        submission.comments.replace_more(limit=0)
        comments = submission.comments.list()
        for comment in comments:
            handle_comment(comment)
    else:
        logging.info('PIF "%s" is not yet tracked', submission.title)
        pif = pif_builder.build_and_init_pif(submission)
        if pif is not None:
            logging.info('Storing LatherBot PIF "%s"', submission.title)
            save_pif(pif)

def has_latherbot_pif_command(submission):
    lines = submission.selftext.lower().split("\n")
    for line in lines:
        if line.strip().startswith("latherbot"):
            logging.info('Post "%s" MIGHT have a LatherBot command', submission.title)
            parts = line.split()
            if parts[1] in pif_builder.known_pif_types:
                logging.info('Submission "%s" is a PIF!', submission.title)
                return True

    return False