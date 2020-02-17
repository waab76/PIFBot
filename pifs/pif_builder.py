from pifs.lottery_pif import Lottery
# from pifs import poker_pif
# from pifs import range_pif


def build_and_init_pif(submission):
    lines = submission.selftext.lower().split("\n")
    for line in lines:
        if line.startswith("latherbot"):
            pif = build_from_post(submission, line)
            if pif is None:
                pass
            else:
                return pif.initialize()
            break;


def build_from_post(submission, line):
    try:
        parts = line.split()
        pifType = parts[1]
    
        if pifType == "lottery":
            return Lottery(submission.id, submission.author.name, parts[2], parts[3])
        elif pifType == "range":
            print("Range PIF - Not yet implemented")
            submission.reply("Sorry, I don't support Pick-a-Number PIFs yet")
            return None
        elif pifType == "poker":
            print("Poker PIF - Not yet implemented")
            submission.reply("Sorry, I don't support Poker PIFs yet")
            return None
        else:
            print("Unsupported PIF type: {}".format(pifType))
            submission.reply("Sorry, I'm not familiar with PIF type [{}]".format(pifType))
    except IndexError:
        print("Not enough PIF parameters in input: {}".format(line))
        submission.reply("""Well this is embarassing. 
        You said *{}* and I couldn't figure out how to handle it. 
        Maybe check the LatherBot documentation and try again.""".format(line))


def build_from_ddb_dict(ddb_dict):
    print(ddb_dict)
    pifType = ddb_dict['PifType']
    
    if pifType == "lottery":
        return Lottery(ddb_dict['SubmissionId'], 
                           ddb_dict['Author'],
                           ddb_dict['MinKarma'],
                           ddb_dict['DurationHours'],
                           ddb_dict['PifOptions'],
                           ddb_dict['PifEntries'])
    elif pifType == "range":
        pass
    elif pifType == "poker":
        pass
    else:
        print("Unsupported PIF type: {}".format(pifType))
