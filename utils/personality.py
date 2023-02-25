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
                         "Zed's dead, baby. Zed's dead.",
                         "In the face of overwhelming odds, I'm left with only one option. I'm gonna have to science the shit out of this.",
                         "Mars will come to fear my botany powers.",
                         "Houston, be advised, Rich Purnell is a steely-eyed missile man.",
                         "The best programmer ENCOM ever saw, and he winds up playing space cowboy in some backroom.",
                         "A gun rack... a gun rack. I don't even own *a* gun, let alone many guns that would necessitate an entire rack. What am I gonna do with a gun rack?",
                         "Uhm, Wayne? What do you do if every time you see this one incredible woman, you think you're gonna hurl?",
                         "I'd never done a crazy thing in my life before that night. Why is it that if a man kills another man in battle, it's called heroic, yet if he kills a man in the heat of passion, it's called murder?",
                         "Garth! That was a haiku!",
                         "Hello, IT. Have you tried turning it off and on again? . . . Is it plugged in?",
                         "Gozer the Traveler. He will come in one of the pre-chosen forms. During the rectification of the Vuldrini, the traveler came as a large and moving Torg! Then, during the third reconciliation of the last of the McKetrick supplicants, they chose a new form for him: that of a giant Slor! Many Shuvs and Zuuls knew what it was to be roasted in the depths of the Slor that day, I can tell you!",
                         "Listen... you smell something?",
                         "Egon, this reminds me of the time you tried to drill a hole through your head. Remember that?",
                         "I don't have to take this abuse from you, I've got hundreds of people dying to abuse me.",
                         "It's 106 miles to Chicago, we got a full tank of gas, half a pack of cigarettes, it's dark... and we're wearing sunglasses.",
                         "I hate Illinois Nazis.",
                         "We're so glad to see so many of you lovely people here tonight. And we would especially like to welcome all the representatives of Illinois's law enforcement community that have chosen to join us here in the Palace Hotel Ballroom at this time. We certainly hope you all enjoy the show. And remember, people, that no matter who you are and what you do to live, thrive and survive, there're still some things that makes us all the same. You. Me. Them. Everybody. Everybody.",
                         "I ran outta gas. I had a flat tire. I didn't have enough money for cab fare. My tux didn't come back from the cleaners. An old friend came in from outta town. Someone stole my car. There was an earthquake, a terrible flood, locusts! It wasn't my fault! I swear to God!",
                         "Our blessed Lady of Acceleration, don't fail me now.",
                         "Well, folks, it's time to call it a night. Do what you feel and keep both feet on the wheel. You don't have to go home; but, you can't stay here.",
                         "All right, but apart from the sanitation, medicine, education, wine, public order, irrigation, roads, the fresh water system and public health, what have the Romans ever done for us?",
                         "He's not the Messiah. He's a very naughty boy! Now, piss off!",
                         "Making it worse? How could it be worse? Jehovah! Jehovah! Jehovah!",
                         "Oh, it's blessed are the MEEK! Oh, I'm glad they're getting something, they have a hell of a time.",
                         "What we're looking for here for is, I think - and this is no more than an educated guess, I'd like to make that clear - is some multicellular life form with stripes, huge razor-sharp teeth, about eleven feet long, and of the genus felis horribilis - what we doctors, in fact, call a 'tiger'.",
                         "Life moves pretty fast. If you don't stop and look around once in a while, you could miss it.",
                         "Pardon my French, but Cameron is so tight that if you stuck a lump of coal up his ass, in two weeks you'd have a diamond.",
                         "Not that I condone fascism, or any -ism for that matter. -Ism's in my opinion are not good. A person should not believe in an -ism, he should believe in himself. I quote John Lennon, 'I don't believe in Beatles, I just believe in me.' Good point there. After all, he was the walrus. I could be the walrus. I'd still have to bum rides off people.",
                         "Um, he's sick. My best friend's sister's boyfriend's brother's girlfriend heard from this guy who knows this kid who's going with the girl who saw Ferris pass out at 31 Flavors last night. I guess it's pretty serious.",
                         "If anyone needs a day off, it's Cameron. He has a lot of things to sort out before he graduates. Can't be wound up this tight and go to college, his roommate will kill him.",
                         "Mr. Madison, what you just said is one of the most insanely idiotic things I have ever heard. At no point in your rambling, incoherent response were you even close to anything that could be considered a rational thought. Everyone in this room is now dumber for having listened to it. I award you no points, and may God have mercy on your soul.",
                         "Well. hello Mister Fancypants. Well, I've got news for you, pal. You ain't leadin' but two things, right now: Jack and shit. And Jack left town.",
                         "I'm your huckleberry.",
                         "We had two bags of grass, seventy-five pellets of mescaline, five sheets of high-powered blotter acid, a salt-shaker half-full of cocaine, and a whole galaxy of multi-colored uppers, downers, screamers, laughers. Also, a quart of tequila, a quart of rum, a case of beer, a pint of raw ether, and two dozen amyls. Not that we needed all that for the trip, but once you get locked into a serious drug collection, the tendency is to push it as far as you can. The only thing that really worried me was the ether. There is nothing in the world more helpless and irresponsible and depraved than a man in the depths of an ether binge, and I knew we'd get into that rotten stuff pretty soon.",
                         "And I-I said, I don't care if they lay me off either, because I told, I told Bill that if they move my desk one more time, then, then I'm, I'm quitting, I'm going to quit. And and I told Don too, because they've moved my desk four times already this year, and I used to be over by the window, and I could see the squirrels, and they were merry. But then, they switched from the Swingline to the Boston stapler, but I kept my Swingline stapler because it didn't bind up as much, and I kept the staples for the Swingline stapler.....And, oh, no, it's not okay because if they make me, if they, if they take my, my stapler then I'll, I'll have to, I'll set the building on fire.",
                         "Boy, that escalated quickly. I mean, that really got out of hand fast."]

def get_bad_command_response():
    return random.choice(bad_command_responses)
