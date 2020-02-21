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

from utils.pif_storage import get_pif, pif_exists, save_pif

def handle_comment(comment):
    # LatherBot shouldn't process its own comments
    if comment.parent_id.startswith("t3"):
        if pif_exists(comment.submission.id):
            pif_obj = get_pif(comment.submission.id)
            pif_obj.handle_comment(comment)
            save_pif(pif_obj)
        else:
            pass
    else:
        pass