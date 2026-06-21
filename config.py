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

# Follower party formation — the crew trail the player in staggered pairs (more
# natural than a single-file conga). See systems/party.py.
PARTY_GROUP_SIZE = 2    # followers per rank (a pair)
PARTY_RANK_GAP   = 2    # breadcrumb steps between successive ranks (the stagger)
PARTY_LATERAL    = 30   # px between a pair (each steps half this to its side)

# Dialogue typewriter (Undertale-style)
DIALOGUE_CPS  = 45.0    # characters revealed per second
DIALOGUE_FAST = 4.0     # multiplier while X (cancel) is held to speed up text

# ── Audio ────────────────────────────────────────────────────────────────────
# One streamed music track at a time; drop .ogg files into assets/ (see MusicPlayer).
ASSET_DIR     = os.path.join(os.path.dirname(__file__), 'assets')
MUSIC_VOLUME  = 0.5     # 0..1 background-music level
MUSIC_FADE_MS = 600     # fade applied on play-in / stop, in ms
SFX_VOLUME    = 0.55    # 0..1 sound-effects level
WHISTLE_VOLUME = 1.0    # the loud recorded whistle (whistle_loud) — overworld/plot only
VB_MUSIC      = os.path.join(ASSET_DIR, 'vball_theme.ogg')  # volleyball match theme (not the tutorial)
KING_ST_MUSIC = os.path.join(ASSET_DIR, 'king_st.ogg')     # plays while on King Street (scene 2)
GYM_MUSIC     = os.path.join(ASSET_DIR, 'gym_theme.ogg')   # plays while in the gym overworld (scene 1)
SALUTATION_MUSIC = os.path.join(ASSET_DIR, 'salutation.ogg')  # the Salutation pub interior (scene 3)
GARDEN_MUSIC  = os.path.join(ASSET_DIR, 'garden.ogg')      # the Salutation beer garden (scene 4)
LATIMER_MUSIC = os.path.join(ASSET_DIR, 'latimer_upper_school.ogg')  # school grounds, not the gym (5-9)
WETHERSPOONS_MUSIC = os.path.join(ASSET_DIR, 'wetherspoons.ogg')  # the Wetherspoons (scene 10)
DIVE_MUSIC    = os.path.join(ASSET_DIR, 'diving.ogg')      # the diving minigame (scene 12)
GAME_OVER_MUSIC = os.path.join(ASSET_DIR, 'game_over.ogg') # the Game Over screen (played once)
MATT_MUSIC    = os.path.join(ASSET_DIR, 'matt_theme.ogg')  # Matt's theme, while he's speaking
CHAPTER_END_MUSIC = os.path.join(ASSET_DIR, 'chapter_end.ogg')  # end-of-chapter results + the finale
INTERLUDE_MUSIC = os.path.join(ASSET_DIR, 'interlude.ogg')   # between-chapter texts-only interludes

# Speaker name -> theme that plays (resuming where it left off) while they talk.
CHARACTER_MUSIC = {'Matt': MATT_MUSIC}

