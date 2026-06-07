"""
Created on Jan 27, 2021

@author: rcurtis
"""

from __future__ import annotations

import logging
import random
from typing import Any

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from pifs.registry import register_pif

instructionTemplate = """
Welcome to {}'s randomizer PIF (managed by LatherBot).

When the PIF is over, the list of qualified entries will be randomized
and prizes will be awarded based
on the randomized order.  In order to qualify, you must have at least {}
karma on the sub in the
last 90 days.

To enter, simply add a top-level comment on the PIF post that includes
(on a line by itself) the command:

`LatherBot in`

I will check your karma and mark you as entered if you qualify.
**Remember**, you only get one shot at
entering, so if you're not sure you've got the karma, use the
`LatherBot karma` command to do a check
before entering.

This PIF will close in {} hour(s).  At that time, I will generate the
randomized list and notify
the PIF's creator.

LatherBot documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

If you see something, say something: [Report PIF Abuse](https://docs.google.com/forms/d/e/1FAIpQLScLVbYclUvKMbhrrz0WhfOKPQyr56_jH-4q8oOJf_emgAew7w/viewform?usp=sf_link)

Good luck!
"""

winner_template = """
The PIF is over!

There were {} qualified entries. The randomized list of qualified entries is:

{}
"""


@register_pif
class Randomizer(BasePIF):
    pif_type = "randomizer"

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
        logging.debug("Building randomizer PIF [%s]", postId)
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
            self.authorName, self.minKarma, self.durationHours
        )

    def handle_entry(
        self, comment: Comment, user: Redditor, command_parts: list[str]
    ) -> None:
        logging.info("User [%s] entered to PIF [%s]", user, self.postId)
        self.pifEntries[user.name] = comment.id
        comment.reply(f"Entry confirmed for {user.name}")
        comment.save()

    def determine_winner(self) -> None:
        winners = list(self.pifEntries.keys())

        logging.info("Before first shuffle: [%s]", ", ".join(winners))
        random.shuffle(winners)

        logging.info("After first shuffle: [%s]", ", ".join(winners))
        random.shuffle(winners)

        logging.info("After second shuffle: [%s]", ", ".join(winners))
        random.shuffle(winners)

        logging.info(
            "After third shuffle: [%s] generated for PIF [%s]",
            ", ".join(winners),
            self.postId,
        )

        self.pifWinner = winners  # type: ignore[assignment]

    def generate_winner_comment(self) -> str:
        randomized_list = ""
        for entrant in self.pifWinner:
            randomized_list += "1) u/" + entrant + "\n"
        return winner_template.format(len(self.pifEntries), randomized_list)
