#!/usr/local/bin/python3
#
#   File = pif_stats.py
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

import time
from typing import Any

from pifs import pif_builder
from utils import poker_util, reddit_helper
from utils.pif_storage import fetch_all_pifs


def main() -> None:
    pif_list = fetch_all_pifs()
    piffers: dict[str, int] = {}
    winners: dict[str, int] = {}
    pif_types: dict[str, int] = {}
    pif_type_entries: dict[str, int] = {}
    entrants: dict[str, int] = {}
    pif_count = 0
    entry_count = 0
    history_days = 180
    thirty_days_ago = time.time() - (history_days * 24 * 60 * 60)
    best_poker_hand_score = 0
    best_poker_hand_user = "TBD"
    best_poker_hand: list[Any] = []

    for pif_type in pif_builder.known_pif_types():
        pif_types[pif_type] = 0
        pif_type_entries[pif_type] = 0

    for pif in pif_list:
        submission = reddit_helper.reddit.submission(pif.postId)
        if submission.created_utc < thirty_days_ago:
            continue

        pif_type = pif.pifType
        pif_count += 1

        if pif.authorName not in piffers:
            piffers[pif.authorName] = 0
        piffers[pif.authorName] += 1

        if pif.pifWinner != "TBD":
            if pif.pifWinner not in winners:
                winners[pif.pifWinner] = 0
            winners[pif.pifWinner] += 1

            if pif_type == "infinite-poker":
                winner_entry = pif.pifEntries[pif.pifWinner]
                assert isinstance(winner_entry, dict)  # EntryDict for infinite-poker
                if winner_entry["HandScore"] > best_poker_hand_score:
                    best_poker_hand_score = winner_entry["HandScore"]
                    best_poker_hand_user = pif.pifWinner
                    best_poker_hand = winner_entry["UserHand"]

        pif_types[pif_type] += 1

        for entrant in pif.pifEntries:
            if entrant not in entrants:
                entrants[entrant] = 0
            entrants[entrant] += 1
            entry_count += 1
            pif_type_entries[pif_type] += 1

    sorted_piffers = sorted(piffers.items(), key=lambda kv: (kv[1], kv[0]))[::-1]
    sorted_pif_types = sorted(pif_types.items(), key=lambda kv: (kv[1], kv[0]))[::-1]
    sorted_winners = sorted(winners.items(), key=lambda kv: (kv[1], kv[0]))[::-1]
    sorted_entrants = sorted(entrants.items(), key=lambda kv: (kv[1], kv[0]))[::-1]

    print(f"""
LatherBot PIF stats for the trailing {history_days} days

\--------------------------------------------

{pif_count} PIFs by {len(piffers)} Redditors:

|Redditor|PIFs|
|:-|:-|""")

    for piffer in sorted_piffers:
        print(f"|u/{piffer[0]}|{piffer[1]}|")

    print(f"""\nThere were {entry_count} entries across the {pif_count} PIFs. The top 10 most active PIF contestants were:

|Redditor|Entries|
|:-|:-|""")
    for i in range(10):
        print(f"|u/{sorted_entrants[i][0]}|{sorted_entrants[i][1]}|")

    print("\nWinningest Redditors:\n\n|Redditor|Wins|\n|:-|:-|")
    for pif_winner in sorted_winners:
        print(f"|u/{pif_winner[0]}|{pif_winner[1]}|")

    print("\nMost popular PIF types:\n\n|PIF Type|Count|Entries per PIF|\n|:-|:-|:-|")
    for pt in sorted_pif_types:
        avg_entries: float = 0
        if pt[1] > 0:
            avg_entries = round(pif_type_entries[pt[0]] / pt[1], 2)
        print(f"|{pt[0]}|{pt[1]}|{avg_entries}|")

    print(
        f"\nBest poker hand: {best_poker_hand_user} with {poker_util.determine_hand(best_poker_hand)}"
    )


if __name__ == "__main__":
    main()
