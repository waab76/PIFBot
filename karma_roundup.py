'''
Created on Feb 2, 2021

@author: rcurtis
'''

from utils.reddit_helper import reddit, subreddit
from utils.karma_calculator import calculate_karma

def get_user_list():
    user_list = set()
    
    sotd_posts = subreddit.search(query="SOTD", sort="new", time_filter="month")
    
    for post in sotd_posts:
        post.comment_sort = 'new'
        post.comments.replace_more(limit=0)
        comments = post.comments.list()
        for comment in comments:
            try:
                user_list.add(comment.author.name)
            except:
                pass
    
    return user_list

if __name__ == '__main__':
    
    print('user,karma,submissions,comments')
    
    user_list = get_user_list()
    
    for user in user_list:
        user_karma = calculate_karma(reddit.redditor(user))
        print('%s,%s,%s,%s' % (user, user_karma[0], user_karma[1], user_karma[2]))
        