"""The screenplay — all narrative content, as data.

Per-chapter phone/text threads, the finale, and STORY_WEEKS: the ordered
beats with their inline cutscene scripts. Flattened and interpreted by
systems/story.py; every script is validated by tests/test_cutscene_scripts.py.
No engine constants belong here — those stay in config.py."""

# Week 2's "ready to start?" prompt — fired both automatically (after greeting) and on
# talking to James again, so declining lets you wander back to him.
_W2_READY_ASK = [
    ('ask', "Now that I've answered all your questions, are we ready to start?", {
        'Yes': ('flag', 'w2_ready_done'),
        'No': [('say', ["Oh ok — come back when you're ready."], "James")],
    }, "James"),
]

_W4_READY_ASK = [
    ('ask', "Let's have fun playing — ready?", {
        'Yes': ('flag', 'w4_ready_done'),
        'No': [('say', ["Oh, ok. Come find me when you're ready."], "James")],
    }, "James"),
]

# Interlude (9th June, between Ch2 and Ch3) — James invites Sarah to scrims.
# POV: James's phone, so James is the "me" (right) side, Sarah on the left.
# (Defined here, above STORY_WEEKS, because a beat references it directly.)
INTERLUDE_SCRIMS = [
    {'sep': '7 Jun 2024'},
    # James's opening pitch — one message with line breaks, as it was sent.
    {'who': 'James', 'text': "Hiii Sarah \U0001F44B\n\n"
                            "I play w a social team most Saturdays, and when we "
                            "don't have a league game we organise scrims to get "
                            "some reps in.\n\n"
                            "We're short one outside for tmz if you want to come? "
                            "\U0001F440"},
    # The forwarded session details — also one message.
    {'who': 'James', 'text': "Next session 8 June (Saturday)\n\n"
                            "\U0001F550 Time: 12:00 - 3:00pm (3 hours)\n\n"
                            "\U0001F389 Signup: 1drv.ms/x/c/8eb19810...JjpLA\n\n"
                            "\U0001F4CD Location: Wembley, Preston Manor High "
                            "School - maps.app.goo.gl/qTzHvhym\n\n"
                            "\U0001F4B8 Price for 3 hrs: £11.57"},
    {'who': 'James', 'text': "This is all the details", 'react': "❤"},
    {'who': 'Sarah', 'text': "yea alr i had no plans"},
    {'who': 'Sarah', 'text': "do u want me to put my name down on this sheet or "
                             "how do i do this"},
    {'who': 'James', 'text': "Yes pls"},
    {'who': 'Sarah', 'text': "... in number 8 i assume"},
    {'who': 'James', 'text': "Yea yea"},
    {'who': 'James', 'text': "Sry its a very confusing document lol"},
    {'who': 'Sarah', 'text': "omg no worried i just didnt wanna fuck up yalls system"},
    {'who': 'James', 'text': "If the template broke I would probably cry"},
    {'who': 'James', 'text': "But we have a million copies so it's ok"},
    {'who': 'Sarah', 'text': "see thats what we dont want", 'react': "\U0001F64F"},
    {'who': 'Sarah', 'text': "no tears today"},
    {'who': 'Sarah', 'text': "also who do i pay or do i pay there"},
    {'who': 'James', 'text': "Friday cryday", 'react': "\U0001FAE1"},
    {'who': 'James', 'text': "After the sesh I'll send a msg np"},
    {'who': 'Sarah', 'text': "\U0001FAE1"},
    {'who': 'Sarah', 'text': "yes captain"},
    {'who': 'James', 'text': "See u tmrr", 'react': "❤"},
    {'who': 'Sarah', 'text': "HEY so this is just a warning, i hope ill feel "
                             "better tomorrow but i ate some bad chicken and have "
                             "been quite sick today, i thought it would pass but it "
                             "hasnt yet so just a warning for tomorrow, im so sorry "
                             "in advance if im too sick to make it (im praying that "
                             "wont be the case)", 'react': "\U0001F622"},
    {'who': 'James', 'text': "Hey hey Sarahh"},
    {'who': 'James', 'text': "Okay"},
    {'who': 'James', 'text': "Rest up sleep good"},
    {'who': 'James', 'text': "And come tmz if you can \U0001F64F"},
    {'sep': '8 Jun 2024'},
    {'who': 'James', 'text': "Hey how are you feeling?"},
    {'who': 'Sarah', 'text': "Much better!"},
    {'who': 'Sarah', 'text': "I didnt mean to worry u lol it was just a failsafe "
                             "text so if i had to miss out i wouldnt come off as "
                             "much as a dick lol"},
    {'who': 'Sarah', 'text': "thanks for inviting me btw i had sm fun! Also how "
                             "to do pay?"},
    {'who': 'James', 'text': "Hey hey I'm glad, this session was rly good"},
    {'who': 'James', 'text': "There's a group that we organise in, I can add you?",
                     'react': "❤"},
    {'who': 'James', 'text': "Since I'll send payment details there anyway"},
    {'who': 'Sarah', 'text': "sounds good!"},
    {'who': 'James', 'text': "You are added \U0001FAE1", 'react': "\U0001F44D"},
    {'who': 'Sarah', 'text': "Appreciated my friend"},
    {'who': 'Sarah', 'text': "\U0001F64C"},
]

# Interlude (21st June, after Ch4) — James tells Dan the news. POV: James's phone.
INTERLUDE_SOMETHING_NEW = [
    {'sep': '21 Jun 2024'},
    {'who': 'James', 'text': "Uh"},
    {'who': 'James', 'text': "Sarah just asked me out"},
    {'who': 'Dan', 'text': "Fucking nice one bro!"},
    {'who': 'James', 'text': "Thanks again"},
    {'who': 'James', 'text': "For this"},
    {'who': 'Dan', 'text': "It would've happened whether I got involved or not"},
    {'who': 'James', 'text': "Maybe"},
    {'who': 'James', 'notif': {'app': 'Messages · 3m ago', 'title': 'Sarah Lenhoff',
                              'body': 'cant wait :)'}},
    {'who': 'James', 'text': "Aaaaaaaaaaahhh"},
    {'who': 'James', 'text': "First wk at work + date w Sarah"},
    {'who': 'James', 'text': "This has been a very good day"},
]

