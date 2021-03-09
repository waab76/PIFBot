#!/usr/bin/env python3
# coding: utf-8
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
import logging
import random

suit_list = ['♠', '♥', '♣', '♦']
value_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']

def new_deck():
    logging.debug('Building new deck')
    deck = list()
    for suit in suit_list:
        for value in value_list:
            card = [value, suit]
            deck.append(card)
    return deck

def deal_card(deck):
    random.seed(None)
    card = random.choice(deck)
    deck.remove(card)
    logging.debug('Dealt {}'.format(format_card(card)))
    return card

def card_name(card):
    if card[0] == 'A':
        return 'Ace'
    elif card[0] == 'K':
        return 'King'
    elif card[0] == 'Q':
        return 'Queen'
    elif card[0] == 'J':
        return 'Jack'
    else:
        return str(card[0])

def card_point_value(card):
    return value_list.index(card[0]) + 1

def format_card(card):
    return '{}{}'.format(card[0], card[1])

def order_cards(hand):
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
def ordered_hand_values(ordered_hand):
    player_values = []
    for card in ordered_hand:
        player_values.append(str(card[0]))
    
    return ''.join(player_values)
        
def is_straight(hand):
    ordered_values = ordered_hand_values(hand)
    if ordered_values in '2345678910JQKA':
        return True
    elif ordered_values == '2345A':
        return True
    return False

def is_flush(hand):
    hand_suit_set = set()
    for card in hand:
        hand_suit_set.add(card[1])
    return len(hand_suit_set) == 1

def check_multiples(hand):
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


def compute_dup_values(hand):
    dupes_list = check_multiples(hand)
    
    if len(dupes_list) == 0:
        return False
    
    if len(dupes_list) == 1:
        if dupes_list[0][1] == 4:
            return 'Four of a kind {}s'.format(card_name(dupes_list[0]))
        if dupes_list[0][1] == 3:
            return 'Three of a kind {}s'.format(card_name(dupes_list[0]))
        if dupes_list[0][1] == 2:
            return 'Pair of {}s'.format(card_name(dupes_list[0]))
    
    if len(dupes_list) == 2:
        if dupes_list[0][1] == 3:
            return 'Full house {}s full of {}s'.format(card_name(dupes_list[0]), card_name(dupes_list[1]))
        elif dupes_list[1][1] == 3:
            return 'Full house {}s full of {}s'.format(card_name(dupes_list[1]), card_name(dupes_list[0]))
        else:
            return 'Two pair {}s and {}s'.format(card_name(dupes_list[0]), card_name(dupes_list[1]))

def determine_hand(hand):
    ordered_hand = order_cards(hand)
    dups_str = compute_dup_values(ordered_hand)
    if is_straight(ordered_hand) and is_flush(ordered_hand):
        high_card = ordered_hand[4]
        if card_name(ordered_hand[3]) == '5' and card_name(ordered_hand[4]) == 'Ace':
            high_card = ordered_hand[3]
        return 'Straight flush to the {}'.format(card_name(high_card))
    elif is_flush(hand):
        return 'Flush {} high'.format(card_name(ordered_hand[4]))
    elif is_straight(hand):
        high_card = ordered_hand[4]
        if card_name(ordered_hand[3]) == '5' and card_name(ordered_hand[4]) == 'Ace':
            high_card = ordered_hand[3]
        return 'Straight to the {}'.format(card_name(high_card))
    elif not dups_str:
        return determine_high_card(ordered_hand)
    else:
        return dups_str
        

def determine_high_card(hand):
    ordered_hand = order_cards(hand)
    return 'High card {}'.format(card_name(ordered_hand[4]))

def hand_score(hand):
    ordered_hand = order_cards(hand)
    hand_label = determine_hand(ordered_hand)
    multiples = check_multiples(ordered_hand)
    
    score = 0
    if hand_label.startswith('Straight flush'):
        score += 8000000
        high_card = ordered_hand[4]
        if card_name(ordered_hand[3]) == '5' and card_name(ordered_hand[4]) == 'Ace':
            high_card = ordered_hand[3]
        score += card_point_value(high_card)
    elif hand_label.startswith('Four'):
        score += 7000000
        score += 15 * card_point_value(multiples[0])
        if ordered_hand[4][0] == multiples[0][0]:
            score += card_point_value(ordered_hand[0])
        else:
            score += card_point_value(ordered_hand[4])
    elif hand_label.startswith('Full'):
        score += 6000000
        multiples = check_multiples(hand)
        if multiples[0][0] == 3:
            score += 15* card_point_value(multiples[0])
            score += card_point_value(multiples[1])
        else:
            score += card_point_value(multiples[0])
            score += 15* card_point_value(multiples[1])
    elif hand_label.startswith('Flush'):
        score += 5000000
        score += (15**4)*card_point_value(ordered_hand[4])
        score += (15**3)*card_point_value(ordered_hand[3])
        score += (15**2)*card_point_value(ordered_hand[2])
        score += 15*card_point_value(ordered_hand[1])
        score += card_point_value(ordered_hand[0])
    elif hand_label.startswith('Straight'):
        high_card = ordered_hand[4]
        if card_name(ordered_hand[3]) == '5' and card_name(ordered_hand[4]) == 'Ace':
            high_card = ordered_hand[3]
        score += 4000000
        score += card_point_value(high_card)
    elif hand_label.startswith('Three'):
        score += 3000000
        score += (15**2)*card_point_value(multiples[0])
        multiple = 1
        for kicker in ordered_hand:
            if kicker[0] != multiples[0][0]:
                score += multiple * card_point_value(kicker)
                multiple *= 15
    elif hand_label.startswith('Two'):
        score += 2000000
        if value_list.index(multiples[0][0]) > value_list.index(multiples[1][0]):
            score += 15*15*card_point_value(multiples[0])
            score += 15*card_point_value(multiples[1])
        else:
            score += 15*15*card_point_value(multiples[1])
            score += 15*card_point_value(multiples[0])
        for kicker in ordered_hand:
            if kicker[0] != multiples[0][0] and kicker[0] != multiples[1][0]:
                score += card_point_value(kicker)
    elif hand_label.startswith('Pair'):
        score += 1000000
        score += (15**3)*card_point_value(multiples[0])
        multiple = 1
        for kicker in ordered_hand:
            if kicker[0] != multiples[0][0]:
                score += multiple * card_point_value(kicker)
                multiple *= 15
    else:
        score += (15**4)*card_point_value(ordered_hand[4])
        score += (15**3)*card_point_value(ordered_hand[3])
        score += (15**2)*card_point_value(ordered_hand[2])
        score += 15*card_point_value(ordered_hand[1])
        score += card_point_value(ordered_hand[0])
    
    return score