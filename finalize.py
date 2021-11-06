'''
Created on Feb 13, 2021

@author: rcurtis
'''

import sys
from utils.pif_storage import get_pif

def finalize(pif_id):
    pif = get_pif(pif_id)
    pif.finalize()

if __name__ == '__main__':
    finalize(sys.argv[1])