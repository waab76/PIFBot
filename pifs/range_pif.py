from random import randrange
from pifs.base_pif import BasePIF

instructionTemplate = """
Welcome to {}'s Pick-a-Number PIF (managed by LatherBot).

When the PIF ends, I'll choose a random number between {} and {}. Whoever guesses closest to 
that number will be the winner. If two entrants are the same distance away, the one who got 
closest without going over will win (Price is Right rules).  In order to qualify, you must 
have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes the line "LatherBot IN <your guess>". 
I will check your karma and record your guess if you qualify.  Example:

*LatherBot IN 23*

This PIF will close in {} hour(s). At that time, I will determine the winner and notify the PIF's creator.

Good luck!
"""

winner_template = """
The PIF is over!

There winning number is {} and the winner is u/{} with a guess of {}.  Congratulations!
"""

class Range(BasePIF):
    def __init__(self, postId, authorName, minKarma, endTime, pifOptions={}, pifEntries={}):
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'range', minKarma, endTime, pifOptions, pifEntries)
    
    def pif_instructions(self):
        return instructionTemplate.format(self.authorName, 
                                          self.minKarma, 
                                          self.durationHours)

    def handle_entry(self, comment, user, command_parts):
        guess = int(command_parts[2])
        
        conflict = self.userAlreadyGuessed(guess)
        if conflict is not None:
            comment.reply("I'm sorry, {} was already taken by {}.  Try again.".format(guess, conflict))
        else:
            entryDetails = dict()
            entryDetails['CommentID'] = comment.id
            entryDetails['Guess'] = guess
            self.pifEntries[user.name] = entryDetails
            comment.reply("Entry confirmed.  Your guess is {}".format(guess))
           
    def determine_winner(self):
        winningNumber = randrange(self.pifOptions['RangeMin'], self.pifOptions['RangeMax']+1)
        
        
    def generate_winner_comment(self):
        return winner_template.format(len(self.pifEntries), self.pifWinner)
    
    def userAlreadyGuessed(self, guess):
        for entry in self.pifEntries.keys():
            if guess == self.pifEntries[entry]['Guess']:
                return entry
        return None
        
