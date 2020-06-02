'''
Created on Jun 1, 2020

@author: rcurtis
'''
from utils.reddit_helper import subreddit

if __name__ == '__main__':
    lg_sotds = subreddit.search(query="Lather Games SOTD", sort="new", time_filter="all")
    lg_participants = set()
    
    for sotd in lg_sotds:
        if '2020' in sotd.title:
            continue
        if 'SOTD' not in sotd.title:
            continue
        if 'Lather Games' not in sotd.title:
            continue
        sotd.comments.replace_more(limit=None)
        for comment in sotd.comments: 
            try:
                lg_participants.add(comment.author.name)
                print(len(lg_participants))
            except:
                pass
            
    for redditor in sorted(lg_participants):
        print(redditor)
        