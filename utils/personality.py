'''
Created on Feb 21, 2020

@author: rcurtis
'''
import random

bad_command_responses = ["My dude, I don't understand what you're trying to do.",
                         "Go home, you're drunk.",
                         "I'm sorry, Dave. I'm afraid I can't do that.",
                         "Error between keyboard and chair.",
                         "Houston, we have a problem.",
                         "You talkin' to me?",
                         "Pajeet that shit!",
                         "Look at these idiots. Just sitting there, covered in lather at a desk, soap all over the table.",
                         "god dam. I thought Reddit was supposed to have intelligent people.",
                         "Life is too short and there are too many good soaps to bother trying to make a shitty one work."]

def get_bad_command_response():
    return random.choice(bad_command_responses)