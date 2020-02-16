from utils.dynamo_helper import pifExists, storePIF

class BasePIF:
    def __init__(self, submission, pifType):
        self.submission = submission
        self.pifType = pifType

    def initialize(self):
        if pifExists(self.submission.id):
            print('PIF found')
        else:
            print('PIF not found, storing')
            storePIF(self.submission.id, self.submission.author.name, self.pifType)