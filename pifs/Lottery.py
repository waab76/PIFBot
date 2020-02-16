from .PIF import BasePIF

class Lottery(BasePIF):

    def __init__(self, submission, options):
        BasePIF.__init__(self, submission, 'lottery')
        # Handle the options