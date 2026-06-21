"""
Created on May 5, 2020

@author: rcurtis
"""

from __future__ import annotations

import logging
from typing import Any

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from config import bot_name
from pifs.base_pif import BasePIF
from pifs.registry import register_pif
from utils.karma_calculator import calculate_karma, formatted_karma
from utils.reddit_helper import get_submission

instructionTemplate = """
Welcome to {}'s PIF (with karma checks by {bot_name}).

In order to qualify, you must have at least {} karma on the sub in the last 90 days.

I will do a karma check on all top-level comments to determine whether
or not the user meets the minimum karma.

This PIF will close in {} hour(s).  At that time, I will lock this post
and the PIF's creator will select the winner.

{bot_name} documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

If you see something, say something: [Report PIF Abuse](https://docs.google.com/forms/d/e/1FAIpQLScLVbYclUvKMbhrrz0WhfOKPQyr56_jH-4q8oOJf_emgAew7w/viewform?usp=sf_link)

Good luck!
"""


@register_pif
class KarmaOnly(BasePIF):
    pif_type = "karma-only"

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
        logging.debug("Building karma-only PIF [%s]", postId)
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
        """Not used for KarmaOnly PIFs — entry logic is in handle_comment."""

    def determine_winner(self) -> None:
        """Not used for KarmaOnly PIFs — no winner determination needed."""

    def generate_winner_comment(self) -> str:
        """Not used for KarmaOnly PIFs — no winner announcement needed."""
        return ""

    def is_already_entered(self, user: Redditor, comment: Comment) -> bool:
        return False

    def handle_comment(self, comment: Comment) -> bool | None:
        user = comment.author
        if not comment.parent_id.startswith("t3_"):
            return None
        karma = calculate_karma(user)
        if karma is None:
            comment.reply("I was unable to calculate your karma. Please try again later.")
            comment.save()
            return True
        formattedKarma = formatted_karma(user, karma)
        if user.name == self.authorName:
            comment.save()
            return None
        elif karma[0] >= self.minKarma:
            logging.debug(
                "User [%s] meets karma requirement for PIF [%s]",
                user.name,
                self.postId,
            )
            comment.reply(
                "Congratulations, you have the karma for this PIF\n\n" + formattedKarma
            )
            comment.save()
            return True
        else:
            logging.info(
                "User [%s] does not meet karma requirement for PIF [%s]",
                user.name,
                self.postId,
            )
            comment.reply(
                "I'm afraid you don't have the karma for this PIF\n\n" + formattedKarma
            )
            comment.save()
            return True

    def finalize(self) -> None:
        logging.info("Finalizing PIF [%s]", self.postId)
        # Get the original PIF post
        submission = get_submission(self.postId)

        comment = submission.reply("The PIF is over!")
        submission.mod.flair(text="PIF - Winner", css_class="orange")
        comment.mod.distinguish("yes", True)

        logging.info("Closing and locking PIF [%s]", self.postId)
        submission.mod.lock()
        self.pifState = "closed"
