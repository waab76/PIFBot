#!/usr/bin/env python3
#
#   File = range_pif.py
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

from random import randrange
from typing import Any

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from pifs.registry import register_pif
from utils.reddit_helper import get_comment

instructionTemplate = """
Welcome to {}'s Pick-a-Number PIF (managed by LatherBot).

When the PIF ends, I'll choose a random number between {} and {}.
Whoever guesses closest to
that number will be the winner. If two entrants are the same distance
away, the one who got
closest without going over will win (Price Is Right tie-breaker).
In order to qualify, you must
have at least {} karma on the sub in the last 90 days.

To enter, simply add a top-level comment on the PIF post that includes
(on a line by itself) the command:

`LatherBot IN <your guess>`

I will check your karma and record your guess if you qualify.  Example:

`LatherBot IN 23`

This PIF will close in {} hour(s). At that time, I will determine the
winner and notify the PIF's creator.

LatherBot documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

If you see something, say something: [Report PIF Abuse](https://docs.google.com/forms/d/e/1FAIpQLScLVbYclUvKMbhrrz0WhfOKPQyr56_jH-4q8oOJf_emgAew7w/viewform?usp=sf_link)

Good luck!
"""

winner_template = """
The PIF is over!

There winning number is {} and the winner is u/{} with a guess of {}.  Congratulations!
"""


@register_pif
class Range(BasePIF):
    pif_type = "range"

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
    ):
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
        return instructionTemplate.format(
            self.authorName,
            self.pifOptions["RangeMin"],
            self.pifOptions["RangeMax"],
            self.minKarma,
            self.durationHours,
        )

    def handle_entry(
        self, comment: Comment, user: Redditor, command_parts: list[str]
    ) -> None:
        guess = None
        try:
            guess = int(command_parts[2])
        except IndexError:
            comment.reply(
                "It looks like you were trying to enter the PIF but something "
                "was wrong with the command you entered.  Please re-read the "
                "instructions and try again on a brand new comment (because "
                "the bot only processes each comment once and this one has "
                "already been processed"
            )
            comment.save()
            return
        except ValueError:
            comment.reply(
                "[{}] isn't a number between {} and {}.  You will need "
                "to try again in a brand new comment.".format(
                    command_parts[2],
                    self.pifOptions["RangeMin"],
                    self.pifOptions["RangeMax"],
                )
            )
            comment.save()
            return

        conflict = self.userAlreadyGuessed(guess)
        if conflict is not None:
            comment.reply(
                f"I'm sorry, {guess} was already taken by {conflict}.  "
                f"Try again in a brand new comment."
            )
            comment.save()
        elif guess > self.pifOptions["RangeMax"]:
            comment.reply(
                "I'm sorry, {} is above the max allowable guess of {}.  "
                "Try again in a brand new comment.".format(
                    guess, self.pifOptions["RangeMax"]
                )
            )
            comment.save()
        elif guess < self.pifOptions["RangeMin"]:
            comment.reply(
                "I'm sorry, {} is below the min allowable guess of {}.  "
                "Try again in a brand new comment.".format(
                    guess, self.pifOptions["RangeMin"]
                )
            )
            comment.save()
        else:
            entryDetails = dict()
            entryDetails["CommentId"] = comment.id
            entryDetails["Guess"] = guess
            self.pifEntries[user.name] = entryDetails  # type: ignore[assignment]
            comment.reply(f"Entry confirmed.  {user.name} guessed {guess}")
            comment.save()

    def determine_winner(self) -> None:
        self.winningNumber = randrange(
            self.pifOptions["RangeMin"], self.pifOptions["RangeMax"] + 1
        )
        currWinner = "TBD"
        currWinningGuess = self.pifOptions["RangeMax"] + 1
        currWinningDistance = currWinningGuess
        for entrant in self.pifEntries:
            if (
                self.postId
                != get_comment(self.pifEntries[entrant]["CommentId"]).submission.id  # type: ignore[index]
            ):
                continue
            guess = self.pifEntries[entrant]["Guess"]  # type: ignore[index]
            guessDistance = abs(guess - self.winningNumber)  # type: ignore[operator]
            if (
                guessDistance < currWinningDistance
                or guessDistance == currWinningDistance
                and guess < currWinningGuess  # type: ignore[operator]
            ):
                currWinner = entrant
                currWinningGuess = guess  # type: ignore[assignment]
                currWinningDistance = guessDistance
        self.pifWinner = currWinner

    def generate_winner_comment(self) -> str:
        return winner_template.format(
            self.winningNumber,
            self.pifWinner,
            self.pifEntries[self.pifWinner]["Guess"],  # type: ignore[index]
        )

    def userAlreadyGuessed(self, guess: int) -> str | None:
        for entry in self.pifEntries:
            if guess == self.pifEntries[entry]["Guess"]:  # type: ignore[index]
                return entry
        return None
