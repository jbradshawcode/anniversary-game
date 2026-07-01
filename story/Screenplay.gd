# The screenplay — all narrative content, as data. Faithful port of
# story_script.py: the ordered STORY_WEEKS beats with inline cutscene scripts, the
# phone/text interludes + finale, and the post-night phone threads. Flattened and
# interpreted by StoryManager; cutscene steps are run by Cutscene. No engine
# constants belong here. Tuples -> Arrays, tiles -> Vector2i, dicts -> Dictionary.
class_name Screenplay
extends RefCounted


# Week 2's "ready to start?" prompt — fired both automatically (after the greeting)
# and on talking to James again, so declining lets you wander back to him.
static func _w2_ready_ask() -> Array:
	return [
		["ask", "Now that I've answered all your questions, are we ready to start?", {
			"Yes": ["flag", "w2_ready_done"],
			"No": [["say", ["Oh ok — come back when you're ready."], "James"]],
		}, "James"],
	]


static func _w4_ready_ask() -> Array:
	return [
		["ask", "Let's have fun playing — ready?", {
			"Yes": ["flag", "w4_ready_done"],
			"No": [["say", ["Oh, ok. Come find me when you're ready."], "James"]],
		}, "James"],
	]


# Interlude (9th June, between Ch2 and Ch3) — James invites Sarah to scrims.
# POV: James's phone, so James is the "me" (right) side, Sarah on the left.
static func _interlude_scrims() -> Array:
	return [
		{"sep": "7 Jun 2024"},
		{"who": "James", "text": "Hiii Sarah 👋\n\n"
			+ "I play w a social team most Saturdays, and when we "
			+ "don't have a league game we organise scrims to get "
			+ "some reps in.\n\n"
			+ "We're short one outside for tmz if you want to come? 👀"},
		{"who": "James", "text": "Next session 8 June (Saturday)\n\n"
			+ "🕐 Time: 12:00 - 3:00pm (3 hours)\n\n"
			+ "🎉 Signup: 1drv.ms/x/c/8eb19810...JjpLA\n\n"
			+ "📍 Location: Wembley, Preston Manor High School - maps.app.goo.gl/qTzHvhym\n\n"
			+ "💸 Price for 3 hrs: £11.57"},
		{"who": "James", "text": "This is all the details", "react": "❤"},
		{"who": "Sarah", "text": "yea alr i had no plans"},
		{"who": "Sarah", "text": "do u want me to put my name down on this sheet or how do i do this"},
		{"who": "James", "text": "Yes pls"},
		{"who": "Sarah", "text": "... in number 8 i assume"},
		{"who": "James", "text": "Yea yea"},
		{"who": "James", "text": "Sry its a very confusing document lol"},
		{"who": "Sarah", "text": "omg no worried i just didnt wanna fuck up yalls system"},
		{"who": "James", "text": "If the template broke I would probably cry"},
		{"who": "James", "text": "But we have a million copies so it's ok"},
		{"who": "Sarah", "text": "see thats what we dont want", "react": "🙏"},
		{"who": "Sarah", "text": "no tears today"},
		{"who": "Sarah", "text": "also who do i pay or do i pay there"},
		{"who": "James", "text": "Friday cryday", "react": "🫡"},
		{"who": "James", "text": "After the sesh I'll send a msg np"},
		{"who": "Sarah", "text": "🫡"},
		{"who": "Sarah", "text": "yes captain"},
		{"who": "James", "text": "See u tmrr", "react": "❤"},
		{"who": "Sarah", "text": "HEY so this is just a warning, i hope ill feel "
			+ "better tomorrow but i ate some bad chicken and have "
			+ "been quite sick today, i thought it would pass but it "
			+ "hasnt yet so just a warning for tomorrow, im so sorry "
			+ "in advance if im too sick to make it (im praying that "
			+ "wont be the case)", "react": "😢"},
		{"who": "James", "text": "Hey hey Sarahh"},
		{"who": "James", "text": "Okay"},
		{"who": "James", "text": "Rest up sleep good"},
		{"who": "James", "text": "And come tmz if you can 🙏"},
		{"sep": "8 Jun 2024"},
		{"who": "James", "text": "Hey how are you feeling?"},
		{"who": "Sarah", "text": "Much better!"},
		{"who": "Sarah", "text": "I didnt mean to worry u lol it was just a failsafe "
			+ "text so if i had to miss out i wouldnt come off as "
			+ "much as a dick lol"},
		{"who": "Sarah", "text": "thanks for inviting me btw i had sm fun! Also how to do pay?"},
		{"who": "James", "text": "Hey hey I'm glad, this session was rly good"},
		{"who": "James", "text": "There's a group that we organise in, I can add you?", "react": "❤"},
		{"who": "James", "text": "Since I'll send payment details there anyway"},
		{"who": "Sarah", "text": "sounds good!"},
		{"who": "James", "text": "You are added 🫡", "react": "👍"},
		{"who": "Sarah", "text": "Appreciated my friend"},
		{"who": "Sarah", "text": "🙌"},
	]


# Interlude (21st June, after Ch4) — James tells Dan the news. POV: James's phone.
static func _interlude_something_new() -> Array:
	return [
		{"sep": "21 Jun 2024"},
		{"who": "James", "text": "Uh"},
		{"who": "James", "text": "Sarah just asked me out"},
		{"who": "Dan", "text": "Fucking nice one bro!"},
		{"who": "James", "text": "Thanks again"},
		{"who": "James", "text": "For this"},
		{"who": "Dan", "text": "It would've happened whether I got involved or not"},
		{"who": "James", "text": "Maybe"},
		{"who": "James", "notif": {"app": "Messages · 3m ago", "title": "Sarah Lenhoff",
			"body": "cant wait :)"}},
		{"who": "James", "text": "Aaaaaaaaaaahhh"},
		{"who": "James", "text": "First wk at work + date w Sarah"},
		{"who": "James", "text": "This has been a very good day"},
	]


