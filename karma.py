'''
Created on May 10, 2020

@author: rcurtis
'''

from utils.karma_calculator import formatted_karma_check

import praw

import sys

bot_name="PIFBot"
user_agent="script:PIFBot:0.1 (by u/BourbonInExile and u/MrSabuhudo)"

def check_karma():
    reddit = praw.Reddit(bot_name, user_agent=user_agent)
    user = reddit.redditor(sys.argv[1])
    print(formatted_karma_check(user))

if __name__ == '__main__':
    check_karma()