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

from pifs.pif_builder import build_from_ddb_dict
from utils.dynamo_helper import open_pif_exists, fetch_pif

def handle_comment(comment):
    if comment.parent_id.startswith("t3"):
        print("Comment by author {} is a top-level comment".format(comment.author.name))
        # Check to see if the parent is a PIF we're tracking an do the thing
        # This kind of implies we'll need a persistent mechanism for tracking PIFs
        if open_pif_exists(comment.submission.id):
            print("It's a comment on a tracked PIF")
            ddb_dict = fetch_pif(comment.submission.id)
            pif_obj = build_from_ddb_dict(ddb_dict)
            pif_obj.handle_entry(comment)
        else:
            pass
    else:
        pass