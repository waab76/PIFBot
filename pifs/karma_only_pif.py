'''
Created on May 5, 2020

@author: rcurtis
'''

import logging

from pifs.base_pif import BasePIF
from utils.karma_calculator import calculate_karma, formatted_karma
from utils.reddit_helper import get_submission

instructionTemplate = """
Welcome to {}'s PIF (with karma checks by LatherBot).

In order to qualify, you must have at least {} karma on the sub in the last 90 days. 

I will do a karma check on all top-level comments to determine whether or not the user meets the minimum karma.

This PIF will close in {} hour(s).  At that time, I will lock this post and the PIF's creator will select the winner.

LatherBot documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

Good luck!
"""

class KarmaOnly(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={}):
        logging.debug('Building karma-only PIF [%s]', postId)
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'karma', minKarma, durationHours, endTime, pifOptions, pifEntries)
        
    def pif_instructions(self):
        logging.info('Printing instructions for PIF [%s]', self.postId)
        return instructionTemplate.format(self.authorName, 
                                          self.minKarma, 
                                          self.durationHours)

    def is_already_entered(self, user, comment):
        return False

    def handle_comment(self, comment):
        user = comment.author
        karma = calculate_karma(user)
        formattedKarma = formatted_karma(user, karma)
        if comment.parent_id.startswith("t3_"):
            if user.name == self.authorName:
                comment.save()
                pass
            elif karma[0] >= self.minKarma:
                logging.debug('User [%s] meets karma requirement for PIF [%s]', user.name, self.postId)
                comment.reply("Congratulations, you have the karma for this PIF\n\n" + formattedKarma)
                comment.save()
            else:
                logging.info('User [%s] does not meet karma requirement for PIF [%s]', user.name, self.postId)
                comment.reply("I'm afraid you don't have the karma for this PIF\n\n" + formattedKarma)
                comment.save()
        
    
    def finalize(self):
        logging.info('Finalizing PIF [%s]', self.postId)
        # Get the original PIF post
        submission = get_submission(self.postId)
        
        comment = submission.reply("The PIF is over!")
        submission.mod.flair(text='PIF - Winner', css_class='orange')
        comment.mod.distinguish('yes', True)
        
        logging.info('Closing and locking PIF [%s]', self.postId)
        submission.mod.lock()
        self.pifState = 'closed'
    
