'''
Created on Mar 29, 2020

@author: rcurtis
'''

import logging
import requests
from bs4 import BeautifulSoup

def download_as(imgurUrl, localFileName):
    if imgurUrl.find('.jpg') > 0:
        downloadSingleImage(imgurUrl, localFileName)
    else:
        downloadFirstAlbumImage(imgurUrl, localFileName)

def downloadSingleImage(imageUrl, localFileName):
    logging.debug('Downloading file from Imgur link [%s] as [%s]', imageUrl, localFileName)
    response = requests.get(imageUrl)
    if response.status_code == 200:
        with open(localFileName, 'wb') as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)

def downloadFirstAlbumImage(albumUrl, localFileName):
    albumSource = requests.get(albumUrl).text
    soup = BeautifulSoup(albumSource)
    matches = soup.findAll('link', rel='image_src')
    downloadSingleImage(matches[0]['href'], localFileName)