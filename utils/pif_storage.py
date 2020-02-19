'''
Created on Feb 18, 2020

@author: rcurtis
'''
from utils.dynamo_helper import create_pif_entry, close_pif, fetch_open_pifs, fetch_pif, open_pif_exists, update_pif_entries
from pifs.pif_builder import build_from_ddb_dict

pif_cache = dict()

def save_pif(pif_obj):
    create_pif_entry(pif_obj)
    pif_cache[pif_obj.postId] = pif_obj

def mark_pif_closed(pif_obj):
    close_pif(pif_obj)
    del pif_cache[pif_obj.postId]

def get_open_pifs():
    json_pifs = fetch_open_pifs()
    pif_objs = list()
    for json_pif in json_pifs:
        pif_obj = build_from_ddb_dict(json_pif)
        pif_objs.append(pif_obj)
        pif_cache[pif_obj.postId] = pif_obj
    return pif_objs

def pif_exists(post_id):
    if post_id in pif_cache:
        return True
    else:
        return open_pif_exists(post_id)

def get_pif(post_id):
    if post_id in pif_cache:
        return pif_cache[post_id]
    else:
        pif_dict = fetch_pif(post_id)
        if pif_dict is None:
            return None
        else:
            pif_obj = build_from_ddb_dict(pif_dict)
            pif_cache[pif_obj.postId] = pif_obj
            return pif_obj

def add_pif_entry(pif_obj):
    pif_cache[pif_obj.postId] = pif_obj
    update_pif_entries(pif_obj.postId, pif_obj.pifEntries)
    