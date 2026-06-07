#!/usr/bin/env python3
#
#   File = poker_util.py
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
from typing import Any, cast

Card = list[int | str]

suit_list = ["♠", "♥", "♣", "♦"]
value_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]


def new_deck() -> list[Card]:
    logging.debug("Building new deck")
    deck: list[Card] = []
    for suit in suit_list:
        for value in value_list:
            deck.append(cast(Card, [value, suit]))
    return deck


def deal_card(deck: list[Card]) -> Card:
    random.seed(None)
    card = random.choice(deck)
    deck.remove(card)
    logging.debug(f"Dealt {format_card(card)}")
    return card


def card_name(card: Card) -> str:
    if card[0] == "A":
        return "Ace"
    elif card[0] == "K":
        return "King"
    elif card[0] == "Q":
        return "Queen"
    elif card[0] == "J":
        return "Jack"
    else:
        return str(card[0])


def card_point_value(card: Card) -> int:
    return value_list.index(card[0]) + 1


def format_card(card: Card) -> str:
    return f"{card[0]}{card[1]}"


def order_cards(hand: list[Card]) -> list[Card]:
    ordered_hand = []
    for value in value_list:
        for card in hand:
            try:
                if int(card[0]) == value:
                    ordered_hand.append(card)
            except ValueError:
                if card[0] == value:
                    ordered_hand.append(card)
    return ordered_hand


# Helper for is_straight()
def ordered_hand_values(ordered_hand: list[Card]) -> str:
    player_values = []
    for card in ordered_hand:
        player_values.append(str(card[0]))

    return "".join(player_values)


def is_straight(hand: list[Card]) -> bool:
    ordered_values = ordered_hand_values(hand)
    return ordered_values in "2345678910JQKA" or ordered_values == "2345A"


def is_flush(hand: list[Card]) -> bool:
    hand_suit_set = set()
    for card in hand:
        hand_suit_set.add(card[1])
    return len(hand_suit_set) == 1


def check_multiples(hand: list[Card]) -> list[list[Any]]:
    values_list = []
    values_set = set()
    for card in hand:
        values_set.add(card[0])
        values_list.append(card[0])

    counted_values = []
    for value in values_set:
        if values_list.count(value) > 1:
            counted_values.append([value, values_list.count(value)])

    return counted_values


def compute_dup_values(hand: list[Card]) -> str | bool:
    dupes_list = check_multiples(hand)

    if len(dupes_list) == 0:
        return False

    if len(dupes_list) == 1:
        if dupes_list[0][1] == 4:
            return f"Four of a kind {card_name(dupes_list[0])}s"
        if dupes_list[0][1] == 3:
            return f"Three of a kind {card_name(dupes_list[0])}s"
        if dupes_list[0][1] == 2:
            return f"Pair of {card_name(dupes_list[0])}s"

    if len(dupes_list) == 2:
        if dupes_list[0][1] == 3:
            return (
                f"Full house {card_name(dupes_list[0])}s full of "
                f"{card_name(dupes_list[1])}s"
            )
        elif dupes_list[1][1] == 3:
            return (
                f"Full house {card_name(dupes_list[1])}s full of "
                f"{card_name(dupes_list[0])}s"
            )
        else:
            return (
                f"Two pair {card_name(dupes_list[0])}s and {card_name(dupes_list[1])}s"
            )

    return False


def determine_hand(hand: list[Card]) -> str:
    ordered_hand = order_cards(hand)
    dups_str = compute_dup_values(ordered_hand)
    if is_straight(ordered_hand) and is_flush(ordered_hand):
        high_card = ordered_hand[4]
        if card_name(ordered_hand[3]) == "5" and card_name(ordered_hand[4]) == "Ace":
            high_card = ordered_hand[3]
        return f"Straight flush to the {card_name(high_card)}"
    elif is_flush(hand):
        return f"Flush {card_name(ordered_hand[4])} high"
    elif is_straight(hand):
        high_card = ordered_hand[4]
        if card_name(ordered_hand[3]) == "5" and card_name(ordered_hand[4]) == "Ace":
            high_card = ordered_hand[3]
        return f"Straight to the {card_name(high_card)}"
    elif not dups_str:
        return determine_high_card(ordered_hand)
    else:
        assert isinstance(dups_str, str)
        return dups_str


def determine_high_card(hand: list[Card]) -> str:
    ordered_hand = order_cards(hand)
    return f"High card {card_name(ordered_hand[4])}"


def hand_score(hand: list[Card]) -> int:
    ordered_hand = order_cards(hand)
    hand_label = determine_hand(ordered_hand)
    multiples = check_multiples(ordered_hand)

    score = 0
    if hand_label.startswith("Straight flush"):
        score += 8000000
        high_card = ordered_hand[4]
        if card_name(ordered_hand[3]) == "5" and card_name(ordered_hand[4]) == "Ace":
            high_card = ordered_hand[3]
        score += card_point_value(high_card)
    elif hand_label.startswith("Four"):
        score += 7000000
        score += 15 * card_point_value(multiples[0])
        if ordered_hand[4][0] == multiples[0][0]:
            score += card_point_value(ordered_hand[0])
        else:
            score += card_point_value(ordered_hand[4])
    elif hand_label.startswith("Full"):
        score += 6000000
        multiples = check_multiples(hand)
        if multiples[0][0] == 3:
            score += 15 * card_point_value(multiples[0])
            score += card_point_value(multiples[1])
        else:
            score += card_point_value(multiples[0])
            score += 15 * card_point_value(multiples[1])
    elif hand_label.startswith("Flush"):
        score += 5000000
        score += (15**4) * card_point_value(ordered_hand[4])
        score += (15**3) * card_point_value(ordered_hand[3])
        score += (15**2) * card_point_value(ordered_hand[2])
        score += 15 * card_point_value(ordered_hand[1])
        score += card_point_value(ordered_hand[0])
    elif hand_label.startswith("Straight"):
        high_card = ordered_hand[4]
        if card_name(ordered_hand[3]) == "5" and card_name(ordered_hand[4]) == "Ace":
            high_card = ordered_hand[3]
        score += 4000000
        score += card_point_value(high_card)
    elif hand_label.startswith("Three"):
        score += 3000000
        score += (15**2) * card_point_value(multiples[0])
        multiple = 1
        for kicker in ordered_hand:
            if kicker[0] != multiples[0][0]:
                score += multiple * card_point_value(kicker)
                multiple *= 15
    elif hand_label.startswith("Two"):
        score += 2000000
        if value_list.index(multiples[0][0]) > value_list.index(multiples[1][0]):
            score += 15 * 15 * card_point_value(multiples[0])
            score += 15 * card_point_value(multiples[1])
        else:
            score += 15 * 15 * card_point_value(multiples[1])
            score += 15 * card_point_value(multiples[0])
        for kicker in ordered_hand:
            if kicker[0] != multiples[0][0] and kicker[0] != multiples[1][0]:
                score += card_point_value(kicker)
    elif hand_label.startswith("Pair"):
        score += 1000000
        score += (15**3) * card_point_value(multiples[0])
        multiple = 1
        for kicker in ordered_hand:
            if kicker[0] != multiples[0][0]:
                score += multiple * card_point_value(kicker)
                multiple *= 15
    else:
        score += (15**4) * card_point_value(ordered_hand[4])
        score += (15**3) * card_point_value(ordered_hand[3])
        score += (15**2) * card_point_value(ordered_hand[2])
        score += 15 * card_point_value(ordered_hand[1])
        score += card_point_value(ordered_hand[0])

    return score
