#!/usr/bin/env python3
# coding: utf-8
#
#   File = poker_pif.py
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

from pifs.base_pif import BasePIF
from utils import poker_util
from utils.reddit_helper import get_comment

instructionTemplate = """
Welcome to {}'s Single-Deck Poker PIF (managed by LatherBot).

I will deal three community cards and two additional cards to each qualified entry. 
In order to qualify, you must have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes (on a line by itself) the command:

`LatherBot in`

I will check your karma and deal your cards if you qualify.

This PIF will close in {} hour(s) or when I run out of cards.  
At that time, I will determine the winner and notify the PIF's creator.

LatherBot documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

Your three community cards are {} {} and {}

Good luck!
"""

entry_template = """
{} drew {} and {}

Your hand is {} {} {} {} {}

{}
"""

winner_template = """
The PIF is over!

u/{} has won with {}
"""

class Poker(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={}, karmaFail={}):
        logging.debug('Building single-deck poker PIF [%s]', postId)
     
        if len(pifOptions) < 1:
            deck = poker_util.new_deck()
            shared_cards = list()
            for i in range(3):
                card = poker_util.deal_card(deck)
                shared_cards.append(card)
            
            shared_cards = poker_util.order_cards(shared_cards)
        
            pifOptions['Deck'] = deck
            pifOptions['SharedCards'] = shared_cards
        
        BasePIF.__init__(self, postId, authorName, 'poker', minKarma, durationHours, endTime, pifOptions, pifEntries, karmaFail)
        
    def pif_instructions(self):
        logging.info('Printing instructions for PIF [%s]', self.postId)
        shared_cards = self.pifOptions['SharedCards']
        return instructionTemplate.format(self.authorName, 
                                          self.minKarma, 
                                          self.durationHours,
                                          poker_util.format_card(shared_cards[0]),
                                          poker_util.format_card(shared_cards[1]),
                                          poker_util.format_card(shared_cards[2]))

    def is_already_entered(self, user, comment):
        if user.name in self.pifEntries:
            logging.info('User [%s] appears to have already entered PIF [%s] with comment [%s]', user.name, self.postId, self.pifEntries[user.name]['CommentId'])
            entered_comment = get_comment(self.pifEntries[user.name]['CommentId'])
            if (entered_comment.submission.id != comment.submission.id):
                logging.warn("Entered comment submission [{}] doesn't match current comment submission [{}] for PIF [{}]".format(entered_comment.submission.id, comment.submission.id, self.postId))
                return False
            else:
                return True
        else:
            return False

    def handle_entry(self, comment, user, command_parts):
        logging.info('User [%s] entered to PIF [%s]', user, self.postId)
        
        deck = self.pifOptions['Deck']
        if len(deck) < 2:
            comment.reply("Sorry, I'm out of cards.  Time to wrap this thing up.")
            comment.save()
            self.finalize()
            return
        
        shared_cards = self.pifOptions['SharedCards']
        user_hand = list()
        user_cards = list()
        
        for card in shared_cards:
            user_hand.append(card)
        
        for i in range(2):
            card = poker_util.deal_card(deck)
            user_cards.append(card)
            user_hand.append(card)
            
        user_hand = poker_util.order_cards(user_hand)
        
        # Gotta put the deck back with fewer cards
        self.pifOptions['Deck'] = deck
        
        entry_details = dict()
        entry_details['CommentId'] = comment.id
        entry_details['UserCards'] = user_cards
        entry_details['UserHand'] = user_hand
        entry_details['HandScore'] = poker_util.hand_score(user_hand)
        
        self.pifEntries[user.name] = entry_details
        
        comment.reply(entry_template.format(
            user.name, 
            poker_util.format_card(user_cards[0]),
            poker_util.format_card(user_cards[1]),
            poker_util.format_card(user_hand[0]),
            poker_util.format_card(user_hand[1]),
            poker_util.format_card(user_hand[2]),
            poker_util.format_card(user_hand[3]),
            poker_util.format_card(user_hand[4]),
            poker_util.determine_hand(user_hand)))
        comment.save()
        
        if len(deck) < 2:
            self.finalize()
           
    def determine_winner(self):
        curr_max_score = 0
        tied_winners = list()
        
        for entrant in self.pifEntries.keys():
            if self.pifEntries[entrant]['HandScore'] > curr_max_score:
                if self.postId != get_comment(self.pifEntries[entrant]['CommentId']).submission.id:
                    continue
                tied_winners = list()
                tied_winners.append(entrant)
                curr_max_score = self.pifEntries[entrant]['HandScore']
            elif self.pifEntries[entrant]['HandScore'] == curr_max_score:
                tied_winners.append(entrant)
        
        if len(tied_winners) == 1:
            self.pifWinner = tied_winners[0]
            logging.info('User [%s] has won PIF [%s]', self.pifWinner, self.postId)
        else:
            logging.info("{} players tied for first", len(tied_winners))
            self.pifWinner = random.choice(tied_winners)
        logging.info('User [%s] has won PIF [%s]', self.pifWinner, self.postId)
        
    def generate_winner_comment(self):
        return winner_template.format(self.pifWinner, 
                                      poker_util.determine_hand(self.pifEntries[self.pifWinner]['UserHand']))