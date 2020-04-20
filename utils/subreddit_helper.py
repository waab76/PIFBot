'''
Created on Apr 1, 2020

@author: rcurtis
'''

import logging
import os
import praw

from time import strftime, strptime

from .file_system_helper import get_files_in_desc_order
from .imgur_helper import download_as
from .reddit_helper import subreddit

stylesheet = subreddit.stylesheet

def download_contest_winners(target_dir):
    files = get_files_in_desc_order(target_dir)
    
    winners = subreddit.search(query="weekly contest results", sort="new", time_filter="month")
    
    for winner in winners:
        titleDate = winner.title[40:]
        winnerDate = strptime(titleDate, "%B %d, %Y")
        winnerFilename = strftime("%Y-%m-%d", winnerDate) + '.jpg'
        if not winnerFilename in files:
            logging.info('Downloading [%s]', winnerFilename)
            firstIndex = winner.selftext.find('1st')
            lastIndex = winner.selftext.find('votes')
            imgurLink = winner.selftext[firstIndex:lastIndex].split(" ")[4]
            download_as(imgurLink, os.path.join(target_dir, winnerFilename))
        else:
            logging.info('[%s] already exists, not downloading', winnerFilename)

def update_subreddit(source_dir, sidebar_file, banner_file):
    update_classic_reddit(source_dir, sidebar_file, banner_file)
    update_new_reddit(source_dir, sidebar_file, banner_file)
    
def update_classic_reddit(source_dir, sidebar_file, banner_file):
    # Update the sidebar image
    stylesheet.delete_image("sidebar-img")
    stylesheet.upload("sidebar-img", os.path.join(source_dir, sidebar_file))

    # Update the banner image
    stylesheet.delete_image("banner")
    stylesheet.upload("banner", os.path.join(source_dir, banner_file))

    # Trigger the update by refreshing the stylesheet
    stylesheet.update(subreddit.stylesheet().stylesheet, "Auto-updating sidebar/banner")


def update_new_reddit(source_dir, sidebar_file, banner_file):
    # Update the sidebar widget
    widgets = subreddit.widgets
    image_widget = None

    for widget in widgets.sidebar:
        if isinstance(widget, praw.models.ImageWidget):
            image_widget = widget
            break

    imageData = [{'width': 512, 'height': 512, 'linkUrl': '',
             'url': widgets.mod.upload_image(os.path.join(source_dir, sidebar_file))}]
    image_widget.mod.update(data=imageData)

    # Update the banner
    stylesheet.upload_banner(os.path.join(source_dir, banner_file))