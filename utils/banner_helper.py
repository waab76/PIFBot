#!/usr/local/bin/python3
# coding: utf-8

'''
Created on Mar 29, 2020

@author: rcurtis
'''
import logging

from utils.file_system_helper import remove_file, get_files_in_desc_order
from utils.imagery_helper import generate_thumbnail_file, generate_banner_image
from utils.subreddit_helper import download_contest_winners, update_subreddit

banner_image_name = "banner.jpg"
sidebar_image_name = "sidebar-img.jpg"
working_dir = './winners'

def banner_update():
    pass
    #logging.info('Clean up old banner and sidebar files if they exist')
    #remove_file(working_dir, banner_image_name)
    #remove_file(working_dir, sidebar_image_name)
    
    #logging.info('Fetch winning images')
    #download_contest_winners(working_dir)
    
    #logging.info('Generate new sidebar image')
    #thumbnail_max_dimensions = 512,512
    #sidebar_input_file = get_files_in_desc_order(working_dir)[0]
    #generate_thumbnail_file(working_dir, sidebar_input_file, sidebar_image_name, 
    #                        thumbnail_max_dimensions)

    #logging.info('Generate new banner image')
    #banner_size = 1920, 256
    #generate_banner_image(working_dir, banner_image_name, banner_size)
    
    #logging.info('Update the subreddit')
    #update_subreddit(working_dir, sidebar_image_name, banner_image_name)

    
if __name__ == '__main__':
    banner_update()