"""
Created on Apr 20, 2020

@author: rcurtis
"""

from __future__ import annotations

import logging
import random
from typing import Any

import pandas as pd  # type: ignore[import-untyped]
from geopy.distance import distance  # type: ignore[import-untyped]
from geopy.geocoders import Nominatim  # type: ignore[import-untyped]
from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from pifs.pif_builder import register_pif
from utils.reddit_helper import get_comment, user_agent

instructionTemplate = """
Welcome to {}'s Geo PIF (managed by LatherBot).

When the PIF ends, I'll choose a random spot on the globe. Whoever's guess is closest to that
spot will be the winner. In order to qualify, you must have at least {} karma on the sub in
the last 90 days.

To enter, simply add a top-level comment on the PIF post that includes (on a line by itself) the command:

`LatherBot in <your guess>`

I will check your karma and record your guess if you qualify.  Example:

`LatherBot in Cleveland, Ohio`

or

`LatherBot in Moscow, Russia`

This PIF will close in {} hour(s). At that time, I will determine the winner and notify the PIF's creator.

LatherBot documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

If you see something, say something: [Report PIF Abuse](https://docs.google.com/forms/d/e/1FAIpQLScLVbYclUvKMbhrrz0WhfOKPQyr56_jH-4q8oOJf_emgAew7w/viewform?usp=sf_link)

Good luck!
"""

winner_template = """
The PIF is over!

The spot on the globe I chose was [({})](https://maps.google.com/maps?q={})

The winner is u/{} with a guess of {} : ({}), {} km away.  Congratulations!
"""

geolocator: Nominatim = Nominatim(user_agent=user_agent)


@register_pif
class Geo(BasePIF):
    pif_type = "geo"

    def __init__(
        self,
        postId: str,
        authorName: str,
        minKarma: int | str,
        durationHours: int | str,
        endTime: int | str,
        pifOptions: dict[str, Any] = {},
        pifEntries: dict[str, Any] = {},
        karmaFail: dict[str, Any] = {},
    ):
        logging.debug("Building Geo PIF [%s]", postId)
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
        guess = None
        try:
            guess = " ".join(command_parts[2:])
        except IndexError:
            comment.reply(
                "It looks like you were trying to enter the PIF but something was wrong with the command you entered.  Please re-read the instructions and try again on a brand new comment (because the bot only processes each comment once and this one has already been processed)"
            )
            comment.save()
            return

        guessed_location = geolocator.geocode(guess)
        if guessed_location is None:
            comment.reply(
                f"I'm sorry, I couldn't find [{guess}] on the map.  You will need to try again in a brand new comment."
            )
            comment.save()
            return

        conflict = self.userAlreadyGuessed(guessed_location.address)
        if conflict is not None:
            comment.reply(
                f"I'm sorry, {guess} was already taken by {conflict}.  You will need to try again in a brand new comment."
            )
            comment.save()
            return

        entryDetails = dict()
        entryDetails["CommentId"] = comment.id
        entryDetails["Guess"] = guess
        entryDetails["GuessAddr"] = guessed_location.address
        entryDetails["GuessLatLon"] = (
            f"{guessed_location.latitude}, {guessed_location.longitude}"
        )
        self.pifEntries[user.name] = entryDetails  # type: ignore[assignment]
        comment.reply(
            f"Entry confirmed.  {user.name} guessed {guessed_location.address} at [lat/lon ({guessed_location.latitude},{guessed_location.longitude})](https://maps.google.com/maps?q={guessed_location.latitude}%2C+{guessed_location.longitude})"
        )
        comment.save()

    def determine_winner(self) -> None:
        win_lat = random.randrange(-900000000, 900000000) / 10000000
        win_lon = random.randrange(-1800000000, 1800000000) / 10000000

        self.pifOptions["WinLatLon"] = f"{win_lat},{win_lon}"

        df = pd.DataFrame(columns=("name", "lat", "lon", "distance"))

        self.pifWinner = "TBD"
        self.winningDistance = 20005
        entrant_num = 0
        for entrant in self.pifEntries.keys():
            if (
                self.postId
                != get_comment(self.pifEntries[entrant]["CommentId"]).submission.id  # type: ignore[index]
            ):
                continue
            guessLatLon = self.pifEntries[entrant]["GuessLatLon"]  # type: ignore[index]
            guess_lat = float(guessLatLon.split(", ")[0])
            guess_lon = float(guessLatLon.split(", ")[1])
            guess_dist = distance((win_lat, win_lon), (guess_lat, guess_lon)).km
            df.loc[entrant_num] = [entrant, guess_lat, guess_lon, guess_dist]
            entrant_num += 1
            if guess_dist < self.winningDistance:
                self.pifWinner = entrant
                self.winningDistance = guess_dist

    def generate_winner_comment(self) -> str:
        return winner_template.format(
            self.pifOptions["WinLatLon"],
            self.pifOptions["WinLatLon"],
            self.pifWinner,
            self.pifEntries[self.pifWinner]["Guess"],  # type: ignore[index]
            self.pifEntries[self.pifWinner]["GuessLatLon"],  # type: ignore[index]
            self.winningDistance,
        )

    def userAlreadyGuessed(self, guess: str) -> str | None:
        for entry in self.pifEntries.keys():
            if guess == self.pifEntries[entry]["GuessAddr"]:  # type: ignore[index]
                return entry
        return None
