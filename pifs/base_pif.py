from utils.karma_calculator import calculate_karma, formatted_karma
from utils.reddit_helper import already_replied, get_submission

class BasePIF:
    def __init__(self, postId, authorName, pifType, minKarma, endTime, 
                 pifOptions={}, pifEntries={}):
        self.postId = postId
        self.authorName = authorName
        self.pifType = pifType
        self.minKarma = int(minKarma)
        self.pifOptions = pifOptions
        self.pifEntries = pifEntries
        self.expireTime = int(endTime)
        self.pifState = 'open'
        self.pifWinner = 'TBD'

    def initialize(self):
        comment = get_submission(self.postId).reply(self.pif_instructions())
        comment.mod.distinguish('yes', True)
            
    def handle_comment(self, comment):
        if already_replied(comment):
            return

        user = comment.author
        if None is user or user.name == self.authorName:
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
                self.handle_entry(comment, user, command_parts)
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
            submission.mod.flair(text='PIF - Closed', css_class='orange')
        else:
            self.determine_winner()
            comment = submission.reply(self.generate_winner_comment())
            submission.mod.flair(text='PIF - Winner', css_class='orange')

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