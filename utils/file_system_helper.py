'''
Created on Apr 1, 2020

@author: rcurtis
'''

import logging
import os

def get_files_in_desc_order(directory):
    create_dir_if_necessary(directory)
    files = os.listdir(directory)
    return sorted(files, reverse=True)

def create_dir_if_necessary(directory):
    if not os.path.isdir(directory):
        logging.info('Creating directory [%s]', directory)
        os.makedirs(directory)
        
def remove_file(directory, filename):
    if not os.path.isdir(directory):
        return
    filepath = os.path.join(directory, filename)
    if os.path.isfile(filepath):
        os.remove(filepath)