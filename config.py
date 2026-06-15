"""Game configuration constants"""
import os

# Screen dimensions
SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 480

# Tile grid
TILE_SIZE  = 32
MAP_COLS   = SCREEN_WIDTH  // TILE_SIZE   # 20
MAP_ROWS   = SCREEN_HEIGHT // TILE_SIZE   # 15

# Colors
WHITE = (255, 255, 255)

# UI fonts — comma lists; SysFont picks the first installed, else a default.
# Body text (dialogue, options, scene titles) vs. a display face for headings.
UI_FONT_NAME = 'Avenir Next,Avenir,Helvetica Neue,Segoe UI,Arial'
UI_TITLE_FONT_NAME = 'Futura,Gill Sans,Avenir Next,Trebuchet MS,Arial'

# Tile-based movement
TILE_MOVE_SPEED = 280   # pixels per second during the smooth slide between tiles

# Dialogue typewriter (Undertale-style)
DIALOGUE_CPS  = 45.0    # characters revealed per second
DIALOGUE_FAST = 4.0     # multiplier while X (cancel) is held to speed up text

# ── Audio ────────────────────────────────────────────────────────────────────
# One streamed music track at a time; drop .ogg files into assets/ (see MusicPlayer).
ASSET_DIR     = os.path.join(os.path.dirname(__file__), 'assets')
MUSIC_VOLUME  = 0.5     # 0..1 background-music level
MUSIC_FADE_MS = 600     # fade applied on play-in / stop, in ms
SFX_VOLUME    = 0.55    # 0..1 sound-effects level
VB_MUSIC      = os.path.join(ASSET_DIR, 'vb_theme.ogg')   # volleyball theme (add this file)
KING_ST_MUSIC = os.path.join(ASSET_DIR, 'king_street.ogg')  # plays while on King Street (scene 2)

# ── Volleyball minigame (scene 11) ──────────────────────────────────────────
VB_NET_Y           = 240     # net line (centre of the 2:1 court, screen mid-height)
VB_ACTOR_SPEED     = 204     # px/s — AI free movement (player uses momentum below)
VB_CONTACT_RADIUS  = 34      # px the actor must be within (ball ground position)
VB_TIMING_WINDOW   = 0.24    # s — "ok" contact window either side of ideal time
VB_PERFECT_WINDOW  = 0.10    # s — tighter "perfect" window (full power/accuracy)
VB_SCORE_TO_WIN    = 7       # first to 7, win by 2

# AI reliability — easy balls almost always come up; hard hits ~60-70%.
VB_AI_DIG_BASE     = 0.97    # dig success on an easy (slow) ball in reach
VB_AI_DIG_HARD     = 0.62    # dig success on the hardest (fastest) ball
VB_AI_REACH_BONUS  = 12      # px extra reach so defenders rarely flub balls near them
VB_AI_ERROR_FRAC   = 0.45    # of failed digs, this fraction are outright errors (point)

# Receive quality — a dig's quality (0..1) decides clean vs shank vs error.
VB_DIG_CLEAN       = 0.60    # quality at/above this -> clean dig to the setter
VB_DIG_SHANK       = 0.28    # quality at/above this -> shank (alive, out of system)
VB_DIG_MOVE_PEN    = 0.45    # quality lost for digging at full speed (vs planted)
VB_DIG_OFFSET_PEN  = 0.55    # quality lost for the ball being fully off-centre
VB_DIG_DIFF_PEN    = 0.40    # quality lost on the hardest incoming ball

# Out-of-system attack — a poor/scrambled set limits the hitter.
VB_OOS_POWER_CAP   = 0.5     # max spike power off a bad set
VB_OOS_RANGE       = 0.42    # fraction of court width the reticle may roam (centred)

# AI attack — when attacking the human, bias the set away from the blocker.
VB_AI_AVOID_BLOCK  = 0.6     # chance the AI setter picks the hitter away from your x
VB_AI_BLOCK_CHANCE = 0.85    # chance the defending setter puts up a block
VB_AI_TIP_CHANCE   = 0.16    # chance an in-system AI attack is a tip into the open front

