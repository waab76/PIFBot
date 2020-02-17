import random

from pifs.base_pif import BasePIF
from utils.karma_calculator import calculate_karma, formatted_karma
from utils.dynamo_helper import update_pif_entries
from utils.reddit_helper import already_replied

instructionTemplate = """
Welcome to {}'s Lottery PIF (managed by LatherBot).

The winner will be randomly selected from all qualified entries.  In order to qualify, 
you must have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes the line "LatherBot in".  
I will check your karma and mark you as entered if you qualify.

This PIF will close in {} hour(s).  At that time, I will select the winner at random and notify 
the PIF's creator.

You can always get a karma check by commenting "LatherBot karma".

Good luck!
"""

winner_template = """
The PIF is over!

There were {} qualified entries and the winner is u/{}.  Congratulations!
"""

class Lottery(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, 
                 pifOptions={}, pifEntries={}):
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'lottery', minKarma, durationHours, 
                         pifOptions, pifEntries)
        
    def pif_instructions(self):
        return instructionTemplate.format(self.authorName, 
                                          self.minKarma, 
                                          self.durationHours)

    def handle_entry(self, comment):
        if already_replied(comment):
            return

        user = comment.author
        if user.name == self.authorName:
            return
        
        parts = []
        for line in comment.body.lower().split('\n'):
            if line.startswith('latherbot '):
                parts = line.split()
                break
        if len(parts) < 2:
            return
        
        activity = calculate_karma(user)
        formattedKarma = formatted_karma(user, activity)

        if parts[1].startswith('in'):
            if user.name in self.pifEntries:
                comment.reply("You're already entered in this PIF")
            elif activity[0] >= self.minKarma:
                self.pifEntries[user.name] = comment.id
                update_pif_entries(self.postId, self.pifEntries)
                comment.reply("Entry confirmed")
            else:
                comment.reply("I'm afraid you don't have the karma for this PIF\n\n" + formattedKarma)
        elif parts[1].startswith('karma'):
            comment.reply(formattedKarma)
        else:
            comment.reply("My dude, I don't understand what you're trying to do")
            
    def determine_winner(self):
        winner = random.choice(list(self.pifEntries.keys()))
        return winner_template.format(len(self.pifEntries), winner)
        