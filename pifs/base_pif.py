import time

from utils.karma_calculator import calculate_karma, formatted_karma
from utils.dynamo_helper import open_pif_exists, create_pif_entry
from utils.reddit_helper import already_replied, get_submission

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
            
    def handle_comment(self, comment):
        if already_replied(comment):
            return

        user = comment.author
        if user.name == self.authorName:
            return
        
        parts = []
        for line in comment.body.lower().split('\n'):
            if line.startswith('latherbot'):
                parts = line.split()
                if len(parts) < 2:
                    continue
                self.handle_command(comment, parts)
        
        
    def handle_command(self, comment, command_parts):
        user = comment.author
        activity = calculate_karma(user)
        formattedKarma = formatted_karma(user, activity)

        if command_parts[1].startswith('in'):
            if user.name in self.pifEntries:
                comment.reply("You're already entered in this PIF")
            elif activity[0] >= self.minKarma:
                self.handle_entry(comment, user)
            else:
                comment.reply("I'm afraid you don't have the karma for this PIF\n\n" + formattedKarma)
        elif command_parts[1].startswith('karma'):
            comment.reply(formattedKarma)
        else:
            comment.reply("My dude, I don't understand what you're trying to do")
    
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
    
    def handle_entry(self, comment, user):
        print("Implement in subclass")
    
    def determine_winner(self):
        print("Implement in subclass")