# Difficulty — scales the OPPONENT (far team) only; your teammates always play at full
# strength. 'hard' == the tuned constants above. Higher dig/block/tip + tighter attack
# spread + more reach = a tougher opponent. Chosen per match (Dan asks before you play).
VB_DIFFICULTY = {
    'easy':   {'dig_base': 0.80, 'dig_hard': 0.28, 'error_frac': 0.65,
               'avoid_block': 0.15, 'block_chance': 0.30, 'tip_chance': 0.06,
               'reach_bonus': 0,  'attack_spread': 2.4, 'serve_aggr': 0.2},
    'medium': {'dig_base': 0.90, 'dig_hard': 0.46, 'error_frac': 0.55,
               'avoid_block': 0.40, 'block_chance': 0.62, 'tip_chance': 0.14,
               'reach_bonus': 6,  'attack_spread': 1.5, 'serve_aggr': 0.55},
    'hard':   {'dig_base': VB_AI_DIG_BASE, 'dig_hard': VB_AI_DIG_HARD,
               'error_frac': VB_AI_ERROR_FRAC, 'avoid_block': VB_AI_AVOID_BLOCK,
               'block_chance': VB_AI_BLOCK_CHANCE, 'tip_chance': VB_AI_TIP_CHANCE,
               'reach_bonus': VB_AI_REACH_BONUS, 'attack_spread': 1.0, 'serve_aggr': 1.0},
}

# Defence — who takes the first ball (agency: you take balls near you).
VB_PLAYER_TAKE_RADIUS = 120  # you (non-setter) take any ball landing within this of you
VB_SETTER_TAKE_RADIUS = 70   # the setter just plays balls this close (no annoying dodge)

# Player movement — momentum (accelerate to held vector, decel to a snappy stop).
VB_TOP_SPEED       = 224     # px/s top free-running speed
VB_ACCEL           = 1500    # px/s^2 ramp toward the held direction
VB_DECEL           = 1900    # px/s^2 stop (> accel = crisp halts, no float)

# Dive — a committed one-tap burst to chase wide balls (key: C).
VB_DIVE_SPEED      = 470     # px/s during the dive
VB_DIVE_DURATION   = 0.22    # s of burst
VB_DIVE_COOLDOWN   = 0.60    # s before you can dive again
VB_DIVE_REACH      = 20      # px bonus contact radius while diving / recovering
VB_DIVE_RECOVER    = 0.18    # s of low-control recovery after the burst

# Aim-step — the spike hero beat: brief slow-mo to steer a reticle + time power.
VB_AIMSTEP_SLOWMO  = 0.20    # gameplay time-scale during the aim-step
VB_AIMSTEP_WINDOW  = 0.95    # real seconds before it auto-fires
VB_RETICLE_SPEED   = 250     # px/s the reticle steers (real time, crisp)

# Spike power — a meter that sweeps continuously upward; the CENTRED sweet band is
# a perfect kill (red -> orange -> green -> orange -> red, best in the middle).
VB_SPIKE_METER_SPEED = 1.3   # power meter sweeps 0..1 this many times per second (wraps)
VB_SPIKE_SWEET_LO    = 0.42  # sweet-spot band low edge (PERFECT between lo..hi, centred)
VB_SPIKE_SWEET_HI    = 0.58  # sweet-spot band high edge
VB_SPIKE_MIN_POWER   = 0.40  # power floor for a badly mistimed hit (the red edges)
VB_AIM_OUT           = 28    # px the reticle may drift past a sideline (wide-out, in system)
VB_OUT_LAND          = 30    # px past the line an "out" ball lands (so it reads as out)

# Serve — two stages: lock depth (power meter), then sweep a left/right marker.
VB_SERVE_METER_SPEED = 1.5   # depth meter sweeps 0..1 this many times per second
VB_SERVE_LAT_SPEED   = 1.3   # lateral marker sweeps 0..1 this many times per second
VB_SERVE_NET_MAX     = 0.22  # power below this drops into the net (fault)
VB_SERVE_OUT_MIN     = 0.88  # power above this sails long (fault)
VB_SERVE_GREEN       = (0.50, 0.74) # power band for a fast, aggressive serve (the green zone)
VB_SERVE_PEAK        = (190, 96)    # arc peak: floaty (orange edge) .. flat & fast (green)
VB_SERVE_DUR         = (1.55, 0.74) # arc duration: floaty slow (edge) .. fast bomb (green)

