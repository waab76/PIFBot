#!/usr/bin/env python3
# coding: utf-8
#
#   File = lottery_pif.py
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
import random

from pifs.base_pif import BasePIF
from utils.reddit_helper import get_comment

instructionTemplate = """
Welcome to {}'s Newbie Lottery PIF (managed by LatherBot).

The winner will be randomly selected from all qualified entries.  In order to qualify, 
you must have less than {} karma on the sub in the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes (on a line by itself) the command:

`LatherBot in`

I will check your karma and mark you as entered if you qualify.

This PIF will close in {} hour(s).  At that time, I will select the winner at random and notify 
the PIF's creator.

LatherBot documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

If you see something, say something: [Report PIF Abuse](https://docs.google.com/forms/d/e/1FAIpQLScLVbYclUvKMbhrrz0WhfOKPQyr56_jH-4q8oOJf_emgAew7w/viewform?usp=sf_link)

Good luck!
"""

winner_template = """
The PIF is over!

There were {} qualified entries and the winner is u/{}.  Congratulations!
"""

class NoobLottery(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={}, karmaFail={}):
        logging.debug('Building noob lottery PIF [%s]', postId)
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'noob lottery', minKarma, durationHours, endTime, pifOptions, pifEntries, karmaFail)
        
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
        logging.info('User [%s] entered to PIF [%s]', user, self.postId)
        self.pifEntries[user.name] = comment.id
        comment.reply("Entry confirmed for {}".format(user.name))
        comment.save()
           
    def determine_winner(self):
        self.pifWinner = random.choice(list(self.pifEntries.keys()))
        while self.postId != get_comment(self.pifEntries[self.pifWinner]).submission.id:
            self.pifWinner = random.choice(list(self.pifEntries.keys()))

        logging.info('User [%s] has won PIF [%s]', self.pifWinner, self.postId)
        
    def generate_winner_comment(self):
        return winner_template.format(len(self.pifEntries), self.pifWinner)