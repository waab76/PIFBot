'''
Created on Feb 16, 2020

@author: rcurtis
'''
import time

from utils.dynamo_helper import fetch_open_pifs
from pifs.pif_builder import build_from_ddb_dict

def check_and_update_pifs():
    print("Checking on and updating open PIFs")
    # Get all open PIFs
    pifs = fetch_open_pifs()
    
    # For each open PIF
    for pif in pifs:
        print(pif)
        # If current time > close time
        timeToExpire = pif['ExpireTime'] - int(time.time())
        if timeToExpire < 1:
            # Finalize the PIF
            print("This PIF ended {} minutes ago and needs to be finalized".format(int(timeToExpire/-60)))
            pif_obj = build_from_ddb_dict(pif)
            pif_obj.finalize()
        else:
            print("PIF {} expires in {} hours".format(pif['SubmissionId'], timeToExpire/3600))