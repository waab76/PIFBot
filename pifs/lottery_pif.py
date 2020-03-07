import logging
import random

from pifs.base_pif import BasePIF

instructionTemplate = """
Welcome to {}'s Lottery PIF (managed by LatherBot).

The winner will be randomly selected from all qualified entries.  In order to qualify, 
you must have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes (on a line by itself) the command:

`LatherBot in`

I will check your karma and mark you as entered if you qualify.

This PIF will close in {} hour(s).  At that time, I will select the winner at random and notify 
the PIF's creator.

You can get a karma check by commenting "LatherBot karma".  LatherBot documentation can be found 
in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

Good luck!
"""

winner_template = """
The PIF is over!

There were {} qualified entries and the winner is u/{}.  Congratulations!
"""

class Lottery(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={}):
        logging.debug('Building lottery PIF [%s]', postId)
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'lottery', minKarma, durationHours, endTime, pifOptions, pifEntries)
        
    def pif_instructions(self):
        logging.info('Printing instructions for PIF [%s]', self.postId)
        return instructionTemplate.format(self.authorName, 
                                          self.minKarma, 
                                          self.durationHours)

    def handle_entry(self, comment, user, command_parts):
        logging.info('User [%s] entered to PIF [%s]', user, self.postId)
        self.pifEntries[user.name] = comment.id
        comment.reply("Entry confirmed for {}".format(user.name))
           
    def determine_winner(self):
        self.pifWinner = random.choice(list(self.pifEntries.keys()))
        logging.info('User [%s] has won PIF [%s]', self.pifWinner, self.postId)
        
    def generate_winner_comment(self):
        return winner_template.format(len(self.pifEntries), self.pifWinner)