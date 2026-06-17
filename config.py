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
WHISTLE_VOLUME = 1.0    # Matúš's whistle in the overworld — loud and annoying (cranked)
WHISTLE_GAME_VOLUME = 0.4  # eased right off while he lazily blows it during a match
VB_MUSIC      = os.path.join(ASSET_DIR, 'vball_theme.ogg')  # volleyball match theme (not the tutorial)
KING_ST_MUSIC = os.path.join(ASSET_DIR, 'king_st.ogg')     # plays while on King Street (scene 2)
GYM_MUSIC     = os.path.join(ASSET_DIR, 'gym_theme.ogg')   # plays while in the gym overworld (scene 1)
MATT_MUSIC    = os.path.join(ASSET_DIR, 'matt_theme.ogg')  # Matt's theme, while he's speaking
CHAPTER_END_MUSIC = os.path.join(ASSET_DIR, 'chapter_end.ogg')  # the end-of-chapter results screen

# Speaker name -> theme that plays (restarted) while that character is talking.
CHARACTER_MUSIC = {'Matt': MATT_MUSIC}

# ── Volleyball minigame (scene 11) ──────────────────────────────────────────
VB_NET_Y           = 240     # net line (centre of the 2:1 court, screen mid-height)
VB_ACTOR_SPEED     = 204     # px/s — AI free movement (player uses momentum below)
VB_BACKPEDAL_FACTOR = 0.6    # speed multiplier for movement AWAY from the net (backpedalling is slow)
VB_CONTACT_RADIUS  = 34      # px the actor must be within (ball ground position)
VB_TIMING_WINDOW   = 0.24    # s — "ok" contact window either side of ideal time (spike/set)
# Dig timing (receive): you can contact from EARLY_EDGE before landing through a short
# GRACE after it; IDEAL is the sweet spot; off-timing scales the pass quality down to
# TIME_FLOOR; within GOOD_TOL of ideal the label reflects pass quality, else EARLY/LATE.
VB_DIG_EARLY_EDGE  = 0.40    # s before landing you can first scrape a dig (early = poor pass)
VB_DIG_IDEAL       = 0.12    # s before landing = the timing sweet spot
VB_DIG_GRACE       = 0.12    # s after the ball lands you can still dig it up (a late pass)
VB_DIG_TOL         = 0.20    # quality falls to the floor this far off ideal
VB_DIG_TIME_FLOOR  = 0.62    # worst timing still yields this fraction of the positional pass
VB_DIG_GOOD_TOL    = 0.09    # within this of ideal = "on time" (label by pass quality)
VB_DIG_SWITCH_MARGIN = 26    # px a new digger must be closer than the current one to take over (hysteresis, no thrash)
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
VB_AI_BLOCK_CHANCE = 0.46    # chance the defending setter puts up a block (recompensed after the block-realism pass)
VB_AI_TIP_CHANCE   = 0.16    # chance an in-system AI attack is a tip into the open front
VB_AI_ATTACK_ERR   = 0.04    # chance a 'hard' AI swing is an unforced error (net/out -> point)
VB_OOS_ERROR_MULT  = 1.8     # out-of-system swings miss more often
VB_RALLY_MAX       = 36      # safety cap on touches in a rally: forces it to end (no soft loop)

# Difficulty — scales the OPPONENT (far team) only; your teammates always play at full
# strength. 'hard' == the tuned constants above. Higher dig/block/tip + tighter attack
# spread + more reach = a tougher opponent. Chosen per match (Dan asks before you play).
VB_DIFFICULTY = {
    'easy':   {'dig_base': 0.80, 'dig_hard': 0.28, 'error_frac': 0.65,
               'avoid_block': 0.15, 'block_chance': 0.18, 'tip_chance': 0.06,
               'reach_bonus': 0,  'attack_spread': 2.4, 'serve_aggr': 0.2,
               'attack_err': 0.14, 'read': 0.25},
    'medium': {'dig_base': 0.90, 'dig_hard': 0.46, 'error_frac': 0.55,
               'avoid_block': 0.40, 'block_chance': 0.32, 'tip_chance': 0.14,
               'reach_bonus': 6,  'attack_spread': 1.5, 'serve_aggr': 0.55,
               'attack_err': 0.08, 'read': 0.55},
    'hard':   {'dig_base': VB_AI_DIG_BASE, 'dig_hard': VB_AI_DIG_HARD,
               'error_frac': VB_AI_ERROR_FRAC, 'avoid_block': VB_AI_AVOID_BLOCK,
               'block_chance': VB_AI_BLOCK_CHANCE, 'tip_chance': VB_AI_TIP_CHANCE,
               'reach_bonus': VB_AI_REACH_BONUS, 'attack_spread': 1.0, 'serve_aggr': 1.0,
               'attack_err': VB_AI_ATTACK_ERR, 'read': 0.80},
}

