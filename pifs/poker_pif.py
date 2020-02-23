import logging
import random

from pifs.base_pif import BasePIF
from utils import poker_util

instructionTemplate = """
Welcome to {}'s Poker PIF (managed by LatherBot).

I will deal three community cards and two additional cards to each qualified entry. 
In order to qualify, you must have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes the line "LatherBot in".  
I will check your karma and deal your cards if you qualify.

This PIF will close in {} hour(s) or when I run out of cards (max 24 entries).  
At that time, I will determine the winner and notify the PIF's creator.

You can get a karma check by commenting "LatherBot karma".  LatherBot documentation can be found 
in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

Your three community cards are {} {} and {}

Good luck!
"""

entry_template = """
Your drew {} and {}

Your hand is {} {} {} {} {}

{}
"""

winner_template = """
{} has won with {}
"""

class Poker(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={}):
        logging.debug('Building poker PIF [%s]', postId)
        
        deck = poker_util.new_deck()
        shared_cards = list()
        for i in range(3):
            shared_cards.append(poker_util.deal_card(deck))
            
        shared_cards = poker_util.order_cards(shared_cards)
        
        pifOptions['Deck'] = deck
        pifOptions['SharedCards'] = shared_cards
        
        BasePIF.__init__(self, postId, authorName, 'poker', minKarma, durationHours, endTime, pifOptions, pifEntries)
        
    def pif_instructions(self):
        logging.info('Printing instructions for PIF [%s]', self.postId)
        shared_cards = self.pifOptions['SharedCards']
        return instructionTemplate.format(self.authorName, 
                                          self.minKarma, 
                                          self.durationHours,
                                          poker_util.format_card(shared_cards[0]),
                                          poker_util.format_card(shared_cards[1]),
                                          poker_util.format_card(shared_cards[2]))

    def handle_entry(self, comment, user, command_parts):
        logging.info('User [%s] entered to PIF [%s]', user, self.postId)
        
        deck = self.pifOptions['Deck']
        shared_cards = self.pifOptions['SharedCards']
        user_hand = list()
        user_cards = list()
        
        for card in shared_cards:
            user_hand.append(card)
        
        for i in range(2):
            card = poker_util.deal_card(deck)
            user_cards.append(card)
            user_hand.append(card)
            
        user_cards = poker_util.order_cards(user_cards)
        user_hand = poker_util.order_cards(user_hand)
        
        self.pifOptions['Deck'] = deck
        
        entry_details = dict()
        entry_details['CommentId'] = comment.id
        entry_details['UserCards'] = user_cards
        entry_details['UserHand'] = user_hand
        entry_details['HandScore'] = poker_util.hand_score(user_hand)
        
        self.pifEntries[user.name] = entry_details
        
        comment.reply(entry_template.format(
            poker_util.format_card(user_cards[0]),
            poker_util.format_card(user_cards[1]),
            poker_util.format_card(user_hand[0]),
            poker_util.format_card(user_hand[1]),
            poker_util.format_card(user_hand[2]),
            poker_util.format_card(user_hand[3]),
            poker_util.format_card(user_hand[4]),
            poker_util.determine_hand(user_hand)))
        
        if len(deck) < 2:
            self.finalize()
           
    def determine_winner(self):
        curr_max_score = 0
        tied_winners = list()
        
        for entrant in self.pifEntries.keys():
            if self.pifEntries[entrant]['HandScore'] > curr_max_score:
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