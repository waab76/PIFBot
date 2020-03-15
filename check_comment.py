#!/usr/bin/env python3
# coding: utf-8
#
#   File = check_comment.py
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

import sys

from utils import reddit_helper
from handlers import comment_handler

def main():
    # print command line arguments
    for arg in sys.argv[1:]:
        print(arg)

def check_comment(comment_id):
    comment = reddit_helper.reddit.comment(id=comment_id)

    print("got comment [{}]".format(comment.body))

    for line in comment.body.lower().split('\n'):
        print(line.split())

    comment_handler.handle_comment(comment)

if __name__ == '__main__':
    check_comment(sys.argv[1])