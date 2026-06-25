# Engine tunables — the Godot mirror of the pygame `config.py` constants.
extends Node

const TILE_SIZE := 32
const MAP_COLS := 20  # SCREEN_WIDTH  / TILE_SIZE
const MAP_ROWS := 15  # SCREEN_HEIGHT / TILE_SIZE
const SCREEN_WIDTH := 640
const SCREEN_HEIGHT := 480
const TILE_MOVE_SPEED := 280.0  # px/sec during the smooth slide between tiles

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