# ── Volleyball minigame (scene 11) ──────────────────────────────────────────
VB_NET_Y           = 240     # net line (centre of the 2:1 court, screen mid-height)
VB_ACTOR_SPEED     = 224     # px/s — AI top speed; equals VB_TOP_SPEED (full player/AI parity)
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
# strength. 'hard' == the tuned constants above. The opponent only differs in skill
# expression (dig success, reaction, attack accuracy, block/tip rates) — never in raw
# capability: reach and movement speed are identical to yours. Chosen per match.
# 'reaction' (s) — a human-like delay before a defender breaks for the read landing
# spot, so a hard/well-placed ball into open court drops before they can cover it
# (they hold their base/zone read until it elapses). Lower = sharper opponent.
VB_DIFFICULTY = {
    'easy':   {'dig_base': 0.80, 'dig_hard': 0.28, 'error_frac': 0.65,
               'avoid_block': 0.15, 'block_chance': 0.18, 'tip_chance': 0.06,
               'attack_spread': 2.4, 'serve_aggr': 0.2,
               'attack_err': 0.14, 'read': 0.25, 'reaction': 0.42},
    'medium': {'dig_base': 0.90, 'dig_hard': 0.46, 'error_frac': 0.55,
               'avoid_block': 0.40, 'block_chance': 0.32, 'tip_chance': 0.14,
               'attack_spread': 1.5, 'serve_aggr': 0.55,
               'attack_err': 0.08, 'read': 0.55, 'reaction': 0.30},
    'hard':   {'dig_base': VB_AI_DIG_BASE, 'dig_hard': VB_AI_DIG_HARD,
               'error_frac': VB_AI_ERROR_FRAC, 'avoid_block': VB_AI_AVOID_BLOCK,
               'block_chance': VB_AI_BLOCK_CHANCE, 'tip_chance': VB_AI_TIP_CHANCE,
               'attack_spread': 1.0, 'serve_aggr': 1.0,
               'attack_err': VB_AI_ATTACK_ERR, 'read': 0.80, 'reaction': 0.20},
    # Ch4 final only — relentless: near-flawless digs, lightning reads, ruthless attack.
    'insane': {'dig_base': 0.99, 'dig_hard': 0.80, 'error_frac': 0.30,
               'avoid_block': 0.80, 'block_chance': 0.55, 'tip_chance': 0.20,
               'attack_spread': 0.7, 'serve_aggr': 1.0,
               'attack_err': 0.02, 'read': 0.95, 'reaction': 0.12},
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
            'leonard': [(16, 7)],        # Leonard's lot — only in Ch1 (absent weeks 2-4)
            'nat': [(8, 1)],             # starts beside Sarah, just inside the doors
            'bailey': [(6, 4)],
            'mayu': [(15, 10)],
            'wallace': [(8, 10)],
            'matus': [(18, 3)],          # the ref, sitting on the right-hand bench
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
                {'scene': 3, 'target': (2, 9), 'cols': (97, 97)},   # -> Salutation (inside front door)
                {'scene': 10, 'target': (9, 13), 'cols': (176, 177)},
            ],
        },
        'entry_points': {'down': (4, 10)},
        # No trees: King St is a paved high street. Street furniture (bollards lining
        # the kerb, bins, a post box) is drawn into the scene background instead.
        'objects': {},
    },
    'salutation': {
        'id': 3,
        # Wide, horizontally-scrolling pub (see scenes/salutation.py + specs): an
        # L-peninsula bar across the top-centre, tartan banquettes along the bottom
        # wall, a glazed conservatory lean-to on the right. Front door off-centre on
        # the WEST edge (off King St); bi-fold garden doors on the EAST edge.
        'map_cols': 34,
        'walkable_cols': (1, 32),
        'walkable_rows': (1, 11),
        'exits': {
            'left': {'scene': 2, 'target': (97, 5), 'rows': (8, 10)},   # front door -> King St (north pavement)
            'right': {'scene': 4, 'target': (2, 7), 'rows': (3, 5)},    # garden doors -> garden
        },
        'entry_points': {'left': (2, 9), 'right': (32, 5)},
        # Milla stands at the right end of the bar (a counter tile, drawn a row back):
        # order from (18, 4) facing up. The entry cutscene walks her to the left end
        # to serve the team, then back here for later "regular" ordering.
        'objects': {'milla': [(18, 3)]},
    },
    'garden': {
        'id': 4,
        # Compact single-screen walled garden: pub conservatory + loose-chair
        # foreground (left), a contiguous pillared booth run lining both walls
        # with the communal table central, deep planting close at the right.
        'walkable_cols': (1, 16),
        'walkable_rows': (1, 13),
        # left: back into the pub through the conservatory doors (rows 6-8)
        'exits': {'left': {'scene': 3, 'target': (32, 5), 'rows': (6, 8)}},
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

# Diving minigame (Ch3) — a "keep it up" digging rally: short balls are fed to your
# side, run under each and dig (or dive for the wide ones). It ramps as the rally
# grows; a dropped ball ends it. Skill = positioning + committing to dives.
DIVE_PLAYER_SPEED = 305      # px/s run speed
DIVE_PLAYER_ACCEL = 2900     # px/s^2 momentum ramp (snappy starts/stops)
DIVE_DIG_REACH    = 46       # px you can dig from a standing position
DIVE_LUNGE_REACH  = 132      # px you can reach with a committed dive
DIVE_FALL_TIME    = 1.30     # base seconds for a fed ball to arc down
DIVE_FALL_MIN     = 0.60     # fastest the feed ramps to
DIVE_DIG_WINDOW   = 0.52     # ball must be this low (s before it lands) to be diggable
DIVE_FEED_GAP     = 0.40     # pause after a dig before the next feed
DIVE_LUNGE_TIME   = 0.52     # how long a dive animation takes
DIVE_LUNGE_HOP    = 18       # px the body lifts at the apex of a dive
DIVE_RESULT_TIME  = 0.9      # verdict pause before the result card
DIVE_TARGET       = 30       # digs that complete the drill (a drop just resets the streak)
DIVE_MAX_FEEDS    = 70       # safety net: the drill always ends after this many fed balls


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
                'locked_exits': {3: ['left', 'right']},
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
                # garden door stays visible, but it's not time for the garden yet in Ch1
                'door_block': {4: ["It's time to go home."]},
                'end_week': 'left',
                'cutscene': [
                    ('say', ["You're feeling pretty tired.",
                             "Might be time to head out."]),
                ],
                'talk_default': ["Cool — see ya!"],
                'talk': {'james': ["See you next week?"],
                         'dan': ["Get home safe!"],
                         'matt': ["Laters! Good to see you."],
                         'nat': ["Byee! Text me when you're home."],
                         'bailey': ["That was really fun. Bye!"],
                         'mayu': ["See you around!"],
                         'wallace': ["Take it easy, yeah?"]},
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
                              'lines': ["Oh hey, what's up.",
                                        "When am I playing? Um... that's a funny story."]},
                    (8, 1):  {'flag': 'w2_g_nat', 'speaker': 'Nat',
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
                    ('sit_all',),
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
                    ('say', ["..."], "James"),
                    ('say', ["So... you speak fluent French."], "James"),
                    ('say', ["Native."], "Nat"),
                    ('say', ["(Oh fuck.) ...lol."], "James"),
                    ('say', ["James slowly backs away..."]),
                    ('walk', 'james', (6, 9)),
                    ('walk', 'james', (1, 9)),          # bolts for the front door
                    ('say', ["...and bolts out the door."]),
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
                'end_week': 'left',
                'locked_exits': {3: ['right']},
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
                    ('move', {'sarah': (14, 5), 'james': (13, 3), 'nat': (13, 4),
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
                    ('move', {'sarah': (14, 5), 'dan': (13, 4),
                              'wallace': (14, 2), 'mayu': (15, 3)}),
                    ('sit', 'sarah', 'up'), ('sit', 'dan', 'right'),
                    ('sit', 'wallace', 'down'), ('sit', 'mayu', 'left'),
                    ('say', ["James is last out. He walks over, pauses..."]),
                    ('walk', 'james', (13, 3)),       # sits by Dan, not the spot beside Sarah
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
