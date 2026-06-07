from __future__ import annotations

from typing import Any

from utils import poker_util


def test_royal_flush_detection() -> None:
    hand: list[Any] = [[10, "♥"], ["J", "♥"], ["Q", "♥"], ["K", "♥"], ["A", "♥"]]
    result = poker_util.determine_hand(hand)
    assert result == "Straight flush to the Ace"


def test_straight_flush_to_the_five() -> None:
    hand: list[Any] = [[2, "♥"], [3, "♥"], [4, "♥"], [5, "♥"], ["A", "♥"]]
    result = poker_util.determine_hand(hand)
    assert "Straight flush" in result
    assert "5" in result


def test_straight_flush_to_the_six() -> None:
    hand: list[Any] = [[2, "♥"], [3, "♥"], [4, "♥"], [5, "♥"], [6, "♥"]]
    result = poker_util.determine_hand(hand)
    assert "Straight flush" in result
    assert "6" in result


def test_four_of_a_kind() -> None:
    hand: list[Any] = [[10, "♦"], [10, "♠"], [10, "♥"], [10, "♣"], ["K", "♥"]]
    assert poker_util.determine_hand(hand) == "Four of a kind 10s"


def test_full_boat() -> None:
    hand: list[Any] = [[10, "♦"], [10, "♠"], [10, "♥"], ["K", "♦"], ["K", "♥"]]
    assert "Full house" in poker_util.determine_hand(hand)


def test_flush() -> None:
    hand: list[Any] = [[2, "♥"], ["J", "♥"], ["Q", "♥"], ["K", "♥"], ["A", "♥"]]
    assert "Flush" in poker_util.determine_hand(hand)


def test_straight() -> None:
    hand: list[Any] = [[10, "♦"], ["J", "♥"], ["Q", "♥"], ["K", "♥"], ["A", "♥"]]
    assert "Straight to" in poker_util.determine_hand(hand)


def test_five_high_straight() -> None:
    hand: list[Any] = [[2, "♦"], [3, "♥"], [4, "♥"], [5, "♥"], ["A", "♥"]]
    result = poker_util.determine_hand(hand)
    assert "Straight" in result
    assert "5" in result


def test_six_high_straight() -> None:
    hand: list[Any] = [[2, "♦"], [3, "♥"], [4, "♥"], [5, "♥"], [6, "♥"]]
    result = poker_util.determine_hand(hand)
    assert "Straight" in result
    assert "6" in result


def test_trips() -> None:
    hand: list[Any] = [[10, "♦"], [10, "♠"], [10, "♥"], ["Q", "♦"], ["K", "♥"]]
    assert "Three of a kind" in poker_util.determine_hand(hand)


def test_two_pair() -> None:
    hand: list[Any] = [[2, "♦"], [10, "♠"], [10, "♥"], ["K", "♦"], ["K", "♥"]]
    assert "Two pair" in poker_util.determine_hand(hand)


def test_pair() -> None:
    hand: list[Any] = [[2, "♦"], [4, "♠"], [6, "♥"], ["K", "♦"], ["K", "♥"]]
    assert "Pair" in poker_util.determine_hand(hand)


def test_high_card() -> None:
    hand: list[Any] = [[2, "♦"], [4, "♥"], [6, "♥"], [8, "♥"], ["K", "♥"]]
    assert "High card" in poker_util.determine_hand(hand)
