import logging

from utils.karma_calculator import calculate_karma, formatted_karma
from utils.reddit_helper import already_replied, get_submission

class BasePIF:
    def __init__(self, postId, authorName, pifType, minKarma, endTime, 
                 pifOptions={}, pifEntries={}):
        logging.debug('Building PIF [%s]', postId)
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
        logging.info('Adding PIF instructions')
        comment = get_submission(self.postId).reply(self.pif_instructions())
        comment.mod.distinguish('yes', True)
            
    def handle_comment(self, comment):
        logging.debug('Handling comment [%s] for PIF [%s]', comment.id, self.postId)
        if already_replied(comment):
            logging.debug('Already replied to comment [%s]', comment.id)
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
                logging.info('Handling command [%s] for PIF [%s] comment [%s]', line, self.postId, comment.id)
                self.handle_command(comment, parts)
        
        
    def handle_command(self, comment, command_parts):
        user = comment.author
        activity = calculate_karma(user)
        formattedKarma = formatted_karma(user, activity)

        if command_parts[1].startswith('in'):
            if user.name in self.pifEntries:
                logging.info('User [%s] has already entered PIF [%s]', user.name, self.postId)
                comment.reply("You're already entered in this PIF")
            elif activity[0] >= self.minKarma:
                logging.debug('User [%s] meets karma requirement for PIF [%s]', user.name, self.postId)
                self.handle_entry(comment, user, command_parts)
            else:
                logging.info('User [%s] does not meet karma requirement for PIF [%s]', user.name, self.postId)
                comment.reply("I'm afraid you don't have the karma for this PIF\n\n" + formattedKarma)
        elif command_parts[1].startswith('karma'):
            logging.info('User [%s] requested karma check', user.name)
            comment.reply(formattedKarma)
        else:
            logging.warning('Invalid command on comment [%s] for PIF [%s]', comment.id, self.postId)
            comment.reply("My dude, I don't understand what you're trying to do")
    
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

        logging.debug('Closing and locking PIF [%s]', self.postId)
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