# Defence — who takes the first ball (agency: you take balls near you).
VB_PLAYER_TAKE_RADIUS = 120  # you (non-setter) take any ball landing within this of you
VB_SETTER_TAKE_RADIUS = 70   # the setter just plays balls this close (no annoying dodge)
VB_SETTER_PLAYER_BIAS = 0.6  # chance your team's AI setter sets to YOU (so you get swings)

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
VB_SERVE_DUR         = (1.55, 0.95) # arc duration: floaty slow (edge) .. fast (green); slowed so serves are receivable (fewer aces)

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
VB_BLOCK_NET_DIST    = 46    # net band used to resolve a block (the jump's reach window)
VB_BLOCK_ELIGIBLE    = 20    # how close to the net you must actually be to START a block (else not allowed)
VB_BLOCK_SQUARE      = 0.30  # within this fraction of reach -> a "square" (well-formed) block
# A single block mostly slows/channels; a clean stuff is a minority outcome (realism).
# Square (well-positioned/timed) block outcome split:
VB_BLOCK_SQ_STUFF  = 0.38    # clean stuff -> point
VB_BLOCK_SQ_SOFT   = 0.30    # soft block -> ball slowed over to the blocker's side, playable
VB_BLOCK_SQ_TOOL   = 0.10    # hitter tools it off the block, out -> attacker's point
#                              (remainder 0.22 -> rebound back to the attacker's side, playable)
# Glancing / off-centre block split (stuff collapses, tooling rises):
VB_BLOCK_GL_STUFF  = 0.10
VB_BLOCK_GL_TOOL   = 0.34
VB_BLOCK_GL_SOFT   = 0.20
VB_BLOCK_GL_ROOF   = 0.16
#                              (remainder 0.20 -> rebound to the attacker's side)
VB_AI_TIP_BIAS     = 0.35    # when the AI reads a block, chance it tips (else places around + powers down)

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
            'bailey': [(6, 4)],
            'mayu': [(15, 10)],
            'wallace': [(8, 10)],
            'matus': [(10, 2)],          # the ref, watching from a central bench
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
        'objects': {'milla': [(3, 8)]},
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
    # Diving minigame (Ch3) — another self-contained real-time scene.
    'dive': {
        'id': 12,
        'walkable_cols': (1, 18),
        'walkable_rows': (1, 13),
        'exits': {},
        'entry_points': {},
        'objects': {},
    },
}

# Diving minigame (Ch3) — a silly reaction drill. Deliberately forgiving.
DIVE_ROUNDS = 6
DIVE_BALL_TIME = 1.25        # seconds for a toss to drop to the floor
DIVE_SAVE_FROM = 0.0        # any correct-direction dive saves (wrong side / no dive misses)
DIVE_RESULT_TIME = 0.9      # how long each toss's verdict lingers
DIVE_LUNGE = 64             # px James flops sideways on a dive


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
#   goto             {'scene': id, 'tile': (col,row)}  relocate the player on beat-enter
#   interact_ask     {'who': name, 'steps': [cutscene]}  talk to that NPC to run a choice cutscene
#   checklist item   may carry 'speaker'; 'check_more'/'check_done' suffixes are optional

