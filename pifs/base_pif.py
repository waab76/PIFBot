import time

from utils.dynamo_helper import pif_exists, store_pif
from utils.reddit_helper import get_submission

class BasePIF:
    def __init__(self, postId, authorName, pifType, minKarma, durationHours):
        self.postId = postId
        self.authorName = authorName
        self.pifOptions = {
            'PifType': pifType,
            'MinKarma': int(minKarma),
            'DurationHours': int(durationHours)
        }
        self.entries = []
        self.expireTime = int(time.time() + 3600 * int(durationHours))

    def initialize(self):
        if pif_exists(self.postId):
            print('PIF already initialized, no-op')
        else:
            print('PIF not found, storing')
            store_pif(self.postId, self.authorName, self.pifOptions, self.expireTime)
            comment = get_submission(self.postId).reply(self.pifInstructions())
            comment.mod.distinguish('yes', True)
            
    def finalize(self):
        # Pick the winner
        winner = self.pick_winner()
        
        # Get the original PIF post
        submission = get_submission(self.postId)
        
        # Lock the submission
        submission.mod.lock()
        
        # Update the flair to 'PIF - Closed'
        submission.mod.flair(text='PIF - Closed', css_class='orange')
    
    def pifInstructions(self):
        return "LatherBot is on the job!"
    
    def pick_winner(self):
        print("Implement in subclass")