# Finale (21st June) — the dishes saga that becomes the date. POV: James <-> Sarah.
static func _finale_the_date() -> Array:
	return [
		{"sep": "21 Jun 2024"},
		{"who": "Sarah", "text": "my dishes didnt get done before i left my apartment "
			+ "and its entirely ur fault 🙈"},
		{"who": "James", "text": "Fuck off"},
		{"who": "James", "text": "I'm writing the msg"},
		{"who": "James", "text": "I'm putting so much effort into it"},
		{"who": "James", "text": "Wait a sec"},
		{"who": "Sarah", "text": "YEA SURE"},
		{"who": "James", "text":
			"🔊🔊🔊 ring ring ring 🔊🔊🔊\n"
			+ "⏰‼️🚨 DO Yur DISHES ⏰‼️🚨\n"
			+ "🦠🦠 stay hygienic 🦠🦠\n"
			+ "🧽🧽 scrub your dishes 🧽🧽\n"
			+ "🇱🇧 this pride month 🇱🇧\n"
			+ "💥👀 or i'll tell your mom 👀💥"},
		{"who": "James", "text": "It didn't work wait"},
		{"who": "James", "text": "There you go"},
		{"who": "James", "text": "How's that"},
		{"who": "Sarah", "text": "The Lebanese flag 💀💀"},
		{"who": "Sarah", "text": "im currently drinking at the pub so like still wont "
			+ "get done even with ur threat but thank u"},
		{"who": "Sarah", "text": "i thought ud forgotten about me :/"},
		{"who": "James", "text": "That's a little upsetting"},
		{"who": "James", "text": "Nah"},
		{"who": "James", "text": "I would never forget", "react": "❤"},
		{"who": "James", "text": "I was only late cos I had to run to Hammersmith right "
			+ "after I finished work🫠"},
		{"who": "Sarah", "text": "mhm sure sounds like excuses to me"},
		{"who": "James", "text": "Fine fine"},
		{"who": "James", "text": "I'll remind you again"},
		{"who": "James", "text": "And it will be on time"},
		{"who": "James", "text": "When do you want it"},
		{"who": "Sarah", "text": "I have a better deal for u"},
		{"who": "Sarah", "text": "ill buy u dinner if u just appear at my apartment and do my dishes"},
		{"who": "Sarah", "text": "i really dont wan to do them"},
		{"who": "Sarah", "text": "if not then probs like 11 pm when im home lmao"},
		{"who": "James", "text": "That is a better deal"},
		{"who": "James", "text": "Not least bcos im going to run out creative alarm clock ideas quickly"},
		{"who": "James", "text": "I'm free tmr night but I'll be sweaty after volleyball"},
		{"who": "James", "text": "How long can ur dishes wait"},
		{"who": "Sarah", "text": "Im gonna use so many dishes in the mean time"},
		{"who": "Sarah", "text": "I have no plans tomorrow night so"},
		{"who": "James", "text": "I can get there before 8 I'm sure", "react": "❤"},
		{"who": "James", "text": "What's your addy"},
		{"who": "James", "text": "Also would I be able to use ur shower rq? All good if not"},
		{"who": "Sarah", "text": "you can use my shower lol"},
		{"who": "Sarah", "text": "Ill be in the park anyways havin a picnic so no rush!"},
		{"who": "Sarah", "text": "cant wait :)"},
	]


# ── Post-night phone threads, shown after each week's results card (James <-> Dan).
static func phone_thread(week: int) -> Array:
	match week:
		1:
			return [
				{"who": "Dan", "shot_me": "Dan", "caption": "Dan sent a screenshot", "shot": [
					["Matt", "Yesterday I overheard you telling a guy to turn the oven "
						+ "on and leave a rug in the room?? what was that about"],
					["Matt", "I forgot to ask you to clarify... was that you talking "
						+ "about the SIMS game??"],
					["Dan", "😂😂😂"],
				]},
				{"who": "James", "text": "lol"},
				{"who": "Dan", "text": "He makes me laugh", "react": "👍"},
				{"who": "James", "notif": {
					"app": "Santander", "title": "You have a new insight",
					"body": "Quick Quiz! What did you spend at THE SALUTATION?"}},
				{"who": "Dan", "text": "Nah whaattttttt 😂😂😂"},
				{"who": "Dan", "text": "That should be illegal"},
				{"who": "James", "text": "Santander want the smoke", "react": "😂"},
				{"who": "James", "text": "I'm here 🥊🚫"},
			]
		2:
			return [
				{"who": "Dan", "text": "Me n Mayu just got off for like an hour"},
				{"who": "James", "text": "Lmao on fucking way"},
				{"who": "Dan", "text": "Don't tell anyone cus we promised not to tell anyone"},
				{"who": "Dan", "text": "And she specifically said James"},
				{"who": "James", "text": "Won't"},
				{"who": "Dan", "text": "But I can't not tell h"},
				{"who": "Dan", "text": "U"},
				{"who": "James", "text": "Real"},
				{"who": "Dan", "text": "For real you can't tell anyone"},
				{"who": "James", "text": "🤐"},
				{"who": "Dan", "text": "Told u I got it", "react": "👍"},
			]
		3:
			return [
				{"who": "Dan", "text": "Back at Natalia's place rn"},
				{"who": "James", "text": "Huh"},
				{"who": "James", "text": "All good?"},
				{"who": "Dan", "text": "Ye"},
				{"who": "Dan", "text": "Slept with her"},
				{"who": "James", "text": "Say ong"},
				{"who": "Dan", "text": "Ong"},
				{"who": "James", "notif": {
					"app": "Messages · 18m ago",
					"title": "Matthew Endicott",
					"body": "I asked out Sarah. She said no. I apologise for going back on what "
						+ "I said last night, I apologise for that. Just to be clear I am not "
						+ "apologising for asking her out, I am apologising for going back on "
						+ "my word yesterday when I said I wouldn't. At the end of"}},
				{"who": "James", "text": "Can't have a normal night out 😭😭"},
				{"who": "Dan", "text": "Fucking hell man 😂😂😂😂"},
				{"who": "Dan", "text": "Fuck spoons"},
				{"who": "Dan", "text": "Nah how can someone do a full 180 like that 😭"},
			]
		4:
			return [
				{"who": "Dan", "text": "Hiya"},
				{"who": "Dan", "text": "Upon reflection"},
				{"who": "Dan", "text": "Natalia asked if I like Sarah"},
				{"who": "Dan", "text": "You asked if Sarah likes me"},
				{"who": "Dan", "text": "Good form"},
				{"who": "Dan", "text": "Thanks"},
			]
	return []


