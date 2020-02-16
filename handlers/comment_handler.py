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

from utils.dynamo_helper import pif_exists

def handle_comment(comment):
    print("Processing comment by author: " + comment.author.name)

    if comment.parent_id.startswith("t3"):
        print("It's a top-level comment")
        # Check to see if the parent is a PIF we're tracking an do the thing
        # This kind of implies we'll need a persistent mechanism for tracking PIFs
        if pif_exists(comment.submission.id):
            print("It's a comment on a tracked PIF")