# Week 2's "ready to start?" prompt — fired both automatically (after greeting) and on
# talking to James again, so declining lets you wander back to him.
_W2_READY_ASK = [
    ('ask', "Sweet — are we ready to start?", {
        'Yes': ('flag', 'w2_ready_done'),
        'No': [('say', ["Oh ok — come back when you're ready."], "James")],
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
    {'who': 'Sarah', 'text': "see thats what we dont want"},
    {'who': 'Sarah', 'text': "\U0001F64F"},
    {'who': 'Sarah', 'text': "no tears today"},
    {'who': 'Sarah', 'text': "also who do i pay or do i pay there"},
    {'who': 'James', 'text': "Friday cryday"},
    {'who': 'James', 'text': "\U0001FAE1"},
    {'who': 'James', 'text': "After the sesh I'll send a msg np"},
    {'who': 'Sarah', 'text': "\U0001FAE1"},
    {'who': 'Sarah', 'text': "yes captain"},
    {'who': 'James', 'text': "See u tmrr", 'react': "❤"},
    {'who': 'Sarah', 'text': "HEY so this is just a warning, i hope ill feel "
                             "better tomorrow but i ate some bad chicken and have "
                             "been quite sick today, i thought it would pass but it "
                             "hasnt yet so just a warning for tomorrow, im so sorry "
                             "in advance if im too sick to make it (im praying that "
                             "wont be the case)"},
    {'who': 'Sarah', 'text': "\U0001F622"},
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
                             "You and me and Matt against Leonard's lot.",
                             "We'll keep it gentle this first time."], "Dan"),
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
                    ('say', ["GG, everyone! I must away — auf Wiedersehen!"], "Leonard"),
                    ('say', ["Leonard strides off into the evening.",
                             "(He is never seen again.)"]),
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
                              'matt': (5, 10), 'nat': (6, 11),
                              'bailey': (4, 9), 'mayu': (4, 10), 'wallace': (4, 11)}),
                    ('say', ["Pints all round — and whatever they're having!"], "Dan"),
                    ('walk', 'matt', (4, 8)),
                    ('walk', 'matt', (9, 8)),
                    ('say', ["Cheers!"], "Matt"),
                    ('walk', 'dan', (4, 8)),
                    ('walk', 'dan', (11, 8)),
                    ('walk', 'james', (4, 8)),
                    ('walk', 'james', (13, 8)),
                    ('say', ["...and squeeze in, you lot!"], "Dan"),
                    ('move', {'bailey': (11, 11), 'mayu': (13, 11), 'wallace': (10, 10)}),
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
                    ('say', ["Hey guys.", "I got you guys stuff...",
                             "From Comic Con!"], "Matt"),
                    ('say', ["(oh yeah)", "...", "(uh oh)",
                             "(...I forgot about this)"], "James"),
                    ('say', ["For you, James..."], "Matt"),
                    ('say', ["Matt rummages around in his bag."]),
                    ('say', ["Here ya go!"], "Matt"),
                    ('say', ["Matt hands over two large anime figurines."]),
                    ('say', ["...", "(Is this guy tryna set me up or what)",
                             "...hey, thanks man.", "This is really cool."], "James"),
                    ('say', ["No worries, dude!",
                             "And I got something for you too, Dan!"], "Matt"),
                    ('say', ["(In front of da hoes??????)"], "Dan"),
                    ('say', ["Matt pulls out a large anime poster."]),
                    ('say', ["Kay, here ya go!"], "Matt"),
                    ('say', ["(LMAO ok — coulda been worse)"], "James"),
                    ('say', ["Dude... ... ..."], "Dan"),
                    ('say', ["Dan looks to James, then back."]),
                    ('say', ["...thanks!"], "Dan"),
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
                    ('say', ["There's a brief lull in conversation...",
                             "You feel a strong urge to fill it."]),
                    ('hub', "", {
                        'In-ground pool': [
                            ('say', ["What the hell is that?"], "James"),
                            ('ask', "Aren't all pools in the ground?",
                             {'Yes': [], 'No': []}, "James"),
                            ('say', ["Somehow that didn't really answer my question.",
                                     "Can I see a picture?"], "James"),
                        ],
                        'Family': [
                            ('say', ["I'm the youngest of 5.",
                                     "My siblings are wayyy older — and I've got "
                                     "5 nieces and nephews."], "Sarah"),
                            ('ask', "Damn — what's that like?",
                             {'Fun': [], 'Not fun': []}, "James"),
                            ('say', ["I can see that.",
                                     "(...man, I suck at socializing)"], "James"),
                        ],
                        'Crazy family': [
                            ('say', ["My sister's in a legal battle with her ex-husband...",
                                     "...and her new boyfriend is #!$%."], "Sarah"),
                            ('say', ["Wow.",
                                     "(I have no idea how to respond to that)"], "James"),
                        ],
                        'Bridge to Canada': [
                            ('say', ["Did you know there's a bridge to Canada you "
                                     "can turn onto by accident...",
                                     "...and then you can't turn off?"], "Sarah"),
                            ('say', ["LMAO that's hilarious.",
                                     "Have you ever taken it?"], "James"),
                            ('say', ["Nah — but my family did, once.",
                                     "They got detained for like 3 hours lol."], "Sarah"),
                            ('say', ["That's pretty funny... (I hope)"], "James"),
                        ],
                    }),
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
                'name': 'w2_arrive',
                'objective': None,
                'goto': {'scene': 1, 'tile': (9, 12)},
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('fade_in', 1.2),
                    ('say', ["Week 2. Another evening at the sports hall."]),
                    ('say', ["Sarah and Nat head in for more volleyball."]),
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
                              'lines': ["Oh hey, what's up.",
                                        "When am I playing? Um... that's a funny story."]},
                    (16, 4): {'flag': 'w2_g_nat', 'speaker': 'Nat',
                              'lines': ["Huh, where did Leonard get to today?",
                                        "(...he was never seen again.)", "(...)",
                                        "(...not in a creepy way tho.)"]},
                    (3, 4):  {'flag': 'w2_g_matt', 'speaker': 'Matt',
                              'lines': ["Good evening, m'lady!", "(Tips fedora.)"]},
                    (15, 10): {'flag': 'w2_g_mayu', 'speaker': 'Mayu',
                               'lines': ["Heyy! Good to see you again.",
                                         "Let's get a win tonight."]},
                    (8, 10): {'flag': 'w2_g_wallace', 'speaker': 'Wallace',
                              'lines': ["Oh — hey.", "Ready when you are."]},
                },
                'checked_again': ["..."],
                'advance_when': 'w2_greeted',
            },
            {
                'name': 'w2_ready',
                'objective': "Talk to James when you're ready",
                'locked_exits': {1: 'all'},
                'cutscene': [
                    ('say', ["Quick heads up — they've stepped it up since last week.",
                             "Proper game tonight. Let's bring it!"], "James"),
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
                    # James & Sarah on the near bench; everyone else round the table,
                    # Mayu & Wallace off at a loose table in their own little chat.
                    ('move', {'james': (9, 9), 'sarah': (10, 9), 'dan': (7, 6),
                              'nat': (12, 6), 'matt': (7, 8), 'bailey': (12, 8),
                              'mayu': (3, 7), 'wallace': (3, 11)}),
                    ('face', 'james', 'up'),
                    ('face', 'sarah', 'up'),
                    ('face', 'dan', 'down'),
                    ('face', 'nat', 'down'),
                    ('face', 'matt', 'down'),
                    ('face', 'bailey', 'down'),
                    ('ask', "So... what do you do right now? Like — in general?", {
                        'I study at Imperial': [
                            ('say', ["Oh, awesome — what are you studying?"], "James"),
                            ('ask', "...", {
                                'Drugs': [('say', ["Huh? ...Oh, right.",
                                                   "Damn, you're super smart."], "James")],
                            }, "Sarah"),
                        ],
                        'Drugs': [('say', ["Huh? ...Oh, right.",
                                           "Damn, you're super smart."], "James")],
                    }, "James"),
                    ('say', ["...hold on. I've heard of Western Blotting.",
                             "...do I want you to explain it in excruciating detail?",
                             "(She is really pretty, after all.)",
                             "...sure. Let's do science!"], "James"),
                    ('fade_out', 1.0),
                    ('wait', 0.9),
                    ('say', ["(Half an hour passes. They discussed Western Blotting.)"]),
                    ('fade_in', 1.0),
                    ('say', ["Okay, okay! So — you take some goo, run it through a "
                             "wiggly machine, and a sticker tells you if the thing's "
                             "in there!"], "James"),
                    ('ask', "Did he get it?", {
                        'Not really': [], 'Not really...': [],
                    }, "Sarah"),
                    ('say', ["Welp. I tried.",
                             "I worked at a Biotech for a while. Didn't work out."], "James"),
                    ('ask', "...", {
                        'Because of the science?': [
                            ('say', ["Uh... you could say that."], "James")],
                        'How come?': [
                            ('say', ["Because of the science, lol."], "James")],
                    }, "Sarah"),
                    ('say', ["I'm late-stage with an Insurtech, so fingers crossed I "
                             "get that!", "...", "I work at a pub right now tho."], "James"),
                    ('say', ["Hey guys — time to come inside!"], "Milla"),
                    ('say', ["Rip. Ok."], "Dan"),
                    ('flag', 'w2_garden_done'),
                ],
                'advance_when': 'w2_garden_done',
            },
            {
                # Inside the Salutation: the chatter resumes, James digs his own
                # grave in French, and Nat happens to be from Martinique.
                'name': 'w2_inside',
                'objective': None,
                'goto': {'scene': 3, 'tile': (9, 11)},
                'locked_exits': {3: 'all'},
                'cutscene': [
                    ('settle',),
                    # Everyone crammed into the big east-wall booth (banquette col 16,
                    # west chairs col 14); Nat's off at a centre table until she clocks it.
                    ('move', {'james': (16, 10), 'sarah': (14, 10), 'dan': (16, 9),
                              'matt': (14, 8), 'bailey': (16, 8), 'mayu': (16, 12),
                              'wallace': (14, 12), 'nat': (9, 9)}),
                    ('face', 'james', 'left'),
                    ('face', 'sarah', 'right'),
                    ('face', 'dan', 'left'),
                    ('say', ["Inside, everyone squeezes into the big booth over "
                             "fresh drinks."]),
                    ('say', ["Yeah, I actually speak pretty good French.",
                             "I'm doing a course on Mondays to keep it up."], "James"),
                    ('say', ["( ! )  Nat's head snaps round."]),
                    ('move', {'nat': (14, 9)}),         # she comes over to the booth
                    ('face', 'nat', 'right'),
                    ('face', 'dan', 'left'),
                    ('face', 'james', 'up'),
                    ('say', ["Oh really? I'm from Martinique!"], "Nat"),
                    ('say', ["..."], "James"),
                    ('say', ["So... you speak fluent French."], "James"),
                    ('say', ["Native."], "Nat"),
                    ('say', ["(Oh fuck.) ...lol."], "James"),
                    ('say', ["James slowly backs away..."]),
                    ('walk', 'james', (13, 11)),
                    ('walk', 'james', (9, 11)),
                    ('walk', 'james', (9, 12)),
                    ('say', ["...and bolts out the door."]),
                    ('face', 'sarah', 'down'),
                    ('say', ["(Ugh, I don't feel great.)",
                             "(...damn, that chicken sucked.)",
                             "(I think I'll head home.)"], "Sarah"),
                    ('flag', 'w2_inside_done'),
                ],
                'advance_when': 'w2_inside_done',
            },
            {
                # Walk out the front door to call it a night -> results + texts.
                'name': 'w2_homeward',
                'objective': 'Head home',
                'end_week': 'down',
                'locked_exits': {3: ['up']},
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
                'card_date': '9 June 2024',
                'advance_when': 'scrims_done',
            },
        ],
    },
    {
        'week': 3,
        'title': 'Week 3',
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
                'party': 'form',
                'locked_exits': {4: 'all'},
                'cutscene': [
                    ('fade_in', 1.0),
                    ('settle',),
                    ('say', ["Afterwards the group pile into the garden — the "
                             "back-left table this time."]),
                    ('move', {'sarah': (3, 4), 'james': (4, 4), 'matt': (2, 3),
                              'dan': (5, 3), 'nat': (3, 2), 'bailey': (6, 4),
                              'mayu': (7, 3), 'wallace': (5, 5)}),
                    ('face', 'sarah', 'up'),
                    ('face', 'james', 'up'),
                    ('say', ["Hm? Your family's visiting in two weeks?"], "Matt"),
                    ('ask', "...", {
                        "Yeah, they're coming to watch you guys play": [],
                        "Yeah, to watch you lot suck at volleyball": [
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
                              'matt': (10, 9), 'bailey': (16, 12), 'mayu': (17, 12),
                              'wallace': (16, 11)}),
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
