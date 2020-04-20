#!/usr/bin/env python3
# coding: utf-8
#
#   File = random.py
#
#      Copyright 2020 Rob Curtis
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
############################################################################
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
                         "we have to be THE dumbest channel on IRC",
                         "I never knew what a friend was until I met Geordi. He spoke to me as though I were human. He treated me no differently from anyone else. He accepted me for what I am. And that, I have learned, is friendship.",
                         "With the first link, the chain is forged. The first speech censured, the first thought forbidden, the first freedom denied - chains us all irrevocably.",
                         "My positronic brain has several layers of shielding to protect me from power surges. It would be possible for you to remove my cranial unit and take it with you.",
                         "Shaka. When the walls fell.",
                         "Temba. His arms wide.",
                         "Sokath! His eyes uncovered!",
                         "Kiazi's children. Their faces wet.",
                         "Darmok and Jalad at Tenagra.",
                         "Shut up, Wesley!",
                         "Could you please continue the petty bickering? I find it most intriguing.",
                         "If winning is not important, then Commander, why keep score?",
                         "It is... it is...  ...it is green.",
                         "Your hesitation suggests you are trying to protect my feelings. However, since I have none, I would prefer you to be honest.",
                         "This is a very complicated case, Maude. You know, a lotta ins, lotta outs, lotta what-have-you's. And, uh, lotta strands to keep in my head, man. Lotta strands in old Duder's head. Luckily I'm adhering to a pretty strict, uh, drug regimen to keep my mind, you know, limber.",
                         "Fuck it, Dude. Let's go bowling.",
                         "Forget it, Donny, you're out of your element!",
                         "I never forget a face, but in your case I'll be glad to make an exception.",
                         "Time flies like an arrow. Fruit flies like a banana.",
                         "You know I could rent you out as a decoy for duck hunters.",
                         "Gentlemen, Chicolini here may talk like an idiot, and look like an idiot. But don't let that fool you. He really is an idiot.",
                         "And there shall in that time be rumours of things going astray, and there will be a great confusion as to where things really are, and nobody will really know where lieth those little things with the sort of raffia work base, that has an attachment…at this time, a friend shall lose his friend’s hammer and the young shall not know where lieth the things possessed by their fathers that their fathers put there only just the night before around eight o’clock...",
                         "Listen. Strange women lying in ponds distributing swords is no basis for a system of government. Supreme executive power derives from a mandate from the masses, not from some farcical aquatic ceremony.",
                         "I don't want to talk to you no more, you empty-headed animal food trough wiper! I fart in your general direction! Your mother was a hamster and your father smelt of elderberries!",
                         "Zed's dead, baby. Zed's dead."]

def get_bad_command_response():
    return random.choice(bad_command_responses)