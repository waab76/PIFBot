'''
Created on Feb 24, 2020

@author: rcurtis
'''
import time

from pifs import pif_builder
from utils import dynamo_helper
from utils import reddit_helper

pif_list = dynamo_helper.fetch_all_pifs()
piffers = dict()
max_col_len = 0
winners = dict()
pif_types = dict()
max_pif_type_name_len = 0
entrants = dict()
pif_count = 0
entry_count = 0
history_days = 30
thirty_days_ago = time.time() - (history_days * 24 * 60 * 60)

for pif_type in pif_builder.known_pif_types:
    pif_types[pif_type] = 0
    if len(pif_type) > max_col_len:
        max_col_len = len(pif_type)

for pif in pif_list:
    submission = reddit_helper.reddit.submission(pif['SubmissionId'])
    if submission.created_utc < thirty_days_ago:
        continue
    
    pif_count += 1
    
    if pif['Author'] not in piffers:
        piffers[pif['Author']] = 0
        if len(pif['Author']) > max_col_len:
            max_col_len = len(pif['Author'])
    piffers[pif['Author']] += 1
    
    if 'TBD' != pif['PifWinner']:
        if pif['PifWinner'] not in winners:
            winners[pif['PifWinner']] = 0
        winners[pif['PifWinner']] += 1
    
    pif_types[pif['PifType']] += 1
    
    for entrant in pif['PifEntries'].keys():
        if entrant not in entrants:
            entrants[entrant] = 0
            if len(entrant) > max_col_len:
                max_col_len = len(entrant)
        entrants[entrant] += 1
        entry_count += 1

sorted_piffers = sorted(piffers.items(), key = lambda kv: (kv[1], kv[0]))[::-1]
sorted_pif_types = sorted(pif_types.items(), key = lambda kv: (kv[1], kv[0]))[::-1]
sorted_winners = sorted(winners.items(), key = lambda kv:(kv[1], kv[0]))[::-1]
sorted_entrants = sorted(entrants.items(), key = lambda kv:(kv[1], kv[0]))[::-1]

print("""
LatherBot PIF stats for the trailing {} days
--------------------------------------------

{} PIFs were run by {} Redditors:""".format(history_days, pif_count, len(piffers)))

for piffer in sorted_piffers:
    print("    u/{}    {}".format(piffer[0].ljust(max_col_len + 1), 
                                  str(piffer[1]).rjust(2)))

print("\nThere were {} entries across the {} PIFs. The top 10 most active PIF contestants were:"
      .format(entry_count, pif_count))
for i in range(10):
    print("    u/{}    {}".format(sorted_entrants[i][0].ljust(max_col_len + 1),
                                str(sorted_entrants[i][1]).rjust(2)))
    
print("\nWinningest Redditors:")
for pif_winner in sorted_winners:
    print("    u/{}    {}".format(pif_winner[0].ljust(max_col_len + 1),
                                str(pif_winner[1]).rjust(2)))
    
print("\nMost popular PIF types:")
for pif_type in sorted_pif_types:
    print("    {}    {}".format(pif_type[0].ljust(max_col_len + 3),
                                str(pif_type[1]).rjust(2)))