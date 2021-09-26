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

from config import blacklist
from utils.karma_calculator import calculate_karma, formatted_karma
from utils.personality import get_bad_command_response
from utils.reddit_helper import get_submission

class BasePIF:
    def __init__(self, postId, authorName, pifType, minKarma, durationHours, endTime, 
                 pifOptions={}, pifEntries={}, karmaFail={}):
        logging.debug('Building PIF [%s]', postId)
        self.postId = postId
        self.authorName = authorName
        self.pifType = pifType
        self.minKarma = int(minKarma)
        self.durationHours = int(durationHours)
        self.pifOptions = pifOptions
        self.pifEntries = pifEntries
        self.karmaFail = karmaFail
        self.expireTime = int(endTime)
        self.pifState = 'open'
        self.pifWinner = 'TBD'

    def initialize(self):
        logging.debug('Adding PIF instructions')
        submission = get_submission(self.postId)
        comment = submission.reply(self.pif_instructions())
        comment.mod.distinguish('yes', True)
        
    def handle_comment(self, comment):
        # Look for a LatherBot command
        for line in comment.body.lower().split('\n'):
            if line.strip().startswith('latherbot'):
                parts = line.split()
                if len(parts) < 2:
                    continue
                logging.info('Handling command [%s] for PIF [%s] comment [%s]', line, comment.submission.id, comment.id)
                user = comment.author
                karma = (1, 1, 1, 1, 1) if self.minKarma < 1 else calculate_karma(user)
                if not karma:
                    comment.reply("I cannot seem to calculate karma for user u/{}".format(user.name))
                    comment.save()
                    return False
                formattedKarma = formatted_karma(user, karma)
    
                if parts[1].startswith('in'):
                    if self.is_already_entered(user, comment):
                        logging.info('User [%s] is already entered in PIF [%s]', user.name, self.postId)
                        comment.reply("User {} is already entered in this PIF".format(user.name))
                        comment.save()
                    elif user.name in blacklist:
                        user.message("PIF Entry Denied", "Your attempt to enter PIF http://redd.it/{} has been denied.\n\n{}".format(self.postId, blacklist[user.name]))
                        comment.save()
                    elif user.name in self.karmaFail:
                        comment.reply('u/{} has already failed the karma check for this PIF'.format(user.name))
                        comment.save()
                    elif user.name == self.authorName:
                        logging.info('User [%s] has tried to enter their own PIF', user.name)
                        comment.reply('Are you kidding me? This is your PIF.  If you want it that much, just keep it.')
                        comment.save()
                    elif karma[0] >= self.minKarma:
                        logging.debug('User [%s] meets karma requirement for PIF [%s]', user.name, self.postId)
                        self.handle_entry(comment, user, parts)
                        return True
                    else:
                        logging.info('User [%s] does not meet karma requirement for PIF [%s]', user.name, self.postId)
                        karma_fail = dict()
                        karma_fail['CommentId'] = comment.id
                        karma_fail['Karma'] = karma[0]
                        self.karmaFail[user.name] = karma_fail
                        comment.reply("I'm afraid you don't have the karma for this PIF\n\n" + formattedKarma + 
                                      "\n\nThe PIF author can override the karma check by responding to this comment with the command `LatherBot override`")
                        comment.save()
                        return True
                elif parts[1].startswith('karma'):
                    logging.info('User [%s] requested karma check', user.name)
                    comment.reply(formattedKarma)
                    comment.downvote()
                    comment.save()
                elif parts[1].startswith('override'):
                    logging.info('User [%s] requested karma override', user.name)
                    self.karma_override(comment)
                    comment.save()
                    return True
                else:
                    logging.warning('Invalid command on comment [%s] for post [%s] by user [%s]', 
                            comment.id, comment.submission.id, comment.author.name)
                    comment.reply("That was not a valid `LatherBot` command.  Whatever you were trying to do, you'll need to try again in a brand new comment.\n\n{}".format(get_bad_command_response()))
                    comment.save()
                
                return False
    
    def finalize(self):
        logging.info('Finalizing PIF [%s]', self.postId)
        # Get the original PIF post
        submission = get_submission(self.postId)
        
        comment = None
        if len(self.pifEntries) < 1:
            logging.warning('PIF [%s] did not receive any entries', self.postId)
            comment = submission.reply("There were no qualified entries. The PIF is a bust.")
            submission.mod.flair(flair_template_id='ddc27296-0d64-11e8-a87d-0e644179e478')
        else:
            self.determine_winner()
            comment = submission.reply(self.generate_winner_comment())
            try:
                submission.mod.flair(flair_template_id='e05501c2-0d64-11e8-80c6-0e2446bb425c')
            except:
                try:
                    submission.mod.flair(flair_template_id='600e182a-fb07-11eb-949a-3234ae962371')
                except:
                    pass

        logging.info('Closing and locking PIF [%s]', self.postId)
        comment.mod.distinguish('yes', True)
        # submission.mod.lock()
        self.pifState = 'closed'
        
    def karma_override(self, comment):
        if comment.author.name == self.authorName:
            logging.info('Passed PIF author check')
            parent_comment = comment.parent()
            if parent_comment.author.name == 'LatherBot':
                logging.info('Passed "responding to LatherBot" check')
                grandparent_comment = parent_comment.parent()
                lucky_stiff = grandparent_comment.author
                if lucky_stiff.name in self.karmaFail.keys():
                    logging.info('[%s] did, indeed, fail the karma check' % lucky_stiff.name)
                    self.karmaFail.pop(lucky_stiff.name)
                    for line in grandparent_comment.body.lower().split('\n'):
                        if line.strip().startswith('latherbot'):
                            parts = line.split()
                            if len(parts) < 2:
                                continue
                            logging.info('Reprocessing command [%s] from user [%s]' % (' '.join(parts), lucky_stiff.name))
                            self.handle_entry(grandparent_comment, lucky_stiff, parts)
                            break
                else:
                    comment.reply('I am confused. u/%s did not fail the karma check' % lucky_stiff)
            else:
                comment.reply('I am not sure what you are trying to do.')
        else:
            logging.warn('Attempted karma override by %s, who is not the PIF author', comment.author.name)
            comment.reply('This is not your PIF and you cannot override the karma check.')
    
    def pif_instructions(self):
        return "LatherBot is on the job!"
    
    def is_already_entered(self, user, comment):
        print("Implement in subclass")
            
    def handle_entry(self, comment, user, command_parts):
        print("Implement in subclass")
    
    def determine_winner(self):
        print("Implement in subclass")
        
    def generate_winner_comment(self):
        print("Implement in subclass")