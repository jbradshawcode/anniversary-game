# Scene 12 — the Ch3 diving drill (real-time, own input). Port of scenes/dive.py.
# Sarah feeds short balls side-on; each is a three-beat dig: STEP (run under the
# telegraphed ring), PUSH (timing needle), SLIDE (second needle — stretched balls
# dive). Self-contained; on_finish returns to the gym and advances the beat.
#
# Like VolleyCourt, it lives on its own CanvasLayer (Main owns it) and covers the
# overworld. Background / ball / fx are _Layer proxies that defer their _draw back
# here; Sarah and James are real entity nodes positioned each frame. Screen shake
# is baked into each draw (not a node offset) so the full-screen fill never gaps.
class_name DiveGame
extends Node2D

# ── Palette (gym skin, side-on) ────────────────────────────────────────────────
const _WALL := Color8(202, 182, 142)
const _WALL_DK := Color8(184, 163, 122)
const _GFLOOR := Color8(66, 130, 180)
const _GFLOOR_SHEEN := Color8(78, 143, 192)
const _LINE := Color8(248, 248, 248)
const _BALL := Color8(245, 238, 220)
const _BALL_EDGE := Color8(200, 190, 170)
const _GOOD := Color8(120, 230, 140)
const _GOLD := Color8(250, 210, 90)
const _BAD := Color8(240, 120, 120)
const _SHANK := Color8(240, 170, 90)
const _TRACK := Color8(28, 32, 38)
const _LOB_PEAK := 132.0           # how high Sarah's feed arcs

const _READY_Y_OFF := 56.0         # ball hovers this far above the floor when set
const _DIG_Y_OFF := 16.0           # contact height above the floor

const _VERDICTS := {
	"perfect": ["PERFECT!", _GOLD],
	"nice": ["NICE!", _GOOD],
	"shank": ["SHANK!", _SHANK],
}
const _STAGE_LABEL := {
	"step": "STEP — get under it", "push": "PUSH — load your legs",
	"slide": "SLIDE — pass it back!",
}

# ── geometry ───────────────────────────────────────────────────────────────────
var _floor_y := int(Config.SCREEN_HEIGHT * 0.70)   # wall/floor boundary; players stand here
var _sx := 70.0                                    # Sarah (the feeder) on the left
var _left := 152.0
var _right := float(Config.SCREEN_WIDTH - 44)      # James's run range, right of Sarah

# ── runtime state ──────────────────────────────────────────────────────────────
var on_finish := Callable()
var fx := VBFX.new()
var _rng := RandomNumberGenerator.new()
var _phase := "done"               # safe default if drawn before enter()
var _streak := 0
var _best := 0
var _digs := 0
var _feeds := 0
var _px := Config.SCREEN_WIDTH / 2.0
var _pvx := 0.0
var _move_x := 0.0

var _dig_anim := 0.0
var _sarah_toss := 0.0
var _step_hint := 0.0
var _pop = null                    # {x,y,vx,vy} the dug ball flying away, or null
var _verdict = null                # {text,col,t,x,y} floating label, or null
var _tx := 0.0
var _needle := 0.0
var _swing_delay := 0.0
var _step_q := 0.0
var _push_q := 0.0
var _slide_q := 0.0
var _slide_pressed := false
var _bx0 := 0.0
var _step_t := 0.0
var _feed_t := 0.0

var _dive_dir := 1
var _dive_x0 := 0.0
var _dive_x1 := 0.0
var _dive_t := 0.0
var _dive_quality := "shank"
var _dive_scored := false

var _confirm := false
var _cancel := false

# ── visual nodes ───────────────────────────────────────────────────────────────
var _james: James
var _sarah: Player
var _bg: _Layer
var _ballnode: _Layer
var _fxnode: _Layer
var _hud: _Layer
var _font: Font


# A Node2D that defers its _draw to a Callable (so DiveGame keeps the draw code).
class _Layer extends Node2D:
	var fn: Callable
	func _draw() -> void:
		if fn.is_valid():
			fn.call(self)


