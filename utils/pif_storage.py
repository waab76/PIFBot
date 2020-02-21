'''
Created on Feb 18, 2020

@author: rcurtis
'''
import logging

from utils import dynamo_helper
from pifs.pif_builder import build_from_ddb_dict

logging.info('Creating PIF cache')
pif_cache = dict()

def save_pif(pif_obj):
    logging.info('Saving PIF [%s]', pif_obj.postId)
    dynamo_helper.save_pif(pif_obj)
    pif_cache[pif_obj.postId] = pif_obj

def get_open_pifs():
    logging.info('Fetching open PIFs')
    json_pifs = dynamo_helper.fetch_open_pifs()
    pif_objs = list()
    for json_pif in json_pifs:
        pif_obj = build_from_ddb_dict(json_pif)
        pif_objs.append(pif_obj)
        pif_cache[pif_obj.postId] = pif_obj
    return pif_objs

def pif_exists(post_id):
    if post_id in pif_cache:
        logging.info('PIF [%s] found in cache', post_id)
        return True
    else:
        logging.info('PIF [%s] not in cache, looking in DDB', post_id)
        return dynamo_helper.open_pif_exists(post_id)

def get_pif(post_id):
    if post_id in pif_cache:
        logging.info('PIF [%s] found in cache', post_id)
        return pif_cache[post_id]
    else:
        logging.info('PIF [%s] not in cache, looking in DDB', post_id)
        pif_dict = dynamo_helper.fetch_pif(post_id)
        if pif_dict is None:
            logging.warning('PIF [%s] not found in DDB', post_id)
            return None
        else:
            pif_obj = build_from_ddb_dict(pif_dict)
            pif_cache[pif_obj.postId] = pif_obj
            return pif_obj
    