# Tutorial pacing — see the ball/players finish each rep before "Nice!"
VB_TUT_RESOLVE       = 2.0   # s cap the action plays out (ends early once the ball settles)
VB_TUT_SUCCESS       = 1.0   # s the "Nice!" banner holds before the next rep
VB_TUT_FAIL          = 1.5   # s the "redo" banner holds before retrying

# Attack — sets go to a contact point AT the net; tip is a quick poke just over it.
VB_NET_CONTACT       = 26    # px from the net where the hitter attacks
VB_TIP_PEAK          = 56    # arc peak of a tip (flatter -> quicker)
VB_TIP_DUR           = 0.72  # arc duration of a tip (snappy, not a slow lob)
VB_TIP_DROP          = 32    # px past the net a tip lands

# Block — a free jump at the net (no slow-mo); outcome by how square you are.
VB_BLOCK_DURATION    = 0.30  # airborne window — short, so you must time the jump
VB_TUT_BLOCK_DURATION = 0.40 # slightly more forgiving block window in the tutorial
VB_BLOCK_Y_BAND      = 26    # px band around the net where an airborne blocker can stuff the ball
VB_BLOCK_COOLDOWN    = 0.4   # cooldown after a block jump
VB_BLOCK_REACH       = 28    # horizontal reach at the net
VB_BLOCK_NET_DIST    = 46    # how close to the net you must be to jump a block
VB_BLOCK_SQUARE      = 0.30  # within this fraction of reach -> a clean stuff
VB_BLOCK_SAVE_CHANCE = 0.25  # chance the attacker digs up a stuffed ball (rally on)
VB_BLOCK_DEFLECT_ROOF = 0.4  # of glancing blocks, fraction that roof onto your court
VB_BLOCK_OUT_CHANCE  = 0.3   # of glancing blocks, fraction that deflect out (attacker's point)