func _ready() -> void:
	_rng.randomize()
	_font = ThemeDB.fallback_font

	_bg = _Layer.new()
	_bg.fn = _draw_bg
	_bg.z_index = -100
	add_child(_bg)

	_sarah = Player.new(0, 0)
	_sarah.z_index = 0
	add_child(_sarah)

	_ballnode = _Layer.new()
	_ballnode.fn = _draw_ball
	_ballnode.z_index = 5
	add_child(_ballnode)

	_james = James.new(0, 0)
	_james.z_index = 10
	add_child(_james)

	_fxnode = _Layer.new()
	_fxnode.fn = _draw_fx
	_fxnode.z_index = 20
	add_child(_fxnode)

	_hud = _Layer.new()
	_hud.fn = _draw_hud
	_hud.z_index = 100
	add_child(_hud)

	enter()
	set_process(true)
	set_process_unhandled_input(true)


# ── Setup ──────────────────────────────────────────────────────────────────────
func enter() -> void:
	_sarah.facing = "right"
	fx = VBFX.new()
	_reset_state()
	_phase = "intro"               # learn the controls; Z starts the first feed


func _reset_state() -> void:
	_px = Config.SCREEN_WIDTH / 2.0
	_pvx = 0.0
	_move_x = 0.0
	_streak = 0
	_best = 0
	_digs = 0
	_feeds = 0
	_dig_anim = 0.0
	_sarah_toss = 0.0
	_step_hint = 0.0
	_pop = null
	_verdict = null
	_tx = _px
	_needle = 0.0
	_swing_delay = 0.0             # the "ready" beat before a bar starts sweeping
	_step_q = 0.0
	_push_q = 0.0
	_slide_q = 0.0
	_slide_pressed = false


func _restart() -> void:
	_reset_state()
	_phase = "intro"


# ── feed / outcomes ────────────────────────────────────────────────────────────
func _feed_or_end() -> void:
	if _feeds >= Config.DIVE_MAX_FEEDS:
		_phase = "done"
	else:
		_toss()


func _toss() -> void:
	_feeds += 1
	var spread: float = minf(Config.DIVE_SPREAD_MAX, Config.DIVE_SPREAD_MIN + Config.DIVE_SPREAD_GROW * _digs)
	var offset := _rng.randf_range(0.45, 1.0) * spread * (1.0 if _rng.randf() < 0.5 else -1.0)
	var margin := 24.0
	_tx = clampf(_px + offset, _left + margin, _right - margin)
	_bx0 = _sx                                     # the ball leaves Sarah's hands
	_step_t = 0.0
	_needle = 0.0
	_swing_delay = 0.0
	_step_q = 0.0
	_push_q = 0.0
	_slide_q = 0.0
	_slide_pressed = false
	_sarah_toss = 0.18                             # her little pass motion
	_pop = null
	_phase = "step"
	Audio.sfx("set")


# ── geometry of the fed ball ───────────────────────────────────────────────────
func _ball_pos() -> Vector2:
	var ready_y := _floor_y - _READY_Y_OFF
	var dig_y := _floor_y - _DIG_Y_OFF
	if _phase == "step":
		var t := _step_t
		var ease := 1.0 - (1.0 - t) * (1.0 - t)
		var x := _bx0 + (_tx - _bx0) * ease
		var hand_y := _floor_y - 24.0
		var y := hand_y + (ready_y - hand_y) * t - _LOB_PEAK * sin(PI * t)
		return Vector2(x, y)
	if _phase == "push":
		return Vector2(_tx, ready_y + (dig_y - ready_y) * (0.5 * _needle))
	if _phase == "slide":
		return Vector2(_tx, ready_y + (dig_y - ready_y) * (0.5 + 0.5 * _needle))
	return Vector2(_tx, dig_y)


# ── scoring helpers ────────────────────────────────────────────────────────────
func _band_score(pos: float, centre: float) -> float:
	var d := absf(pos - centre)
	if d <= Config.DIVE_BAND_PERFECT:
		return 1.0
	if d <= Config.DIVE_BAND_GOOD:
		return 1.0 - 0.5 * (d - Config.DIVE_BAND_PERFECT) / (Config.DIVE_BAND_GOOD - Config.DIVE_BAND_PERFECT)
	return maxf(0.0, 0.5 - 2.0 * (d - Config.DIVE_BAND_GOOD))


