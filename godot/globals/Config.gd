# Engine tunables — the Godot mirror of the pygame `config.py` constants.
extends Node

const TILE_SIZE := 32
const MAP_COLS := 20  # SCREEN_WIDTH  / TILE_SIZE
const MAP_ROWS := 15  # SCREEN_HEIGHT / TILE_SIZE
const SCREEN_WIDTH := 640
const SCREEN_HEIGHT := 480
const TILE_MOVE_SPEED := 280.0  # px/sec during the smooth slide between tiles

# Supersample factor for the native-art bake (Main._bake): backdrops/player are baked
# at this multiple of world resolution, then the runtime renders them at 1/BAKE_SS with
# LINEAR filtering — SSAA that smooths the procedural art's edges (the project default is
# NEAREST, zoom is 1:1). Single source of truth: the bake side AND the runtime downscale
# both read this, so the two can't drift. 2 is the ceiling on GL Compatibility — KingSt's
# 5760px width × 3 would exceed the 16384 max texture size.
const BAKE_SS := 2

# Dev-only hotkeys (force party / quick save / quick load / demo cutscene) are
# gated behind this — the Godot mirror of pygame's ANNIV_DEV. Off in a shipped build.
static var DEV := OS.get_environment("ANNIV_DEV") == "1"

# ── Audio (mirror of config.py audio block) ───────────────────────────────────
const MUSIC_VOLUME := 0.5        # 0..1 background-music level
const MUSIC_FADE_MS := 600       # fade applied on play-in / stop, in ms
const SFX_VOLUME := 0.55         # 0..1 sound-effects level
const WHISTLE_VOLUME := 1.0      # the loud recorded whistle (whistle_loud) — overworld/plot only
const VB_MUSIC := "res://assets/vball_theme.ogg"            # volleyball match theme (not the tutorial)
const KING_ST_MUSIC := "res://assets/king_st.ogg"          # plays while on King Street (scene 2)
const GYM_MUSIC := "res://assets/gym_theme.ogg"            # plays while in the gym overworld (scene 1)
const SALUTATION_MUSIC := "res://assets/salutation.ogg"    # the Salutation pub interior (scene 3)
const GARDEN_MUSIC := "res://assets/garden.ogg"            # the Salutation beer garden (scene 4)
const LATIMER_MUSIC := "res://assets/latimer_upper_school.ogg"  # school grounds, not the gym (5-9)
const WETHERSPOONS_MUSIC := "res://assets/wetherspoons.ogg"  # the Wetherspoons (scene 10)
const DIVE_MUSIC := "res://assets/diving.ogg"              # the diving minigame (scene 12)
const GAME_OVER_MUSIC := "res://assets/game_over.ogg"      # the Game Over screen (played once)
const MATT_MUSIC := "res://assets/matt_theme.ogg"          # Matt's theme, while he's speaking
const CHAPTER_END_MUSIC := "res://assets/chapter_end.ogg"  # end-of-chapter results + the finale
const INTERLUDE_MUSIC := "res://assets/interlude.ogg"      # between-chapter texts-only interludes

# A speaking character's theme overrides the scene's music while they talk.
const CHARACTER_MUSIC := {"Matt": MATT_MUSIC}

# Closing card shown after the finale (and when loading a completed save).
const END_DEDICATION := [
	"Thanks for playing.",
	"Here's to us. Happy anniversary.",
]


# Star rating for the end-of-week results card: fewer volleyball attempts = more
# stars (mirror of config.stars_for_attempts).
func stars_for_attempts(attempts: int) -> int:
	if attempts < 3:
		return 5
	if attempts < 5:
		return 4
	if attempts < 10:
		return 3
	if attempts < 15:
		return 2
	return 1

const DIALOGUE_CPS := 45.0   # characters revealed per second (typewriter)
const DIALOGUE_FAST := 4.0   # multiplier while X (cancel) is held

