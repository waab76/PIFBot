'''
Created on Jan 27, 2021

@author: rcurtis
'''

import logging
import random

from pifs.base_pif import BasePIF
from utils.reddit_helper import get_comment

instructionTemplate = """
Welcome to {}'s randomizer PIF (managed by LatherBot).

When the PIF is over, the list of qualified entries will be randomized and prizes will be awarded based 
on the randomized order.  In order to qualify, you must have at least {} karma on the sub in the 
last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes (on a line by itself) the command:

`LatherBot in`

I will check your karma and mark you as entered if you qualify. **Remember**, you only get one shot at 
entering, so if you're not sure you've got the karma, use the `LatherBot karma` command to do a check 
before entering.

This PIF will close in {} hour(s).  At that time, I will generate the randomized list and notify 
the PIF's creator.

LatherBot documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

If you see something, say something: [Report PIF Abuse](https://docs.google.com/forms/d/e/1FAIpQLScLVbYclUvKMbhrrz0WhfOKPQyr56_jH-4q8oOJf_emgAew7w/viewform?usp=sf_link)

Good luck!
"""

winner_template = """
The PIF is over!

There were {} qualified entries. The randomized list of qualified entries is:

{}
"""

class Randomizer(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={}, karmaFail={}):
        logging.debug('Building randomizer PIF [%s]', postId)
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'randomizer', minKarma, durationHours, endTime, pifOptions, pifEntries, karmaFail)
        
    def pif_instructions(self):
        logging.info('Printing instructions for PIF [%s]', self.postId)
        return instructionTemplate.format(self.authorName, 
                                          self.minKarma, 
                                          self.durationHours)

    def handle_entry(self, comment, user, command_parts):
        logging.info('User [%s] entered to PIF [%s]', user, self.postId)
        self.pifEntries[user.name] = comment.id
        comment.reply("Entry confirmed for {}".format(user.name))
        comment.save()
           
    def determine_winner(self):
        self.pifWinner = list(self.pifEntries.keys())
        
        logging.info('Before first shuffle: [%s]', ', '.join(self.pifWinner))
        random.shuffle(self.pifWinner)
        
        logging.info('After first shuffle: [%s]', ', '.join(self.pifWinner))
        random.shuffle(self.pifWinner)
        
        logging.info('After second shuffle: [%s]', ', '.join(self.pifWinner))
        random.shuffle(self.pifWinner)
        
        logging.info('After third shuffle: [%s] generated for PIF [%s]', ', '.join(self.pifWinner), self.postId)
        
    def generate_winner_comment(self):
        randomized_list = ''
        for entrant in self.pifWinner:
            randomized_list += '1) u/' + entrant + '\n'
        return winner_template.format(len(self.pifEntries), randomized_list)