# Finale (21st June) — the dishes saga that becomes the date. POV: James <-> Sarah.
FINALE_THE_DATE = [
    {'sep': '21 Jun 2024'},
    {'who': 'Sarah', 'text': "my dishes didnt get done before i left my apartment "
                             "and its entirely ur fault \U0001F648"},
    {'who': 'James', 'text': "Fuck off"},
    {'who': 'James', 'text': "I'm writing the msg"},
    {'who': 'James', 'text': "I'm putting so much effort into it"},
    {'who': 'James', 'text': "Wait a sec"},
    {'who': 'Sarah', 'text': "YEA SURE"},
    {'who': 'James', 'text':
        "\U0001F50A\U0001F50A\U0001F50A ring ring ring \U0001F50A\U0001F50A\U0001F50A\n"
        "⏰‼️\U0001F6A8 DO Yur DISHES ⏰‼️\U0001F6A8\n"
        "\U0001F9A0\U0001F9A0 stay hygienic \U0001F9A0\U0001F9A0\n"
        "\U0001F9FD\U0001F9FD scrub your dishes \U0001F9FD\U0001F9FD\n"
        "\U0001F1F1\U0001F1E7 this pride month \U0001F1F1\U0001F1E7\n"
        "\U0001F4A5\U0001F440 or i'll tell your mom \U0001F440\U0001F4A5"},
    {'who': 'James', 'text': "It didn't work wait"},
    {'who': 'James', 'text': "There you go"},
    {'who': 'James', 'text': "How's that"},
    {'who': 'Sarah', 'text': "The Lebanese flag \U0001F480\U0001F480"},
    {'who': 'Sarah', 'text': "im currently drinking at the pub so like still wont "
                             "get done even with ur threat but thank u"},
    {'who': 'Sarah', 'text': "i thought ud forgotten about me :/"},
    {'who': 'James', 'text': "That's a little upsetting"},
    {'who': 'James', 'text': "Nah"},
    {'who': 'James', 'text': "I would never forget", 'react': "❤"},
    {'who': 'James', 'text': "I was only late cos I had to run to Hammersmith right "
                            "after I finished work\U0001FAE0"},
    {'who': 'Sarah', 'text': "mhm sure sounds like excuses to me"},
    {'who': 'James', 'text': "Fine fine"},
    {'who': 'James', 'text': "I'll remind you again"},
    {'who': 'James', 'text': "And it will be on time"},
    {'who': 'James', 'text': "When do you want it"},
    {'who': 'Sarah', 'text': "I have a better deal for u"},
    {'who': 'Sarah', 'text': "ill buy u dinner if u just appear at my apartment and "
                             "do my dishes"},
    {'who': 'Sarah', 'text': "i really dont wan to do them"},
    {'who': 'Sarah', 'text': "if not then probs like 11 pm when im home lmao"},
    {'who': 'James', 'text': "That is a better deal"},
    {'who': 'James', 'text': "Not least bcos im going to run out creative alarm "
                            "clock ideas quickly"},
    {'who': 'James', 'text': "I'm free tmr night but I'll be sweaty after volleyball"},
    {'who': 'James', 'text': "How long can ur dishes wait"},
    {'who': 'Sarah', 'text': "Im gonna use so many dishes in the mean time"},
    {'who': 'Sarah', 'text': "I have no plans tomorrow night so"},
    {'who': 'James', 'text': "I can get there before 8 I'm sure", 'react': "❤"},
    {'who': 'James', 'text': "What's your addy"},
    {'who': 'James', 'text': "Also would I be able to use ur shower rq? All good if not"},
    {'who': 'Sarah', 'text': "you can use my shower lol"},
    {'who': 'Sarah', 'text': "Ill be in the park anyways havin a picnic so no rush!"},
    {'who': 'Sarah', 'text': "cant wait :)"},
]

