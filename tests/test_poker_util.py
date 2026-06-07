from __future__ import annotations

from typing import Any

import pytest

from utils import poker_util


def test_new_deck_has_52_cards() -> None:
    deck = poker_util.new_deck()
    assert len(deck) == 52


def test_new_deck_all_suits() -> None:
    deck = poker_util.new_deck()
    suits = {card[1] for card in deck}
    assert suits == {"♠", "♥", "♣", "♦"}


def test_new_deck_all_values() -> None:
    deck = poker_util.new_deck()
    values = {card[0] for card in deck}
    assert values == {2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"}


def test_deal_card_removes_from_deck() -> None:
    deck = poker_util.new_deck()
    card = poker_util.deal_card(deck)
    assert len(deck) == 51
    assert card not in deck


def test_card_name_ace() -> None:
    assert poker_util.card_name(["A", "♠"]) == "Ace"


def test_card_name_king() -> None:
    assert poker_util.card_name(["K", "♠"]) == "King"


def test_card_name_number() -> None:
    assert poker_util.card_name([10, "♠"]) == "10"


def test_card_point_value_ace() -> None:
    assert poker_util.card_point_value(["A", "♠"]) == 13


def test_card_point_value_two() -> None:
    assert poker_util.card_point_value([2, "♠"]) == 1


def test_format_card() -> None:
    assert poker_util.format_card(["A", "♠"]) == "A♠"


def test_order_cards() -> None:
    hand: list[Any] = [["K", "♥"], [2, "♠"], ["A", "♦"]]
    ordered = poker_util.order_cards(hand)
    assert ordered[0][0] == 2
    assert ordered[-1][0] == "A"


def test_ordered_hand_values() -> None:
    hand: list[Any] = [[2, "♠"], [3, "♥"], [4, "♦"], [5, "♣"], ["A", "♥"]]
    assert poker_util.ordered_hand_values(hand) == "2345A"


def test_is_straight_ace_low() -> None:
    hand: list[Any] = [["A", "♠"], [2, "♥"], [3, "♦"], [4, "♣"], [5, "♥"]]
    assert poker_util.is_straight(poker_util.order_cards(hand))


def test_is_straight_ten_to_ace() -> None:
    hand: list[Any] = [[10, "♠"], ["J", "♥"], ["Q", "♦"], ["K", "♣"], ["A", "♥"]]
    assert poker_util.is_straight(poker_util.order_cards(hand))


def test_is_straight_false() -> None:
    hand: list[Any] = [[2, "♠"], [4, "♥"], [6, "♦"], [8, "♣"], [10, "♥"]]
    assert not poker_util.is_straight(poker_util.order_cards(hand))


def test_is_flush_true() -> None:
    hand: list[Any] = [[2, "♥"], [5, "♥"], [9, "♥"], ["J", "♥"], ["A", "♥"]]
    assert poker_util.is_flush(hand)


def test_is_flush_false() -> None:
    hand: list[Any] = [[2, "♥"], [5, "♠"], [9, "♥"], ["J", "♥"], ["A", "♥"]]
    assert not poker_util.is_flush(hand)


def test_check_multiples_pair() -> None:
    hand: list[Any] = [[2, "♠"], [2, "♥"], [5, "♦"], [9, "♣"], ["K", "♥"]]
    multiples = poker_util.check_multiples(hand)
    assert len(multiples) == 1
    assert multiples[0] == [2, 2]


def test_check_multiples_two_pair() -> None:
    hand: list[Any] = [[2, "♠"], [2, "♥"], ["K", "♦"], ["K", "♣"], [9, "♥"]]
    multiples = poker_util.check_multiples(hand)
    assert len(multiples) == 2


def test_check_multiples_three_of_a_kind() -> None:
    hand: list[Any] = [[10, "♠"], [10, "♥"], [10, "♦"], ["K", "♣"], [2, "♥"]]
    multiples = poker_util.check_multiples(hand)
    assert multiples[0] == [10, 3]


def test_check_multiples_four_of_a_kind() -> None:
    hand: list[Any] = [[10, "♠"], [10, "♥"], [10, "♦"], [10, "♣"], ["K", "♥"]]
    multiples = poker_util.check_multiples(hand)
    assert multiples[0] == [10, 4]


def test_check_multiples_none() -> None:
    hand: list[Any] = [[2, "♠"], [5, "♥"], [9, "♦"], ["J", "♣"], ["A", "♥"]]
    assert poker_util.check_multiples(hand) == []


def test_determine_hand_royal_flush() -> None:
    hand: list[Any] = [[10, "♥"], ["J", "♥"], ["Q", "♥"], ["K", "♥"], ["A", "♥"]]
    result = poker_util.determine_hand(hand)
    assert "Straight flush" in result
    assert "Ace" in result


def test_determine_hand_straight_flush() -> None:
    hand: list[Any] = [[2, "♥"], [3, "♥"], [4, "♥"], [5, "♥"], [6, "♥"]]
    result = poker_util.determine_hand(hand)
    assert "Straight flush" in result
    assert "6" in result


def test_determine_hand_four_of_a_kind() -> None:
    hand: list[Any] = [[10, "♦"], [10, "♠"], [10, "♥"], [10, "♣"], ["K", "♥"]]
    assert "Four of a kind" in poker_util.determine_hand(hand)


def test_determine_hand_full_house() -> None:
    hand: list[Any] = [[10, "♦"], [10, "♠"], [10, "♥"], ["K", "♦"], ["K", "♥"]]
    assert "Full house" in poker_util.determine_hand(hand)


def test_determine_hand_flush() -> None:
    hand: list[Any] = [[2, "♥"], ["J", "♥"], ["Q", "♥"], ["K", "♥"], ["A", "♥"]]
    assert "Flush" in poker_util.determine_hand(hand)


def test_determine_hand_straight() -> None:
    hand: list[Any] = [[10, "♦"], ["J", "♥"], ["Q", "♥"], ["K", "♥"], ["A", "♥"]]
    assert "Straight to" in poker_util.determine_hand(hand)


def test_determine_hand_five_high_straight() -> None:
    hand: list[Any] = [[2, "♦"], [3, "♥"], [4, "♥"], [5, "♥"], ["A", "♥"]]
    result = poker_util.determine_hand(hand)
    assert "Straight" in result
    assert "5" in result


def test_determine_hand_three_of_a_kind() -> None:
    hand: list[Any] = [[10, "♦"], [10, "♠"], [10, "♥"], ["Q", "♦"], ["K", "♥"]]
    assert "Three of a kind" in poker_util.determine_hand(hand)


def test_determine_hand_two_pair() -> None:
    hand: list[Any] = [[2, "♦"], [10, "♠"], [10, "♥"], ["K", "♦"], ["K", "♥"]]
    assert "Two pair" in poker_util.determine_hand(hand)


def test_determine_hand_pair() -> None:
    hand: list[Any] = [[2, "♦"], [4, "♠"], [6, "♥"], ["K", "♦"], ["K", "♥"]]
    assert "Pair" in poker_util.determine_hand(hand)


def test_determine_hand_high_card() -> None:
    hand: list[Any] = [[2, "♦"], [4, "♥"], [6, "♥"], [8, "♥"], ["K", "♥"]]
    assert "High card" in poker_util.determine_hand(hand)


def test_hand_score_straight_flush_beats_four_of_a_kind() -> None:
    straight_flush: list[Any] = [[2, "♥"], [3, "♥"], [4, "♥"], [5, "♥"], [6, "♥"]]
    four_kind: list[Any] = [[10, "♦"], [10, "♠"], [10, "♥"], [10, "♣"], ["K", "♥"]]
    assert poker_util.hand_score(straight_flush) > poker_util.hand_score(four_kind)


def test_hand_score_higher_pair_beats_lower_pair() -> None:
    high_pair: list[Any] = [["A", "♦"], ["A", "♠"], [2, "♥"], [3, "♦"], [4, "♥"]]
    low_pair: list[Any] = [[2, "♦"], [2, "♠"], [3, "♥"], [4, "♦"], [5, "♥"]]
    assert poker_util.hand_score(high_pair) > poker_util.hand_score(low_pair)


def test_hand_score_same_hand_different_kickers() -> None:
    high_kicker: list[Any] = [["K", "♦"], ["K", "♠"], ["A", "♥"], [2, "♦"], [3, "♥"]]
    low_kicker: list[Any] = [["K", "♦"], ["K", "♠"], [2, "♥"], [3, "♦"], [4, "♥"]]
    assert poker_util.hand_score(high_kicker) > poker_util.hand_score(low_kicker)


def test_compute_dup_values_pair() -> None:
    hand: list[Any] = [[2, "♦"], [2, "♠"], [5, "♥"], [9, "♦"], ["K", "♥"]]
    result = poker_util.compute_dup_values(hand)
    assert isinstance(result, str)
    assert "Pair" in result


def test_compute_dup_values_none() -> None:
    hand: list[Any] = [[2, "♦"], [5, "♠"], [9, "♥"], ["J", "♦"], ["A", "♥"]]
    assert poker_util.compute_dup_values(hand) is False


def test_determine_high_card() -> None:
    hand: list[Any] = [[2, "♦"], [5, "♠"], [9, "♥"], ["J", "♦"], ["A", "♥"]]
    assert "High card Ace" in poker_util.determine_high_card(hand)
