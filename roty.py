'''
Created on Jun 1, 2020

@author: rcurtis
'''
from utils.reddit_helper import subreddit

if __name__ == '__main__':
    lg_sotds = subreddit.search(query="Lather Games SOTD", sort="new", time_filter="day")
    
    for sotd in lg_sotds:
        if 'SOTD' not in sotd.title:
            continue
        if 'Lather Games' not in sotd.title:
            continue
        
        print(sotd.title)
        
        sotd.comments.replace_more(limit=None)
        lg_participants = set()
        for comment in sotd.comments: 
            try:
                lg_participants.add(comment.author.name)
            except:
                pass
            
        for redditor in sorted(lg_participants):
            print(redditor)
        