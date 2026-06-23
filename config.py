"""Game configuration constants"""
import os

# Dev tools (chapter-skip / garden-advance cheat keys, dev prints) are OFF in the
# shipped build; run with ANNIV_DEV=1 to enable them while testing.
DEV = os.environ.get('ANNIV_DEV') == '1'

# Closing card shown after the finale (and when loading a completed save).
# Personalise these two lines — they're the last words of the game.
END_DEDICATION = [
    "Thanks for playing.",
    "Here's to us. Happy anniversary.",
]

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
VB_DIG_INSTANT_RADIUS = 108  # a digger breaks for the ball at once — skipping the read/hold — when it
                             # lands this close: a ball clearly theirs by proximity is always played
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
VB_AI_BLOCK_CHANCE = 0.80    # chance the defending setter puts up a block
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
               'avoid_block': 0.15, 'block_chance': 0.80, 'tip_chance': 0.06,
               'attack_spread': 2.4, 'serve_aggr': 0.2,
               'attack_err': 0.14, 'read': 0.25, 'reaction': 0.42},
    'medium': {'dig_base': 0.90, 'dig_hard': 0.46, 'error_frac': 0.55,
               'avoid_block': 0.40, 'block_chance': 0.80, 'tip_chance': 0.14,
               'attack_spread': 1.5, 'serve_aggr': 0.55,
               'attack_err': 0.08, 'read': 0.55, 'reaction': 0.30},
    'hard':   {'dig_base': VB_AI_DIG_BASE, 'dig_hard': VB_AI_DIG_HARD,
               'error_frac': VB_AI_ERROR_FRAC, 'avoid_block': VB_AI_AVOID_BLOCK,
               'block_chance': VB_AI_BLOCK_CHANCE, 'tip_chance': VB_AI_TIP_CHANCE,
               'attack_spread': 1.0, 'serve_aggr': 1.0,
               'attack_err': VB_AI_ATTACK_ERR, 'read': 0.80, 'reaction': 0.20},
    # Ch4 final only — relentless: near-flawless digs, lightning reads, ruthless attack.
    'insane': {'dig_base': 0.99, 'dig_hard': 0.80, 'error_frac': 0.30,
               'avoid_block': 0.80, 'block_chance': 0.80, 'tip_chance': 0.20,
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


# Diving minigame (Ch3) — a "keep it up" digging rally: short balls are fed to your
# side, run under each and dig (or dive for the wide ones). It ramps as the rally
# grows; a dropped ball ends it. Skill = positioning + committing to dives.
# Diving drill (Ch3) — a three-stage dig: STEP (position under the feed), PUSH
# (load your legs on a timing bar), SLIDE (extend/dive on a second timing bar).
# Tuned to be rhythmic and forgiving, NOT a reaction test: feeds land close with
# low, capped variation and the timing tempo is constant every ball, so the rally
# is learnable. The dive is what the SLIDE looks like when you're stretched — it's
# never a button you press.
DIVE_PLAYER_SPEED = 320      # px/s run speed while positioning (the STEP)
DIVE_PLAYER_ACCEL = 3000     # px/s^2 momentum ramp (snappy starts/stops)
DIVE_STEP_TIME    = 1.05     # s of airtime to get under the feed before the swing
DIVE_SWING_PREROLL = 0.18    # s the timing bar shows (needle held at 0) before it sweeps —
                             # a "ready" beat so PUSH/SLIDE never ambush you
DIVE_PUSH_SWEEP   = 0.90     # s for the PUSH needle to cross the bar
DIVE_SLIDE_SWEEP  = 1.00     # s for the SLIDE needle — slower than PUSH, so the rhythm
                             # decelerates into the contact rather than speeding up
DIVE_PUSH_CENTRE  = 0.58     # where on the 0..1 bar the PUSH band sits
DIVE_SLIDE_CENTRE = 0.60     # where the SLIDE band sits
DIVE_BAND_GOOD    = 0.18     # half-width (fraction of bar) of the green 'good' band
DIVE_BAND_PERFECT = 0.05     # half-width of the gold 'perfect' centre
DIVE_SLIDE_CONNECT = 0.30    # minimum SLIDE score to make contact at all — press well
                             # outside the band (even when set) and you drop it
DIVE_SET_GOOD     = 46       # px from the target = a clean standing dig
DIVE_SET_PERFECT  = 20       # px = perfect footwork
DIVE_REACH        = 128      # px the SLIDE can extend to still reach the ball
DIVE_SPREAD_MIN   = 36       # px the feed lands either side of you (first digs)
DIVE_SPREAD_MAX   = 104      # px cap on that offset (nothing lands miles away)
DIVE_SPREAD_GROW  = 6        # px added to the landing spread per dig, up to the cap
DIVE_PERFECT_AT   = 0.86     # blended STEP+PUSH+SLIDE score for a PERFECT (needs all three)
DIVE_NICE_AT      = 0.55     # ...for a NICE; below this still counts as a SHANK
DIVE_DIVE_CAP     = 0.80     # a stretched dive never blends above this (scrappy by nature)
DIVE_LUNGE_TIME   = 0.46     # s the slide/dive animation takes
DIVE_LUNGE_HOP    = 16       # px the body lifts at the apex of a dive
DIVE_FEED_GAP     = 0.45     # pause after a dig before the next feed
DIVE_TARGET       = 12       # digs that complete the drill (a short warm-up before the match)
DIVE_MAX_FEEDS    = 22       # safety net: the drill always ends after this many fed balls
                             # (tight enough that careless play can fall just short)


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