# Scene configs — scenes are defined in tile coordinates.
# walkable_cols / walkable_rows are inclusive ranges.
# Add 'exits' to wire up transitions without touching code.
SCENE_CONFIGS = {
    'gym': {
        'id': 1,
        'walkable_cols': (1, 18),
        'walkable_rows': (1, 13),
        # up: through the double doors at the top (cols 8-11)
        'exits': {'up': {'scene': 5, 'cols': (8, 11)}},
        'entry_points': {'down': (9, 1)},
        'objects': {
            'trees': [], 'rocks': [],
            'ball_baskets': [(2, 7), (17, 7)],
            'james': [(5, 7)], 'dan': [(14, 7)],
            'matt': [(3, 4)],
            'nat': [(16, 4)],
            'leonard': [(3, 10)],
            'benches': [(1, 2, 5), (1, 8, 5), (18, 2, 5), (18, 8, 5)],
        },
    },
    'king_st': {
        'id': 2,
        'map_cols': 180,
        'walkable_cols': (0, 179),
        'walkable_rows': (4, 10),
        'exits': {
            'down': {'scene': 7, 'cols': (3, 5)},
            # two doors on the north side: the Salutation (col 97) and the
            # Wetherspoons / William Morris (the far east frontage, cols 176-177)
            'up': [
                {'scene': 3, 'cols': (97, 97)},
                {'scene': 10, 'target': (9, 13), 'cols': (176, 177)},
            ],
        },
        'entry_points': {'down': (4, 10)},
        'objects': {
            'trees': [
                (5, 4), (16, 4), (30, 4), (38, 4), (50, 4),
                (56, 4), (68, 4), (75, 4), (84, 4), (95, 4),
                (8, 10), (20, 10), (35, 10), (48, 10),
                (58, 10), (70, 10), (84, 10), (94, 10),
            ],
        },
    },
    'salutation': {
        'id': 3,
        # Wide main bar room (rows 6-12) opening into a NARROWER rear conservatory
        # wing (cols 10-16, rows 1-5) on the right; the rear-left is outside.
        'walkable_cols': (2, 16),
        'walkable_rows': (1, 12),
        'exits': {
            # down: out the front door onto King St (door cols 8-11)
            'down': {'scene': 2, 'target': (97, 4), 'cols': (8, 11)},
            # up: through the bi-fold garden doors at the far-right of the wing
            'up': {'scene': 4, 'cols': (14, 16)},
        },
        'entry_points': {'up': (9, 11)},
        'objects': {'barkeep': [(3, 8)]},
    },
    'garden': {
        'id': 4,
        # Compact single-screen walled garden: pub conservatory + loose-chair
        # foreground (left), a contiguous pillared booth run lining both walls
        # with the communal table central, deep planting close at the right.
        'walkable_cols': (1, 16),
        'walkable_rows': (1, 13),
        # left: back into the pub through the conservatory doors (rows 6-8)
        'exits': {'left': {'scene': 3, 'target': (15, 1), 'rows': (6, 8)}},
        'entry_points': {'up': (2, 7)},
        'objects': {},
    },
    'corridor': {
        'id': 5,
        'walkable_cols': (1, 18),
        'walkable_rows': (4, 13),
        'exits': {
            # right: out the east end of the hallway (rows 4-6)
            'right': {'scene': 6, 'rows': (4, 6)},
            # down: down the stem to the gym doors (cols 8-11)
            'down': {'scene': 1, 'cols': (8, 11)},
        },
        'entry_points': {
            'up': (10, 13),
            'left': (18, 5),
        },
        'objects': {},
    },
    'reception': {
        'id': 6,
        'walkable_cols': (1, 14),
        'walkable_rows': (5, 10),
        'exits': {
            # left/right doors sit at rows 6-7
            'left': {'scene': 5, 'rows': (6, 7)},
            'right': {'scene': 8, 'rows': (6, 7)},
        },
        'entry_points': {
            'right': (2, 7),
            'left': (14, 7),
        },
        'objects': {},
    },
    'courtyard': {
        'id': 7,
        'walkable_cols': (3, 16),
        'walkable_rows': (2, 12),
        'exits': {
            # up: through the gap between the buildings where the path runs (cols 9-10)
            'up': {'scene': 2, 'target': (4, 10), 'cols': (9, 10)},
            # Door back to courts sits at the foot of the central path (col 10),
            # one column off the col-9 arrival from courts so a held Down key
            # can't re-trigger it.
            'down': {'scene': 9, 'target': (5, 13), 'cols': (10, 10)},
        },
        'entry_points': {
            'up': (10, 11),
            'down': (10, 3),
        },
        'objects': {},
    },
    'passage': {
        'id': 8,
        'walkable_cols': (1, 18),
        'walkable_rows': (5, 12),
        'exits': {
            # left: out the reception door at the bottom-left (row 11)
            'left': {'scene': 6, 'rows': (11, 11)},
            'right': {'scene': 9, 'target': (3, 3), 'rows': (5, 7)},
        },
        'entry_points': {
            'right': (1, 11),
            'left': (17, 6),
        },
        'objects': {},
    },
    'courts': {
        'id': 9,
        'walkable_cols': (2, 16),
        'walkable_rows': (2, 14),
        'exits': {
            'left': {'scene': 8, 'target': (17, 6), 'rows': (2, 3)},
            # Exit at the bottom-left gate (cols 3,4) drops you at the foot of
            # the courtyard's central path (col 9), one column off the
            # courtyard's return-door so a held Down key won't bounce you back.
            'down': {'scene': 7, 'target': (9, 12), 'cols': (3, 4)},
        },
        'entry_points': {
            'right': (3, 3),
            'down': (10, 13),
        },
        'objects': {},
    },
    'wetherspoons': {
        'id': 10,
        'walkable_cols': (1, 18),
        'walkable_rows': (3, 13),
        'exits': {
            # out the front doors back onto King St, by the frontage
            'down': {'scene': 2, 'target': (177, 4), 'cols': (8, 11)},
        },
        'entry_points': {'up': (9, 13)},
        'objects': {},
    },
    # Volleyball minigame — self-contained real-time scene (free movement, own
    # input). The tile grid is unused; actors move on free pixel coordinates.
    'court': {
        'id': 11,
        'walkable_cols': (1, 18),
        'walkable_rows': (1, 13),
        'exits': {},
        'entry_points': {},
        'objects': {},
    },
}


