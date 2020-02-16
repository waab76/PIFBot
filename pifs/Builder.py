from .Lottery import Lottery
from .Poker import Poker
from .Range import Range

def buildPIF(submission):
    lines = submission.selftext.lower().split("\n")
    parts = None
    for line in lines:
        if line.startswith("pifbot"):
            parts = line.split()
            break

    if parts[1] == "lottery":
        return Lottery(submission, parts[2:])
    elif parts[1] == "range":
        return Range(submission, parts[2:])
    elif parts[1] == "poker":
        return Poker(submission, parts[2:])