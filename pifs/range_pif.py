#!/usr/bin/env python3
# coding: utf-8
#
#   File = range_pif.py
#
#      Copyright 2020 Rob Curtis
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
import logging

from random import randrange
from pifs.base_pif import BasePIF
from utils.reddit_helper import get_comment

instructionTemplate = """
Welcome to {}'s Pick-a-Number PIF (managed by LatherBot).

When the PIF ends, I'll choose a random number between {} and {}. Whoever guesses closest to 
that number will be the winner. If two entrants are the same distance away, the one who got 
closest without going over will win (Price Is Right tie-breaker).  In order to qualify, you must 
have at least {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes (on a line by itself) the command:

`LatherBot IN <your guess>`
 
I will check your karma and record your guess if you qualify.  Example:

`LatherBot IN 23`

This PIF will close in {} hour(s). At that time, I will determine the winner and notify the PIF's creator.

You can get a karma check by commenting "LatherBot karma".  LatherBot documentation can be found 
in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

Good luck!
"""

winner_template = """
The PIF is over!

There winning number is {} and the winner is u/{} with a guess of {}.  Congratulations!
"""

class Range(BasePIF):
    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={}):
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'range', minKarma, durationHours, endTime, pifOptions, pifEntries)
    
    def pif_instructions(self):
        return instructionTemplate.format(self.authorName, 
                                          self.pifOptions['RangeMin'],
                                          self.pifOptions['RangeMax'],
                                          self.minKarma, 
                                          self.durationHours)

    def is_already_entered(self, user, comment):
        if user.name in self.pifEntries:
            logging.info('User [%s] appears to have already entered PIF [%s] with comment [%s]', user.name, self.postId, self.pifEntries[user.name]['CommentId'])
            entered_comment = get_comment(self.pifEntries[user.name]['CommentId'])
            if (entered_comment.submission.id != comment.submission.id):
                logging.warn("Entered comment submission [{}] doesn't match current comment submission [{}] for PIF [{}]".format(entered_comment.submission.id, comment.submission.id, self.postId))
                return False
            else:
                return True
        else:
            return False

    def handle_entry(self, comment, user, command_parts):
        guess = None
        try:
            guess = int(command_parts[2])
        except IndexError:
            comment.reply("It looks like you didn't pick a number.  Care to try again?")
            comment.save()
            return
        except ValueError:
            comment.reply("[{}] isn't a number between {} and {}.  Care to try again?"
                          .format(command_parts[2], self.pifOptions['RangeMin'], self.pifOptions['RangeMax']))
            comment.save()
            return
        
        conflict = self.userAlreadyGuessed(guess)
        if conflict is not None:
            comment.reply("I'm sorry, {} was already taken by {}.  Try again.".format(guess, conflict))
            comment.save()
        elif guess > self.pifOptions['RangeMax']:
            comment.reply("I'm sorry, {} is above the max allowable guess of {}.  Care to try again?"
                          .format(guess, self.pifOptions['RangeMax']))
            comment.save()
        elif guess < self.pifOptions['RangeMin']:
            comment.reply("I'm sorry, {} is below the min allowable guess of {}.  Care to try again?"
                          .format(guess, self.pifOptions['RangeMin']))
            comment.save()
        else:
            entryDetails = dict()
            entryDetails['CommentId'] = comment.id
            entryDetails['Guess'] = guess
            self.pifEntries[user.name] = entryDetails
            comment.reply("Entry confirmed.  {} guessed {}".format(user.name, guess))
            comment.save()
           
    def determine_winner(self):
        self.winningNumber = randrange(self.pifOptions['RangeMin'], self.pifOptions['RangeMax']+1)
        currWinner = 'TBD'
        currWinningGuess = self.pifOptions['RangeMax'] + 1
        currWinningDistance = currWinningGuess
        for entrant in self.pifEntries.keys():
            if self.postId != get_comment(self.pifEntries[entrant]['CommentId']).submission.id:
                    continue
            guess = self.pifEntries[entrant]['Guess']
            guessDistance = abs(guess - self.winningNumber)
            if guessDistance < currWinningDistance:
                currWinner = entrant
                currWinningGuess = guess
                currWinningDistance = guessDistance
            elif guessDistance == currWinningDistance and guess < currWinningGuess:
                currWinner = entrant
                currWinningGuess = guess
                currWinningDistance = guessDistance
        self.pifWinner = currWinner
        
        
    def generate_winner_comment(self):
        return winner_template.format(self.winningNumber, self.pifWinner, self.pifEntries[self.pifWinner]['Guess'])
    
    def userAlreadyGuessed(self, guess):
        for entry in self.pifEntries.keys():
            if guess == self.pifEntries[entry]['Guess']:
                return entry
        return None
        