func _set_score(gap: float) -> float:
	if gap <= Config.DIVE_SET_PERFECT:
		return 1.0
	if gap <= Config.DIVE_SET_GOOD:
		return 1.0 - 0.4 * (gap - Config.DIVE_SET_PERFECT) / (Config.DIVE_SET_GOOD - Config.DIVE_SET_PERFECT)
	if gap <= Config.DIVE_REACH:
		return maxf(0.0, 0.6 * (1.0 - (gap - Config.DIVE_SET_GOOD) / (Config.DIVE_REACH - Config.DIVE_SET_GOOD)))
	return 0.0


# ── input ──────────────────────────────────────────────────────────────────────
func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_Z, KEY_ENTER:
			_confirm = true
		KEY_X:
			_cancel = true


func _handle_action(confirm: bool) -> void:
	if _phase == "done":                           # drill over
		var won := _digs >= Config.DIVE_TARGET     # won -> Z/X continue; short -> Z Retry, X give up
		if confirm and not won:
			_restart()
		elif on_finish.is_valid():                 # confirm or cancel -> finish
			on_finish.call()
		return
	if not confirm:
		return
	if _phase == "intro":
		_toss()
	elif _phase == "step":                         # too early — the ball's still up
		_step_hint = 0.6
		fx.shake(2, 0.12)
	elif _phase == "push":
		if _swing_delay <= 0:                       # ignore presses during the ready beat
			_push_q = _band_score(_needle, Config.DIVE_PUSH_CENTRE)
			_enter_slide()
	elif _phase == "slide":
		if _swing_delay <= 0:
			_slide_pressed = true
			_slide_q = _band_score(_needle, Config.DIVE_SLIDE_CENTRE)
			_resolve()
	elif _phase == "over":                          # acknowledge the drop, feed on
		_streak = 0
		_feed_or_end()


func _enter_slide() -> void:
	_needle = 0.0
	_swing_delay = Config.DIVE_SWING_PREROLL
	_phase = "slide"
	Audio.sfx("serve")


# ── resolve a dig ──────────────────────────────────────────────────────────────
func _resolve() -> void:
	var gap := absf(_px - _tx)
	# How far you extend is set by how well you loaded (PUSH) and reached (SLIDE):
	# a clean swing covers the full reach, a sloppy one barely leaves your stance.
	# Good footwork (small gap) reaches regardless, so timing only bites when stretched.
	var power := 0.35 * _push_q + 0.65 * _slide_q
	var eff_reach := Config.DIVE_SET_GOOD + (Config.DIVE_REACH - Config.DIVE_SET_GOOD) * power
	if not _slide_pressed or _slide_q < Config.DIVE_SLIDE_CONNECT or gap > eff_reach:
		_miss()                                    # whiffed the contact, or couldn't get there
		return
	var diving := gap > Config.DIVE_SET_GOOD
	var combine := 0.34 * _step_q + 0.33 * _push_q + 0.33 * _slide_q
	if diving:
		combine = minf(combine, Config.DIVE_DIVE_CAP)   # a scrappy dive never reads "perfect"
	var quality := ("perfect" if combine >= Config.DIVE_PERFECT_AT else
		"nice" if combine >= Config.DIVE_NICE_AT else "shank")
	if diving:
		_start_dive(quality)
	else:
		_dig_anim = 0.22
		_score(quality, _tx)
		_after_contact()


func _score(quality: String, x: float) -> void:
	_digs += 1
	_streak += 1
	_best = maxi(_best, _streak)
	Audio.sfx("dig")
	fx.emit_burst(x, _floor_y - 16, Color8(180, 220, 255), 9, 130)
	_pop = {"x": x, "y": float(_floor_y - 16),
		"vx": (_sx - x) * 0.9, "vy": -320.0}        # dug back up towards Sarah
	var v: Array = _VERDICTS[quality]
	_verdict = {"text": v[0], "col": v[1], "t": 0.7, "x": x, "y": float(_floor_y - 48)}


func _after_contact() -> void:
	if _digs >= Config.DIVE_TARGET:
		_phase = "done"
	else:
		_phase = "feed"
		_feed_t = Config.DIVE_FEED_GAP


