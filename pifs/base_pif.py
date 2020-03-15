#!/usr/bin/env python3
# coding: utf-8
#
#   File = base_pif.py
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

from utils.karma_calculator import formatted_karma
from utils.reddit_helper import get_submission

class BasePIF:
    def __init__(self, postId, authorName, pifType, minKarma, durationHours, endTime, 
                 pifOptions={}, pifEntries={}):
        logging.debug('Building PIF [%s]', postId)
        self.postId = postId
        self.authorName = authorName
        self.pifType = pifType
        self.minKarma = int(minKarma)
        self.durationHours = int(durationHours)
        self.pifOptions = pifOptions
        self.pifEntries = pifEntries
        self.expireTime = int(endTime)
        self.pifState = 'open'
        self.pifWinner = 'TBD'

    def initialize(self):
        logging.debug('Adding PIF instructions')
        submission = get_submission(self.postId)
        submission.mod.flair(text='PIF - Open', css_class='orange')
        comment = submission.reply(self.pif_instructions())
        comment.mod.distinguish('yes', True)
            
    def handle_entry_request(self, comment, karma, command_parts):
        user = comment.author
        formattedKarma = formatted_karma(user, karma)

        if user.name in self.pifEntries:
            logging.info('User [%s] has already entered PIF [%s]', user.name, self.postId)
            comment.reply("You're already entered in this PIF")
            comment.save()
        elif user.name == self.authorName:
            logging.info('User [%s] has tried to enter their own PIF', user.name)
            comment.reply('Are you kidding me? This is your PIF.  If you want it that much, just keep it.')
            comment.save()
        elif karma[0] >= self.minKarma:
            logging.debug('User [%s] meets karma requirement for PIF [%s]', user.name, self.postId)
            self.handle_entry(comment, user, command_parts)
        else:
            logging.info('User [%s] does not meet karma requirement for PIF [%s]', user.name, self.postId)
            comment.reply("I'm afraid you don't have the karma for this PIF\n\n" + formattedKarma)
            comment.save()
    
    def finalize(self):
        logging.info('Finalizing PIF [%s]', self.postId)
        # Get the original PIF post
        submission = get_submission(self.postId)
        
        comment = None
        if len(self.pifEntries) < 1:
            logging.warning('PIF [%s] did not receive any entries', self.postId)
            comment = submission.reply("There were no qualified entries. The PIF is a bust.")
            submission.mod.flair(text='PIF - Closed', css_class='orange')
        else:
            self.determine_winner()
            comment = submission.reply(self.generate_winner_comment())
            submission.mod.flair(text='PIF - Winner', css_class='orange')

        logging.info('Closing and locking PIF [%s]', self.postId)
        comment.mod.distinguish('yes', True)
        submission.mod.lock()
        self.pifState = 'closed'
    
    def pif_instructions(self):
        return "LatherBot is on the job!"
    
    def handle_entry(self, comment, user, command_parts):
        print("Implement in subclass")
    
    def determine_winner(self):
        print("Implement in subclass")
        
    def generate_winner_comment(self):
        print("Implement in subclass")