static func weeks() -> Array:
	return [_week1(), _week2(), _interlude_first_contact(), _week3(), _week4(),
		_interlude_something_new_week(), _finale_week()]


static func _week1() -> Dictionary:
	return {
		"week": 1, "title": "Week 1",
		"beats": [
			{
				"name": "check_baskets",
				"objective": "Check the ball baskets",
				"locked_exits": {1: "all"},
				"cutscene": [
					["fade_in", 1.2],
					["say", ["Thursday evening. The sports hall hums with the",
						"squeak of fresh trainers on the floor."]],
					["say", ["Sarah and Nat walk in through the doors."]],
					["say", ["So... what's the plan?"], "Nat"],
					["say", ["Let's grab a volleyball and warm up.",
						"There should be one in the ball baskets."], "Sarah"],
					["say", ["I'm gonna go get changed."], "Nat"],
					["walk", "nat", Vector2i(2, 1)],
					["walk", "nat", Vector2i(2, 3)],
					["walk", "nat", Vector2i(1, 3)],
					["sit", "nat", "right"],
				],
				"checklist": {
					Vector2i(2, 7): {"flag": "w1_basket_near", "lines": []},
					Vector2i(17, 7): {"flag": "w1_basket_far", "lines": []},
				},
				"check_more": ["You check the basket.",
					"It is entirely empty.",
					"What did you expect to find in there?"],
				"check_done": ["You check the basket.",
					"The void stares back at you.",
					"Is this your first day at GoMammoth?"],
				"checked_again": ["You already checked this one — still empty."],
				"advance_when": "w1_baskets_done",
				"locked_msg": ["Grab a ball first — check the baskets."],
			},
			{
				"name": "leonard_offer",
				"locked_exits": {1: "all"},
				"cutscene": [
					["say", ["Hey, ve haf a ball, you can come play mit us!"], "Leonard"],
					["say", ["I am tall und I am also German"], "Leonard"],
					["say", ["..."], "James"],
					["flag", "w1_leonard"],
				],
				"advance_when": "w1_leonard",
			},
			{
				"name": "vb_setup",
				"locked_exits": {1: "all"},
				"cutscene": [
					["say", ["Alright, alright, let's get this party started!"], "Dan"],
					["ask", "You ready?", {
						"Warm-up": [["flag", "w1_want_tut"],
							["say", ["Sweet ok.", "It's finally my time to shine."], "Dan"],
							["flag", "w1_vb_set"]],
						"Jump right in": [["say", ["Sweet ok.",
							"It's finally my time to shine."], "Dan"],
							["flag", "w1_vb_set"]],
					}, "Dan"],
				],
				"advance_when": "w1_vb_set",
			},
			{
				"name": "gym_match",
				"objective": "Win the 3v3",
				"launch_volleyball": true,
				"locked_exits": {1: "all"},
				"advance_when": "w1_won_vb",
			},
			{
				"name": "pub_invite",
				"locked_exits": {1: "all"},
				"cutscene": [
					["say", ["GG, everyone! I must away — auf Wiedersehen!"], "Leonard"],
					["vanish", "leonard", 1.3],
					["say", ["(He is never seen again.)"]],
					["move", {"dan": Vector2i(10, 2), "james": Vector2i(11, 3)}],
					["face", "sarah", "down"],
					["say", ["Good game!"], "Dan"],
					["ask", "Hey, wanna go to the pub?", {
						"Sure": ["flag", "w1_pub_yes"],
						"Not today": ["game_over", [
							"That's not what happened, dummy.",
							"You lose, I guess.",
							"...let's run that back."]],
					}, "Dan"],
				],
				"advance_when": "w1_pub_yes",
			},
			{
				"name": "walk_to_pub",
				"objective": "Head to The Salutation",
				"party": "form",
				"advance_on_enter": 3,
				"door_block": {10: ["This isn't The Salutation — wrong pub!"]},
				"locked_exits": {},
				"advance_when": "w1_at_pub",
			},
			{
				"name": "pub_queue",
				"objective": "Get a round in",
				"locked_exits": {3: ["left", "right"]},
				"cutscene": [
					["say", ["The whole team piles into The Salutation."]],
					["move", {"dan": Vector2i(10, 4), "james": Vector2i(9, 5), "sarah": Vector2i(8, 6),
						"matt": Vector2i(7, 6), "nat": Vector2i(6, 7), "bailey": Vector2i(5, 7),
						"mayu": Vector2i(4, 8), "wallace": Vector2i(3, 9)}],
					["walk", "milla", Vector2i(11, 3)],
					["face", "milla", "down"],
					["walk", "dan", Vector2i(10, 3)], ["face", "dan", "right"],
					["say", ["Could I have one million beers please.", "James?"], "Dan"],
					["say", ["Um yeah sure, me too"], "James"],
					["hold", "dan", "beer"], ["walkto", "dan", Vector2i(12, 11)],
					["move", {"james": Vector2i(10, 4), "sarah": Vector2i(9, 5), "matt": Vector2i(8, 6),
						"nat": Vector2i(7, 6), "bailey": Vector2i(6, 7), "mayu": Vector2i(5, 7),
						"wallace": Vector2i(4, 8)}],
					["walk", "james", Vector2i(10, 3)], ["face", "james", "right"],
					["hold", "james", "beer"], ["walkto", "james", Vector2i(11, 9)],
					["move", {"sarah": Vector2i(10, 4), "matt": Vector2i(9, 5), "nat": Vector2i(8, 6),
						"bailey": Vector2i(7, 6), "mayu": Vector2i(6, 7), "wallace": Vector2i(5, 7)}],
					["walk", "sarah", Vector2i(10, 3)], ["face", "sarah", "right"],
					["say", ["And for you?"], "Milla"],
					["ask", "", {
						"Cider": [["hold", "sarah", "cider"], ["flag", "sarah_cider"]],
						"White Wine": [["hold", "sarah", "white_wine"],
							["flag", "sarah_wine"], ["flag", "sarah_white"]],
						"Red Wine": [["hold", "sarah", "red_wine"],
							["flag", "sarah_wine"], ["flag", "sarah_red"]],
					}, "Milla"],
					["say", ["Coming right up."], "Milla"],
					["walkto", "sarah", Vector2i(12, 9)],
					["move", {"matt": Vector2i(10, 4), "nat": Vector2i(9, 5), "bailey": Vector2i(8, 6),
						"mayu": Vector2i(7, 6), "wallace": Vector2i(6, 7)}],
					["walk", "matt", Vector2i(10, 3)], ["face", "matt", "right"],
					["hold", "matt", "beer"], ["walkto", "matt", Vector2i(13, 11)],
					["move", {"nat": Vector2i(10, 4), "bailey": Vector2i(9, 5), "mayu": Vector2i(8, 6),
						"wallace": Vector2i(7, 6)}],
					["walk", "nat", Vector2i(10, 3)], ["face", "nat", "right"],
					["hold", "nat", "white_wine"], ["walkto", "nat", Vector2i(13, 9)],
					["move", {"bailey": Vector2i(10, 4), "mayu": Vector2i(9, 5), "wallace": Vector2i(8, 6)}],
					["walk", "bailey", Vector2i(10, 3)], ["face", "bailey", "right"],
					["hold", "bailey", "cider"], ["walkto", "bailey", Vector2i(10, 9)],
					["move", {"mayu": Vector2i(10, 4), "wallace": Vector2i(9, 5)}],
					["walk", "mayu", Vector2i(10, 3)], ["face", "mayu", "right"],
					["hold", "mayu", "white_wine"], ["walkto", "mayu", Vector2i(11, 11)],
					["move", {"wallace": Vector2i(10, 4)}],
					["walk", "wallace", Vector2i(10, 3)], ["face", "wallace", "right"],
					["hold", "wallace", "beer"], ["walkto", "wallace", Vector2i(10, 11)],
					["walk", "milla", Vector2i(18, 3)],
					["face", "milla", "down"],
					["settle"],
					["sit", "bailey", "down"], ["sit", "james", "down"],
					["sit", "sarah", "down"], ["sit", "nat", "down"],
					["sit", "wallace", "up"], ["sit", "mayu", "up"],
					["sit", "dan", "up"], ["sit", "matt", "up"],
					["say", ["Hey, is that any good?"], "James"],
					["ask", "", {
						"Yeah": [],
						"Nope": [
							["if_flag", "sarah_cider",
								[["say", ["Damn, sucks to be you I guess."], "James"]]],
							["if_flag", "sarah_wine",
								[["say", ["Don't know what you expected from pub wine tbh."], "James"]]],
						],
					}, "Sarah"],
					["flag", "w1_seated"],
				],
				"advance_when": "w1_seated",
			},
			{
				"name": "gifts",
				"locked_exits": {3: ["left", "right"]},
				"cutscene": [
					["say", ["Hey guys.", "I got you guys stuff from Comic-Con!"], "Matt"],
					["say", ["Oh! Really? (...)"], "James"],
					["say", ["For you, James:"], "Matt"],
					["say", ["Matt rummages around in his bag."]],
					["say", ["Here ya go!"], "Matt"],
					["say", ["Matt hands over two large anime figurines."]],
					["say", ["(Dawg I'm actually being set up right now)",
						"... Hey, thanks man! This is really cool."], "James"],
					["say", ["And I got something for you too, Dan!"], "Matt"],
					["say", ["Matt pulls out a large anime poster."]],
					["say", ["Kay, here ya go!"], "Matt"],
					["say", ["In front of the hoes?!"], "Dan"],
					["say", ["(LMAO OK, coulda been worse)"], "James"],
					["say", ["Dan looks to James, then back."]],
					["say", ["Dude...thanks so much!", "This is really thoughful of you"], "Dan"],
					["say", ["No problem, guys!"], "Matt"],
					["say", ["..."]],
					["flag", "w1_gifts"],
				],
				"advance_when": "w1_gifts",
			},
			{
				"name": "where_from",
				"locked_exits": {3: ["left", "right"]},
				"cutscene": [
					["say", ["There's a brief lull in conversation...",
						"You feel a strong urge to fill it."]],
					["hub", "", {
						"In-ground pool": [
							["ask", "Uhm, not to kill your vibe, but aren't all pools in the ground?", {
								"That's just what they're called": [
									["say", ["Okay well I appreciate your honesty."], "James"]],
								"No": [
									["ask", "What kind of pool isn't in ground?", {
										"Paddling pool": [
											["say", ["I'll give you that but feels like a TKO"], "James"]],
										"Infinity pool": [],
									}, "James"],
								],
							}, "James"],
							["say", ["So you're rich rich huh?"], "James"],
						],
						"Family": [
							["say", ["I'm the youngest of 5, and I have 5 nieces and nephews."], "Sarah"],
							["ask", "Wow you must love kids so much", {
								"I do": [
									["say", ["That's awesome, I'm sure we won't have any turbulence",
										"in our future related to you and kids."], "James"]],
								"I don't": [
									["say", ["(I wonder what she means by this?",
										"Oh well, no harm in leaving this open to interpretation)"], "James"]],
							}, "James"],
						],
						"Crazy family": [
							["say", ["My sister's in a legal battle with her ex-husband and her boyfriend sucks."], "Sarah"],
							["say", ["(Graphic detail follows)"], "Sarah"],
							["say", ["Wow. That's terrible.",
								"We just met today, you know that right?"], "James"],
						],
					}],
					["flag", "w1_chat"],
				],
				"advance_when": "w1_chat",
			},
			{
				"name": "wind_down",
				"objective": "Say your goodbyes and head out",
				"door_block": {4: ["It's time to go home."]},
				"end_week": "left",
				"cutscene": [
					["say", ["You're feeling pretty tired.", "Might be time to head out."]],
				],
				"talk": {"james": ["Hope I'll see you next week!"],
					"dan": ["Peace out."],
					"matt": ["Laters! Good to see you."],
					"nat": ["Byee! Text me when you're home."],
					"bailey": ["See you!"],
					"mayu": ["Bye bye!"],
					"wallace": ["Bye"]},
				"advance_when": "w1_left",
			},
		],
	}


