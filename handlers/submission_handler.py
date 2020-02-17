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

from pifs.pif_builder import build_and_init_pif
from utils.dynamo_helper import open_pif_exists

def handle_submission(submission):
    # Decide what kind of post this is and proceed appropriately.  Maybe check
    # the flair to see if it's "PIF - Open" and then kick it over to a PIF
    # handler?
    if submission.link_flair_text == "PIF - Open":
        handle_pif(submission)
    else:
        pass

def handle_pif(submission):
    if open_pif_exists(submission.id):
        pass
    else:
        build_and_init_pif(submission)