# End-of-week star rating, earned from how many volleyball attempts a win took.
def stars_for_attempts(attempts: int) -> int:
    if attempts < 3:
        return 5
    if attempts < 5:
        return 4
    if attempts < 10:
        return 3
    if attempts < 15:
        return 2
    return 1


# The story is a list of WEEKS, each with an ordered list of beats; overall beat
# order == progression. StoryManager flattens these. A beat gates movement/exits
# and scripts dialogue/cutscenes; it completes when its 'advance_when' flag gets
# set (None = terminal). Beat keys:
#   objective        str   on-screen banner text while this beat is active
#   cutscene         [steps]  scripted sequence run on beat-enter (see systems/cutscene.py)
#   launch_volleyball bool  on beat-enter, drop straight into the 3v3 minigame
#   on_enter_scene   {scene_id: [lines]}  one-shot line when that scene becomes active
#   advance_on_enter scene_id  entering that scene completes the beat
#   on_reach         {scene_id: [(col, row), ...]}  standing on a tile completes the beat
#   dialogue         {(col, row): [lines]}  story line for the object on that tile
#   talk             {name: [lines]}  line said when you talk to a seated follower
#   talk_default     [lines]  fallback follower line (if not in 'talk')
#   party            'form' | {'settle': {scene_id: [(col, row), ...]}}  spawn / seat the crew
#   locked_exits     {scene_id: 'all' | ['up', 'down', ...]}  doors sealed this beat
#   confine          {scene_id: ((col0, row0), (col1, row1))} | None  sub-region held to
#   end_week         'down'|...  leaving the scene this way ends the week (results screen)
#   advance_when     flag name that completes the beat (None = final beat)
#   locked_msg       [lines]  shown when a sealed exit is bumped
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
                    ('say', ["Saturday morning. The sports hall hums with the",
                             "squeak of fresh trainers on the floor."]),
                    ('say', ["Sarah and Nat walk in through the doors."]),
                    ('say', ["So... what's the plan?"], "Nat"),
                    ('say', ["Let's grab a volleyball and warm up",
                             "before the others get here.",
                             "There should be one in the ball baskets."], "Sarah"),
                ],
                'checklist': {
                    (2, 7):  {'flag': 'w1_basket_near',
                              'lines': ["You dig through the near basket... nothing."]},
                    (17, 7): {'flag': 'w1_basket_far',
                              'lines': ["You check the far basket... nothing."]},
                },
                'check_more': ["\"Empty? Check the other basket.\""],
                'check_done': ["\"Great. No balls anywhere. Brilliant start.\""],
                'checked_again': ["You already checked this one — still empty."],
                'advance_when': 'w1_baskets_done',
                'locked_msg': ["Grab a ball first — check the baskets."],
            },
            {
                'name': 'leonard_offer',
                'objective': None,
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('say', ["I HAVE A BALL! You can play with us!"], "Leonard"),
                    ('say', ["Furthermore, I am tall AND German."], "Leonard"),
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
                    ('say', ["Six of us — so it's three on three.",
                             "You and me and Matt against Leonard's lot."], "Dan"),
                    ('ask', "How are we playing it?", {
                        'Easy': ('flag', 'w1_diff_easy'),
                        'Medium': ('flag', 'w1_diff_medium'),
                        'Hard': ('flag', 'w1_diff_hard'),
                    }, "Dan"),
                    ('ask', "Want a quick warm-up to learn the controls first?", {
                        'Yes please': [('flag', 'w1_want_tut'), ('flag', 'w1_vb_set')],
                        "I'm good": ('flag', 'w1_vb_set'),
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
                'on_enter_scene': {10: ["This isn't The Salutation — wrong pub!",
                                        "Head back out and find the right door."]},
                'locked_exits': {},
                'advance_when': 'w1_at_pub',
            },
            {
                'name': 'pub_queue',
                'objective': 'Get a round in',
                'locked_exits': {3: ['down', 'up']},
                'cutscene': [
                    ('say', ["The whole gang piles into The Salutation."]),
                    ('move', {'james': (5, 9), 'dan': (6, 9),
                              'matt': (5, 10), 'leonard': (6, 10), 'nat': (6, 11)}),
                    ('say', ["Six pints and whatever they're having!"], "Dan"),
                    ('walk', 'leonard', (4, 8)),
                    ('walk', 'leonard', (7, 8)),
                    ('walk', 'matt', (4, 8)),
                    ('walk', 'matt', (9, 8)),
                    ('say', ["Cheers!"], "Matt"),
                    ('walk', 'dan', (4, 8)),
                    ('walk', 'dan', (11, 8)),
                    ('walk', 'james', (4, 8)),
                    ('walk', 'james', (13, 8)),
                    ('say', ["Just you two left."], "Dan"),
                    ('walk', 'sarah', (4, 8)),
                    ('say', ["Two more over here, please."], "Sarah"),
                    ('walk', 'nat', (5, 9)),
                    ('walk', 'sarah', (9, 11)),
                    ('walk', 'nat', (7, 11)),
                    ('settle',),
                    ('flag', 'w1_seated'),
                ],
                'advance_when': 'w1_seated',
            },
            {
                'name': 'gifts',
                'objective': None,
                'locked_exits': {3: ['down', 'up']},
                'cutscene': [
                    ('say', ["Matt rummages around in his bag.",
                             "Hey — I got you guys stuff from Comic Con!"], "Matt"),
                    ('say', ["(oh yeah)", "(uh oh)"], "James"),
                    ('say', ["I got two of your fave characters —",
                             "Denji AND Luffy figures!"], "Matt"),
                    ('say', ["(Is this guy tryna set me up or what)",
                             "...hey, thanks man."], "James"),
                    ('say', ["And for you, Dan, I found some really cool art..."], "Matt"),
                    ('say', ["Matt unfurls a HUGE poster of Levi Ackerman."]),
                    ('say', ["(LMAO ok — coulda been worse)"], "James"),
                    ('say', ["Dude... ... ...", "...thanks!"], "Dan"),
                    ('say', ["..."]),
                    ('flag', 'w1_gifts'),
                ],
                'advance_when': 'w1_gifts',
            },
            {
                'name': 'where_from',
                'objective': None,
                'locked_exits': {3: ['down', 'up']},
                'cutscene': [
                    ('ask', "So... where are you from?", {
                        'MI babyyyy': [
                            ('say', ["oh that's cool", "...where the hell is that?"],
                             "James")],
                        'I have an inground pool': [
                            ('say', ["I definitely didn't ask you that.",
                                     "What does that even mean — like it's in the ground?",
                                     "That's just a normal pool, right?"], "James")],
                    }, "James"),
                    ('flag', 'w1_chat'),
                ],
                'advance_when': 'w1_chat',
            },
            {
                'name': 'wind_down',
                'objective': 'Say your goodbyes and head out',
                'locked_exits': {3: ['up']},
                'end_week': 'down',
                'cutscene': [
                    ('say', ["You're feeling pretty tired.",
                             "Might be time to head out."]),
                ],
                'talk_default': ["Cool — see ya later!"],
                'talk': {'dan': ["Get home safe!"],
                         'matt': ["Laters! Enjoy the figures haha"]},
                'advance_when': 'w1_left',
            },
        ],
    },
    {
        'week': 2,
        'title': 'Week 2',
        'beats': [
            {
                'name': 'week2_start',
                'objective': None,
                'on_enter_scene': {3: ["Week 2 — coming soon."]},
                'advance_when': None,
            },
        ],
    },
]


# Post-night phone thread shown after the Week 1 results card (James <-> Dan).
# See systems/screens.py Phone for the entry schema.
PHONE_THREAD = [
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
