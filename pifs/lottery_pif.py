import random

from pifs.base_pif import BasePIF

instructionTemplate = """
Welcome to {}'s Lottery PIF (managed by LatherBot).

The winner will be randomly selected from all qualified entries.  In order to qualify, 
you must have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes the line "LatherBot in".  
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

    def __init__(self, postId, authorName, minKarma, endTime, pifOptions={}, pifEntries={}):
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'lottery', minKarma, endTime, pifOptions, pifEntries)
        
    def pif_instructions(self):
        return instructionTemplate.format(self.authorName, 
                                          self.minKarma, 
                                          self.durationHours)

    def handle_entry(self, comment, user, command_parts):
        self.pifEntries[user.name] = comment.id
        comment.reply("Entry confirmed")
           
    def determine_winner(self):
        self.pifWinner = random.choice(list(self.pifEntries.keys()))
        
    def generate_winner_comment(self):
        return winner_template.format(len(self.pifEntries), self.pifWinner)