import logging

from pifs.lottery_pif import Lottery
from pifs.range_pif import Range


def build_and_init_pif(submission):
    logging.info('Scanning submission [%s] for a LatherBot command', submission.id)
    lines = submission.selftext.lower().split("\n")
    for line in lines:
        if line.startswith("latherbot"):
            pif = build_from_post(submission, line)
            if pif is None:
                return None
            else:
                logging.info('Initializing PIF [%s]', submission.id)
                pif.initialize()
                return pif
            break;
    return None

def build_from_post(submission, line):
    logging.info('Building PIF from command [%s] for submission [%s]', line, submission.id)
    try:
        parts = line.split()
        pifType = parts[1]
        minKarma = parts[2]
        durationHours = parts[3]
        endTime = int(submission.created_utc) + 3600 * int(durationHours)
        
        if pifType == "lottery":
            return Lottery(submission.id, submission.author.name, minKarma, durationHours, endTime)
        elif pifType == "range":
            pifOptions = dict()
            pifOptions['RangeMin'] = int(parts[4])
            pifOptions['RangeMax'] = int(parts[5])
            return Range(submission.id, submission.author.name, minKarma, durationHours, endTime, pifOptions)
        elif pifType == "poker":
            print("Poker PIF - Not yet implemented")
            submission.reply("Sorry, I don't support Poker PIFs yet")
            return None
        else:
            logging.warning('Unsupported PIF type [%s]', pifType)
            submission.reply("Sorry, I'm not familiar with PIF type [{}]".format(pifType))
    except IndexError:
        logging.error("Not enough PIF parameters in input: [%s]", line)
        submission.reply("""Well this is embarassing. 
        You said *{}* and I couldn't figure out how to handle it. 
        Maybe check the LatherBot documentation and try again.""".format(line))


def build_from_ddb_dict(ddb_dict):
    logging.info('Building PIF object from DDB data %s', ddb_dict)
    pifType = ddb_dict['PifType']
    
    if pifType == "lottery":
        return Lottery(ddb_dict['SubmissionId'], 
                           ddb_dict['Author'],
                           ddb_dict['MinKarma'],
                           0,
                           ddb_dict['ExpireTime'],
                           ddb_dict['PifOptions'],
                           ddb_dict['PifEntries'])
    elif pifType == "range":
        return Range(ddb_dict['SubmissionId'], 
                           ddb_dict['Author'],
                           ddb_dict['MinKarma'],
                           0,
                           ddb_dict['ExpireTime'],
                           ddb_dict['PifOptions'],
                           ddb_dict['PifEntries'])
    elif pifType == "poker":
        pass
    else:
        logging.warning('Unsupported PIF type [%s]', pifType)