'''
Created on Feb 16, 2020

@author: rcurtis
'''
import time

from utils.dynamo_helper import fetch_open_pifs, close_pif
from pifs.pif_builder import build_from_ddb_dict

def check_and_update_pifs():
    print("Checking on and updating open PIFs")
    # Get all open PIFs
    pifs = fetch_open_pifs()
    
    print("Found {} open PIFs".format(len(pifs)))
    
    # For each open PIF
    for pif in pifs:
        # If current time > close time
        timeToExpire = pif['ExpireTime'] - int(time.time())
        if timeToExpire < 1:
            # Finalize the PIF
            print("PIF {} ended {} minutes ago and needs to be finalized".format(pif['SubmissionId'], int(timeToExpire/-60)))
            pif_obj = build_from_ddb_dict(pif)
            pif_obj.finalize()
            close_pif(pif_obj.postId)
        else:
            print("PIF {} expires in {} hours".format(pif['SubmissionId'], timeToExpire/3600))