func _start_dive(quality: String) -> void:
	_phase = "dive"
	_dive_dir = 1 if _tx >= _px else -1
	_dive_x0 = _px
	_dive_x1 = clampf(_tx, _left, _right)
	_dive_t = 0.0
	_dive_quality = quality
	_dive_scored = false
	_pvx = 0.0
	fx.emit_dust(_px, _floor_y, 7)


func _miss() -> void:
	var bx := _ball_pos().x
	fx.emit_dust(bx, _floor_y, 8)
	fx.shake(4, 0.2)
	_verdict = null
	_phase = "over"                                # wait for Z, then reset streak and feed on


# ── update ─────────────────────────────────────────────────────────────────────
func _update(dt: float) -> void:
	fx.update(dt)
	if _dig_anim > 0:
		_dig_anim = maxf(0.0, _dig_anim - dt)
	if _sarah_toss > 0:
		_sarah_toss = maxf(0.0, _sarah_toss - dt)
	if _step_hint > 0:
		_step_hint = maxf(0.0, _step_hint - dt)
	if _pop != null:                               # the dug ball flying away
		_pop["vy"] += 900.0 * dt
		_pop["x"] += _pop["vx"] * dt
		_pop["y"] += _pop["vy"] * dt
		if _pop["y"] > Config.SCREEN_HEIGHT:
			_pop = null
	if _verdict != null:                           # PERFECT/NICE/SHANK drifts up and fades
		_verdict["t"] -= dt
		_verdict["y"] -= 34.0 * dt
		if _verdict["t"] <= 0:
			_verdict = null

	if _phase == "step":
		_move_player(dt)
		_step_t += dt / Config.DIVE_STEP_TIME
		if _step_t >= 1.0:
			_step_t = 1.0
			_step_q = _set_score(absf(_px - _tx))
			_needle = 0.0
			_swing_delay = Config.DIVE_SWING_PREROLL    # a ready beat before PUSH sweeps
			_phase = "push"
	elif _phase == "push":
		if _swing_delay > 0:
			_swing_delay = maxf(0.0, _swing_delay - dt)
		else:
			_needle += dt / Config.DIVE_PUSH_SWEEP
			if _needle >= 1.0:                      # let it sweep past — a no-press push scores 0
				_needle = 1.0
				_push_q = 0.0
				_enter_slide()
	elif _phase == "slide":
		if _swing_delay > 0:
			_swing_delay = maxf(0.0, _swing_delay - dt)
		else:
			_needle += dt / Config.DIVE_SLIDE_SWEEP
			if _needle >= 1.0:                      # never pressed slide -> dropped
				_needle = 1.0
				_resolve()
	elif _phase == "dive":
		_update_dive(dt)
	elif _phase == "feed":
		_feed_t -= dt
		if _feed_t <= 0:
			_feed_or_end()


func _move_player(dt: float) -> void:
	var target := _move_x * Config.DIVE_PLAYER_SPEED
	if _pvx < target:
		_pvx = minf(target, _pvx + Config.DIVE_PLAYER_ACCEL * dt)
	else:
		_pvx = maxf(target, _pvx - Config.DIVE_PLAYER_ACCEL * dt)
	_px = clampf(_px + _pvx * dt, _left, _right)
	if (_px <= _left and _pvx < 0) or (_px >= _right and _pvx > 0):
		_pvx = 0.0
	_james.walk_phase += absf(_pvx) * dt * 0.02


func _update_dive(dt: float) -> void:
	_dive_t += dt / Config.DIVE_LUNGE_TIME
	if not _dive_scored and _dive_t >= 0.5:        # contact at full extension
		_dive_scored = true
		_score(_dive_quality, _dive_x1)
		fx.shake(6, 0.26)
	if _dive_t >= 1.0:
		fx.emit_dust(_dive_x1, _floor_y, 10)       # landing slide
		_px = _dive_x1
		_after_contact()


# ── process: input -> sim -> mirror to nodes ───────────────────────────────────
func _process(delta: float) -> void:
	var ax := Input.get_axis("ui_left", "ui_right")
	_move_x = -1.0 if ax < -0.3 else (1.0 if ax > 0.3 else 0.0)

	if _confirm:
		_handle_action(true)
	elif _cancel:
		_handle_action(false)
	_confirm = false
	_cancel = false

	# update() runs every frame (as in dive.py): the per-phase block is a no-op on
	# intro/over/done, but fx, the flying pop ball and the fading verdict still tick.
	_update(delta)

	_place_sarah()
	_place_james()
	_bg.queue_redraw()
	_ballnode.queue_redraw()
	_fxnode.queue_redraw()
	_hud.queue_redraw()