# ── Volleyball minigame (mirror of config.py VB_* block) ──────────────────────
const VB_NET_Y := 240
const VB_ACTOR_SPEED := 224.0
const VB_BACKPEDAL_FACTOR := 0.6
const VB_CONTACT_RADIUS := 34.0
const VB_TIMING_WINDOW := 0.24
const VB_DIG_EARLY_EDGE := 0.40
const VB_DIG_IDEAL := 0.12
const VB_DIG_GRACE := 0.12
const VB_DIG_TOL := 0.20
const VB_DIG_TIME_FLOOR := 0.62
const VB_DIG_GOOD_TOL := 0.09
const VB_DIG_SWITCH_MARGIN := 26.0
const VB_DIG_INSTANT_RADIUS := 108.0
const VB_PERFECT_WINDOW := 0.10
const VB_SCORE_TO_WIN := 7
const VB_AI_DIG_BASE := 0.97
const VB_AI_DIG_HARD := 0.62
const VB_AI_ERROR_FRAC := 0.45
const VB_DIG_CLEAN := 0.60
const VB_DIG_SHANK := 0.28
const VB_DIG_MOVE_PEN := 0.45
const VB_DIG_OFFSET_PEN := 0.55
const VB_DIG_DIFF_PEN := 0.40
const VB_OOS_POWER_CAP := 0.5
const VB_OOS_RANGE := 0.42
const VB_AI_AVOID_BLOCK := 0.6
const VB_AI_BLOCK_CHANCE := 0.80
const VB_AI_TIP_CHANCE := 0.16
const VB_AI_ATTACK_ERR := 0.04
const VB_OOS_ERROR_MULT := 1.8
const VB_RALLY_MAX := 36
const VB_PLAYER_TAKE_RADIUS := 120.0
const VB_SETTER_TAKE_RADIUS := 70.0
const VB_SETTER_PLAYER_BIAS := 0.6
const VB_TOP_SPEED := 224.0
const VB_ACCEL := 1500.0
const VB_DECEL := 1900.0
const VB_AIMSTEP_SLOWMO := 0.20
const VB_AIMSTEP_WINDOW := 0.95
const VB_RETICLE_SPEED := 250.0
const VB_SPIKE_METER_SPEED := 1.3
const VB_SPIKE_SWEET_LO := 0.42
const VB_SPIKE_SWEET_HI := 0.58
const VB_SPIKE_MIN_POWER := 0.40
const VB_AIM_OUT := 28.0
const VB_OUT_LAND := 30.0
const VB_SERVE_METER_SPEED := 1.5
const VB_SERVE_LAT_SPEED := 1.3
const VB_SERVE_NET_MAX := 0.22
const VB_SERVE_OUT_MIN := 0.88
const VB_SERVE_GREEN := Vector2(0.50, 0.74)
const VB_SERVE_PEAK := Vector2(190, 96)
const VB_SERVE_DUR := Vector2(1.55, 0.95)
const VB_TUT_RESOLVE := 2.0
const VB_TUT_SUCCESS := 1.0
const VB_TUT_FAIL := 1.5
const VB_NET_CONTACT := 26.0
const VB_TIP_PEAK := 56.0
const VB_TIP_DUR := 0.72
const VB_TIP_DROP := 32.0
const VB_BLOCK_DURATION := 0.30
const VB_TUT_BLOCK_DURATION := 0.40
const VB_BLOCK_Y_BAND := 26.0
const VB_BLOCK_COOLDOWN := 0.4
const VB_BLOCK_REACH := 28.0
const VB_BLOCK_NET_DIST := 46.0
const VB_BLOCK_ELIGIBLE := 20.0
const VB_BLOCK_SQUARE := 0.30
const VB_BLOCK_SQ_STUFF := 0.38
const VB_BLOCK_SQ_SOFT := 0.30
const VB_BLOCK_SQ_TOOL := 0.10
const VB_BLOCK_GL_STUFF := 0.10
const VB_BLOCK_GL_TOOL := 0.34
const VB_BLOCK_GL_SOFT := 0.20
const VB_BLOCK_GL_ROOF := 0.16
const VB_AI_TIP_BIAS := 0.35

