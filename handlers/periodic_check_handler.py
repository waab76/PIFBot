'''
Created on Feb 16, 2020

@author: rcurtis
'''
import time

from utils.pif_storage import get_open_pifs, save_pif

def check_and_update_pifs():
    print("Checking on and updating open PIFs")
    # Get all open PIFs
    pifs = get_open_pifs()
    
    print("Found {} open PIFs".format(len(pifs)))
    
    # For each open PIF
    for pif in pifs:
        # If current time > close time
        timeToExpire = int(pif.expireTime) - int(time.time())
        if timeToExpire < 1:
            # Finalize the PIF
            print("PIF {} ended {} minutes ago and needs to be finalized".format(pif.postId, int(timeToExpire/-60)))
            pif.finalize()
            save_pif(pif)
        else:
            print("PIF {} expires in {} hours".format(pif.postId, timeToExpire/3600))