func _place_sarah() -> void:
	var off := fx.offset()
	_sarah.facing = "right"                        # facing James, across the court
	var bob := 4.0 if _sarah_toss > 0 else 0.0     # little toss bob
	_sarah.position = Vector2(_sx + off.x, _floor_y - 14 - bob + off.y)
	_sarah.queue_redraw()


func _place_james() -> void:
	var off := fx.offset()
	var j := _james
	if _phase == "dive":
		var t: float = minf(1.0, _dive_t)
		j.diving = "right" if _dive_dir > 0 else "left"
		var ease := 1.0 - (1.0 - t) * (1.0 - t)
		j.position = Vector2(_dive_x0 + (_dive_x1 - _dive_x0) * ease + off.x,
			_floor_y - 4 - Config.DIVE_LUNGE_HOP * sin(PI * t) + off.y)
	else:
		j.diving = ""
		var crouch := 6.0 if (_dig_anim > 0 or _phase == "push" or _phase == "slide") else 0.0
		j.position = Vector2(_px + off.x, _floor_y - 14 + crouch + off.y)
		if _phase == "step" and absf(_pvx) > 24:
			j.walking = true
			j.facing = "right" if _pvx > 0 else "left"
		else:
			j.walking = false
			j.facing = "up"
	j.queue_redraw()


# ── Draw: background (z -100) — wall + floor + court line + landing ring ────────
func _draw_bg(c: CanvasItem) -> void:
	var off := fx.offset()
	var fy := _floor_y + off.y
	var sw := Config.SCREEN_WIDTH
	var sh := Config.SCREEN_HEIGHT
	c.draw_rect(Rect2(0, 0, sw, sh), _WALL)                            # pale-timber clad wall
	var x := 0
	while x < sw:
		c.draw_line(Vector2(x, 0), Vector2(x, fy), _WALL_DK, 1)
		x += 9
	c.draw_rect(Rect2(0, fy, sw, sh - fy), _GFLOOR)                    # sprung floor
	var i := 0
	while i < sh - _floor_y:
		if (i / 14) % 3 == 0:
			c.draw_rect(Rect2(0, fy + i, sw, 5), _GFLOOR_SHEEN)
		i += 14
	c.draw_line(Vector2(0, fy), Vector2(sw, fy), _LINE, 3)             # court line
	if _phase == "step" or _phase == "push" or _phase == "slide":
		_draw_target(c, off)


func _draw_target(c: CanvasItem, off: Vector2) -> void:
	# The landing ring on the floor — telegraphed the instant the ball is fed.
	var tx := _tx + off.x
	var fy := _floor_y + off.y
	var gap := absf(_px - _tx)
	var set_now := gap <= Config.DIVE_SET_GOOD
	var col := _GOOD if set_now else Color8(210, 196, 150)
	# the ring swells in the last beat of STEP so PUSH doesn't ambush you
	var arriving := _phase == "step" and _step_t > 0.78
	var grow := (6.0 * sin(_step_t * PI * 6)) if arriving else 0.0
	_ell_out(c, tx - 26 - grow, fy - 7, 52 + 2 * grow, 14, col, 2)
	_ell_out(c, tx - 13, fy - 4, 26, 8, col, 1)
	if _phase == "step" and set_now:
		_text(c, tx, fy - 30, "SET", 14, _GOOD, true)


