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
                         "Life is too short and there are too many good soaps to bother trying to make a shitty one work.",
                         ".grab shavebutt",
                         "this fetish doesn't appear to align with my personal ones.",
                         "I got an idea for a video series. We'll find an idiot. Then we'll just let him shave. That's as far as I got.",
                         " I’m an idiot but I’m not that much of an idiot ",
                         "I hope that dude is hot enough to be this dumb...",
                         "we have to be THE dumbest channel on IRC"]

def get_bad_command_response():
    return random.choice(bad_command_responses)