STORY_WEEKS = [
    {
        'week': 1,
        'title': 'Week 1',
        'beats': [
            {
                # Check both ball baskets in EITHER order; the beat advances once both
                # are ticked off (see StoryManager._interact_checklist).
                'name': 'check_baskets',
                'objective': 'Check the ball baskets',
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('fade_in', 1.2),
                    ('say', ["Thursday evening. The sports hall hums with the",
                             "squeak of fresh trainers on the floor."]),
                    ('say', ["Sarah and Nat walk in through the doors."]),
                    ('say', ["So... what's the plan?"], "Nat"),
                    ('say', ["Let's grab a volleyball and warm up.",
                             "There should be one in the ball baskets."], "Sarah"),
                    ('say', ["I'm gonna go get changed."], "Nat"),
                    ('walk', 'nat', (2, 1)),         # heads over to the left bench...
                    ('walk', 'nat', (2, 3)),
                    ('walk', 'nat', (1, 3)),         # ...and sits on it
                    ('sit', 'nat', 'right'),
                ],
                'checklist': {                              # text is order-based (see check_more/done)
                    (2, 7):  {'flag': 'w1_basket_near', 'lines': []},
                    (17, 7): {'flag': 'w1_basket_far', 'lines': []},
                },
                'check_more': ["You check the basket.",
                               "It is entirely empty.",
                               "What did you expect to find in there?"],
                'check_done': ["You check the basket.",
                               "The void stares back at you.",
                               "Is this your first day at GoMammoth?"],
                'checked_again': ["You already checked this one — still empty."],
                'advance_when': 'w1_baskets_done',
                'locked_msg': ["Grab a ball first — check the baskets."],
            },
            {
                'name': 'leonard_offer',
                'objective': None,
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('say', ["Hey, ve haf a ball, you can come play mit us!"], "Leonard"),
                    ('say', ["I am tall und I am also German"], "Leonard"),
                    ('say', ["..."], "James"),
                    ('flag', 'w1_leonard'),
                ],
                'advance_when': 'w1_leonard',
            },
            {
                # Dan sets the match up: pick a difficulty (scales the opponent only)
                # and optionally run the controls warm-up first. Both choices set
                # 'w1_vb_set' LAST so the cutscene finishes before the court takes
                # over input; game._launch_match reads the difficulty / tutorial flags.
                'name': 'vb_setup',
                'objective': None,
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('say', ["Alright, alright, let's get this party started!"], "Dan"),
                    ('ask', "You ready?", {
                        'Warm-up': [('flag', 'w1_want_tut'),
                                    ('say', ["Sweet ok.",
                                             "It's finally my time to shine."], "Dan"),
                                    ('flag', 'w1_vb_set')],
                        'Jump right in': [('say', ["Sweet ok.",
                                                   "It's finally my time to shine."], "Dan"),
                                          ('flag', 'w1_vb_set')],
                    }, "Dan"),
                ],
                'advance_when': 'w1_vb_set',
            },
            {
                'name': 'gym_match',
                'objective': 'Win the 3v3',
                'launch_volleyball': True,
                'locked_exits': {1: 'all'},
                'advance_when': 'w1_won_vb',
            },
            {
                'name': 'pub_invite',
                'objective': None,
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('say', ["GG, everyone! I must away — auf Wiedersehen!"], "Leonard"),
                    ('vanish', 'leonard', 1.3),            # fades into the evening...
                    ('say', ["(He is never seen again.)"]),
                    ('move', {'dan': (10, 2), 'james': (11, 3)}),
                    ('face', 'sarah', 'down'),
                    ('say', ["Good game!"], "Dan"),
                    ('ask', "Hey, wanna go to the pub?", {
                        'Sure': ('flag', 'w1_pub_yes'),
                        'Not today': ('game_over', [
                            "That's not what happened, dummy.",
                            "You lose, I guess.",
                            "...let's run that back."]),
                    }, "Dan"),
                ],
                'advance_when': 'w1_pub_yes',
            },
            {
                'name': 'walk_to_pub',
                'objective': 'Head to The Salutation',
                'party': 'form',
                'advance_on_enter': 3,
                'door_block': {10: ["This isn't The Salutation — wrong pub!"]},
                'locked_exits': {},
                'advance_when': 'w1_at_pub',
            },
            {
                'name': 'pub_queue',
                'objective': 'Get a round in',
                'locked_exits': {3: ['left', 'right']},
                'cutscene': [
                    ('say', ["The whole team piles into The Salutation."]),
                    # The team queue from the front door up to the bar — Dan at the front (he's
                    # getting the round in), then James, then Sarah, then the rest. After each
                    # person collects, the rest shuffle forward one slot so the line advances.
                    # Seat-walks use 'walkto' so they pathfind round the table/fireplace.
                    ('move', {'dan': (10, 4), 'james': (9, 5), 'sarah': (8, 6),
                              'matt': (7, 6), 'nat': (6, 7), 'bailey': (5, 7),
                              'mayu': (4, 8), 'wallace': (3, 9)}),
                    ('walk', 'milla', (11, 3)),             # Milla comes over to serve
                    ('face', 'milla', 'down'),
                    # ── Dan (front) ──
                    ('walk', 'dan', (10, 3)), ('face', 'dan', 'right'),
                    ('say', ["Could I have one million beers please.", "James?"], "Dan"),
                    ('say', ["Um yeah sure, me too"], "James"),
                    ('hold', 'dan', 'beer'), ('walkto', 'dan', (12, 11)),
                    ('move', {'james': (10, 4), 'sarah': (9, 5), 'matt': (8, 6), 'nat': (7, 6),
                              'bailey': (6, 7), 'mayu': (5, 7), 'wallace': (4, 8)}),
                    # ── James (already called it from the queue) ──
                    ('walk', 'james', (10, 3)), ('face', 'james', 'right'),
                    ('hold', 'james', 'beer'), ('walkto', 'james', (11, 9)),
                    ('move', {'sarah': (10, 4), 'matt': (9, 5), 'nat': (8, 6),
                              'bailey': (7, 6), 'mayu': (6, 7), 'wallace': (5, 7)}),
                    # ── Sarah orders her own drink ──
                    ('walk', 'sarah', (10, 3)), ('face', 'sarah', 'right'),
                    ('say', ["And for you?"], "Milla"),
                    ('ask', "", {
                        'Cider': [('hold', 'sarah', 'cider'), ('flag', 'sarah_cider')],
                        'White Wine': [('hold', 'sarah', 'white_wine'),
                                       ('flag', 'sarah_wine'), ('flag', 'sarah_white')],
                        'Red Wine': [('hold', 'sarah', 'red_wine'),
                                     ('flag', 'sarah_wine'), ('flag', 'sarah_red')],
                    }, "Milla"),
                    ('say', ["Coming right up."], "Milla"),
                    ('walkto', 'sarah', (12, 9)),
                    ('move', {'matt': (10, 4), 'nat': (9, 5), 'bailey': (8, 6),
                              'mayu': (7, 6), 'wallace': (6, 7)}),
                    # ── Matt ──
                    ('walk', 'matt', (10, 3)), ('face', 'matt', 'right'),
                    ('hold', 'matt', 'beer'), ('walkto', 'matt', (13, 11)),
                    ('move', {'nat': (10, 4), 'bailey': (9, 5), 'mayu': (8, 6), 'wallace': (7, 6)}),
                    # ── Nat ──
                    ('walk', 'nat', (10, 3)), ('face', 'nat', 'right'),
                    ('hold', 'nat', 'white_wine'), ('walkto', 'nat', (13, 9)),
                    ('move', {'bailey': (10, 4), 'mayu': (9, 5), 'wallace': (8, 6)}),
                    # ── Bailey ──
                    ('walk', 'bailey', (10, 3)), ('face', 'bailey', 'right'),
                    ('hold', 'bailey', 'cider'), ('walkto', 'bailey', (10, 9)),
                    ('move', {'mayu': (10, 4), 'wallace': (9, 5)}),
                    # ── Mayu ──
                    ('walk', 'mayu', (10, 3)), ('face', 'mayu', 'right'),
                    ('hold', 'mayu', 'white_wine'), ('walkto', 'mayu', (11, 11)),
                    ('move', {'wallace': (10, 4)}),
                    # ── Wallace (last) ──
                    ('walk', 'wallace', (10, 3)), ('face', 'wallace', 'right'),
                    ('hold', 'wallace', 'beer'), ('walkto', 'wallace', (10, 11)),
                    ('walk', 'milla', (18, 3)),             # Milla heads back to her end of the bar
                    ('face', 'milla', 'down'),
                    # chairs (row 9): Bailey, James, Sarah, Nat / banquette (row 11): Wallace, Mayu, Dan, Matt
                    ('settle',),
                    ('sit', 'bailey', 'down'), ('sit', 'james', 'down'),
                    ('sit', 'sarah', 'down'), ('sit', 'nat', 'down'),
                    ('sit', 'wallace', 'up'), ('sit', 'mayu', 'up'),
                    ('sit', 'dan', 'up'), ('sit', 'matt', 'up'),
                    ('say', ["Hey, is that any good?"], "James"),
                    ('ask', "", {
                        'Yeah': [],
                        'Nope': [
                            ('if_flag', 'sarah_cider',
                             [('say', ["Damn, sucks to be you I guess."], "James")]),
                            ('if_flag', 'sarah_wine',
                             [('say', ["Don't know what you expected from pub wine tbh."], "James")]),
                        ],
                    }, "Sarah"),
                    ('flag', 'w1_seated'),
                ],
                'advance_when': 'w1_seated',
            },
            {
                'name': 'gifts',
                'objective': None,
                'locked_exits': {3: ['left', 'right']},
                'cutscene': [
                    ('say', ["Hey guys.",
                             "I got you guys stuff from Comic-Con!"], "Matt"),
                    ('say', ["Oh! Really? (...)"], "James"),
                    ('say', ["For you, James:"], "Matt"),
                    ('say', ["Matt rummages around in his bag."]),
                    ('say', ["Here ya go!"], "Matt"),
                    ('say', ["Matt hands over two large anime figurines."]),
                    ('say', ["(Dawg I'm actually being set up right now)",
                             "... Hey, thanks man! This is really cool."], "James"),
                    ('say', ["And I got something for you too, Dan!"], "Matt"),
                    ('say', ["Matt pulls out a large anime poster."]),
                    ('say', ["Kay, here ya go!"], "Matt"),
                    ('say', ["In front of the hoes?!"], "Dan"),
                    ('say', ["(LMAO OK, coulda been worse)"], "James"),
                    ('say', ["Dan looks to James, then back."]),
                    ('say', ["Dude...thanks so much!",
                             "This is really thoughful of you"], "Dan"),
                    ('say', ["No problem, guys!"], "Matt"),
                    ('say', ["..."]),
                    ('flag', 'w1_gifts'),
                ],
                'advance_when': 'w1_gifts',
            },
            {
                'name': 'where_from',
                'objective': None,
                'locked_exits': {3: ['left', 'right']},
                'cutscene': [
                    ('say', ["There's a brief lull in conversation...",
                             "You feel a strong urge to fill it."]),
                    ('hub', "", {
                        'In-ground pool': [
                            ('ask', "Uhm, not to kill your vibe, but aren't all "
                                    "pools in the ground?", {
                                "That's just what they're called": [
                                    ('say', ["Okay well I appreciate your honesty."],
                                     "James")],
                                'No': [
                                    ('ask', "What kind of pool isn't in ground?", {
                                        'Paddling pool': [
                                            ('say', ["I'll give you that but feels "
                                                     "like a TKO"], "James")],
                                        'Infinity pool': [],
                                    }, "James"),
                                ],
                            }, "James"),
                            ('say', ["So you're rich rich huh?"], "James"),
                        ],
                        'Family': [
                            ('say', ["I'm the youngest of 5, and I have 5 nieces "
                                     "and nephews."], "Sarah"),
                            ('ask', "Wow you must love kids so much", {
                                'I do': [
                                    ('say', ["That's awesome, I'm sure we won't have "
                                             "any turbulence",
                                             "in our future related to you and "
                                             "kids."], "James")],
                                "I don't": [
                                    ('say', ["(I wonder what she means by this?",
                                             "Oh well, no harm in leaving this open "
                                             "to interpretation)"], "James")],
                            }, "James"),
                        ],
                        'Crazy family': [
                            ('say', ["My sister's in a legal battle with her "
                                     "ex-husband and her boyfriend sucks."], "Sarah"),
                            ('say', ["(Graphic detail follows)"], "Sarah"),
                            ('say', ["Wow. That's terrible.",
                                     "We just met today, you know that "
                                     "right?"], "James"),
                        ],
                    }),
                    ('flag', 'w1_chat'),
                ],
                'advance_when': 'w1_chat',
            },
            {
                'name': 'wind_down',
                'objective': 'Say your goodbyes and head out',
                # garden door stays visible, but it's not time for the garden yet in Ch1
                'door_block': {4: ["It's time to go home."]},
                'end_week': 'left',
                'cutscene': [
                    ('say', ["You're feeling pretty tired.",
                             "Might be time to head out."]),
                ],
                'talk': {'james': ["Hope I'll see you next week!"],
                         'dan': ["Peace out."],
                         'matt': ["Laters! Good to see you."],
                         'nat': ["Byee! Text me when you're home."],
                         'bailey': ["See you!"],
                         'mayu': ["Bye bye!"],
                         'wallace': ["Bye"]},
                'advance_when': 'w1_left',
            },
        ],
    },
    {
        'week': 2,
        'title': 'Week 2',
        'absent': ['Leonard'],             # Leonard left after Ch1 — never seen again
        'beats': [
            {
                'name': 'w2_arrive',
                'objective': None,
                'goto': {'scene': 1, 'tile': (9, 1)},     # enter from the top, like Ch1
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('fade_in', 1.2),
                    ('face', 'sarah', 'down'),
                    ('say', ['Week 2. Another wonderful evening of GoMammoth "volleyball"']),
                    ('say', ["I'm gonna go get ready."], "Nat"),
                    ('say', ["(I should go say hi to everyone.)"], "Sarah"),
                    ('flag', 'w2_arrived'),
                ],
                'advance_when': 'w2_arrived',
            },
            {
                'name': 'w2_greet',
                'objective': 'Greet everyone',
                'locked_exits': {1: 'all'},
                'checklist': {
                    (14, 7): {'flag': 'w2_g_dan', 'speaker': 'Dan',
                              'lines': ["Wagwan g."]},
                    (5, 7):  {'flag': 'w2_g_james', 'speaker': 'James',
                              'steps': [
                                  ('say', ["Oh hey, what's up!"], "James"),
                                  ('ask', "", {
                                      'When are you playing?': [
                                          ('say', ["Uhh that's a funny story."],
                                           "James")],
                                      'Good evening handsome': ('game_over', [
                                          "James panicks and runs out the door, "
                                          "into the night.",
                                          "You lose, I guess.",
                                          "...let's run that back."]),
                                  }, "James"),
                              ]},
                    (8, 1):  {'flag': 'w2_g_nat', 'speaker': 'Nat',
                              'lines': ["Huh, where did Leonard get to today?",
                                        "I'm sure we'll see him again."]},
                    (3, 4):  {'flag': 'w2_g_matt', 'speaker': 'Matt',
                              'lines': ["Good evening, m'lady!", "(Tips fedora.)"]},
                    (15, 10): {'flag': 'w2_g_mayu', 'speaker': 'Mayu',
                               'lines': ["Heyy! Good to see you again."]},
                    (8, 10): {'flag': 'w2_g_wallace', 'speaker': 'Wallace',
                              'lines': ["Oh — hey!."]},
                },
                'checked_again': ["..."],
                'advance_when': 'w2_greeted',
            },
            {
                'name': 'w2_ready',
                'objective': "Talk to James when you're ready",
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('say', ["Oh by the way, everyone is slightly better at "
                             "volleyball this week."], "James"),
                    ('say', ["How come? Uhm the plot"], "James"),
                ] + _W2_READY_ASK,
                'interact_ask': {'who': 'James', 'steps': _W2_READY_ASK},
                'advance_when': 'w2_ready_done',
            },
            {
                'name': 'w2_match',
                'objective': 'Win the 3v3 (Medium)',
                'launch_volleyball': True,
                'locked_exits': {1: 'all'},
                'advance_when': 'w2_won_vb',
            },
            {
                # Beer garden: the group settles round the communal table, James
                # and Sarah on the near pair of chairs.
                'name': 'w2_garden',
                'objective': None,
                'goto': {'scene': 4, 'tile': (2, 7)},
                'party': 'form',
                'locked_exits': {4: 'all'},
                'cutscene': [
                    ('fade_in', 1.0),
                    ('settle',),
                    ('say', ["The group heads round to the Salutation's beer "
                             "garden and piles in around the big table."]),
                    # All eight around the communal table: Sarah & James lead the top
                    # bench (row 5, facing down), the rest fill out the benches.
                    ('moveto', {'sarah': (8, 5), 'james': (9, 5), 'dan': (10, 5),
                                'nat': (11, 5), 'matt': (8, 9), 'bailey': (9, 9),
                                'mayu': (10, 9), 'wallace': (11, 9)}),
                    ('face', 'sarah', 'down'),
                    ('face', 'james', 'down'),
                    ('face', 'dan', 'down'),
                    ('face', 'nat', 'down'),
                    ('face', 'matt', 'up'),
                    ('face', 'bailey', 'up'),
                    ('face', 'mayu', 'up'),
                    ('face', 'wallace', 'up'),
                    ('sit_all',),
                    ('say', ["(I'm sitting next to Sarah...)"], "James"),
                    ('say', ["(I should try to make an effort)"], "James"),
                    ('ask', "So what do you do?", {
                        'I study at Imperial': [
                            ('say', ["Oh, that's an awesome university"], "James"),
                            ('say', ["Have you heard of UCL? That, on the other "
                                     "hand, is not an awesome university"], "James"),
                            ('ask', "What are you studying?", {
                                'Neuroscience': [
                                    ('say', ["Bullshit."], "James"),
                                    ('ask', "What am I thinking of right now.", {
                                        "That's not how it works.": [
                                            ('say', ["Wrong, I was thinking of a "
                                                     "banana."], "James")],
                                        'Banana.': [
                                            ('say', ["Holy shit."], "James")],
                                    }, "James"),
                                ],
                            }, "James"),
                        ],
                    }, "James"),
                    ('say', ["I'm somethnig of a scientist myself."], "James"),
                    ('ask', "I worked a Biotech for 5 months. Then got fired lol", {
                        "I'm working on my Western Blotting right now.": [],
                    }, "James"),
                    ('say', ["Ooh you should explain it to me in excruciating "
                             "detail"], "James"),
                    ('fade_out', 1.0),
                    ('wait', 0.9),
                    ('say', ["(Half an hour passes. They discussed Western Blotting.)"]),
                    ('fade_in', 1.0),
                    ('ask', "Okay okay! Did I get it?", {
                        'Not really': [], 'Definitely not': [],
                    }, "James"),
                    ('say', ["Welp. I tried."], "James"),
                    ('say', ["Hey guys — time to come inside!"], "Milla"),
                    ('flag', 'w2_garden_done'),
                ],
                'advance_when': 'w2_garden_done',
            },
            {
                # Inside the Salutation: the chatter resumes, James digs his own
                # grave in French, and Nat happens to be from Martinique.
                'name': 'w2_inside',
                'objective': None,
                'goto': {'scene': 3, 'tile': (4, 9)},
                'locked_exits': {3: 'all'},
                'cutscene': [
                    ('settle',),
                    # Everyone piles into the bottom-wall booth over fresh drinks;
                    # Nat's off to the side until she clocks James's French.
                    ('move', {'james': (10, 9), 'sarah': (10, 11), 'dan': (11, 9),
                              'matt': (12, 9), 'bailey': (11, 11), 'mayu': (12, 11),
                              'wallace': (13, 11), 'nat': (4, 9)}),
                    ('sit', 'james', 'down'), ('sit', 'sarah', 'up'), ('sit', 'dan', 'down'),
                    ('sit', 'matt', 'down'), ('sit', 'bailey', 'up'),
                    ('sit', 'mayu', 'up'), ('sit', 'wallace', 'up'),
                    ('say', ["Inside, everyone settles into the booth, two rows facing."]),
                    ('say', ["Yeah, I actually speak pretty good French.",
                             "I'm doing a course on Mondays to keep it up."], "James"),
                    ('say', ["( ! )  Nat's head snaps round."]),
                    ('walk', 'nat', (13, 9)),           # she comes over to the table
                    ('sit', 'nat', 'down'),
                    ('say', ["Oh really? I'm from Martinique!"], "Nat"),
                    ('say', ["So... you speak fluent French."], "James"),
                    ('say', ["Native."], "Nat"),
                    ('say', ["... did I say fluent French? What I actually "
                             "meant, was uh"], "James"),
                    ('say', ["James slowly backs away..."]),
                    ('walk', 'james', (6, 9)),
                    ('walk', 'james', (1, 9)),          # bolts for the front door
                    ('say', ["...and bolts out the door."]),
                    ('say', ["(The power of undercooked chicken courses through "
                             "your veins)"]),
                    ('say', ["(Damn I feel awful.)",
                             "(I think I'll head home.)"], "Sarah"),
                    ('flag', 'w2_inside_done'),
                ],
                'advance_when': 'w2_inside_done',
            },
            {
                # Walk out the front door to call it a night -> results + texts.
                'name': 'w2_homeward',
                'objective': 'Head home',
                'end_week': 'left',
                # garden's done for the night — the door back out just sends you home
                'door_block': {4: ["It's time to go home."]},
                'settle_party': True,                  # the crew stays at the pub as you leave
                'advance_when': 'w2_left',
            },
        ],
    },
    {
        'week': 2, 'title': 'Interlude — First Contact',
        'beats': [
            {
                # Texts-only interlude (9th June): James invites Sarah to scrims.
                'name': 'scrims_texts',
                'objective': None,
                'phone': INTERLUDE_SCRIMS,
                'phone_with': 'Sarah',
                'card_date': '7 June 2024',
                'advance_when': 'scrims_done',
            },
        ],
    },
    {
        'week': 3,
        'title': 'Week 3',
        'absent': ['Leonard'],
        'beats': [
            {
                # Sarah arrives to find James flat on the floor; agree to teach him.
                'name': 'w3_arrive',
                'objective': None,
                'goto': {'scene': 1, 'tile': (9, 12)},
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('fade_in', 1.0),
                    ('pose', 'james', 'right'),       # sprawled flat on the floor
                    ('say', ["Week 3. Sarah heads into the sports hall..."]),
                    ('say', ["...and finds James flat on the floor."]),
                    ('walk', 'sarah', (5, 9)),
                    ('face', 'sarah', 'up'),
                    ('say', ["Huh? Am I okay?", "Do I look like okay?!",
                             "...yea, of course I am."], "James"),
                    ('say', ["I kinda realised, watching you at scrims, that I "
                             "suck at diving."], "James"),
                    ('ask', "...", {
                        'I can teach you': [],
                        'Sucks to be you': [
                            ('say', ["Dude, what the hell.",
                                     "Can you help me out pls?"], "James"),
                            ('ask', "...", {'Yes': [], 'Fine, ok': []}, "Sarah"),
                        ],
                    }, "Sarah"),
                    ('say', ["Awesome!", "Let's give it a go..."], "James"),
                    ('flag', 'w3_arrived'),
                ],
                'advance_when': 'w3_arrived',
            },
            {
                'name': 'w3_dive',
                'objective': 'Teach James to dive',
                'launch_dive': True,
                'locked_exits': {1: 'all'},
                'advance_when': 'w3_dove',
            },
            {
                'name': 'w3_postdive',
                'objective': None,
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('pose', 'james', None),          # back on his feet after the drill
                    ('say', ["Thanks! I feel less scared to dive now.",
                             "Not sure I actually got any better.",
                             "But that's a problem for another day."], "James"),
                    ('say', ["Are you guys gonna come play?!"], "Matt"),
                    ('say', ["(Oh yeah.)"], "James"),
                    ('say', ["Oh yeah, the difficulty went up again lol.",
                             "So good luck with that."], "James"),
                    ('flag', 'w3_ready'),
                ],
                'advance_when': 'w3_ready',
            },
            {
                'name': 'w3_match',
                'objective': 'Win the 3v3 (Hard)',
                'launch_volleyball': True,
                'locked_exits': {1: 'all'},
                'advance_when': 'w3_won_vb',
            },
            {
                # Beer garden, back-left table. Family-visit chat; Sarah feels rough
                # and heads home early.
                'name': 'w3_garden',
                'objective': None,
                'goto': {'scene': 4, 'tile': (2, 7)},
                'party': {'form': ['Bailey']},        # Bailey heads home after the match
                'locked_exits': {4: 'all'},
                'cutscene': [
                    ('fade_in', 1.0),
                    ('settle',),
                    ('say', ["Afterwards the group pack into the garden's "
                             "top-right booth."]),
                    ('moveto', {'sarah': (14, 5), 'james': (13, 3), 'nat': (13, 4),
                                'dan': (13, 2), 'matt': (14, 2), 'mayu': (15, 2),
                                'wallace': (15, 3)}),
                    ('sit', 'sarah', 'up'),
                    ('sit', 'james', 'right'), ('sit', 'nat', 'right'),
                    ('sit', 'dan', 'down'), ('sit', 'matt', 'down'), ('sit', 'mayu', 'down'),
                    ('sit', 'wallace', 'left'),
                    ('say', ["Hm? Your family's visiting in two weeks?"], "Matt"),
                    ('ask', "...", {
                        "Yeah, they'll watch you guys play": [],
                        "Yeah, to watch you lot suck at it": [
                            ('say', ["(Ouch.)"], "James")],
                    }, "Sarah"),
                    ('say', ["I'm sure they're going to be...",
                             "...very entertained by what they see."], "Dan"),
                    ('say', ["Too right."], "James"),
                    ('say', ["(Sarah's stomach turns. Oh no. Not again.)"]),
                    ('say', ["Are you feeling ok?"], "Matt"),
                    ('say', ["(Blasted chicken.)"]),
                    ('say', ["Damn, no worries.",
                             "Have a good night — see ya next week!"], "James"),
                    ('say', ["Sarah slips out and heads home."]),
                    ('flag', 'w3_garden_done'),
                ],
                'advance_when': 'w3_garden_done',
            },
            {
                # James's POV: the lads carry on to Wetherspoons. Sarah's gone, so
                # her sprite is hidden for this scene.
                'name': 'w3_spoons',
                'objective': None,
                'goto': {'scene': 10, 'tile': (2, 13)},
                'hide_player': True,
                'locked_exits': {10: 'all'},
                'cutscene': [
                    ('fade_out', 0.8),
                    ('wait', 0.6),
                    ('say', ["(Meanwhile — James, Dan, Nat and Matt carry on to "
                             "Wetherspoons.)"]),
                    ('fade_in', 1.0),
                    ('settle',),
                    ('move', {'james': (8, 8), 'dan': (10, 8), 'nat': (8, 9),
                              'matt': (10, 9), 'mayu': (17, 12), 'wallace': (16, 11)}),
                    ('face', 'james', 'right'),
                    ('face', 'dan', 'left'),
                    ('say', ["So... who's Sarah interested in?"], "Dan"),
                    ('say', ["You can't tell anyone."], "Nat"),
                    ('say', ["Of course, of course."], "Dan"),
                    ('say', ["..."], "James"),
                    ('say', ["Do you know Leonard?"], "Nat"),
                    ('say', ["...", "Who the hell is Leonard?"], "James"),
                    ('say', ["He's tall and also German."], "Nat"),
                    ('say', ["I have literally never met this guy before."], "James"),
                    ('say', ["The guy that made us run round in circles the "
                             "first week?"], "Dan"),
                    ('say', ["Oh, nvm, I do know that guy.", "...",
                             "I'm gonna grab another drink."], "James"),
                    ('walk', 'james', (8, 6)),
                    ('walk', 'james', (6, 4)),
                    ('face', 'james', 'up'),
                    ('say', ["Me too."], "Matt"),
                    ('walk', 'matt', (10, 6)),
                    ('walk', 'matt', (7, 4)),
                    ('face', 'matt', 'up'),
                    ('face', 'james', 'right'),
                    ('face', 'matt', 'left'),
                    ('say', ["Hey man."], "Matt"),
                    ('say', ["Yo."], "James"),
                    ('say', ["What do you think about that whole Leonard thing?"], "Matt"),
                    ('say', ["Idk dude. Good for her?"], "James"),
                    ('say', ["Were you interested in her as well?"], "Matt"),
                    ('say', ["No, no — not really."], "James"),
                    ('say', ["Well, between you and me, I think this might be for "
                             "the best.",
                             "We don't want something silly like this coming "
                             "between two bros, y'know."], "Matt"),
                    ('say', ["Lol, for sure man."], "James"),
                    ('say', ["Let's make a pact.",
                             "Neither of us asks Sarah on a date, and we both just "
                             "keep on going with everything."], "Matt"),
                    ('say', ["A pact?", "...", "...sure?"], "James"),
                    ('say', ["Sweet — this is a good thing, trust me."], "Matt"),
                    ('walk', 'matt', (10, 6)),
                    ('walk', 'matt', (10, 9)),
                    ('say', ["(...okay.)"], "James"),
                    ('walk', 'james', (8, 6)),
                    ('walk', 'james', (8, 8)),
                    ('fade_out', 1.0),
                    ('wait', 0.5),
                    ('flag', 'w3_spoons_done'),
                ],
                'advance_when': 'w3_spoons_done',
            },
            {
                # End of chapter -> results card + the Week 3 texts.
                'name': 'w3_end',
                'objective': None,
                'end_chapter': True,
                'advance_when': 'w3_left',
            },
        ],
    },
    {
        'week': 4,
        'title': 'Week 4',
        'absent': ['Nat', 'Leonard'],      # Nat stays home; Leonard long gone — not in the gym
        'beats': [
            {
                'name': 'w4_arrive',
                'objective': None,
                'goto': {'scene': 1, 'tile': (9, 12)},
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('fade_in', 1.0),
                    ('say', ["Week 4. The season finale."]),
                    ('say', ["Sarah walks into the sports hall."]),
                    ('say', ["( ! )  Dan waves her over."]),
                    ('say', ["Hey! Final game of the season today.",
                             "Good luck — you're gonna need it."], "Dan"),
                    ('ask', "...", {
                        'Are we on the same team?': [
                            ('say', ["Tbf, I have no idea."], "Dan")],
                        "I'll see u on the court, sport": [
                            ('say', ["That was a pretty lame response.",
                                     "Surprised that's the best you could come up with.",
                                     "Really not a lot of creativity on display."], "Dan")],
                    }, "Sarah"),
                    ('flag', 'w4_arrived'),
                ],
                'advance_when': 'w4_arrived',
            },
            {
                'name': 'w4_greet',
                'objective': 'Speak to everyone before the final',
                'locked_exits': {1: 'all'},
                'checklist': {
                    (6, 4):  {'flag': 'w4_g_bailey', 'speaker': 'Bailey',
                              'lines': ["I don't even really like volleyball that much.",
                                        "Being here is fun tho."]},
                    (3, 4):  {'flag': 'w4_g_matt', 'speaker': 'Matt',
                              'lines': ["Oh... hi.", "(Nervously shuffles away.)"]},
                    (8, 10): {'flag': 'w4_g_wallace', 'speaker': 'Wallace',
                              'lines': ["Hey hey hey.", "Good luck today!",
                                        "...that rhymed."]},
                },
                'checked_again': ["..."],
                'advance_when': 'w4_greeted',
            },
            {
                'name': 'w4_ready',
                'objective': "Talk to James when you're ready",
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('say', ["Oh hey, what's up... friend.", "...",
                             "Let's have fun playing. See ya."], "James"),
                ] + _W4_READY_ASK,
                'interact_ask': {'who': 'James', 'steps': _W4_READY_ASK},
                'advance_when': 'w4_ready_done',
            },
            {
                'name': 'w4_match',
                'objective': 'Win the final (INSANE)',
                'launch_volleyball': True,
                'locked_exits': {1: 'all'},
                'advance_when': 'w4_won_vb',
            },
            {
                'name': 'w4_trophy',
                'objective': None,
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('say', ["The whistle goes — game, set, season!"]),
                    ('say', ["Champions. Someone produces a slightly dented trophy.",
                             "(You hoist it anyway. Glorious.)"]),
                    ('flag', 'w4_trophied'),
                ],
                'advance_when': 'w4_trophied',
            },
            {
                # Beer garden, left-wall booth. Matt's a no-show; the Endicott saga
                # comes out, and Sarah lets slip she's not looking to date.
                'name': 'w4_garden',
                'objective': None,
                'goto': {'scene': 4, 'tile': (2, 7)},
                'party': {'form': ['Matt', 'Nat', 'Bailey']},  # Matt in the gym; Nat home; Bailey home
                'locked_exits': {4: 'all'},
                'cutscene': [
                    ('fade_in', 1.0),
                    ('settle',),
                    ('say', ["Is Matt not coming to the pub tonight?"], "Dan"),
                    ('say', ["I guess not.", "(...wonder why lol.)"], "James"),
                    ('say', ["The group pack into the garden's top-right booth."]),
                    ('moveto', {'sarah': (14, 5), 'dan': (13, 4),
                                'wallace': (14, 2), 'mayu': (15, 3)}),
                    ('sit', 'sarah', 'up'), ('sit', 'dan', 'right'),
                    ('sit', 'wallace', 'down'), ('sit', 'mayu', 'left'),
                    ('say', ["James is last out. He walks over, pauses..."]),
                    ('walkto', 'james', (13, 3)),       # sits by Dan, not the spot beside Sarah
                    ('sit', 'james', 'right'),
                    ('say', ["...", "Hey, what's good dude.",
                             "I actually wanted to sit over there.",
                             "Let's swap places."], "Dan"),
                    ('say', ["(Dawg, what the hell.)", "Uhmmm, no — I'm comfy now.",
                             "Thanks though."], "James"),
                    ('say', ["(An uncomfortable silence. Someone stretches.)"]),
                    ('say', ["Sooo... what the hell was up with Matt Endicott today?"],
                     "Wallace"),
                    ('say', ["(The group laughs. James looks relieved.)"]),
                    ('say', ["Yeah, I don't know what happened???",
                             "He asked me out, like, late on Thursday last week."],
                     "Sarah"),
                    ('say', ["Oh yeah. I thiiiink I know what mighta happened there."],
                     "Dan"),
                    ('say', ["Yeah we, uh, ended up at Spoons.",
                             "He kinda brought up that he wasn't gonna do that.",
                             "Which was a weirdly specific thing to say, I guess."],
                     "James"),
                    ('say', ["Yeah, honestly, for the best.",
                             "The LAST thing I wanna do right now is date again."],
                     "Sarah"),
                    ('say', ["(...oh.)"], "James"),
                    ('say', ["My last boyfriend was super abusive. And, even worse...",
                             "he was \"French\"."], "Sarah"),
                    ('say', ["Wow. This guy sounds awful."], "James"),
                    ('say', ["Yeah. I can't even go to Canary Wharf anymore, in case "
                             "I run into him."], "Sarah"),
                    ('say', ["I'll beat him up for you."], "James"),
                    ('say', ["He's super tall and he did kickboxing."], "Sarah"),
                    ('say', ["I willll talk shit to him.", "From a safe distance."],
                     "James"),
                    ('say', ["Time to come inside, guys — sorry lol."], "Milla"),
                    ('flag', 'w4_garden_done'),
                ],
                'advance_when': 'w4_garden_done',
            },
            {
                # Inside: Dan plays wingman; Sarah leaves James with a "remind me to
                # do my dishes" — the spark neither of them quite reads yet.
                'name': 'w4_inside',
                'objective': None,
                'goto': {'scene': 3, 'tile': (4, 9)},
                'locked_exits': {3: 'all'},
                'cutscene': [
                    ('settle',),
                    ('move', {'james': (10, 9), 'dan': (11, 9), 'sarah': (10, 11),
                              'mayu': (11, 11), 'wallace': (12, 11)}),
                    ('sit', 'james', 'down'), ('sit', 'dan', 'down'), ('sit', 'sarah', 'up'),
                    ('sit', 'mayu', 'up'), ('sit', 'wallace', 'up'),
                    ('say', ["Inside, James and Dan look at each other."]),
                    ('say', ["Another drink?"], "Dan"),
                    ('say', ["Yeah.", "That would be real good."], "James"),
                    ('say', ["(Dan downs his drink.)"]),
                    ('say', ["Don't worry bro. I got you."], "Dan"),
                    ('say', ["Wait.", "What — did I miss something?"], "James"),
                    ('say', ["I'll brb."], "Dan"),
                    ('walk', 'dan', (9, 11)),
                    ('face', 'dan', 'right'),
                    ('say', ["Yo Sarah, can I pull you for a chat?"], "Dan"),
                    ('say', ["(OH BOY.)"], "James"),
                    ('say', ["Oh, sure."], "Sarah"),
                    ('fade_out', 1.0),
                    ('wait', 0.7),
                    ('say', ["(Some time passes.)"]),
                    ('fade_in', 1.0),
                    ('walk', 'dan', (11, 9)),
                    ('sit', 'dan', 'down'),
                    ('say', ["What happened man?????"], "James"),
                    ('say', ["Nothin' much, nothin' much.",
                             "Just went and laid it all out."], "Dan"),
                    ('say', ["So??"], "James"),
                    ('say', ["I asked her:", "What do ya think of ma boy James?"], "Dan"),
                    ('say', ["Dude, no way.", "Is this High School Musical?"], "James"),
                    ('say', ["I guess so dude."], "Dan"),
                    ('say', ["Listen man, I don't think-"], "James"),
                    ('say', ["Hey, I'm heading out."], "Sarah"),
                    ('say', ["Oh, cool, okay."], "James"),
                    ('say', ["Dude, I have so many dishes at home right now."], "Sarah"),
                    ('say', ["That's a little dramatic.", "They're just dishes."], "James"),
                    ('say', ["Yea, but I keep forgetting to wash them.", "Ok, listen here.",
                             "I need you to remind me to do my dishes.",
                             "Since you're soooo on top of this, apparently."], "Sarah"),
                    ('say', ["Okay yeah??? Easy."], "James"),
                    ('say', ["Sweet.", "See you later!"], "Sarah"),
                    ('walk', 'sarah', (8, 9)),
                    ('walk', 'sarah', (1, 9)),
                    ('say', ["(Sarah leaves.)"]),
                    ('say', ["Huh.", "What was that about?",
                             "(She clearly said she wasn't interested... so...)"], "James"),
                    ('flag', 'w4_inside_done'),
                ],
                'advance_when': 'w4_inside_done',
            },
            {
                'name': 'w4_end',
                'objective': None,
                'end_chapter': True,
                'advance_when': 'w4_left',
            },
        ],
    },
    {
        'week': 4, 'title': 'Interlude — Something New',
        'beats': [
            {
                'name': 'something_new',
                'objective': None,
                'phone': INTERLUDE_SOMETHING_NEW,
                'phone_with': 'Dan',
                'card_date': '21 June 2024',
                'advance_when': 'something_new_done',
            },
        ],
    },
    {
        'week': 4, 'title': 'Finale — The Date',
        'beats': [
            {
                'name': 'the_date',
                'objective': None,
                'phone': FINALE_THE_DATE,
                'phone_with': 'Sarah',
                'card_date': '21 June 2024',
                'end_game': True,                 # finale -> roll the closing card
                'advance_when': 'the_date_done',
            },
        ],
    },
]