# ── Draw: ball layer (z 5) — pop ball + live fed ball with floor shadow ─────────
func _draw_ball(c: CanvasItem) -> void:
	var off := fx.offset()
	if _pop != null:
		var pp := Vector2(_pop["x"] + off.x, _pop["y"] + off.y)
		c.draw_circle(pp, 8, _BALL)
		c.draw_arc(pp, 8, 0, TAU, 20, _BALL_EDGE, 1)
	var live := (_phase == "step" or _phase == "push" or _phase == "slide"
		or (_phase == "dive" and not _dive_scored))
	if not live:
		return
	var bx: float
	var by: float
	var drop: float
	if _phase == "dive":
		bx = _tx
		by = _floor_y - _DIG_Y_OFF
		drop = 1.0
	else:
		var bp := _ball_pos()
		bx = bp.x
		by = bp.y
		drop = (_step_t if _phase == "step" else                       # 0..1 of the full descent
			0.5 * _needle if _phase == "push" else
			0.5 + 0.5 * _needle)
	bx += off.x
	by += off.y
	var shw := 10.0 + 16.0 * drop
	_ell_fill(c, bx - shw / 2.0, _floor_y + off.y + 2, shw, 6, Color8(12, 16, 18))
	c.draw_circle(Vector2(bx, by), 9, _BALL)
	c.draw_arc(Vector2(bx, by), 9, 0, TAU, 20, _BALL_EDGE, 1)


# ── Draw: fx layer (z 20) — particles + the floating verdict ───────────────────
func _draw_fx(c: CanvasItem) -> void:
	var off := fx.offset()
	fx.draw(c)                                     # particles at raw sim coords (as in dive.py)
	if _verdict != null:
		_text(c, _verdict["x"] + off.x, _verdict["y"] + off.y, _verdict["text"], 24,
			_verdict["col"], true, true)


# ── Draw: HUD layer (z 100), screen-space ──────────────────────────────────────
func _draw_hud(c: CanvasItem) -> void:
	if _phase == "intro":
		_draw_intro(c)
		return
	_draw_hud_text(c)
	if _phase == "push" or _phase == "slide":
		_draw_timing(c)
	if _phase == "done":
		_draw_done(c)


func _draw_hud_text(c: CanvasItem) -> void:
	var sw := Config.SCREEN_WIDTH
	_text(c, sw / 2.0, 16, "DIG RALLY", 28, Color8(56, 48, 36), true)   # dark, on the tan wall
	var col := Color8(44, 110, 56) if _streak >= 5 else Color8(72, 64, 52)
	_text(c, sw / 2.0, 50, "Streak %d   ·   Best %d   ·   %d/%d" % [
		_streak, _best, _digs, Config.DIVE_TARGET], 16, col, true)
	if _phase == "step":
		_text(c, sw / 2.0, _floor_y + 34, _STAGE_LABEL["step"], 16, Color8(236, 240, 244), true)
		if _step_hint > 0:                                              # pressed Z too early
			_text(c, sw / 2.0, _floor_y + 58, "wait for it…", 15, _GOLD, true)
		else:
			_text(c, sw / 2.0, _floor_y + 58, "<-  ->  move", 15, Color8(210, 216, 222), true)
	elif _phase == "over":
		_text(c, sw / 2.0, _floor_y + 26, "DROPPED!", 32, _BAD, true, true)
		_text(c, sw / 2.0, _floor_y + 60, "Z to continue", 16, Color8(236, 240, 244), true)


func _draw_timing(c: CanvasItem) -> void:
	# The PUSH / SLIDE bar: green good band, gold perfect centre, sweeping needle.
	var centre: float = Config.DIVE_PUSH_CENTRE if _phase == "push" else Config.DIVE_SLIDE_CENTRE
	var w := 340.0
	var h := 22.0
	var x0 := Config.SCREEN_WIDTH / 2.0 - w / 2.0
	var y0 := _floor_y + 40
	_text(c, Config.SCREEN_WIDTH / 2.0, y0 - 26, _STAGE_LABEL[_phase], 16, Color8(236, 240, 244), true)
	c.draw_rect(Rect2(x0, y0, w, h), _TRACK)
	c.draw_rect(Rect2(x0 + (centre - Config.DIVE_BAND_GOOD) * w, y0,
		2 * Config.DIVE_BAND_GOOD * w, h), _GOOD)
	c.draw_rect(Rect2(x0 + (centre - Config.DIVE_BAND_PERFECT) * w, y0,
		2 * Config.DIVE_BAND_PERFECT * w, h), _GOLD)
	var ready := _swing_delay > 0                                       # pre-roll: needle parked, dimmed
	var nx := x0 + clampf(_needle, 0.0, 1.0) * w
	c.draw_rect(Rect2(nx - 2, y0 - 5, 4, h + 10),
		Color8(120, 124, 130) if ready else Color8(250, 250, 252))
	c.draw_rect(Rect2(x0, y0, w, h), Color8(250, 250, 252), false, 2)
	_text(c, Config.SCREEN_WIDTH / 2.0, y0 + h + 6, "ready…" if ready else "Z", 15,
		Color8(210, 216, 222), true)


