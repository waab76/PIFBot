#!/usr/bin/env python3
# coding: utf-8
#
#   File = pif_builder.py
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

from pifs.battleship_pif import Battleship
from pifs.geo_pif import Geo
from pifs.holdem_poker_pif import HoldemPoker
from pifs.infinite_poker_pif import InfinitePoker
from pifs.karma_only_pif import KarmaOnly
from pifs.lottery_pif import Lottery
from pifs.poker_pif import Poker
from pifs.range_pif import Range
from pifs.randomizer_pif import Randomizer

known_pif_types = [
    'lottery',
    'range', 'poker',
    'infinite-poker',
    'geo',
    'karma-only',
    'battleship',
    'holdem-poker',
    'randomizer',
]

def build_and_init_pif(submission):
    logging.info('Scanning submission "%s" for a LatherBot command', submission.title)
    lines = submission.selftext.lower().split("\n")
    for line in lines:
        if line.strip().startswith('latherbot'):
            pif = build_from_post(submission, line)
            if pif is None:
                continue
            else:
                logging.info('Initializing PIF "%s"', submission.title)
                pif.initialize()
                return pif
            break;
    logging.warning('No LatherBot command found in submission [%s]', submission.id)
    return None

def build_from_post(submission, line):
    logging.info('Building PIF from command [%s] for submission "%s"', line, submission.title)
    try:
        parts = line.split()
        pifType = parts[1]
        if pifType not in known_pif_types:
            return None
        minKarma = parts[2]
        durationHours = parts[3]
        endTime = int(submission.created_utc) + 3600 * int(durationHours)
        
        if endTime < time.time():
            logging.info('PIF "%s" should already be closed', submission.title)
            submission.mod.flair(text='PIF - Closed', css_class='orange')
            submission.mod.lock()
        elif pifType == "lottery":
            return Lottery(submission.id, submission.author.name, minKarma, durationHours, endTime, pifOptions={}, pifEntries={},
                 karmaFail={})
        elif pifType == "range":
            rangeMin = int(parts[4])
            rangeMax = int(parts[5])
            
            if rangeMax <= rangeMin:
                submission.reply("I think you got your min and max mixed up")
            
            pifOptions = dict()
            pifOptions['RangeMin'] = rangeMin
            pifOptions['RangeMax'] = rangeMax
            return Range(submission.id, submission.author.name, minKarma, durationHours, endTime, pifOptions, pifEntries={},
                 karmaFail={})
        elif pifType == "poker":
            return Poker(submission.id, submission.author.name, minKarma, durationHours, endTime, pifOptions={}, pifEntries={},
                 karmaFail={})
        elif pifType == "infinite-poker":
            return InfinitePoker(submission.id, submission.author.name, minKarma, durationHours, endTime, pifOptions={}, pifEntries={},
                 karmaFail={})
        elif pifType == "holdem-poker":
            return HoldemPoker(submission.id, submission.author.name, minKarma, durationHours, endTime, pifOptions={}, pifEntries={},
                 karmaFail={})
        elif pifType == "geo":
            return Geo(submission.id, submission.author.name, minKarma, durationHours, endTime, pifOptions={}, pifEntries={},
                 karmaFail={})
        elif pifType == "battleship":
            return Battleship(submission.id, submission.author.name, minKarma, durationHours, endTime, pifOptions=None, pifEntries={},
                 karmaFail={})
        elif pifType == "karma-only":
            return KarmaOnly(submission.id, submission.author.name, minKarma, durationHours, endTime, pifOptions={}, pifEntries={},
                 karmaFail={})
        elif pifType == "randomizer":
            return Randomizer(submission.id, submission.author.name, minKarma, durationHours, endTime, pifOptions={}, pifEntries={},
                 karmaFail={})
        else:
            logging.warning('Unsupported PIF type [%s]', pifType)
            submission.reply("Sorry, I'm not familiar with PIF type [{}]".format(pifType))
    except IndexError:
        logging.error("Not enough PIF parameters in input: [%s]", line)
        submission.reply("""Well this is embarassing. 
        You said *{}* and I couldn't figure out how to handle it. 
        Maybe check the LatherBot documentation and try again.""".format(line))


def build_from_ddb_dict(ddb_dict):
    logging.debug('Building PIF object from DDB data %s', ddb_dict)
    pifType = ddb_dict['PifType']
    
    if pifType == "lottery":
        return Lottery(ddb_dict['SubmissionId'], 
                           ddb_dict['Author'],
                           ddb_dict['MinKarma'],
                           0,
                           ddb_dict['ExpireTime'],
                           ddb_dict['PifOptions'],
                           ddb_dict['PifEntries'],
                           ddb_dict['KarmaFail'])
    elif pifType == "range":
        return Range(ddb_dict['SubmissionId'], 
                           ddb_dict['Author'],
                           ddb_dict['MinKarma'],
                           0,
                           ddb_dict['ExpireTime'],
                           ddb_dict['PifOptions'],
                           ddb_dict['PifEntries'],
                           ddb_dict['KarmaFail'])
    elif pifType == "poker":
        return Poker(ddb_dict['SubmissionId'], 
                           ddb_dict['Author'],
                           ddb_dict['MinKarma'],
                           0,
                           ddb_dict['ExpireTime'],
                           ddb_dict['PifOptions'],
                           ddb_dict['PifEntries'],
                           ddb_dict['KarmaFail'])
    elif pifType == "infinite-poker":
        return InfinitePoker(ddb_dict['SubmissionId'],
                             ddb_dict['Author'],
                             ddb_dict['MinKarma'],
                             0,
                             ddb_dict['ExpireTime'],
                             ddb_dict['PifOptions'],
                             ddb_dict['PifEntries'],
                             ddb_dict['KarmaFail'])
    elif pifType == "holdem-poker":
        return HoldemPoker(ddb_dict['SubmissionId'],
                             ddb_dict['Author'],
                             ddb_dict['MinKarma'],
                             0,
                             ddb_dict['ExpireTime'],
                             ddb_dict['PifOptions'],
                             ddb_dict['PifEntries'],
                             ddb_dict['KarmaFail'])
    elif pifType == "geo":
        return Geo(ddb_dict['SubmissionId'], 
                   ddb_dict['Author'],
                   ddb_dict['MinKarma'],
                   0,
                   ddb_dict['ExpireTime'],
                   ddb_dict['PifOptions'],
                   ddb_dict['PifEntries'],
                   ddb_dict['KarmaFail'])
    elif pifType == "battleship":
        return Battleship(ddb_dict['SubmissionId'], 
                   ddb_dict['Author'],
                   ddb_dict['MinKarma'],
                   0,
                   ddb_dict['ExpireTime'],
                   ddb_dict['PifOptions'],
                   ddb_dict['PifEntries'],
                   ddb_dict['KarmaFail'])
    elif pifType == "karma-only":
        return KarmaOnly(ddb_dict['SubmissionId'], 
                   ddb_dict['Author'],
                   ddb_dict['MinKarma'],
                   0,
                   ddb_dict['ExpireTime'],
                   ddb_dict['PifOptions'],
                   ddb_dict['PifEntries'],
                   ddb_dict['KarmaFail'])
    elif pifType == "randomizer":
        return Randomizer(ddb_dict['SubmissionId'], 
                   ddb_dict['Author'],
                   ddb_dict['MinKarma'],
                   0,
                   ddb_dict['ExpireTime'],
                   ddb_dict['PifOptions'],
                   ddb_dict['PifEntries'],
                   ddb_dict['KarmaFail'])
    else:
        logging.warning('Unsupported PIF type [%s]', pifType)
