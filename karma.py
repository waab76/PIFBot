"""
Created on May 10, 2020

@author: rcurtis
"""

from __future__ import annotations

import sys

import praw  # type: ignore[import-untyped]

from utils.karma_calculator import formatted_karma_check

bot_name: str = "PIFBot"
user_agent: str = "script:PIFBot:0.1 (by u/BourbonInExile and u/MrSabuhudo)"


def check_karma() -> None:
    reddit: praw.Reddit = praw.Reddit(bot_name, user_agent=user_agent)
    user = reddit.redditor(sys.argv[1])
    print(formatted_karma_check(user))


if __name__ == "__main__":
    check_karma()
