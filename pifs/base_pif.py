import time

from utils.dynamo_helper import open_pif_exists, create_pif_entry
from utils.reddit_helper import get_submission

class BasePIF:
    def __init__(self, postId, authorName, pifType, minKarma, durationHours, 
                 pifOptions={}, pifEntries={}):
        self.postId = postId
        self.authorName = authorName
        self.pifType = pifType
        self.minKarma = int(minKarma)
        self.durationHours = int(durationHours)
        self.pifOptions = pifOptions
        self.pifEntries = pifEntries
        self.expireTime = int(time.time() + 3600 * int(durationHours))

    def initialize(self):
        if open_pif_exists(self.postId):
            print('PIF already initialized, no-op')
        else:
            print('PIF not found, storing in DDB')
            create_pif_entry(self)
            comment = get_submission(self.postId).reply(self.pif_instructions())
            comment.mod.distinguish('yes', True)
            
    def finalize(self):
        # Get the original PIF post
        submission = get_submission(self.postId)
        
        comment = None
        if len(self.pifEntries) < 1:
            comment = submission.reply("There were no qualified entries. The PIF is a bust.")
        else:
            comment = submission.reply(self.determine_winner())
        comment.mod.distinguish('yes', True)
        
        submission.mod.lock()
        submission.mod.flair(text='PIF - Closed', css_class='orange')
    
    def pif_instructions(self):
        return "LatherBot is on the job!"
    
    def handle_entry(self, comment):
        print("Implement in subclass")
    
    def determine_winner(self):
        print("Implement in subclass")