# The Story of Us — Full Script

Every voice line in the game, in story order. Auto-generated from `config.py` (`STORY_WEEKS`). Speakers in **bold**; *italics* = narration / on-screen text; → = a player choice or chat topic.

---

## 1 — Week 1

### check_baskets  — *objective: Check the ball baskets*

> *Thursday evening. The sports hall hums with the*

> *squeak of fresh trainers on the floor.*

> *Sarah and Nat walk in through the doors.*

**Nat:** So... what's the plan?

**Sarah:** Let's grab a volleyball and warm up.

**Sarah:** There should be one in the ball baskets.

**Nat:** I'm gonna go get changed.

*(blocked)*

> *Grab a ball first — check the baskets.*

*(if more to do)*

> *You check the basket.*

> *It is entirely empty.*

> *What did you expect to find in there?*

*(when all done)*

> *You check the basket.*

> *The void stares back at you.*

> *Is this your first day at GoMammoth?*

*(already done)*

> *You already checked this one — still empty.*

### leonard_offer

**Leonard:** Hey, ve haf a ball, you can come play mit us!

**Leonard:** I am tall und I am also German

**James:** ...

### vb_setup

**Dan:** Alright, alright, let's get this party started!

**Dan:** You ready?  *(choice)*

  → choose **“Warm-up”**

**    Dan:** Sweet ok.

**    Dan:** It's finally my time to shine.

  → choose **“Jump right in”**

**    Dan:** Sweet ok.

**    Dan:** It's finally my time to shine.

### gym_match  — *objective: Win the 3v3*

*(no dialogue — gameplay / transition)*

### pub_invite

**Leonard:** GG, everyone! I must away — auf Wiedersehen!

> *(He is never seen again.)*

**Dan:** Good game!

**Dan:** Hey, wanna go to the pub?  *(choice)*

  → choose **“Sure”**

  → choose **“Not today”**

    > *That's not what happened, dummy.*

    > *You lose, I guess.*

    > *...let's run that back.*

### walk_to_pub  — *objective: Head to The Salutation*

*(blocked door)*

> *This isn't The Salutation — wrong pub!*

### pub_queue  — *objective: Get a round in*

> *The whole team piles into The Salutation.*

**Dan:** Could I have one million beers please.

**Dan:** James?

**James:** Um yeah sure, me too

**Milla:** And for you?

  → choose **“Cider”**

  → choose **“White Wine”**

  → choose **“Red Wine”**

**Milla:** Coming right up.

**James:** Hey, is that any good?

  → choose **“Yeah”**

  → choose **“Nope”**

**    James:** Damn, sucks to be you I guess.

**    James:** Don't know what you expected from pub wine tbh.

### gifts

**Matt:** Hey guys.

**Matt:** I got you guys stuff from Comic-Con!

**James:** Oh! Really? (...)

**Matt:** For you, James:

> *Matt rummages around in his bag.*

**Matt:** Here ya go!

> *Matt hands over two large anime figurines.*

