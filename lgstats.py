'''
Created on Jun 28, 2021

@author: rcurtis
'''

import re
from utils.subreddit_helper import subreddit

title_pattern = re.compile('.*Lather Games SOTD Thread.*2021')
sotd_pattern = re.compile('.*Lather:.*')
posts = subreddit.search(query="Lather Games SOTD Thread 2021", sort="new", time_filter="all")
shave_count = 0
shavers = set()


for post in posts:
    if title_pattern.match(post.title):
        print(post.title)
        post.comment_sort = 'new'
        post.comments.replace_more(limit=0)
        sotds = post.comments.list()
        sotd_count = 0
        for sotd in sotds:
            if sotd.parent_id.startswith('t3_'):
                try:
                    sotd_count += 1
                    shave_count += 1
                    shavers.add(sotd.author.name)
                except:
                    pass
        print('{} shaves'.format(sotd_count))
            
print('{} shaves from {} unique shavers'.format(shave_count, len(shavers)))