#! /usr/local/bin/python3
'''
Created on Feb 24, 2020

@author: rcurtis
'''
import time

from pifs import pif_builder
from utils import dynamo_helper
from utils import reddit_helper
from utils import poker_util

pif_list = dynamo_helper.fetch_all_pifs()
piffers = dict()
winners = dict()
pif_types = dict()
pif_type_entries = dict()
max_pif_type_name_len = 0
entrants = dict()
pif_count = 0
entry_count = 0
history_days = 30
thirty_days_ago = time.time() - (history_days * 24 * 60 * 60)
best_poker_hand_score = 0
best_poker_hand_user = 'TBD'
best_poker_hand = []

for pif_type in pif_builder.known_pif_types:
    pif_types[pif_type] = 0
    pif_type_entries[pif_type] = 0

for pif in pif_list:
    submission = reddit_helper.reddit.submission(pif['SubmissionId'])
    if submission.created_utc < thirty_days_ago:
        continue
    
    pif_type = pif['PifType']
    pif_count += 1
    
    if pif['Author'] not in piffers:
        piffers[pif['Author']] = 0
    piffers[pif['Author']] += 1
    
    if 'TBD' != pif['PifWinner']:
        if pif['PifWinner'] not in winners:
            winners[pif['PifWinner']] = 0
        winners[pif['PifWinner']] += 1
        
        if pif_type == 'infinite-poker':
            if pif['PifEntries'][pif['PifWinner']]['HandScore'] > best_poker_hand_score:
                best_poker_hand_score = pif['PifEntries'][pif['PifWinner']]['HandScore']
                best_poker_hand_user = pif['PifWinner']
                best_poker_hand = pif['PifEntries'][pif['PifWinner']]['UserHand']
    
    pif_types[pif_type] += 1
    
    for entrant in pif['PifEntries'].keys():
        if entrant not in entrants:
            entrants[entrant] = 0
        entrants[entrant] += 1
        entry_count += 1
        pif_type_entries[pif_type] += 1

sorted_piffers = sorted(piffers.items(), key = lambda kv: (kv[1], kv[0]))[::-1]
sorted_pif_types = sorted(pif_types.items(), key = lambda kv: (kv[1], kv[0]))[::-1]
sorted_winners = sorted(winners.items(), key = lambda kv:(kv[1], kv[0]))[::-1]
sorted_entrants = sorted(entrants.items(), key = lambda kv:(kv[1], kv[0]))[::-1]

print("""
LatherBot PIF stats for the trailing {} days

\--------------------------------------------

{} PIFs by {} Redditors:

|Redditor|PIFs|
|:-|:-|""".format(history_days, pif_count, len(piffers)))

for piffer in sorted_piffers:
    print("|u/{}|{}|".format(piffer[0], piffer[1]))

print("""\nThere were {} entries across the {} PIFs. The top 10 most active PIF contestants were:

|Redditor|Entries|
|:-|:-|""".format(entry_count, pif_count))
for i in range(10):
    print("|u/{}|{}|".format(sorted_entrants[i][0], sorted_entrants[i][1]))
    
print("\nWinningest Redditors:\n\n|Redditor|Wins|\n|:-|:-|")
for pif_winner in sorted_winners:
    print("|u/{}|{}|".format(pif_winner[0], pif_winner[1]))
    
print("\nMost popular PIF types:\n\n|PIF Type|Count|Entries per PIF|\n|:-|:-|:-|")
for pif_type in sorted_pif_types:
    print("|{}|{}|{}|".format(pif_type[0], pif_type[1], round(pif_type_entries[pif_type[0]] / pif_type[1], 2)))
    
print("\nBest poker hand: {} with {}".format(best_poker_hand_user, poker_util.determine_hand(best_poker_hand)))