static func _week2() -> Dictionary:
	return {
		"week": 2, "title": "Week 2", "absent": ["Leonard"],
		"beats": [
			{
				"name": "w2_arrive",
				"goto": {"scene": 1, "tile": Vector2i(9, 1)},
				"locked_exits": {1: "all"},
				"cutscene": [
					["fade_in", 1.2],
					["face", "sarah", "down"],
					["say", ["Week 2. Another wonderful evening of GoMammoth \"volleyball\""]],
					["say", ["I'm gonna go get ready."], "Nat"],
					["say", ["(I should go say hi to everyone.)"], "Sarah"],
					["flag", "w2_arrived"],
				],
				"advance_when": "w2_arrived",
			},
			{
				"name": "w2_greet",
				"objective": "Greet everyone",
				"locked_exits": {1: "all"},
				"checklist": {
					Vector2i(14, 7): {"flag": "w2_g_dan", "speaker": "Dan",
						"lines": ["Wagwan g."]},
					Vector2i(5, 7): {"flag": "w2_g_james", "speaker": "James",
						"steps": [
							["say", ["Oh hey, what's up!"], "James"],
							["ask", "", {
								"When are you playing?": [
									["say", ["Uhh that's a funny story."], "James"]],
								"Good evening handsome": ["game_over", [
									"James panicks and runs out the door, into the night.",
									"You lose, I guess.",
									"...let's run that back."]],
							}, "James"],
						]},
					Vector2i(8, 1): {"flag": "w2_g_nat", "speaker": "Nat",
						"lines": ["Huh, where did Leonard get to today?",
							"I'm sure we'll see him again."]},
					Vector2i(3, 4): {"flag": "w2_g_matt", "speaker": "Matt",
						"lines": ["Good evening, m'lady!", "(Tips fedora.)"]},
					Vector2i(15, 10): {"flag": "w2_g_mayu", "speaker": "Mayu",
						"lines": ["Heyy! Good to see you again."]},
					Vector2i(8, 10): {"flag": "w2_g_wallace", "speaker": "Wallace",
						"lines": ["Oh — hey!."]},
				},
				"checked_again": ["..."],
				"advance_when": "w2_greeted",
			},
			{
				"name": "w2_ready",
				"objective": "Talk to James when you're ready",
				"locked_exits": {1: "all"},
				"cutscene": [
					["say", ["Oh by the way, everyone is slightly better at volleyball this week."], "James"],
					["say", ["How come? Uhm the plot"], "James"],
				] + _w2_ready_ask(),
				"interact_ask": {"who": "James", "steps": _w2_ready_ask()},
				"advance_when": "w2_ready_done",
			},
			{
				"name": "w2_match",
				"objective": "Win the 3v3 (Medium)",
				"launch_volleyball": true,
				"locked_exits": {1: "all"},
				"advance_when": "w2_won_vb",
			},
			{
				"name": "w2_garden",
				"goto": {"scene": 4, "tile": Vector2i(2, 7)},
				"party": "form",
				"locked_exits": {4: "all"},
				"cutscene": [
					["fade_in", 1.0],
					["settle"],
					["say", ["The group heads round to the Salutation's beer garden and piles in around the big table."]],
					["moveto", {"sarah": Vector2i(8, 5), "james": Vector2i(9, 5), "dan": Vector2i(10, 5),
						"nat": Vector2i(11, 5), "matt": Vector2i(8, 9), "bailey": Vector2i(9, 9),
						"mayu": Vector2i(10, 9), "wallace": Vector2i(11, 9)}],
					["face", "sarah", "down"], ["face", "james", "down"],
					["face", "dan", "down"], ["face", "nat", "down"],
					["face", "matt", "up"], ["face", "bailey", "up"],
					["face", "mayu", "up"], ["face", "wallace", "up"],
					["sit_all"],
					["say", ["(I'm sitting next to Sarah...)"], "James"],
					["say", ["(I should try to make an effort)"], "James"],
					["ask", "So what do you do?", {
						"I study at Imperial": [
							["say", ["Oh, that's an awesome university"], "James"],
							["say", ["Have you heard of UCL? That, on the other hand, is not an awesome university"], "James"],
							["ask", "What are you studying?", {
								"Neuroscience": [
									["say", ["Bullshit."], "James"],
									["ask", "What am I thinking of right now.", {
										"That's not how it works.": [
											["say", ["Wrong, I was thinking of a banana."], "James"]],
										"Banana.": [
											["say", ["Holy shit."], "James"]],
									}, "James"],
								],
							}, "James"],
						],
					}, "James"],
					["say", ["I'm somethnig of a scientist myself."], "James"],
					["ask", "I worked a Biotech for 5 months. Then got fired lol", {
						"I'm working on my Western Blotting right now.": [],
					}, "James"],
					["say", ["Ooh you should explain it to me in excruciating detail"], "James"],
					["fade_out", 1.0],
					["wait", 0.9],
					["say", ["(Half an hour passes. They discussed Western Blotting.)"]],
					["fade_in", 1.0],
					["ask", "Okay okay! Did I get it?", {
						"Not really": [], "Definitely not": [],
					}, "James"],
					["say", ["Welp. I tried."], "James"],
					["say", ["Hey guys — time to come inside!"], "Milla"],
					["flag", "w2_garden_done"],
				],
				"advance_when": "w2_garden_done",
			},
			{
				"name": "w2_inside",
				"goto": {"scene": 3, "tile": Vector2i(4, 9)},
				"locked_exits": {3: "all"},
				"cutscene": [
					["settle"],
					["move", {"james": Vector2i(10, 9), "sarah": Vector2i(10, 11), "dan": Vector2i(11, 9),
						"matt": Vector2i(12, 9), "bailey": Vector2i(11, 11), "mayu": Vector2i(12, 11),
						"wallace": Vector2i(13, 11), "nat": Vector2i(4, 9)}],
					["sit", "james", "down"], ["sit", "sarah", "up"], ["sit", "dan", "down"],
					["sit", "matt", "down"], ["sit", "bailey", "up"],
					["sit", "mayu", "up"], ["sit", "wallace", "up"],
					["say", ["Inside, everyone settles into the booth, two rows facing."]],
					["say", ["Yeah, I actually speak pretty good French.",
						"I'm doing a course on Mondays to keep it up."], "James"],
					["say", ["( ! )  Nat's head snaps round."]],
					["walk", "nat", Vector2i(13, 9)],
					["sit", "nat", "down"],
					["say", ["Oh really? I'm from Martinique!"], "Nat"],
					["say", ["So... you speak fluent French."], "James"],
					["say", ["Native."], "Nat"],
					["say", ["... did I say fluent French? What I actually meant, was uh"], "James"],
					["say", ["James slowly backs away..."]],
					["walk", "james", Vector2i(6, 9)],
					["walk", "james", Vector2i(1, 9)],
					["say", ["...and bolts out the door."]],
					["say", ["(The power of undercooked chicken courses through your veins)"]],
					["say", ["(Damn I feel awful.)", "(I think I'll head home.)"], "Sarah"],
					["flag", "w2_inside_done"],
				],
				"advance_when": "w2_inside_done",
			},
			{
				"name": "w2_homeward",
				"objective": "Head home",
				"end_week": "left",
				"door_block": {4: ["It's time to go home."]},
				"settle_party": true,
				"advance_when": "w2_left",
			},
		],
	}


