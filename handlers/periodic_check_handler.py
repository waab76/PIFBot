#!/usr/bin/env python3
# coding: utf-8
#
#   File = periodic_check_handler.py
#
#      Copyright 2020 Rob Curtis
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
############################################################################
import logging
import time

from utils.pif_storage import get_open_pifs, save_pif

def check_and_update_pifs():
    logging.debug('Checking and updating tracked PIFs')
    # Get all open PIFs
    pifs = get_open_pifs()
    
    logging.info('Processing %s tracked PIFs', len(pifs))
    
    # For each open PIF
    for pif in pifs:
        # If current time > close time
        timeToExpire = int(pif.expireTime) - int(time.time())
        if timeToExpire < 1:
            # Finalize the PIF
            logging.info('PIF %s ended %s minutes ago and needs to be finalized', pif.postId, int(timeToExpire/-60))
            pif.finalize()
            save_pif(pif)
        else:
            logging.info('PIF %s expires in %s hours', pif.postId, timeToExpire/3600)