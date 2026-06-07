#!/usr/local/bin/python3
#
#   File = poker.py
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

from typing import Any

from utils import poker_util


def test_hands() -> None:
    hands: list[list[Any]] = list()
    royal_flush: list[Any] = [[10, "♥"], ["J", "♥"], ["Q", "♥"], ["K", "♥"], ["A", "♥"]]
    hands.append(royal_flush)
    straight_flush_to_the_five: list[Any] = [
        [2, "♥"],
        [3, "♥"],
        [4, "♥"],
        [5, "♥"],
        ["A", "♥"],
    ]
    hands.append(straight_flush_to_the_five)
    straight_flush_to_the_six: list[Any] = [
        [2, "♥"],
        [3, "♥"],
        [4, "♥"],
        [5, "♥"],
        [6, "♥"],
    ]
    hands.append(straight_flush_to_the_six)
    four_of_a_kind: list[Any] = [[10, "♦"], [10, "♠"], [10, "♥"], [10, "♣"], ["K", "♥"]]
    hands.append(four_of_a_kind)
    full_boat: list[Any] = [[10, "♦"], [10, "♠"], [10, "♥"], ["K", "♦"], ["K", "♥"]]
    hands.append(full_boat)
    flush: list[Any] = [[2, "♥"], ["J", "♥"], ["Q", "♥"], ["K", "♥"], ["A", "♥"]]
    hands.append(flush)
    straight: list[Any] = [[10, "♦"], ["J", "♥"], ["Q", "♥"], ["K", "♥"], ["A", "♥"]]
    hands.append(straight)
    five_high_straight: list[Any] = [[2, "♦"], [3, "♥"], [4, "♥"], [5, "♥"], ["A", "♥"]]
    hands.append(five_high_straight)
    six_high_straight: list[Any] = [[2, "♦"], [3, "♥"], [4, "♥"], [5, "♥"], [6, "♥"]]
    hands.append(six_high_straight)
    trips: list[Any] = [[10, "♦"], [10, "♠"], [10, "♥"], ["Q", "♦"], ["K", "♥"]]
    hands.append(trips)
    two_pair: list[Any] = [[2, "♦"], [10, "♠"], [10, "♥"], ["K", "♦"], ["K", "♥"]]
    hands.append(two_pair)
    pair: list[Any] = [[2, "♦"], [4, "♠"], [6, "♥"], ["K", "♦"], ["K", "♥"]]
    hands.append(pair)
    high_card: list[Any] = [[2, "♦"], [4, "♥"], [6, "♥"], [8, "♥"], ["K", "♥"]]
    hands.append(high_card)
    low_ace_straight: list[Any] = [[2, "♦"], [3, "♥"], [4, "♥"], [5, "♥"], ["A", "♥"]]
    hands.append(low_ace_straight)

    for hand in hands:
        print(
            f"{hand} - {poker_util.determine_hand(hand)} - {poker_util.hand_score(hand)}"
        )


def test_poker() -> None:
    deck: list[Any] = poker_util.new_deck()
    tied_winners: list[list[Any]] = list()
    curr_max_score: int = 0

    shared_cards: list[list[Any]] = list()
    for i in range(3):
        shared_cards.append(poker_util.deal_card(deck))

        print("--------------------")
        print(f"Shared cards: {poker_util.order_cards(shared_cards)}")

    while len(deck) > 2:
        hand = list()
        for card in shared_cards:
            hand.append(card)
        for i in range(2):
            hand.append(poker_util.deal_card(deck))
        ordered = poker_util.order_cards(hand)
        print(
            f"{ordered} - {poker_util.determine_hand(hand)} - {poker_util.hand_score(hand)}"
        )
        if poker_util.hand_score(ordered) > curr_max_score:
            tied_winners = list()
            tied_winners.append(ordered)
            curr_max_score = poker_util.hand_score(ordered)
        elif poker_util.hand_score(ordered) == curr_max_score:
            tied_winners.append(ordered)

    print("--------------------")

    if len(tied_winners) == 1:
        print(
            f"{tied_winners[0]} - {poker_util.determine_hand(tied_winners[0])} - {poker_util.hand_score(tied_winners[0])}"
        )
    else:
        print(
            f"{len(tied_winners)} hands tied for win: {tied_winners[0]} - {poker_util.determine_hand(tied_winners[0])} - {poker_util.hand_score(tied_winners[0])}"
        )


if __name__ == "__main__":
    test_hands()