# Post-night phone threads shown after each week's results card (James <-> Dan).
# See systems/screens.py Phone for the entry schema.
PHONE_THREAD_W1 = [
    {'who': 'Dan', 'shot_me': 'Dan', 'caption': 'Dan sent a screenshot', 'shot': [
        ('Matt', "Yesterday I overheard you telling a guy to turn the oven "
                 "on and leave a rug in the room?? what was that about"),
        ('Matt', "I forgot to ask you to clarify... was that you talking "
                 "about the SIMS game??"),
        ('Dan', "\U0001F602\U0001F602\U0001F602"),
    ]},
    {'who': 'James', 'text': "lol"},
    {'who': 'Dan', 'text': "He makes me laugh", 'react': "\U0001F44D"},
    {'who': 'James', 'notif': {
        'app': 'Santander', 'title': 'You have a new insight',
        'body': 'Quick Quiz! What did you spend at THE SALUTATION?'}},
    {'who': 'Dan', 'text': "Nah whaattttttt \U0001F602\U0001F602\U0001F602"},
    {'who': 'Dan', 'text': "That should be illegal"},
    {'who': 'James', 'text': "Santander want the smoke", 'react': "\U0001F602"},
    {'who': 'James', 'text': "I'm here \U0001F94A\U0001F6AB"},
]

