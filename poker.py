#!/usr/local/bin/python3
# coding: utf-8
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
from utils import poker_util

def test_hands():
    hands = list()
    royal_flush = [[10,'♥'],['J','♥'],['Q','♥'],['K','♥'],['A','♥']]
    hands.append(royal_flush)
    straight_flush_to_the_five = [[2,'♥'],[3,'♥'],[4,'♥'],[5,'♥'],['A','♥']]
    hands.append(straight_flush_to_the_five)
    straight_flush_to_the_six = [[2,'♥'],[3,'♥'],[4,'♥'],[5,'♥'],[6,'♥']]
    hands.append(straight_flush_to_the_six)
    four_of_a_kind = [[10,'♦'],[10,'♠'],[10,'♥'],[10,'♣'],['K','♥']]
    hands.append(four_of_a_kind)
    full_boat = [[10,'♦'],[10,'♠'],[10,'♥'],['K','♦'],['K','♥']]
    hands.append(full_boat)
    flush = [[2,'♥'],['J','♥'],['Q','♥'],['K','♥'],['A','♥']]
    hands.append(flush)
    straight = [[10,'♦'],['J','♥'],['Q','♥'],['K','♥'],['A','♥']]
    hands.append(straight)
    five_high_straight = [[2,'♦'],[3,'♥'],[4,'♥'],[5,'♥'],['A','♥']]
    hands.append(five_high_straight)
    six_high_straight = [[2,'♦'],[3,'♥'],[4,'♥'],[5,'♥'],[6,'♥']]
    hands.append(six_high_straight)
    trips = [[10,'♦'],[10,'♠'],[10,'♥'],['Q','♦'],['K','♥']]
    hands.append(trips)
    two_pair = [[2,'♦'],[10,'♠'],[10,'♥'],['K','♦'],['K','♥']]
    hands.append(two_pair)
    pair = [[2,'♦'],[4,'♠'],[6,'♥'],['K','♦'],['K','♥']]
    hands.append(pair)
    high_card = [[2,'♦'],[4,'♥'],[6,'♥'],[8,'♥'],['K','♥']]
    hands.append(high_card)
    low_ace_straight = [[2,'♦'],[3,'♥'],[4,'♥'],[5,'♥'],['A','♥']]
    hands.append(low_ace_straight)
    
    for hand in hands:
        print("{} - {} - {}".format(hand, 
                                    poker_util.determine_hand(hand),
                                    poker_util.hand_score(hand)))


def test_poker():
    deck = poker_util.new_deck()
    tied_winners = list()
    curr_max_score = 0

    shared_cards = list()
    for i in range(3):
        shared_cards.append(poker_util.deal_card(deck))
    
        print('--------------------')
        print("Shared cards: {}".format(poker_util.order_cards(shared_cards)))

    while len(deck) > 2:
        hand = list()
        for card in shared_cards:
            hand.append(card)
        for i in range(2):
            hand.append(poker_util.deal_card(deck))
        ordered = poker_util.order_cards(hand)
        print("{} - {} - {}".format(ordered, 
                                    poker_util.determine_hand(hand),
                                    poker_util.hand_score(hand)))
        if poker_util.hand_score(ordered) > curr_max_score:
            tied_winners = list()
            tied_winners.append(ordered)
            curr_max_score = poker_util.hand_score(ordered)
        elif poker_util.hand_score(ordered) == curr_max_score:
            tied_winners.append(ordered)
    
    print('--------------------')
    
    if len(tied_winners) == 1:
        print("{} - {} - {}".format(tied_winners[0], 
                                    poker_util.determine_hand(tied_winners[0]),
                                    poker_util.hand_score(tied_winners[0])))
    else:
        print("{} hands tied for win: {} - {} - {}".format(len(tied_winners), 
                                                           tied_winners[0], 
                                                           poker_util.determine_hand(tied_winners[0]),
                                                           poker_util.hand_score(tied_winners[0])))
        
if __name__ == '__main__':
    test_hands()