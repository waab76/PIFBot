'''
Created on May 5, 2020

@author: rcurtis
'''
import logging
import random
import string

from pifs.base_pif import BasePIF
from utils.reddit_helper import get_comment
from docutils.nodes import row
from math import sqrt

instructionTemplate = """
Welcome to {}'s Battleship PIF (managed by LatherBot).

I have placed my battleship somewhere on a 26x26 board.  Anyone with enough karma can take a shot. 
At the end of the PIF, I will reveal the location of my battleship and whoever was the first person 
to score a hit will be declared the winner.  If  nobody hits my battleship, then whoever came 
closest to hitting will be the be the winner.  

In order to qualify, you must have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes (on a line by itself) the command:

`LatherBot in <target coordinates>` where the target coordinates are a letter (A-Z) for the column 
then a blank space then a number (1-26) for the row.  Please format your entry correctly like so:

`LatherBot in A 3`

or

`LatherBot in C 1`

I will check your karma and record your entry if you qualify.

This PIF will close in {} hour(s).  At that time, I will reveal the location of my battleship and 
notify the PIF's creator.

You can get a karma check by commenting "LatherBot karma".  LatherBot documentation can be found 
in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

Good luck!
"""

winner_template = """
{} The PIF is over!

There were {} shots fired and the winner is u/{}.  Congratulations!

Here's the game board:


```
{}

Legend
.    Ocean
B    Battleship
*    Miss
X    Hit
```
"""

nautical_ranks = ["Seaman",
                  "Petty Officer",
                  "Chief Warrant Officer",
                  "Cadet",
                  "Quarter-master",
                  "Chief Engineer",
                  "Ensign",
                  "Midshipman",
                  "Sublieutenant",
                  "Lieutenant",
                  "Lt. Commander",
                  "Commander",
                  "Captain",
                  "Commodore",
                  "Rear Admiral",
                  "Vice Admiral",
                  "Admiral"]

nautical_jargon = ["Aye aye, sir!",
                   "Aye aye, Keptin!",
                   "Avast, ye scurvy dogs!",
                   "Damn the torpedoes, Full speed ahead!",
                   "I have not yet begun to fight!",
                   "I wish to have no connection with any ship that does not sail fast for I intend to go in harm's way.",
                   "Don't give up the ship!",
                   "We have met the enemy and they are ours…",
                   "You may fire when you are ready Gridley.",
                   "A good Navy is not a provocation to war. It is the surest guaranty of peace.",
                   "Praise the Lord and pass the ammunition!",
                   "Crazy Ivan! All stop!",
                   "Open the outer doors, firing point procedures. Now if that bastard so much as twitches, I'm going to blow him straight to Mars.",
                   "Re-verify our range to target... one ping only.",
                   "My Morse is so rusty, I could be sending him dimensions on Playmate of the Month."]