func _draw_intro(c: CanvasItem) -> void:
	var sw := Config.SCREEN_WIDTH
	var sh := Config.SCREEN_HEIGHT
	c.draw_rect(Rect2(0, 0, sw, sh), Color(0, 0, 0, 150.0 / 255))
	var cx := sw / 2.0
	_text(c, cx, sh / 2.0 - 118, "DIG RALLY", 40, Color8(245, 238, 220), true, true)
	var lines := [
		"Sarah feeds you short balls. Keep the rally alive.",
		"Three beats to every dig:",
		"STEP   <-  ->   onto the ring on the floor.",
		"PUSH   Z  in the band as the needle sweeps.",
		"SLIDE  Z  again to pass it back — stretched balls dive.",
		"Drop one and the streak resets. Get to %d digs." % Config.DIVE_TARGET,
	]
	for i in lines.size():
		var ln: String = lines[i]
		var big := ln.begins_with("STEP") or ln.begins_with("PUSH") or ln.begins_with("SLIDE")
		_text(c, cx, sh / 2.0 - 64 + i * 28, ln, 18,
			Color8(228, 232, 238) if big else Color8(200, 204, 212), true)
	_text(c, cx, sh - 44, "Z to start", 18, Color8(245, 238, 220), true)


func _draw_done(c: CanvasItem) -> void:
	var sw := Config.SCREEN_WIDTH
	var sh := Config.SCREEN_HEIGHT
	c.draw_rect(Rect2(0, 0, sw, sh), Color(0, 0, 0, 150.0 / 255))
	var cx := sw / 2.0
	_text(c, cx, sh / 2.0 - 40, "Best rally: %d" % _best, 40, Color8(240, 240, 245), true, true)
	var quip := ("A literal wall." if _best >= 12 else
		"Proper hands on you!" if _best >= 6 else
		"Getting there." if _best >= 2 else
		"Welp. We'll work on it.")
	_text(c, cx, sh / 2.0 + 14, quip, 18, Color8(200, 204, 210), true)
	var prompt: String
	if _digs >= Config.DIVE_TARGET:
		prompt = "Z to continue"
	else:
		_text(c, cx, sh / 2.0 + 42, "%d / %d digs" % [_digs, Config.DIVE_TARGET], 15,
			Color8(180, 184, 190), true)
		prompt = "Z - Retry     X - Give up"
	_text(c, cx, sh - 40, prompt, 16, Color8(170, 174, 180), true)


# ── Draw primitives ────────────────────────────────────────────────────────────
func _ell_out(c: CanvasItem, x: float, y: float, w: float, h: float, col: Color, width: float) -> void:
	c.draw_set_transform(Vector2(x + w / 2.0, y + h / 2.0), 0, Vector2(w / 2.0, h / 2.0))
	c.draw_arc(Vector2.ZERO, 1.0, 0, TAU, 24, col, width / maxf(w, h) * 2.0)
	c.draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


func _ell_fill(c: CanvasItem, x: float, y: float, w: float, h: float, col: Color) -> void:
	c.draw_set_transform(Vector2(x + w / 2.0, y + h / 2.0), 0, Vector2(w / 2.0, h / 2.0))
	c.draw_circle(Vector2.ZERO, 1.0, col)
	c.draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


func _text(c: CanvasItem, x: float, y: float, s: String, size: int, col: Color,
		center := false, shadow := false) -> void:
	var px := x
	if center:
		px -= _text_w(s, size) / 2.0
	if shadow:
		c.draw_string(_font, Vector2(px + 2, y + size + 2), s, HORIZONTAL_ALIGNMENT_LEFT, -1,
			size, Color(0, 0, 0, 0.5))
	c.draw_string(_font, Vector2(px, y + size), s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


func _text_w(s: String, size: int) -> float:
	return _font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