**James:** (Dawg I'm actually being set up right now)

**James:** ... Hey, thanks man! This is really cool.

**Matt:** And I got something for you too, Dan!

> *Matt pulls out a large anime poster.*

**Matt:** Kay, here ya go!

**Dan:** In front of the hoes?!

**James:** (LMAO OK, coulda been worse)

> *Dan looks to James, then back.*

**Dan:** Dude...thanks so much!

**Dan:** This is really thoughful of you

**Matt:** No problem, guys!

> *...*

### where_from

> *There's a brief lull in conversation...*

> *You feel a strong urge to fill it.*

> **(branching chat — player picks topics)**

  → topic **“In-ground pool”**

**    James:** Uhm, not to kill your vibe, but aren't all pools in the ground?  *(choice)*

      → choose **"That's just what they're called"**

          **    James:** Okay well I appreciate your honesty.

      → choose **"No"**

          **    James:** What kind of pool isn't in ground?  *(choice)*

              → choose **"Paddling pool"**

                  **  James:** I'll give you that but feels like a TKO

              → choose **"Infinity pool"**

**    James:** So you're rich rich huh?

  → topic **“Family”**

**    Sarah:** I'm the youngest of 5, and I have 5 nieces and nephews.

**    James:** Wow you must love kids so much  *(choice)*

      → choose **"I do"**

          **    James:** That's awesome, I'm sure we won't have any turbulence in our future related to you and kids.

      → choose **“I don't"**

          **    James:** (I wonder what she means by this? Oh well, no harm in leaving this open to interpretation)

  → topic **“Crazy family”**

**    Sarah:** My sister's in a legal battle with her ex-husband and her boyfriend sucks.

**    Sarah:** (Graphic detail follows)

**    James:** Wow. That's terrible.

**    James:** We just met today, you know that right?

### wind_down  — *objective: Say your goodbyes and head out*

> *You're feeling pretty tired.*

> *Might be time to head out.*

*(blocked door)*

> *It's time to go home.*

**James:** Hope I'll see you next week!

**Dan:** Peace out.

**Matt:** Laters! Good to see you.

**Nat:** Byee! Text me when you're home.

**Bailey:** See you!

**Mayu:** Bye bye!

**Wallace:** Bye

---

## 2 — Week 2

### w2_arrive

> *Week 2. Another wonderful evening of GoMammoth "volleyball"*

**Nat:** I'm gonna go get ready.

**Sarah:** (I should go say hi to everyone.)

### w2_greet  — *objective: Greet everyone*

**Dan:** Wagwan g.

**James:** Oh hey, what's up!

    → choose **"When are you playing?"**

        **    James:** Uhh that's a funny story.

    → choose **"Good evening handsome"**

        (Game over screen)
        > *James panicks and runs out the door, into the night.*

        > *You lose, I guess.*

        > *...let's run that back.*

**Nat:** Huh, where did Leonard get to today?

**Nat:** I'm sure we'll see him again.

**Matt:** Good evening, m'lady!

**Matt:** (Tips fedora.)

**Mayu:** Heyy! Good to see you again.

**Wallace:** Oh — hey!.

*(already done)*

> *...*

### w2_ready  — *objective: Talk to James when you're ready*

**James:** Oh by the way, everyone is slightly better at volleyball this week.

**James:** How come? Uhm the plot

**James:** Now that I've answered all your questions, are we ready to start?  *(choice)*

  → choose **“Yes”**

  → choose **“No”**

**    James:** Oh ok — come back when you're ready.

### w2_match  — *objective: Win the 3v3 (Medium)*

*(no dialogue — gameplay / transition)*

### w2_garden

> *The group heads round to the Salutation's beer garden and piles in around the big table.*

**James:** (I'm sitting next to Sarah...)

**James:** (I should try to make an effort)

**James:** So what do you do?  *(choice)*

  → choose **“I study at Imperial”**

**    James:** Oh, that's an awesome university

**    James:** Have you heard of UCL? That, on the other hand, is not an awesome university

**    James:** What are you studying?   *(choice)*

      → choose **Neuroscience**

**        James:** Bullshit.

**        James:** What am I thinking of right now.  *(choice)*

      → choose **That's not how it works.**

**        James:** Wrong, I was thinking of a banana.

      → choose **Banana.**

**        James:** Holy shit.

**James:** I'm somethnig of a scientist myself.

**James:** I worked a Biotech for 5 months. Then got fired lol  *(choice)*

      → choose **I'm working on my Western Blotting right now.**

**James:** Ooh you should explain it to me in excruciating detail

> *(Half an hour passes. They discussed Western Blotting.)*

**James:** Okay okay! Did I get it? *(choice)*

  → choose **“Not really”**

  → choose **"Definitely not”**

**James:** Welp. I tried.

**Milla:** Hey guys — time to come inside!

### w2_inside

> *Inside, everyone settles into the booth, two rows facing.*

**James:** Yeah, I actually speak pretty good French.

**James:** I'm doing a course on Mondays to keep it up.

> *( ! )  Nat's head snaps round.*

**Nat:** Oh really? I'm from Martinique!

**James:** So... you speak fluent French.

**Nat:** Native.

**James:** ... did I say fluent French? What I actually meant, was uh

> *James slowly backs away...*

> *...and bolts out the door.*

(The power of undercooked chicken courses through your veins)

**Sarah:** (Damn I feel awful.)

**Sarah:** (I think I'll head home.)

### w2_homeward  — *objective: Head home*

*(no dialogue — gameplay / transition)*

---

## 2 — Interlude — First Contact

### scrims_texts  — *7 June 2024*

— *7 Jun 2024* —

**James:** Hiii Sarah 👋  
      
    I play w a social team most Saturdays, and when we don't have a league game we organise scrims to get some reps in.  
      
    We're short one outside for tmz if you want to come? 👀

**James:** Next session 8 June (Saturday)  
      
    🕐 Time: 12:00 - 3:00pm (3 hours)  
      
    🎉 Signup: 1drv.ms/x/c/8eb19810...JjpLA  
      
    📍 Location: Wembley, Preston Manor High School - maps.app.goo.gl/qTzHvhym  
      
    💸 Price for 3 hrs: £11.57

**James:** This is all the details  _(reaction: ❤)_

**Sarah:** yea alr i had no plans

**Sarah:** do u want me to put my name down on this sheet or how do i do this

**James:** Yes pls

**Sarah:** ... in number 8 i assume

**James:** Yea yea

**James:** Sry its a very confusing document lol

**Sarah:** omg no worried i just didnt wanna fuck up yalls system

**James:** If the template broke I would probably cry

**James:** But we have a million copies so it's ok

**Sarah:** see thats what we dont want  _(reaction: 🙏)_

**Sarah:** no tears today

**Sarah:** also who do i pay or do i pay there

**James:** Friday cryday  _(reaction: 🫡)_

**James:** After the sesh I'll send a msg np

**Sarah:** 🫡

**Sarah:** yes captain

**James:** See u tmrr  _(reaction: ❤)_

**Sarah:** HEY so this is just a warning, i hope ill feel better tomorrow but i ate some bad chicken and have been quite sick today, i thought it would pass but it hasnt yet so just a warning for tomorrow, im so sorry in advance if im too sick to make it (im praying that wont be the case)  _(reaction: 😢)_

**James:** Hey hey Sarahh

**James:** Okay

**James:** Rest up sleep good

**James:** And come tmz if you can 🙏

— *8 Jun 2024* —

**James:** Hey how are you feeling?

**Sarah:** Much better!

**Sarah:** I didnt mean to worry u lol it was just a failsafe text so if i had to miss out i wouldnt come off as much as a dick lol

**Sarah:** thanks for inviting me btw i had sm fun! Also how to do pay?

**James:** Hey hey I'm glad, this session was rly good

**James:** There's a group that we organise in, I can add you?  _(reaction: ❤)_

**James:** Since I'll send payment details there anyway

**Sarah:** sounds good!

**James:** You are added 🫡  _(reaction: 👍)_

**Sarah:** Appreciated my friend

**Sarah:** 🙌

---

## 3 — Week 3

### w3_arrive

> *Week 3. Sarah heads into the sports hall...*

> *...and finds James flat on the floor.*

**James:** Huh? Am I okay?

**James:** Do I look like okay?!

**James:** ...yea, of course I am.

**James:** I kinda realised, watching you at scrims, that I suck at diving.

**Sarah:** ...  *(choice)*

  → choose **“I can teach you”**

  → choose **“Sucks to be you”**

**    James:** Dude, what the hell.

**    James:** Can you help me out pls?

**    Sarah:** ...  *(choice)*

      → choose **“Yes”**

      → choose **“Fine, ok”**

**James:** Awesome!

**James:** Let's give it a go...

### w3_dive  — *objective: Teach James to dive*

*(no dialogue — gameplay / transition)*

### w3_postdive

**James:** Thanks! I feel less scared to dive now.

**James:** Not sure I actually got any better.

**James:** But that's a problem for another day.

**Matt:** Are you guys gonna come play?!

**James:** (Oh yeah.)

**James:** Oh yeah, the difficulty went up again lol.

**James:** So good luck with that.

### w3_match  — *objective: Win the 3v3 (Hard)*

*(no dialogue — gameplay / transition)*

### w3_garden

> *Afterwards the group pack into the garden's top-right booth.*

**Matt:** Hm? Your family's visiting in two weeks?

**Sarah:** ...  *(choice)*

  → choose **“Yeah, they'll watch you guys play”**

  → choose **“Yeah, to watch you lot suck at it”**

**    James:** (Ouch.)

**Dan:** I'm sure they're going to be...

**Dan:** ...very entertained by what they see.

**James:** Too right.

> *(Sarah's stomach turns. Oh no. Not again.)*

**Matt:** Are you feeling ok?

> *(Blasted chicken.)*

**James:** Damn, no worries.

**James:** Have a good night — see ya next week!

> *Sarah slips out and heads home.*

### w3_spoons

> *(Meanwhile — James, Dan, Nat and Matt carry on to Wetherspoons.)*

**Dan:** So... who's Sarah interested in?

**Nat:** You can't tell anyone.

**Dan:** Of course, of course.

**James:** ...

**Nat:** Do you know Leonard?

**James:** ...

**James:** Who the hell is Leonard?

**Nat:** He's tall and also German.

**James:** I have literally never met this guy before.

**Dan:** The guy that made us run round in circles the first week?

**James:** Oh, nvm, I do know that guy.

**James:** ...

**James:** I'm gonna grab another drink.

**Matt:** Me too.

**Matt:** Hey man.

**James:** Yo.

**Matt:** What do you think about that whole Leonard thing?

**James:** Idk dude. Good for her?

**Matt:** Were you interested in her as well?

**James:** No, no — not really.

**Matt:** Well, between you and me, I think this might be for the best.

**Matt:** We don't want something silly like this coming between two bros, y'know.

**James:** Lol, for sure man.

**Matt:** Let's make a pact.

**Matt:** Neither of us asks Sarah on a date, and we both just keep on going with everything.

**James:** A pact?

**James:** ...

**James:** ...sure?

**Matt:** Sweet — this is a good thing, trust me.

**James:** (...okay.)

### w3_end

*(no dialogue — gameplay / transition)*

---

## 4 — Week 4

### w4_arrive

> *Week 4. The season finale.*

> *Sarah walks into the sports hall.*

> *( ! )  Dan waves her over.*

**Dan:** Hey! Final game of the season today.

**Dan:** Good luck — you're gonna need it.

**Sarah:** ...  *(choice)*

  → choose **“Are we on the same team?”**

**    Dan:** Tbf, I have no idea.

  → choose **“I'll see u on the court, sport”**

**    Dan:** That was a pretty lame response.

**    Dan:** Surprised that's the best you could come up with.

**    Dan:** Really not a lot of creativity on display.

### w4_greet  — *objective: Speak to everyone before the final*

**Bailey:** I don't even really like volleyball that much.

**Bailey:** Being here is fun tho.

**Matt:** Oh... hi.

**Matt:** (Nervously shuffles away.)

**Wallace:** Hey hey hey.

**Wallace:** Good luck today!

**Wallace:** ...that rhymed.

*(already done)*

> *...*

### w4_ready  — *objective: Talk to James when you're ready*

**James:** Oh hey, what's up... friend.

**James:** ...

**James:** Let's have fun playing. See ya.

**James:** Let's have fun playing — ready?  *(choice)*

  → choose **“Yes”**

  → choose **“No”**

**    James:** Oh, ok. Come find me when you're ready.

**James:** Let's have fun playing — ready?  *(choice)*

  → choose **“Yes”**

  → choose **“No”**

**    James:** Oh, ok. Come find me when you're ready.

### w4_match  — *objective: Win the final (INSANE)*

*(no dialogue — gameplay / transition)*

### w4_trophy

> *The whistle goes — game, set, season!*

> *Champions. Someone produces a slightly dented trophy.*

> *(You hoist it anyway. Glorious.)*

### w4_garden

**Dan:** Is Matt not coming to the pub tonight?

**James:** I guess not.

**James:** (...wonder why lol.)

> *The group pack into the garden's top-right booth.*

> *James is last out. He walks over, pauses...*

**Dan:** ...

**Dan:** Hey, what's good dude.

**Dan:** I actually wanted to sit over there.

**Dan:** Let's swap places.

**James:** (Dawg, what the hell.)

**James:** Uhmmm, no — I'm comfy now.

**James:** Thanks though.

> *(An uncomfortable silence. Someone stretches.)*

**Wallace:** Sooo... what the hell was up with Matt Endicott today?

> *(The group laughs. James looks relieved.)*

**Sarah:** Yeah, I don't know what happened???

**Sarah:** He asked me out, like, late on Thursday last week.

**Dan:** Oh yeah. I thiiiink I know what mighta happened there.

**James:** Yeah we, uh, ended up at Spoons.

**James:** He kinda brought up that he wasn't gonna do that.

**James:** Which was a weirdly specific thing to say, I guess.

**Sarah:** Yeah, honestly, for the best.

**Sarah:** The LAST thing I wanna do right now is date again.

**James:** (...oh.)

**Sarah:** My last boyfriend was super abusive. And, even worse...

**Sarah:** he was "French".

**James:** Wow. This guy sounds awful.

**Sarah:** Yeah. I can't even go to Canary Wharf anymore, in case I run into him.

**James:** I'll beat him up for you.

**Sarah:** He's super tall and he did kickboxing.

**James:** I willll talk shit to him.

**James:** From a safe distance.

**Milla:** Time to come inside, guys — sorry lol.

### w4_inside

> *Inside, James and Dan look at each other.*

**Dan:** Another drink?

**James:** Yeah.

**James:** That would be real good.

> *(Dan downs his drink.)*

**Dan:** Don't worry bro. I got you.

**James:** Wait.

**James:** What — did I miss something?

**Dan:** I'll brb.

**Dan:** Yo Sarah, can I pull you for a chat?

**James:** (OH BOY.)

**Sarah:** Oh, sure.

> *(Some time passes.)*

**James:** What happened man?????

**Dan:** Nothin' much, nothin' much.

**Dan:** Just went and laid it all out.

**James:** So??

**Dan:** I asked her:

**Dan:** What do ya think of ma boy James?

**James:** Dude, no way.

**James:** Is this High School Musical?

**Dan:** I guess so dude.

**James:** Listen man, I don't think-

**Sarah:** Hey, I'm heading out.

**James:** Oh, cool, okay.

**Sarah:** Dude, I have so many dishes at home right now.

**James:** That's a little dramatic.

**James:** They're just dishes.

**Sarah:** Yea, but I keep forgetting to wash them.

**Sarah:** Ok, listen here.

**Sarah:** I need you to remind me to do my dishes.

**Sarah:** Since you're soooo on top of this, apparently.

**James:** Okay yeah??? Easy.

**Sarah:** Sweet.

**Sarah:** See you later!

> *(Sarah leaves.)*

**James:** Huh.

**James:** What was that about?

**James:** (She clearly said she wasn't interested... so...)

### w4_end

*(no dialogue — gameplay / transition)*

---

## 4 — Interlude — Something New

### something_new  — *21 June 2024*

— *21 Jun 2024* —

**James:** Uh

**James:** Sarah just asked me out

**Dan:** Fucking nice one bro!

**James:** Thanks again

**James:** For this

**Dan:** It would've happened whether I got involved or not

**James:** Maybe

> 🔔 *push — Messages · 3m ago — Sarah Lenhoff: cant wait :)*

**James:** Aaaaaaaaaaahhh

**James:** First wk at work + date w Sarah

**James:** This has been a very good day

---

## 4 — Finale — The Date

### the_date  — *21 June 2024*

— *21 Jun 2024* —

**Sarah:** my dishes didnt get done before i left my apartment and its entirely ur fault 🙈

**James:** Fuck off

**James:** I'm writing the msg

**James:** I'm putting so much effort into it

**James:** Wait a sec

**Sarah:** YEA SURE

**James:** 🔊🔊🔊 ring ring ring 🔊🔊🔊  
    ⏰‼️🚨 DO Yur DISHES ⏰‼️🚨  
    🦠🦠 stay hygienic 🦠🦠  
    🧽🧽 scrub your dishes 🧽🧽  
    🇱🇧 this pride month 🇱🇧  
    💥👀 or i'll tell your mom 👀💥

**James:** It didn't work wait

**James:** There you go

**James:** How's that

**Sarah:** The Lebanese flag 💀💀

**Sarah:** im currently drinking at the pub so like still wont get done even with ur threat but thank u

**Sarah:** i thought ud forgotten about me :/

**James:** That's a little upsetting

**James:** Nah

**James:** I would never forget  _(reaction: ❤)_

**James:** I was only late cos I had to run to Hammersmith right after I finished work🫠

**Sarah:** mhm sure sounds like excuses to me

**James:** Fine fine

**James:** I'll remind you again

**James:** And it will be on time

**James:** When do you want it

**Sarah:** I have a better deal for u

**Sarah:** ill buy u dinner if u just appear at my apartment and do my dishes

**Sarah:** i really dont wan to do them

**Sarah:** if not then probs like 11 pm when im home lmao

**James:** That is a better deal

**James:** Not least bcos im going to run out creative alarm clock ideas quickly

**James:** I'm free tmr night but I'll be sweaty after volleyball

**James:** How long can ur dishes wait

**Sarah:** Im gonna use so many dishes in the mean time

**Sarah:** I have no plans tomorrow night so

**James:** I can get there before 8 I'm sure  _(reaction: ❤)_

**James:** What's your addy

**James:** Also would I be able to use ur shower rq? All good if not

**Sarah:** you can use my shower lol

**Sarah:** Ill be in the park anyways havin a picnic so no rush!

**Sarah:** cant wait :)

---

## Closing card

> *Thanks for playing.*

> *Here's to us. Happy anniversary.*
