#! /usr/local/bin/python3

'''
Created on Feb 24, 2020

@author: rcurtis
'''
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