'''
Created on Apr 20, 2020

@author: rcurtis
'''
import logging
import random

from geopy.distance import distance
from geopy.geocoders import Nominatim

from pifs.base_pif import BasePIF
from utils.reddit_helper import get_comment, user_agent

instructionTemplate = """
Welcome to {}'s Geo PIF (managed by LatherBot).

When the PIF ends, I'll choose a random spot on the globe. Whoever's guess is closest to that 
spot will be the winner. In order to qualify, you must have at least {} karma on the sub in 
the last 90 days. 

To enter, simply add a top-level comment on the PIF post that includes (on a line by itself) the command:

`LatherBot in <your guess>`
 
I will check your karma and record your guess if you qualify.  Example:

`LatherBot in Cleveland, Ohio`

or

`LatherBot in Moscow, Russia`

This PIF will close in {} hour(s). At that time, I will determine the winner and notify the PIF's creator.

You can get a karma check by commenting "LatherBot karma".  LatherBot documentation can be found 
in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

Good luck!
"""

winner_template =  """
The PIF is over!

The spot on the globe I chose was [({}, {})](https://maps.google.com/maps?q={}%2C+{})

The winner is u/{} with a guess of {} : ({}), {} km away.  Congratulations!
"""

geolocator = Nominatim(user_agent=user_agent)

class Geo(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={}):
        logging.debug('Building Geo PIF [%s]', postId)
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'geo', minKarma, durationHours, endTime, pifOptions, pifEntries)
        
    def pif_instructions(self):
        logging.info('Printing instructions for PIF [%s]', self.postId)
        return instructionTemplate.format(self.authorName, 
                                          self.minKarma, 
                                          self.durationHours)

    def is_already_entered(self, user, comment):
        if user.name in self.pifEntries:
            logging.info('User [%s] appears to have already entered PIF [%s] with comment [%s]', user.name, self.postId, self.pifEntries[user.name]['CommentId'])
            entered_comment = get_comment(self.pifEntries[user.name]['CommentId'])
            if (entered_comment.submission.id != comment.submission.id):
                logging.warn("Entered comment submission [{}] doesn't match current comment submission [{}] for PIF [{}]".format(entered_comment.submission.id, comment.submission.id, self.postId))
                return False
            else:
                return True
        else:
            return False

    def handle_entry(self, comment, user, command_parts):
        guess = None
        try:
            guess = ' '.join(command_parts[2:])
        except IndexError:
            comment.reply("It looks like you didn't pick a location.  Care to try again?")
            comment.save()
            return
        
        guessed_location = geolocator.geocode(guess)
        if guessed_location is None:
            comment.reply("I'm sorry, I couldn't find [{}] on the map.  Care to try again?.".format(guess))
            comment.save()
            return
        
        conflict = self.userAlreadyGuessed(guessed_location.address)
        if conflict is not None:
            comment.reply("I'm sorry, {} was already taken by {}.  Try again.".format(guess, conflict))
            comment.save()
            return

        entryDetails = dict()
        entryDetails['CommentId'] = comment.id
        entryDetails['Guess'] = guess
        entryDetails['GuessAddr'] = guessed_location.address
        entryDetails['GuessLatLon'] = '{}, {}'.format(guessed_location.latitude, guessed_location.longitude)
        self.pifEntries[user.name] = entryDetails
        comment.reply("Entry confirmed.  {} guessed {} at [lat/lon ({},{})](https://maps.google.com/maps?q={}%2C+{})".format(user.name, 
                                                                       guessed_location.address, 
                                                                       guessed_location.latitude,
                                                                       guessed_location.longitude, 
                                                                       guessed_location.latitude,
                                                                       guessed_location.longitude))
        comment.save()
           
    def determine_winner(self):
        self.win_latitude = random.randrange(-900000000, 900000000)/10000000
        self.win_longitude = random.randrange(-1800000000, 1800000000)/10000000
        
        self.pifWinner = 'TBD'
        self.winningDistance = 20005
        for entrant in self.pifEntries.keys():
            if self.postId != get_comment(self.pifEntries[entrant]['CommentId']).submission.id:
                    continue
            guessLatLon = self.pifEntries[entrant]['GuessLatLon']
            guess_lat = float(guessLatLon.split(', ')[0])
            guess_lon = float(guessLatLon.split(', ')[1])
            guessDistance = distance((self.win_latitude, self.win_longitude),
                                     (guess_lat, guess_lon)).km
            if guessDistance < self.winningDistance:
                self.pifWinner = entrant
                self.winningDistance = guessDistance
        
    def generate_winner_comment(self):
        return winner_template.format(self.win_latitude, self.win_longitude, self.win_latitude, self.win_longitude, 
                                      self.pifWinner, self.pifEntries[self.pifWinner]['Guess'],
                                      self.pifEntries[self.pifWinner]['GuessLatLon'],
                                      self.winningDistance)
    
    def userAlreadyGuessed(self, guess):
        for entry in self.pifEntries.keys():
            if guess == self.pifEntries[entry]['GuessAddr']:
                return entry
        return None
        
