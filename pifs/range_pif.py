from pifs.base_pif import BasePIF

instructionTemplate = """
Welcome to {}'s Pick-a-Number PIF (managed by LatherBot).

I will deal three community cards and two additional cards to each qualified entry. 
In order to qualify, you must have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes the line "LatherBot in".  
I will check your karma and deal your cards if you qualify.

This PIF will close in {} hour(s) or when I run out of cards (max 24 entries).  
At that time, I will determine the winner and notify the PIF's creator.

Your three community cards are {} {} and {}

Good luck!
"""

class Range(BasePIF):
    def __init__(self, submission, options):
        # Handle the options
        BasePIF.__init__(self, submission, 'range', 0, 1)
        
    def initialize(self):
        print("PIF type not implemented")