static func _interlude_first_contact() -> Dictionary:
	return {
		"week": 2, "title": "Interlude — First Contact",
		"beats": [
			{
				"name": "scrims_texts",
				"phone": _interlude_scrims(),
				"phone_with": "Sarah",
				"card_date": "7 June 2024",
				"advance_when": "scrims_done",
			},
		],
	}


static func _week3() -> Dictionary:
	return {
		"week": 3, "title": "Week 3", "absent": ["Leonard"],
		"beats": [
			{
				"name": "w3_arrive",
				"goto": {"scene": 1, "tile": Vector2i(9, 12)},
				"locked_exits": {1: "all"},
				"cutscene": [
					["fade_in", 1.0],
					["pose", "james", "right"],
					["say", ["Week 3. Sarah heads into the sports hall..."]],
					["say", ["...and finds James flat on the floor."]],
					["walk", "sarah", Vector2i(5, 9)],
					["face", "sarah", "up"],
					["say", ["Huh? Am I okay?", "Do I look like okay?!",
						"...yea, of course I am."], "James"],
					["say", ["I kinda realised, watching you at scrims, that I suck at diving."], "James"],
					["ask", "...", {
						"I can teach you": [],
						"Sucks to be you": [
							["say", ["Dude, what the hell.", "Can you help me out pls?"], "James"],
							["ask", "...", {"Yes": [], "Fine, ok": []}, "Sarah"],
						],
					}, "Sarah"],
					["say", ["Awesome!", "Let's give it a go..."], "James"],
					["flag", "w3_arrived"],
				],
				"advance_when": "w3_arrived",
			},
			{
				"name": "w3_dive",
				"objective": "Teach James to dive",
				"launch_dive": true,
				"locked_exits": {1: "all"},
				"advance_when": "w3_dove",
			},
			{
				"name": "w3_postdive",
				"locked_exits": {1: "all"},
				"cutscene": [
					["pose", "james", null],
					["say", ["Thanks! I feel less scared to dive now.",
						"Not sure I actually got any better.",
						"But that's a problem for another day."], "James"],
					["say", ["Are you guys gonna come play?!"], "Matt"],
					["say", ["(Oh yeah.)"], "James"],
					["say", ["Oh yeah, the difficulty went up again lol.",
						"So good luck with that."], "James"],
					["flag", "w3_ready"],
				],
				"advance_when": "w3_ready",
			},
			{
				"name": "w3_match",
				"objective": "Win the 3v3 (Hard)",
				"launch_volleyball": true,
				"locked_exits": {1: "all"},
				"advance_when": "w3_won_vb",
			},
			{
				"name": "w3_garden",
				"goto": {"scene": 4, "tile": Vector2i(2, 7)},
				"party": {"form": ["Bailey"]},
				"locked_exits": {4: "all"},
				"cutscene": [
					["fade_in", 1.0],
					["settle"],
					["say", ["Afterwards the group pack into the garden's top-right booth."]],
					["moveto", {"sarah": Vector2i(14, 5), "james": Vector2i(13, 3), "nat": Vector2i(13, 4),
						"dan": Vector2i(13, 2), "matt": Vector2i(14, 2), "mayu": Vector2i(15, 2),
						"wallace": Vector2i(15, 3)}],
					["sit", "sarah", "up"],
					["sit", "james", "right"], ["sit", "nat", "right"],
					["sit", "dan", "down"], ["sit", "matt", "down"], ["sit", "mayu", "down"],
					["sit", "wallace", "left"],
					["say", ["Hm? Your family's visiting in two weeks?"], "Matt"],
					["ask", "...", {
						"Yeah, they'll watch you guys play": [],
						"Yeah, to watch you lot suck at it": [
							["say", ["(Ouch.)"], "James"]],
					}, "Sarah"],
					["say", ["I'm sure they're going to be...",
						"...very entertained by what they see."], "Dan"],
					["say", ["Too right."], "James"],
					["say", ["(Sarah's stomach turns. Oh no. Not again.)"]],
					["say", ["Are you feeling ok?"], "Matt"],
					["say", ["(Blasted chicken.)"]],
					["say", ["Damn, no worries.", "Have a good night — see ya next week!"], "James"],
					["say", ["Sarah slips out and heads home."]],
					["flag", "w3_garden_done"],
				],
				"advance_when": "w3_garden_done",
			},
			{
				"name": "w3_spoons",
				"goto": {"scene": 10, "tile": Vector2i(2, 13)},
				"hide_player": true,
				"locked_exits": {10: "all"},
				"cutscene": [
					["fade_out", 0.8],
					["wait", 0.6],
					["say", ["(Meanwhile — James, Dan, Nat and Matt carry on to Wetherspoons.)"]],
					["fade_in", 1.0],
					["settle"],
					["move", {"james": Vector2i(8, 8), "dan": Vector2i(10, 8), "nat": Vector2i(8, 9),
						"matt": Vector2i(10, 9), "mayu": Vector2i(17, 12), "wallace": Vector2i(16, 11)}],
					["face", "james", "right"],
					["face", "dan", "left"],
					["say", ["So... who's Sarah interested in?"], "Dan"],
					["say", ["You can't tell anyone."], "Nat"],
					["say", ["Of course, of course."], "Dan"],
					["say", ["..."], "James"],
					["say", ["Do you know Leonard?"], "Nat"],
					["say", ["...", "Who the hell is Leonard?"], "James"],
					["say", ["He's tall and also German."], "Nat"],
					["say", ["I have literally never met this guy before."], "James"],
					["say", ["The guy that made us run round in circles the first week?"], "Dan"],
					["say", ["Oh, nvm, I do know that guy.", "...",
						"I'm gonna grab another drink."], "James"],
					["walk", "james", Vector2i(8, 6)],
					["walk", "james", Vector2i(6, 4)],
					["face", "james", "up"],
					["say", ["Me too."], "Matt"],
					["walk", "matt", Vector2i(10, 6)],
					["walk", "matt", Vector2i(7, 4)],
					["face", "matt", "up"],
					["face", "james", "right"],
					["face", "matt", "left"],
					["say", ["Hey man."], "Matt"],
					["say", ["Yo."], "James"],
					["say", ["What do you think about that whole Leonard thing?"], "Matt"],
					["say", ["Idk dude. Good for her?"], "James"],
					["say", ["Were you interested in her as well?"], "Matt"],
					["say", ["No, no — not really."], "James"],
					["say", ["Well, between you and me, I think this might be for the best.",
						"We don't want something silly like this coming between two bros, y'know."], "Matt"],
					["say", ["Lol, for sure man."], "James"],
					["say", ["Let's make a pact.",
						"Neither of us asks Sarah on a date, and we both just keep on going with everything."], "Matt"],
					["say", ["A pact?", "...", "...sure?"], "James"],
					["say", ["Sweet — this is a good thing, trust me."], "Matt"],
					["walk", "matt", Vector2i(10, 6)],
					["walk", "matt", Vector2i(10, 9)],
					["say", ["(...okay.)"], "James"],
					["walk", "james", Vector2i(8, 6)],
					["walk", "james", Vector2i(8, 8)],
					["fade_out", 1.0],
					["wait", 0.5],
					["flag", "w3_spoons_done"],
				],
				"advance_when": "w3_spoons_done",
			},
			{
				"name": "w3_end",
				"end_chapter": true,
				"advance_when": "w3_left",
			},
		],
	}