# Week 2: Dan can't keep a secret.
PHONE_THREAD_W2 = [
    {'who': 'Dan', 'text': "Me n Mayu just got off for like an hour"},
    {'who': 'James', 'text': "Lmao on fucking way"},
    {'who': 'Dan', 'text': "Don't tell anyone cus we promised not to tell anyone"},
    {'who': 'Dan', 'text': "And she specifically said James"},
    {'who': 'James', 'text': "Won't"},
    {'who': 'Dan', 'text': "But I can't not tell h"},
    {'who': 'Dan', 'text': "U"},
    {'who': 'James', 'text': "Real"},
    {'who': 'Dan', 'text': "For real you can't tell anyone"},
    {'who': 'James', 'text': "\U0001F910"},
    {'who': 'Dan', 'text': "Told u I got it", 'react': "\U0001F44D"},
]

# Week 3: Dan's night out, then Matt does a full 180 on the pact.
PHONE_THREAD_W3 = [
    {'who': 'Dan', 'text': "Back at Natalia's place rn"},
    {'who': 'James', 'text': "Huh"},
    {'who': 'James', 'text': "All good?"},
    {'who': 'Dan', 'text': "Ye"},
    {'who': 'Dan', 'text': "Slept with her"},
    {'who': 'James', 'text': "Say ong"},
    {'who': 'Dan', 'text': "Ong"},
    # ...scroll past some texts...
    {'who': 'James', 'notif': {
        'app': 'Messages · 18m ago',
        'title': 'Matthew Endicott',
        'body': "I asked out Sarah. She said no. I apologise for going back on what "
                "I said last night, I apologise for that. Just to be clear I am not "
                "apologising for asking her out, I am apologising for going back on "
                "my word yesterday when I said I wouldn't. At the end of"}},
    {'who': 'James', 'text': "Can't have a normal night out \U0001F62D\U0001F62D"},
    {'who': 'Dan', 'text': "Fucking hell man \U0001F602\U0001F602\U0001F602\U0001F602"},
    {'who': 'Dan', 'text': "Fuck spoons"},
    {'who': 'Dan', 'text': "Nah how can someone do a full 180 like that \U0001F62D"},
]

# Week 4 (season final) — Dan connects the dots.
PHONE_THREAD_W4 = [
    {'who': 'Dan', 'text': "Hiya"},
    {'who': 'Dan', 'text': "Upon reflection"},
    {'who': 'Dan', 'text': "Natalia asked if I like Sarah"},
    {'who': 'Dan', 'text': "You asked if Sarah likes me"},
    {'who': 'Dan', 'text': "Good form"},
    {'who': 'Dan', 'text': "Thanks"},
]
