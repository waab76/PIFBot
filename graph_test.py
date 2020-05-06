'''
Created on Apr 23, 2020

@author: rcurtis
'''
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import random

from geopy.distance import distance

from imgurpython import ImgurClient

from config import imgur_client_id, imgur_client_secret
from utils.pif_storage import get_pif

def main():
    pio.orca.config.executable = '/home/ec2-user/anaconda3/bin/orca'
    pio.orca.config.save()
    pif_id = 'gdoxlp'
    pif = get_pif(pif_id)
    win_lat = random.randrange(-900000000, 900000000)/10000000
    win_lon = random.randrange(-1800000000, 1800000000)/10000000
    
    df = pd.DataFrame(columns=('name', 'lat', 'lon', 'distance'))
    
    # df.loc[0] = ['LatherBot', win_lat, win_lon, 0]
    
    entrant_num = 0
    for entrant in pif.pifEntries.keys():
        guessLatLon = pif.pifEntries[entrant]['GuessLatLon']
        guess_lat = float(guessLatLon.split(', ')[0])
        guess_lon = float(guessLatLon.split(', ')[1])
        guess_dist = distance((win_lat, win_lon), (guess_lat, guess_lon)).km
        df.loc[entrant_num] = [entrant, guess_lat, guess_lon, guess_dist]
        entrant_num += 1
    
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
        lon = [win_lon],
        lat = [win_lat],
        marker = dict(
            size = 10,
            opacity = 1,
            symbol = 'star',
            color = '#ce1123'
        )))
    
    fig.update_traces(textposition='top center')
    
    fig.update_layout(
        title = "{}'s PIF Results".format(pif.authorName),
        geo = dict(
            projection  = dict (
                type = 'kavrayskiy7',
                rotation_lon = win_lon
            ),
            showland = True,
            landcolor = "rgb(250, 250, 250)"
        ),
    )
        
    fig.write_image(file="pif_{}_result.png".format(pif_id), width=1024, scale=3)
    
    imgur = ImgurClient(imgur_client_id, imgur_client_secret)
    image = imgur.upload_from_path("pif_{}_result.png".format(pif_id))
    print(image['link'])

if __name__ == '__main__':
    main()