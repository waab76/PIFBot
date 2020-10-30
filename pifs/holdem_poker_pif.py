#!/usr/bin/env python3
# coding: utf-8
#
#   File = holdem_poker_pif.py
#
#      Copyright 2020 relided
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
import itertools
import json
import logging
import random

from pifs.base_pif import BasePIF
from utils import poker_util
from utils.reddit_helper import get_comment

instructionTemplate = """
Welcome to {}'s Psuedo Texas Hold'em Poker PIF (managed by LatherBot).

In order to qualify, you must have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes (on a line by itself) the command:

`LatherBot in`

I will check your karma and deal your cards if you qualify.

This PIF will close in {} hour(s) or when I run out of unique hands (~1000).  
At that time, I will determine the winner and notify the PIF's creator.

LatherBot documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

The flop cards will be drawn now while the turn and river cards will be revealed at the end of the PIF.

You will be dealt a unique combination of two hole cards. IE while two players may be dealt the Queen of Hearts, 
only one player will ever be dealt the Queen of Hearts + the King of Hearts.

Per Texas Hold'em rules the player who makes the best five card poker hand out of their hole cards, the flop, turn and river cards will win.
In the event of a tie a winner will be selected randomly from the tied players. 

Your three flop cards are {} {} and {}


Good luck!
"""

entry_template = """
{} was dealt {} and {} as their hole cards

Good luck!
"""

winner_template = """
The PIF is over!

The flop cards were {}

The turn card was {}

The river card was {}

u/{} has won with {} ({})

{}
"""


class HoldemPoker(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={},
                 karmaFail={}):
        logging.debug('Building holdem poker PIF [%s]', postId)

        if len(pifOptions) < 1:
            deck = poker_util.new_deck()
            flop_cards = list()
            for i in range(3):
                card = poker_util.deal_card(deck)
                flop_cards.append(card)

            flop_cards = poker_util.order_cards(flop_cards)

            river_card = poker_util.deal_card(deck)
            turn_card = poker_util.deal_card(deck)
            # remove 3 cards (ie never dealt) so these dont appear as hold cards
            # and so users cant infer river and flop cards from looking at all dealt hands
            for i in range(3):
                poker_util.deal_card(deck)

            pifOptions['FlopCards'] = poker_util.order_cards(flop_cards)
            pifOptions['RiverCard'] = river_card
            pifOptions['TurnCard'] = turn_card
            pifOptions['ExtraInfo'] = ''

            remaining_cards = list()
            while True:
                try:
                    remaining_cards.append(poker_util.deal_card(deck))
                except IndexError:
                    break

            # make a set of possible two card combinations for dealing
            # note that two users can be dealt the same card, but not the exact same combination of cards
            # make into a list to prevent issues with serialising / storage of hands
            pifOptions['hands'] = list(itertools.combinations(remaining_cards, 2))
            random.shuffle(pifOptions['hands'])
            # convert to json to avoid issues with persistence to dynamodb
            pifOptions['hands'] = json.dumps(pifOptions['hands'])

        BasePIF.__init__(self, postId, authorName, 'holdem-poker', minKarma, durationHours, endTime, pifOptions, pifEntries,
                         karmaFail)

    def pif_instructions(self):
        logging.info('Printing instructions for PIF [%s]', self.postId)
        flop_cards = self.pifOptions['FlopCards']
        return instructionTemplate.format(self.authorName,
                                          self.minKarma,
                                          self.durationHours,
                                          poker_util.format_card(flop_cards[0]),
                                          poker_util.format_card(flop_cards[1]),
                                          poker_util.format_card(flop_cards[2]))

    def is_already_entered(self, user, comment):
        if user.name in self.pifEntries:
            logging.info('User [%s] appears to have already entered PIF [%s] with comment [%s]', user.name, self.postId,
                         self.pifEntries[user.name]['CommentId'])
            entered_comment = get_comment(self.pifEntries[user.name]['CommentId'])
            if (entered_comment.submission.id != comment.submission.id):
                logging.warn(
                    "Entered comment submission [{}] doesn't match current comment submission [{}] for PIF [{}]".format(
                        entered_comment.submission.id, comment.submission.id, self.postId))
                return False
            else:
                return True
        else:
            return False

    def handle_entry(self, comment, user, command_parts):
        logging.info('User [%s] entered to PIF [%s]', user, self.postId)

        hands = json.loads(self.pifOptions['hands'])

        if not self.pifOptions['hands']:
            comment.reply("Sorry, I'm out of cards.  Time to wrap this thing up.")
            comment.save()
            self.finalize()
            return

        user_hand = hands.pop()
        user_hand = poker_util.order_cards(user_hand)

        entry_details = dict()
        entry_details['CommentId'] = comment.id
        entry_details['UserHoleCards'] = user_hand

        self.pifEntries[user.name] = entry_details

        comment.reply(entry_template.format(
            user.name,
            poker_util.format_card(user_hand[0]),
            poker_util.format_card(user_hand[1]),
        ))
        comment.save()

        if not hands:
            self.finalize()
        else:
            # persist hands minus the one dealt
            self.pifOptions['hands'] = json.dumps(hands)

    def determine_winner(self):
        curr_max_score = 0
        tied_winners = list()

        for entrant in self.pifEntries.keys():

            # determine the entrants best possible hand by combining their hole cards with
            # the flop, turn and river cards
            entrant_best_score = 0
            entrant_card_pool = self.pifEntries[entrant]['UserHoleCards']
            entrant_card_pool.extend(self.pifOptions['FlopCards'])
            entrant_card_pool.append(self.pifOptions['TurnCard'])
            entrant_card_pool.append(self.pifOptions['RiverCard'])

            for possible_hand in itertools.combinations(entrant_card_pool, 5):
                hand_score = poker_util.hand_score(possible_hand)
                if hand_score > entrant_best_score:
                    entrant_best_score = hand_score
                    self.pifEntries[entrant]['BestHand'] = poker_util.order_cards(list(possible_hand))
                    self.pifEntries[entrant]['HandScore'] = hand_score

            if entrant_best_score > curr_max_score:
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
            self.pifWinner = random.choice(tied_winners)
            logging.info("{} players tied for first", len(tied_winners))
            self.pifOptions['ExtraInfo'] = "{} players tied for first, a winner was selected randomly".format(len(tied_winners))
        logging.info('User [%s] has won PIF [%s]', self.pifWinner, self.postId)

    def generate_winner_comment(self):
        return winner_template.format(
            ' '.join(
                [poker_util.format_card(x) for x in self.pifOptions['FlopCards']]
            ),
            poker_util.format_card(self.pifOptions['TurnCard']),
            poker_util.format_card(self.pifOptions['RiverCard']),
            self.pifWinner,
            ' '.join(
                [poker_util.format_card(x) for x in self.pifEntries[self.pifWinner]['BestHand']]
            ),
            poker_util.determine_hand(self.pifEntries[self.pifWinner]['BestHand']),
            self.pifOptions['ExtraInfo'],
        )

