'''
Created on Feb 16, 2020

@author: rcurtis
'''
import logging
import time

from utils.pif_storage import get_open_pifs, save_pif

def check_and_update_pifs():
    logging.info('Checking and updating tracked PIFs')
    # Get all open PIFs
    pifs = get_open_pifs()
    
    logging.info('Processing %s tracked PIFs', len(pifs))
    
    # For each open PIF
    for pif in pifs:
        # If current time > close time
        timeToExpire = int(pif.expireTime) - int(time.time())
        if timeToExpire < 1:
            # Finalize the PIF
            logging.info('PIF [%s] ended %s minutes ago and needs to be finalized', pif.postId, int(timeToExpire/-60))
            pif.finalize()
            save_pif(pif)
        else:
            logging.info('PIF [%s] expires in %s hours', pif.postId, timeToExpire/3600)