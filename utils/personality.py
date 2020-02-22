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
                         "Pajeet that shit!"]

def get_bad_command_response():
    return random.choice(bad_command_responses)