class Battleship(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={}):
        logging.debug('Building battleship PIF [%s]', postId)
        
        # If the options aren't present, let's build our board and place our battleship
        if not pifOptions:
            pifOptions = {}
            
            # Build a blank board
            board = [["." for i in range(26)] for j in range(26)]
            
            # North-South vs East-West
            north_south = random.randint(0,1)
            
            # Pick the start point
            start_row = random.randint(0,25)
            start_col = random.randint(0,25)
            
            # Place the battleship on the board
            if north_south:
                if start_row > 23: 
                    start_row = 23
                board[start_row][start_col] = 'B'
                board[start_row + 1][start_col] = 'B'
                board[start_row + 2][start_col] = 'B'
            else:
                if start_col > 23:
                    start_col = 23
                board[start_row][start_col] = 'B'
                board[start_row][start_col + 1] = 'B'
                board[start_row][start_col + 2] = 'B'
            
            pifOptions['Board'] = board
            pifOptions['NorthSouth'] = north_south
            pifOptions['StartRow'] = start_row
            pifOptions['StartCol'] = start_col
            
        BasePIF.__init__(self, postId, authorName, 'battleship', minKarma, durationHours, endTime, pifOptions, pifEntries)
        
    def pif_instructions(self):
        logging.info('Printing instructions for PIF [%s]', self.postId)
        return instructionTemplate.format(self.authorName, 
                                          self.minKarma, 
                                          self.durationHours)

    def is_already_entered(self, user, comment):
        if user.name in self.pifEntries:
            logging.info('User [%s] appears to have already entered PIF [%s] with comment [%s]', user.name, self.postId, self.pifEntries[user.name])
            entered_comment = get_comment(self.pifEntries[user.name])
            if (entered_comment.submission.id != comment.submission.id):
                logging.warn("Entered comment submission [{}] doesn't match current comment submission [{}] for PIF [{}]".format(entered_comment.submission.id, comment.submission.id, self.postId))
                return False
            else:
                return True
        else:
            return False

    def handle_entry(self, comment, user, command_parts):
        guess_col = None
        guess_col_num = None
        guess_row = None
        
        try:
            if len(command_parts[2]) > 1:
                guess_col = command_parts[2][0].upper()
                if command_parts[2][1] == '-':
                    guess_row = int(command_parts[2][2:])
                else:
                    guess_row = int(command_parts[2][1:])
            else:
                guess_col = command_parts[2].upper()[0]
                guess_row = int(command_parts[3])
                
            guess_col_num = string.ascii_uppercase.index(guess_col)
            if guess_row > 26:
                raise IndexError()
        except (ValueError, IndexError):
            comment.reply("It looks like you were trying to enter the PIF but something was wrong with the command you entered.  Please re-read the instructions and try again on a brand new comment (because the bot only processes each comment once and this one has already been processed)")
            comment.save()
            return
        
        guess_str = '{}-{}'.format(guess_col, guess_row)
        
        conflict = self.userAlreadyGuessed(guess_col, guess_row)
        if conflict is not None:
            comment.reply("I'm sorry, {} was already blown up by {}.  Try again in a brand new comment.".format(guess_str, conflict))
            comment.save()
            return
        
        logging.info('User [%s] entered to PIF [%s]', user, self.postId)
        entry_details = dict()
        entry_details['CommentId'] = comment.id
        entry_details['GuessTime'] = int(comment.created_utc)
        entry_details['GuessCol'] = guess_col
        entry_details['GuessRow'] = guess_row
        
        
        if self.pifOptions['Board'][guess_row - 1][guess_col_num] == '.':
            self.pifOptions['Board'][guess_row - 1][guess_col_num] = '*'
        elif self.pifOptions['Board'][guess_row - 1][guess_col_num] == 'B':
            self.pifOptions['Board'][guess_row - 1][guess_col_num] = 'X'
            if self.pifWinner == 'TBD':
                self.pifWinner = user.name

        self.pifEntries[user.name] = entry_details        
        comment.reply("{}\n\n{} {} has fired on location {}".format(random.choice(nautical_jargon), random.choice(nautical_ranks), user.name, guess_str))
        comment.save()
           
    def determine_winner(self):
        if self.pifWinner == 'TBD':
            win_dist = 999
            win_timestamp = 0
            for entrant in self.pifEntries.keys():
                entry_dist = self.calc_distance(string.ascii_uppercase.index(self.pifEntries[entrant]['GuessCol']), self.pifEntries[entrant]['GuessRow'])
                if entry_dist < win_dist or \
                (entry_dist == win_dist and self.pifEntries[entrant]['GuessTime'] < win_timestamp):
                    self.pifWinner = entrant
                    win_dist = entry_dist
                    win_timestamp = self.pifEntries[entrant]['GuessTime']
        
        logging.info('User [%s] has won PIF [%s]', self.pifWinner, self.postId)
        
    def generate_winner_comment(self):
        return winner_template.format(random.choice(nautical_jargon), len(self.pifEntries), self.pifWinner, self.print_board())
    
    def userAlreadyGuessed(self, guess_col, guess_row):
        for entry in self.pifEntries.keys():
            if guess_col == self.pifEntries[entry]['GuessCol'] and guess_row == self.pifEntries[entry]['GuessRow']:
                return entry
        return None

    def calc_distance(self, guess_col, guess_row):
        min_distance = 50
        for i in range(3):
            shot_dist = 51
            if self.pifOptions['NorthSouth']:
                shot_dist = sqrt((guess_col - self.pifOptions['StartCol'])**2 + (guess_row - 1 - (self.pifOptions['StartRow'] + i))**2)
            else:
                shot_dist = sqrt((guess_col - (self.pifOptions['StartCol'] + i))**2 + (guess_row - 1 + self.pifOptions['StartRow'])**2)
            
            if shot_dist < min_distance:
                min_distance = shot_dist
        
        return min_distance
        
    def print_board(self):
        header_row_str = '   '
        for let in string.ascii_uppercase:
            header_row_str = header_row_str + let + ' '
        board_str = header_row_str + '\n'    
        for row in range(26):
            row_str = ''
            if row < 9:
                row_str = ' ' + str(row + 1) + ' '
            else:
                row_str = str(row + 1) + ' '
            for col in range(26):
                row_str += self.pifOptions['Board'][row][col]
                row_str += ' '
            board_str = board_str + row_str + '\n' 
        return board_str