static func _week4() -> Dictionary:
	return {
		"week": 4, "title": "Week 4", "absent": ["Nat", "Leonard"],
		"beats": [
			{
				"name": "w4_arrive",
				"goto": {"scene": 1, "tile": Vector2i(9, 12)},
				"locked_exits": {1: "all"},
				"cutscene": [
					["fade_in", 1.0],
					["say", ["Week 4. The season finale."]],
					["say", ["Sarah walks into the sports hall."]],
					["say", ["( ! )  Dan waves her over."]],
					["say", ["Hey! Final game of the season today.",
						"Good luck — you're gonna need it."], "Dan"],
					["ask", "...", {
						"Are we on the same team?": [
							["say", ["Tbf, I have no idea."], "Dan"]],
						"I'll see u on the court, sport": [
							["say", ["That was a pretty lame response.",
								"Surprised that's the best you could come up with.",
								"Really not a lot of creativity on display."], "Dan"]],
					}, "Sarah"],
					["flag", "w4_arrived"],
				],
				"advance_when": "w4_arrived",
			},
			{
				"name": "w4_greet",
				"objective": "Speak to everyone before the final",
				"locked_exits": {1: "all"},
				"checklist": {
					Vector2i(6, 4): {"flag": "w4_g_bailey", "speaker": "Bailey",
						"lines": ["I don't even really like volleyball that much.",
							"Being here is fun tho."]},
					Vector2i(3, 4): {"flag": "w4_g_matt", "speaker": "Matt",
						"lines": ["Oh... hi.", "(Nervously shuffles away.)"]},
					Vector2i(8, 10): {"flag": "w4_g_wallace", "speaker": "Wallace",
						"lines": ["Hey hey hey.", "Good luck today!", "...that rhymed."]},
				},
				"checked_again": ["..."],
				"advance_when": "w4_greeted",
			},
			{
				"name": "w4_ready",
				"objective": "Talk to James when you're ready",
				"locked_exits": {1: "all"},
				"cutscene": [
					["say", ["Oh hey, what's up... friend.", "...",
						"Let's have fun playing. See ya."], "James"],
				] + _w4_ready_ask(),
				"interact_ask": {"who": "James", "steps": _w4_ready_ask()},
				"advance_when": "w4_ready_done",
			},
			{
				"name": "w4_match",
				"objective": "Win the final (INSANE)",
				"launch_volleyball": true,
				"locked_exits": {1: "all"},
				"advance_when": "w4_won_vb",
			},
			{
				"name": "w4_trophy",
				"locked_exits": {1: "all"},
				"cutscene": [
					["say", ["The whistle goes — game, set, season!"]],
					["say", ["Champions. Someone produces a slightly dented trophy.",
						"(You hoist it anyway. Glorious.)"]],
					["flag", "w4_trophied"],
				],
				"advance_when": "w4_trophied",
			},
			{
				"name": "w4_garden",
				"goto": {"scene": 4, "tile": Vector2i(2, 7)},
				"party": {"form": ["Matt", "Nat", "Bailey"]},
				"locked_exits": {4: "all"},
				"cutscene": [
					["fade_in", 1.0],
					["settle"],
					["say", ["Is Matt not coming to the pub tonight?"], "Dan"],
					["say", ["I guess not.", "(...wonder why lol.)"], "James"],
					["say", ["The group pack into the garden's top-right booth."]],
					["moveto", {"sarah": Vector2i(14, 5), "dan": Vector2i(13, 4),
						"wallace": Vector2i(14, 2), "mayu": Vector2i(15, 3)}],
					["sit", "sarah", "up"], ["sit", "dan", "right"],
					["sit", "wallace", "down"], ["sit", "mayu", "left"],
					["say", ["James is last out. He walks over, pauses..."]],
					["walkto", "james", Vector2i(13, 3)],
					["sit", "james", "right"],
					["say", ["...", "Hey, what's good dude.",
						"I actually wanted to sit over there.",
						"Let's swap places."], "Dan"],
					["say", ["(Dawg, what the hell.)", "Uhmmm, no — I'm comfy now.",
						"Thanks though."], "James"],
					["say", ["(An uncomfortable silence. Someone stretches.)"]],
					["say", ["Sooo... what the hell was up with Matt Endicott today?"], "Wallace"],
					["say", ["(The group laughs. James looks relieved.)"]],
					["say", ["Yeah, I don't know what happened???",
						"He asked me out, like, late on Thursday last week."], "Sarah"],
					["say", ["Oh yeah. I thiiiink I know what mighta happened there."], "Dan"],
					["say", ["Yeah we, uh, ended up at Spoons.",
						"He kinda brought up that he wasn't gonna do that.",
						"Which was a weirdly specific thing to say, I guess."], "James"],
					["say", ["Yeah, honestly, for the best.",
						"The LAST thing I wanna do right now is date again."], "Sarah"],
					["say", ["(...oh.)"], "James"],
					["say", ["My last boyfriend was super abusive. And, even worse...",
						"he was \"French\"."], "Sarah"],
					["say", ["Wow. This guy sounds awful."], "James"],
					["say", ["Yeah. I can't even go to Canary Wharf anymore, in case I run into him."], "Sarah"],
					["say", ["I'll beat him up for you."], "James"],
					["say", ["He's super tall and he did kickboxing."], "Sarah"],
					["say", ["I willll talk shit to him.", "From a safe distance."], "James"],
					["say", ["Time to come inside, guys — sorry lol."], "Milla"],
					["flag", "w4_garden_done"],
				],
				"advance_when": "w4_garden_done",
			},
			{
				"name": "w4_inside",
				"goto": {"scene": 3, "tile": Vector2i(4, 9)},
				"locked_exits": {3: "all"},
				"cutscene": [
					["settle"],
					["move", {"james": Vector2i(10, 9), "dan": Vector2i(11, 9), "sarah": Vector2i(10, 11),
						"mayu": Vector2i(11, 11), "wallace": Vector2i(12, 11)}],
					["sit", "james", "down"], ["sit", "dan", "down"], ["sit", "sarah", "up"],
					["sit", "mayu", "up"], ["sit", "wallace", "up"],
					["say", ["Inside, James and Dan look at each other."]],
					["say", ["Another drink?"], "Dan"],
					["say", ["Yeah.", "That would be real good."], "James"],
					["say", ["(Dan downs his drink.)"]],
					["say", ["Don't worry bro. I got you."], "Dan"],
					["say", ["Wait.", "What — did I miss something?"], "James"],
					["say", ["I'll brb."], "Dan"],
					["walk", "dan", Vector2i(9, 11)],
					["face", "dan", "right"],
					["say", ["Yo Sarah, can I pull you for a chat?"], "Dan"],
					["say", ["(OH BOY.)"], "James"],
					["say", ["Oh, sure."], "Sarah"],
					["fade_out", 1.0],
					["wait", 0.7],
					["say", ["(Some time passes.)"]],
					["fade_in", 1.0],
					["walk", "dan", Vector2i(11, 9)],
					["sit", "dan", "down"],
					["say", ["What happened man?????"], "James"],
					["say", ["Nothin' much, nothin' much.",
						"Just went and laid it all out."], "Dan"],
					["say", ["So??"], "James"],
					["say", ["I asked her:", "What do ya think of ma boy James?"], "Dan"],
					["say", ["Dude, no way.", "Is this High School Musical?"], "James"],
					["say", ["I guess so dude."], "Dan"],
					["say", ["Listen man, I don't think-"], "James"],
					["say", ["Hey, I'm heading out."], "Sarah"],
					["say", ["Oh, cool, okay."], "James"],
					["say", ["Dude, I have so many dishes at home right now."], "Sarah"],
					["say", ["That's a little dramatic.", "They're just dishes."], "James"],
					["say", ["Yea, but I keep forgetting to wash them.", "Ok, listen here.",
						"I need you to remind me to do my dishes.",
						"Since you're soooo on top of this, apparently."], "Sarah"],
					["say", ["Okay yeah??? Easy."], "James"],
					["say", ["Sweet.", "See you later!"], "Sarah"],
					["walk", "sarah", Vector2i(8, 9)],
					["walk", "sarah", Vector2i(1, 9)],
					["say", ["(Sarah leaves.)"]],
					["say", ["Huh.", "What was that about?",
						"(She clearly said she wasn't interested... so...)"], "James"],
					["flag", "w4_inside_done"],
				],
				"advance_when": "w4_inside_done",
			},
			{
				"name": "w4_end",
				"end_chapter": true,
				"advance_when": "w4_left",
			},
		],
	}


static func _interlude_something_new_week() -> Dictionary:
	return {
		"week": 4, "title": "Interlude — Something New",
		"beats": [
			{
				"name": "something_new",
				"phone": _interlude_something_new(),
				"phone_with": "Dan",
				"card_date": "21 June 2024",
				"advance_when": "something_new_done",
			},
		],
	}


static func _finale_week() -> Dictionary:
	return {
		"week": 4, "title": "Finale — The Date",
		"beats": [
			{
				"name": "the_date",
				"phone": _finale_the_date(),
				"phone_with": "Sarah",
				"card_date": "21 June 2024",
				"end_game": true,
				"advance_when": "the_date_done",
			},
		],
	}
