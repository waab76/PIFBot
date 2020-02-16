from pifs.base_pif import BasePIF

instructionTemplate = """
Welcome to {}'s Lottery PIF (managed by LatherBot).

The winner will be randomly selected from all qualified entries.  In order to qualify, 
you must have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes the line "LatherBot in".  
I will check your karma and mark you as entered if you qualify.

This PIF will close in {} hour(s).  At that time, I will select the winner at random and notify 
the PIF's creator.

Good luck!
"""

class Lottery(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours):
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'lottery', minKarma, durationHours)
        
    def pifInstructions(self):
        return instructionTemplate.format(self.authorName, 
                                          self.pifOptions['MinKarma'], 
                                          self.pifOptions['DurationHours'])

    def pick_winner(self):
        print("Pick the winner for the Lottery PIF")