const VB_DIFFICULTY := {
	"easy": {"dig_base": 0.80, "dig_hard": 0.28, "error_frac": 0.65,
		"avoid_block": 0.15, "block_chance": 0.80, "tip_chance": 0.06,
		"attack_spread": 2.4, "serve_aggr": 0.2,
		"attack_err": 0.14, "read": 0.25, "reaction": 0.42},
	"medium": {"dig_base": 0.90, "dig_hard": 0.46, "error_frac": 0.55,
		"avoid_block": 0.40, "block_chance": 0.80, "tip_chance": 0.14,
		"attack_spread": 1.5, "serve_aggr": 0.55,
		"attack_err": 0.08, "read": 0.55, "reaction": 0.30},
	"hard": {"dig_base": VB_AI_DIG_BASE, "dig_hard": VB_AI_DIG_HARD,
		"error_frac": VB_AI_ERROR_FRAC, "avoid_block": VB_AI_AVOID_BLOCK,
		"block_chance": VB_AI_BLOCK_CHANCE, "tip_chance": VB_AI_TIP_CHANCE,
		"attack_spread": 1.0, "serve_aggr": 1.0,
		"attack_err": VB_AI_ATTACK_ERR, "read": 0.80, "reaction": 0.20},
	"insane": {"dig_base": 0.99, "dig_hard": 0.80, "error_frac": 0.30,
		"avoid_block": 0.80, "block_chance": 0.80, "tip_chance": 0.20,
		"attack_spread": 0.7, "serve_aggr": 1.0,
		"attack_err": 0.02, "read": 0.95, "reaction": 0.12},
}

# Diving drill (Ch3) — a three-stage dig: STEP (position under the feed), PUSH
# (load your legs on a timing bar), SLIDE (extend/dive on a second timing bar).
# Tuned to be rhythmic and forgiving, NOT a reaction test. See config.py for the
# full design notes; these are the same numbers.
const DIVE_PLAYER_SPEED := 320.0   # px/s run speed while positioning (the STEP)
const DIVE_PLAYER_ACCEL := 3000.0  # px/s^2 momentum ramp (snappy starts/stops)
const DIVE_STEP_TIME := 1.05       # s of airtime to get under the feed before the swing
const DIVE_SWING_PREROLL := 0.18   # s the timing bar shows (needle at 0) before it sweeps
const DIVE_PUSH_SWEEP := 0.90      # s for the PUSH needle to cross the bar
const DIVE_SLIDE_SWEEP := 1.00     # s for the SLIDE needle — slower than PUSH
const DIVE_PUSH_CENTRE := 0.58     # where on the 0..1 bar the PUSH band sits
const DIVE_SLIDE_CENTRE := 0.60    # where the SLIDE band sits
const DIVE_BAND_GOOD := 0.18       # half-width (fraction of bar) of the green 'good' band
const DIVE_BAND_PERFECT := 0.05    # half-width of the gold 'perfect' centre
const DIVE_SLIDE_CONNECT := 0.30   # minimum SLIDE score to make contact at all
const DIVE_SET_GOOD := 46.0        # px from the target = a clean standing dig
const DIVE_SET_PERFECT := 20.0     # px = perfect footwork
const DIVE_REACH := 128.0          # px the SLIDE can extend to still reach the ball
const DIVE_SPREAD_MIN := 36.0      # px the feed lands either side of you (first digs)
const DIVE_SPREAD_MAX := 104.0     # px cap on that offset
const DIVE_SPREAD_GROW := 6.0      # px added to the landing spread per dig, up to the cap
const DIVE_PERFECT_AT := 0.86      # blended STEP+PUSH+SLIDE score for a PERFECT
const DIVE_NICE_AT := 0.55         # ...for a NICE; below this still counts as a SHANK
const DIVE_DIVE_CAP := 0.80        # a stretched dive never blends above this
const DIVE_LUNGE_TIME := 0.46      # s the slide/dive animation takes
const DIVE_LUNGE_HOP := 16.0       # px the body lifts at the apex of a dive
const DIVE_FEED_GAP := 0.45        # pause after a dig before the next feed
const DIVE_TARGET := 12            # digs that complete the drill
const DIVE_MAX_FEEDS := 22         # safety net: the drill always ends after this many feeds
