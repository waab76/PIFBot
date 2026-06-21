#!/usr/bin/env python3
#
#   File = lottery_pif.py
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
from __future__ import annotations

import logging
import random
from typing import Any

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from config import bot_name
from pifs.base_pif import BasePIF
from pifs.registry import register_pif
from utils.reddit_helper import get_comment

instructionTemplate = """
Welcome to {}'s Lottery PIF (managed by {bot_name}).

The winner will be randomly selected from all qualified entries.  In order to qualify,
you must have at least {} karma on the sub in the last 90 days.

To enter, simply add a top-level comment on the PIF post that includes
(on a line by itself) the command:

`{bot_name} in`

I will check your karma and mark you as entered if you qualify.

This PIF will close in {} hour(s).  At that time, I will select the
winner at random and notify
the PIF's creator.

{bot_name} documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

If you see something, say something: [Report PIF Abuse](https://docs.google.com/forms/d/e/1FAIpQLScLVbYclUvKMbhrrz0WhfOKPQyr56_jH-4q8oOJf_emgAew7w/viewform?usp=sf_link)

Good luck!
"""

winner_template = """
The PIF is over!

There were {} qualified entries and the winner is u/{}.  Congratulations!
"""


@register_pif
class Lottery(BasePIF):
    pif_type = "lottery"

    def __init__(
        self,
        postId: str,
        authorName: str,
        minKarma: int | str,
        durationHours: int | str,
        endTime: int | str,
        pifOptions: dict[str, Any] | None = None,
        pifEntries: dict[str, Any] | None = None,
        karmaFail: dict[str, Any] | None = None,
    ) -> None:
        logging.debug("Building lottery PIF [%s]", postId)
        super().__init__(
            postId=postId,
            authorName=authorName,
            pifType=self.pif_type,
            minKarma=minKarma,
            durationHours=durationHours,
            endTime=endTime,
            pifOptions=pifOptions,  # type: ignore[arg-type]
            pifEntries=pifEntries,
            karmaFail=karmaFail,
        )

    def pif_instructions(self) -> str:
        logging.info("Printing instructions for PIF [%s]", self.postId)
        return instructionTemplate.format(
            self.authorName, self.minKarma, self.durationHours, bot_name=bot_name
        )

    def handle_entry(
        self, comment: Comment, user: Redditor, command_parts: list[str]
    ) -> None:
        logging.info("User [%s] entered to PIF [%s]", user, self.postId)
        self.pifEntries[user.name] = comment.id
        comment.reply(f"Entry confirmed for {user.name}")
        comment.save()

    def determine_winner(self) -> None:
        candidates = list(self.pifEntries.keys())
        random.shuffle(candidates)
        for candidate in candidates:
            if self.postId == get_comment(self.pifEntries[candidate]).submission.id:  # type: ignore[arg-type]
                self.pifWinner = candidate
                logging.info("User [%s] has won PIF [%s]", self.pifWinner, self.postId)
                return
        self.pifWinner = candidates[0]
        logging.warning(
            "No valid entry verified for PIF [%s]; selecting %s as fallback",
            self.postId,
            self.pifWinner,
        )

    def generate_winner_comment(self) -> str:
        return winner_template.format(len(self.pifEntries), self.pifWinner)
