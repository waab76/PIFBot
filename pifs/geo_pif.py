'''
Created on Apr 20, 2020

@author: rcurtis
'''
import logging
import random

import pandas as pd
import plotly.graph_objects as go

from geopy.distance import distance
from geopy.geocoders import Nominatim

# from imgurpython import ImgurClient

# from config import imgur_client_id, imgur_client_secret
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

LatherBot documentation can be found in [the wiki](https://www.reddit.com/r/Wetshaving/wiki/latherbot)

Good luck!
"""

winner_template =  """
The PIF is over!

The spot on the globe I chose was [({}, {})](https://maps.google.com/maps?q={}%2C+{})

The winner is u/{} with a guess of {} : ({}), {} km away.  Congratulations!
"""

geolocator = Nominatim(user_agent=user_agent)

class Geo(BasePIF):

    def __init__(self, postId, authorName, minKarma, durationHours, endTime, pifOptions={}, pifEntries={}, karmaFail={}):
        logging.debug('Building Geo PIF [%s]', postId)
        # Handle the options
        BasePIF.__init__(self, postId, authorName, 'geo', minKarma, durationHours, endTime, pifOptions, pifEntries, karmaFail)
        
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
            comment.reply("It looks like you were trying to enter the PIF but something was wrong with the command you entered.  Please re-read the instructions and try again on a brand new comment (because the bot only processes each comment once and this one has already been processed)")
            comment.save()
            return
        
        guessed_location = geolocator.geocode(guess)
        if guessed_location is None:
            comment.reply("I'm sorry, I couldn't find [{}] on the map.  You will need to try again in a brand new comment.".format(guess))
            comment.save()
            return
        
        conflict = self.userAlreadyGuessed(guessed_location.address)
        if conflict is not None:
            comment.reply("I'm sorry, {} was already taken by {}.  You will need to try again in a brand new comment.".format(guess, conflict))
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
        self.pifOptions['WinLat'] = self.win_latitude
        self.pifOptions['WinLon'] = self.win_longitude
        
        df = pd.DataFrame(columns=('name', 'lat', 'lon', 'distance'))
        
        self.pifWinner = 'TBD'
        self.winningDistance = 20005
        entrant_num = 0
        for entrant in self.pifEntries.keys():
            if self.postId != get_comment(self.pifEntries[entrant]['CommentId']).submission.id:
                    continue
            guessLatLon = self.pifEntries[entrant]['GuessLatLon']
            guess_lat = float(guessLatLon.split(', ')[0])
            guess_lon = float(guessLatLon.split(', ')[1])
            guess_dist = distance((self.win_latitude, self.win_longitude), (guess_lat, guess_lon)).km
            df.loc[entrant_num] = [entrant, guess_lat, guess_lon, guess_dist]
            entrant_num += 1
            if guess_dist < self.winningDistance:
                self.pifWinner = entrant
                self.winningDistance = guess_dist
        
        fig = go.Figure(data=go.Scattergeo(
            lon = df['lon'],
            lat = df['lat'],
            marker = dict(
                size = 6,
                opacity = 0.8,
                reversescale = True,
                autocolorscale = False,
                symbol = 'square',
                line = dict(
                    width=1,
                    color='rgba(102, 102, 102)'
                ),
                colorscale = 'rdylgn',
                cmin = 0,
                color = df['distance'],
                cmax = df['distance'].max(),
                colorbar_title="Distance From Selected Point (km)"
            )))
    
        fig.add_traces(go.Scattergeo(
            lon = [self.win_latitude],
            lat = [self.win_longitude],
            marker = dict(
            size = 10,
            opacity = 1,
            symbol = 'star',
            color = '#ce1123'
        )))
    
        fig.update_traces(textposition='top center')
    
        fig.update_layout(
            title = "{}'s PIF Results".format(self.authorName),
            geo = dict(
                projection  = dict (
                    type = 'kavrayskiy7',
                    rotation_lon = self.win_longitude
                ),
                showland = True,
                landcolor = "rgb(250, 250, 250)"
            ),
        )
    
        # fig.write_image(file="pif_{}_result.png".format(self.postId), width=1024, scale=3)
        
    
        # imgur = ImgurClient(imgur_client_id, imgur_client_secret)
        # image = imgur.upload_from_path("pif_{}_result.png".format(self.postId))
        # self.imageLink = image['link']
        
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
        
