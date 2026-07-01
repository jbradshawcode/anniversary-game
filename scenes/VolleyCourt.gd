# Scene 11 — 3v3 volleyball minigame (real-time, free movement, own input).
# Port of scenes/court.py. Enlarged top-down court: your team near (bottom),
# opponents far (top), net across the middle. You control one player with momentum
# movement (arrows); the other five are AI. Z = dig/attack/serve/block, X = set,
# C = tip/dump. Launched from the gym coach; on_finish returns there.
#
# Lives on its own CanvasLayer (Main owns it), so the world camera doesn't touch it
# and it covers the overworld. Visuals are child nodes (court/ref/actors/ball draw
# themselves); the dim + reticle + fx + HUD are Layer proxies drawn over the top.
class_name VolleyCourt
extends Node2D

# Role / Pose aliases (mirror VBActor's enums)
const SETTER := VBActor.Role.SETTER
const HITTER_L := VBActor.Role.HITTER_L
const HITTER_R := VBActor.Role.HITTER_R
const _ROLES := [SETTER, HITTER_L, HITTER_R]
const P_READY := VBActor.Pose.READY
const P_RUN := VBActor.Pose.RUN
const P_DIG := VBActor.Pose.DIG
const P_JUMP := VBActor.Pose.JUMP
const P_BLOCK := VBActor.Pose.BLOCK
const P_CELEBRATE := VBActor.Pose.CELEBRATE
const P_PRONE := VBActor.Pose.PRONE

const PHASE_SERVE := 0
const PHASE_RALLY := 1
const PHASE_POINT := 2
const PHASE_OVER := 3

# clockwise rotation: setter -> hitter_r -> hitter_l -> setter
const _CW := {SETTER: HITTER_R, HITTER_R: HITTER_L, HITTER_L: SETTER}

# ── Palette ──────────────────────────────────────────────────────────────────
const _CLAD := Color8(22, 26, 34)
const _FLOOR := Color8(52, 112, 160)
const _FLOOR_CT := Color8(70, 140, 192)
const _FLOOR_ATK := Color8(61, 126, 178)
const _FLOOR_EDGE := Color8(34, 78, 116)
const _LINE := Color8(244, 247, 250)
const _NET_W := Color8(252, 252, 252)
const _NET_BG := Color8(40, 84, 158)
const _NET_MESH := Color8(152, 180, 222)
const _POST := Color8(172, 176, 186)
const _MARK := Color8(250, 230, 120)
const _BANNER := Color8(20, 24, 30)
const _GREEN := Color8(90, 230, 120)
const _RED := Color8(235, 80, 70)
const _GUIDE := Color8(150, 172, 205)
const _PANEL := Color(16.0 / 255, 20.0 / 255, 30.0 / 255, 185.0 / 255)
const _PANEL_BD := Color(92.0 / 255, 122.0 / 255, 168.0 / 255, 130.0 / 255)

# ── Geometry (pixels) — literals from court.py; net Y comes from Config ────────
const _H_L := 150.0
const _H_R := 490.0     # 150 + 340
const _H_T := 6.0
const _H_B := 474.0     # 6 + 468
const _C_L := 206.0
const _C_R := 434.0     # 206 + 228
const _C_T := 26.0
const _C_B := 454.0     # 26 + 428
const _C_W := 228.0
const _ATTACK := 76.0
const _RUN := 40.0
const _CX := 320.0      # court centre x
const _HX := 58.0
const _X_MIN := 166.0   # _C_L - _RUN
const _X_MAX := 474.0   # _C_R + _RUN

# arc tuning: Vector2(peak px, duration s)
const _DIG := Vector2(120, 1.00)
const _SET := Vector2(115, 0.95)
const _SPIKE_AI := Vector2(56, 0.68)
const _REBOUND := Vector2(40, 0.6)

# Tutorial: one mechanic at a time. {hit}/{set}/{move} filled per device in _draw_tut.
const _TUT_STEPS := [
	["serve", "SERVE — tap {hit} for power, then {hit} again to aim. Land it in."],
	["dig", "DIG — run under the ball with the {move}, then {hit} to bump it up."],
	["set", "SET — the pass floats up to you at the net. {set} to set either way."],
	["spike", "SPIKE — run up from the back, {hit} to leap, aim, then {hit} to swing."],
	["block", "BLOCK — move to their hitter and TIME your jump. {hit} to stuff it."],
]

# NET-derived geometry (set in _init from Config.VB_NET_Y)
var _NET := 240.0
var _NEAR_MIN_Y := 252.0
var _NEAR_MAX_Y := 462.0
var _FAR_MIN_Y := 18.0
var _FAR_MAX_Y := 228.0
var _HOME := {}
var _SERVE_POS := {}
var _ROSTERS := {}

# ── runtime state ─────────────────────────────────────────────────────────────
var on_finish := Callable()
var near: Array[VBActor] = []
var far: Array[VBActor] = []
var ball: VolleyBall
var fx := VBFX.new()
var _ref: Node2D
var _rng := RandomNumberGenerator.new()
var _prev_y := 0.0
var _mode := "match"
var _level := "hard"
var _week := 1
var _opp := {}
var _tut = null

var score := [0, 0]
var serving := 0
var phase := PHASE_SERVE
var _await = null               # [kind:String, contactor:VBActor|null] or null
var _crossing := false
var _move := Vector2.ZERO
var _face := Vector2(0, -1)
var _vel := Vector2.ZERO
var _action := false
var _set_pressed := false
var _tip_pressed := false
var _aimstep = null
var _setstep = null
var _in_system := true
var _block_jump := 0.0
var _block_cd := 0.0
var _ai_block_jump := 0.0
var _block_target = null
var _planned_spike = null       # Vector2 or null
var _recv_cache = null          # [key, VBActor]
var _react_t := 0.0
var _was_crossing := false
var _last_contact: VBActor = null
var _touches := 0
var _time_scale := 1.0
var _time_target := 1.0
var _serve_meter := 0.0
var _serve_dir := 1
var _serve_stage := "power"
var _serve_lat := 0.0
var _serve_lat_dir := 1
var _serve_power := 0.5
var _serve_fault := false
var _serve_outcome = null       # [kind, winner, msg]
var _rally_touches := 0
var _dig_grace := 0.0
var _hit_feedback = null        # [label, t]
var _banner := ""
var _timer := 0.0
var _serve_timer := 0.0
var _last_winner := 0
var _intro := true

# ── visual nodes ──────────────────────────────────────────────────────────────
var _world: Node2D
var _play: _Layer
var _ballnode: VolleyBall
var _dim: _Layer
var _top: _Layer
var _hud: _Layer
var _font: Font


# A Node2D that defers its _draw to a Callable (so VolleyCourt keeps the draw code).
class _Layer extends Node2D:
	var fn: Callable
	func _draw() -> void:
		if fn.is_valid():
			fn.call(self)


func _init() -> void:
	_NET = float(Config.VB_NET_Y)
	_NEAR_MIN_Y = _NET + 12.0
	_NEAR_MAX_Y = _H_B - 12.0
	_FAR_MIN_Y = _H_T + 12.0
	_FAR_MAX_Y = _NET - 12.0
	_HOME = {
		0: {SETTER: Vector2(_CX, _NET + 56), HITTER_L: Vector2(_CX - _HX, _C_B - 56),
			HITTER_R: Vector2(_CX + _HX, _C_B - 56)},
		1: {SETTER: Vector2(_CX, _NET - 56), HITTER_L: Vector2(_CX + _HX, _C_T + 56),
			HITTER_R: Vector2(_CX - _HX, _C_T + 56)},
	}
	_SERVE_POS = {0: Vector2(_CX, _C_B - 12), 1: Vector2(_CX, _C_T + 12)}
	# 3v3 rosters by chapter (near = your side, far = opponents). HITTER_R near is
	# always the human. Leonard leaves after Ch1, so Week 2 reshuffles the sides.
	_ROSTERS = {
		1: [{HITTER_R: Player, SETTER: Dan, HITTER_L: Matt},
			{SETTER: James, HITTER_L: Nat, HITTER_R: Leonard}],
		2: [{HITTER_R: Player, SETTER: James, HITTER_L: Nat},
			{SETTER: Dan, HITTER_L: Matt, HITTER_R: Bailey}],
		3: [{HITTER_R: Player, SETTER: James, HITTER_L: Nat},
			{SETTER: Dan, HITTER_L: Matt, HITTER_R: Bailey}],
		4: [{HITTER_R: Player, SETTER: James, HITTER_L: Nat},
			{SETTER: Dan, HITTER_L: Matt, HITTER_R: Bailey}],
	}
	ball = VolleyBall.new()
	_opp = (Config.VB_DIFFICULTY["hard"] as Dictionary).duplicate()


func configure(mode := "match", level := "hard", week := 1) -> void:
	_mode = mode
	_level = level if Config.VB_DIFFICULTY.has(level) else "hard"
	_week = week if _ROSTERS.has(week) else 1


# The match verdict — your team outscored the opponent.
func player_won() -> bool:
	return score[0] > score[1]


func _ready() -> void:
	_rng.randomize()
	_font = ThemeDB.fallback_font
	_world = Node2D.new()
	add_child(_world)
	_play = _Layer.new()
	_play.fn = _draw_court
	_play.z_index = -10
	_world.add_child(_play)

	_ref = Matus.new(0, 0)
	_ref.bare = true
	_ref.position = Vector2(_H_L + 26, _NET + 6)
	_ref.facing = "right"
	_ref.z_index = -5
	_world.add_child(_ref)

	_ballnode = ball
	_ballnode.z_index = 1000
	_world.add_child(_ballnode)

	_dim = _Layer.new()
	_dim.fn = _draw_dim
	_dim.z_index = 1500
	_world.add_child(_dim)

	_top = _Layer.new()
	_top.fn = _draw_top
	_top.z_index = 2000
	_world.add_child(_top)

	_hud = _Layer.new()
	_hud.fn = _draw_overlay
	_hud.z_index = 3000
	add_child(_hud)

	enter()
	set_process(true)
	set_process_unhandled_input(true)


# ── Setup ────────────────────────────────────────────────────────────────────
func enter() -> void:
	var roster: Array = _ROSTERS.get(_week, _ROSTERS[1])
	var near_cls: Dictionary = roster[0]
	var far_cls: Dictionary = roster[1]
	near = []
	far = []
	for r in _ROLES:
		var spr = near_cls[r].new(0, 0)
		var a := VBActor.new(_HOME[0][r].x, _HOME[0][r].y, 0, r, spr, r == HITTER_R)
		near.append(a)
		_world.add_child(a)
	for r in _ROLES:
		var spr = far_cls[r].new(0, 0)
		var a := VBActor.new(_HOME[1][r].x, _HOME[1][r].y, 1, r, spr, false)
		far.append(a)
		_world.add_child(a)
	fx = VBFX.new()
	_opp = (Config.VB_DIFFICULTY[_level] as Dictionary).duplicate()
	score = [0, 0]
	serving = _rng.randi_range(0, 1)
	_await = null
	_crossing = false
	_move = Vector2.ZERO
	_face = Vector2(0, -1)
	_vel = Vector2.ZERO
	_action = false
	_set_pressed = false
	_tip_pressed = false
	_aimstep = null
	_setstep = null
	_in_system = true
	_block_jump = 0.0
	_block_cd = 0.0
	_ai_block_jump = 0.0
	_block_target = null
	_planned_spike = null
	_recv_cache = null
	_react_t = 0.0
	_was_crossing = false
	_last_contact = null
	_touches = 0
	_time_scale = 1.0
	_time_target = 1.0
	_serve_meter = 0.0
	_serve_dir = 1
	_serve_stage = "power"
	_serve_lat = 0.0
	_serve_lat_dir = 1
	_serve_power = 0.5
	_serve_fault = false
	_serve_outcome = null
	_rally_touches = 0
	_dig_grace = 0.0
	_hit_feedback = null
	_banner = ""
	_timer = 0.0
	_serve_timer = 0.0
	_last_winner = 0
	_intro = true
	_tut = null
	phase = PHASE_SERVE
	_prev_y = ball.y
	_start_serve()
	if _mode == "tutorial":
		_intro = false
		_tut_setup(0)


# ── Input ────────────────────────────────────────────────────────────────────
func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and (not event.pressed or event.echo):
		return
	if event.is_action_pressed("confirm"):       # Z / Cross — dig/attack/serve/block
		_action = true
	elif event.is_action_pressed("cancel"):      # X / Circle — set
		_set_pressed = true
	elif event.is_action_pressed("menu"):        # C / Square — tip / dump
		_tip_pressed = true


# ── Helpers ──────────────────────────────────────────────────────────────────
func _team(t: int) -> Array:
	return near if t == 0 else far


func _role(t: int, role) -> VBActor:
	for a in _team(t):
		if a.role == role:
			return a
	return null


func _player() -> VBActor:
	for a in near:
		if a.is_player:
			return a
	return null


func _opp_half(t: int) -> Array:
	var lo := _C_L + 12
	var hi := _C_R - 12
	if t == 0:
		return [lo, hi, _C_T + 12, _NET - 12]
	return [lo, hi, _NET + 12, _C_B - 12]


func _min_by(arr: Array, key: Callable):
	var best = null
	var best_v := INF
	for a in arr:
		var v: float = key.call(a)
		if v < best_v:
			best_v = v
			best = a
	return best


func _max_by(arr: Array, key: Callable):
	var best = null
	var best_v := -INF
	for a in arr:
		var v: float = key.call(a)
		if v > best_v:
			best_v = v
			best = a
	return best


func _first(arr: Array, pred: Callable):
	for a in arr:
		if pred.call(a):
			return a
	return null


func _nearest_defender(team: int, pt: Vector2) -> VBActor:
	var defenders := _team(team).filter(func(a): return a.role != SETTER)
	return _min_by(defenders, func(a): return a.dist_to(pt.x, pt.y))


func _receiver(team: int) -> VBActor:
	var pt: Vector2 = ball.end
	var elig := _team(team).filter(func(a): return a != _last_contact)
	if elig.is_empty():
		elig = _team(team)
	var setter := _role(team, SETTER)
	var backs := elig.filter(func(a): return a.role != SETTER)
	var human = _first(elig, func(a): return a.is_player)
	var h_d: float = human.dist_to(pt.x, pt.y) if human != null else 1e9
	var setter_on: bool = setter in elig and setter.dist_to(pt.x, pt.y) <= Config.VB_SETTER_TAKE_RADIUS
	if setter_on and setter.dist_to(pt.x, pt.y) <= h_d:
		return setter
	if human != null and human.role != SETTER and h_d <= Config.VB_PLAYER_TAKE_RADIUS:
		return human
	if setter_on:
		return setter
	var reach: float = Config.VB_ACTOR_SPEED * maxf(0.05, ball.remaining()) + Config.VB_CONTACT_RADIUS
	var in_reach := backs.filter(func(a): return a.dist_to(pt.x, pt.y) <= reach)
	if not in_reach.is_empty():
		return _min_by(in_reach, func(a): return a.dist_to(pt.x, pt.y))
	if setter in elig and setter.dist_to(pt.x, pt.y) <= reach:
		return setter
	return _min_by(backs, func(a): return a.dist_to(pt.x, pt.y)) if not backs.is_empty() else elig[0]


func _best_digger(team: int) -> VBActor:
	var pt: Vector2 = ball.end
	var elig := _team(team).filter(func(a): return a != _last_contact)
	if elig.is_empty():
		elig = _team(team)
	var setter := _role(team, SETTER)
	var human = _first(elig, func(a): return a.is_player)
	var h_d: float = human.dist_to(pt.x, pt.y) if human != null else 1e9
	if (setter in elig and not setter.is_player
			and setter.dist_to(pt.x, pt.y) <= Config.VB_SETTER_TAKE_RADIUS
			and setter.dist_to(pt.x, pt.y) <= h_d):
		return setter
	if human != null and human.role != SETTER and h_d <= Config.VB_PLAYER_TAKE_RADIUS:
		return human
	var reach: float = Config.VB_ACTOR_SPEED * maxf(0.05, ball.remaining()) + Config.VB_CONTACT_RADIUS
	var backs := elig.filter(func(a): return a.role != SETTER and not a.is_player)
	var reachable := backs.filter(func(a): return a.dist_to(pt.x, pt.y) <= reach)
	if not reachable.is_empty():
		return _min_by(reachable, func(a): return a.dist_to(pt.x, pt.y))
	if setter in elig and not setter.is_player and setter.dist_to(pt.x, pt.y) <= reach:
		return setter
	return _min_by(backs, func(a): return a.dist_to(pt.x, pt.y)) if not backs.is_empty() else elig[0]


func _current_contactor() -> VBActor:
	if _await == null:
		return null
	var kind: String = _await[0]
	var c = _await[1]
	if kind == "receive":
		return c if c != null else _nearest_defender(ball.team, ball.end)
	return c


func _player_radius() -> float:
	return Config.VB_CONTACT_RADIUS


func _at_net(a: VBActor) -> bool:
	return absf(a.y - _NET) < Config.VB_BLOCK_NET_DIST


func _block_read(tgt_x: float, read: float) -> float:
	var err := (1.0 - read) * 55.0
	return clampf(tgt_x + _rng.randf_range(-err, err), _C_L + 20, _C_R - 20)


func _commit_block(hitter: VBActor) -> void:
	var blocker := _role(1 - hitter.team, SETTER)
	_planned_spike = null
	if blocker.is_player or _rng.randf() >= _opp["block_chance"]:
		_block_target = null
		return
	var tgt: Vector2 = _spike_target_ai(hitter.team, true)
	_planned_spike = tgt
	var read: float = _team_diff(blocker.team).get("read", 0.5)
	var lane_x := _block_read(tgt.x, read)
	var reach: float = Config.VB_ACTOR_SPEED * _SET.y * 0.9
	var late := absf(blocker.x - lane_x) > reach
	_block_target = {"blocker": blocker, "lane_x": lane_x, "late": late}


func _net_point(team: int, x: float) -> Vector2:
	var nx := clampf(x, _C_L + 16, _C_R - 16)
	var ny := _NET + Config.VB_NET_CONTACT if team == 0 else _NET - Config.VB_NET_CONTACT
	return Vector2(nx, ny)


# ── Serve ────────────────────────────────────────────────────────────────────
func _start_serve() -> void:
	phase = PHASE_SERVE
	_await = null
	_crossing = false
	_last_contact = null
	_touches = 0
	_serve_fault = false
	_serve_meter = 0.0
	_serve_dir = 1
	_serve_stage = "power"
	_serve_lat = 0.0
	_serve_lat_dir = 1
	_serve_power = 0.5
	_rally_touches = 0
	_in_system = true
	_vel = Vector2.ZERO
	_setstep = null
	_block_jump = 0.0
	_ai_block_jump = 0.0
	_block_target = null
	_time_target = 1.0
	for a in near + far:
		a.x = a.home.x
		a.y = a.home.y
		a.vx = 0.0
		a.vy = 0.0
		a.set_pose(P_READY)
		a.z = 0.0
	var srv := _server()
	srv.x = _SERVE_POS[serving].x
	srv.y = _SERVE_POS[serving].y
	_serve_timer = 0.8
	ball.hold_at(_SERVE_POS[serving].x, _SERVE_POS[serving].y)


func _server() -> VBActor:
	return _role(serving, HITTER_R)


func _do_serve() -> void:
	var half := _opp_half(serving)
	var x0: float = half[0]
	var x1: float = half[1]
	var aggr: float = _opp["serve_aggr"]
	var cx := (x0 + x1) / 2.0
	var net_side: float = half[3] if serving == 0 else half[2]
	var base: float = half[2] if serving == 0 else half[3]
	var target := Vector2(
		lerpf(cx, _rng.randf_range(x0 + 40, x1 - 40), aggr),
		lerpf(net_side, base, _rng.randf_range(0.45, 0.78)))
	var peak: float = lerpf(Config.VB_SERVE_PEAK.x, Config.VB_SERVE_PEAK.y, 0.5)
	var dur: float = lerpf(Config.VB_SERVE_DUR.x, Config.VB_SERVE_DUR.y, 0.5)
	ball.launch(_SERVE_POS[serving], target, peak, dur)
	ball.team = serving
	_crossing = true
	_rally_touches = 1
	Audio.sfx("serve")
	phase = PHASE_RALLY


func _serve_target(power: float, lateral: float, server: int) -> Array:
	var half := _opp_half(server)
	var x0: float = half[0]
	var x1: float = half[1]
	var lat := lerpf(x0 + 10, x1 - 10, lateral)
	var net_side: float = half[3] if server == 0 else half[2]
	var base: float = half[2] if server == 0 else half[3]
	if power < Config.VB_SERVE_NET_MAX:
		return [Vector2(lat, _NET), "net", 0.0]
	if power > Config.VB_SERVE_OUT_MIN:
		var out_y := _C_T - Config.VB_OUT_LAND if server == 0 else _C_B + Config.VB_OUT_LAND
		return [Vector2(lat, out_y), "out", 1.0]
	var frac := (power - Config.VB_SERVE_NET_MAX) / (Config.VB_SERVE_OUT_MIN - Config.VB_SERVE_NET_MAX)
	return [Vector2(lat, net_side + (base - net_side) * frac), "in", frac]


func _serve_quality(power: float) -> float:
	var glo: float = Config.VB_SERVE_GREEN.x
	var ghi: float = Config.VB_SERVE_GREEN.y
	var q: float
	if power <= glo:
		q = (power - Config.VB_SERVE_NET_MAX) / (glo - Config.VB_SERVE_NET_MAX)
	elif power >= ghi:
		q = (Config.VB_SERVE_OUT_MIN - power) / (Config.VB_SERVE_OUT_MIN - ghi)
	else:
		q = 1.0
	return clampf(q, 0.0, 1.0)


func _execute_serve(power: float, lateral: float) -> void:
	var server := serving
	var res := _serve_target(power, lateral, server)
	var target: Vector2 = res[0]
	var zone: String = res[1]
	ball.team = server
	_serve_outcome = null
	_rally_touches = 1
	var sp: Vector2 = _SERVE_POS[server]
	fx.emit_burst(sp.x, sp.y - 16, Color8(255, 240, 150), 8, 130)
	Audio.sfx("serve")
	if zone == "in":
		var q := _serve_quality(power)
		var peak: float = lerpf(Config.VB_SERVE_PEAK.x, Config.VB_SERVE_PEAK.y, q)
		var dur: float = lerpf(Config.VB_SERVE_DUR.x, Config.VB_SERVE_DUR.y, q)
		ball.launch(sp, target, peak, dur)
		_crossing = true
		_serve_fault = false
	else:
		var peak := 70.0 if zone == "net" else 130.0
		var dur := 0.7 if zone == "net" else 1.05
		ball.launch(sp, target, peak, dur)
		_crossing = false
		_serve_fault = true
		_serve_outcome = ["fault", 1 - server,
			"In the net!" if zone == "net" else "Serve out!"]
	phase = PHASE_RALLY
	if not _serve_fault:
		_tut_player_action("serve")


# ── Contacts / net ───────────────────────────────────────────────────────────
func _on_cross_net() -> void:
	ball.team = 1 - ball.team
	_crossing = false
	_block_target = null
	_last_contact = null
	_touches = 0
	_await = ["receive", _receiver(ball.team)]


func _check_block() -> bool:
	var attacker := ball.team
	var defteam := 1 - attacker
	var candidates: Array[VBActor] = []
	var human := _player()
	if (human.team == defteam and _block_jump > 0
			and absf(human.y - _NET) < Config.VB_BLOCK_NET_DIST + 8):
		candidates.append(human)
	var setter := _role(defteam, SETTER)
	if (not setter.is_player and _ai_block_jump > 0
			and absf(setter.y - _NET) < Config.VB_BLOCK_NET_DIST + 8):
		candidates.append(setter)
	var in_lane := candidates.filter(func(b): return absf(b.x - ball.x) <= Config.VB_BLOCK_REACH)
	if in_lane.is_empty():
		return false
	var p: VBActor = _min_by(in_lane, func(b): return absf(b.x - ball.x))
	if p.is_player:
		_tut_player_action("block")
	var offset := absf(p.x - ball.x)
	p.set_pose(P_BLOCK)
	fx.emit_burst(p.x, p.y - 24, Color8(255, 240, 150), 16, 220)
	var start := Vector2(ball.x, _NET)
	var r := _rng.randf()
	if offset <= Config.VB_BLOCK_REACH * Config.VB_BLOCK_SQUARE:
		if r < Config.VB_BLOCK_SQ_STUFF:
			var ax := clampf(ball.x, _C_L + 16, _C_R - 16)
			var ay := _NET - 38 if attacker == 1 else _NET + 38
			fx.shake(7, 0.26)
			_block_send(1 - attacker, start, Vector2(ax, ay), 30, 0.42, "Block!")
		elif r < Config.VB_BLOCK_SQ_STUFF + Config.VB_BLOCK_SQ_SOFT:
			fx.shake(3, 0.16)
			_block_outcome(1 - attacker, false)
		elif r < Config.VB_BLOCK_SQ_STUFF + Config.VB_BLOCK_SQ_SOFT + Config.VB_BLOCK_SQ_TOOL:
			_tool_out(attacker, start, ball.end.y)
		else:
			fx.shake(4, 0.18)
			_block_outcome(attacker, true)
		return true
	if r < Config.VB_BLOCK_GL_STUFF:
		var ax := clampf(ball.x, _C_L + 16, _C_R - 16)
		var ay := _NET - 38 if attacker == 1 else _NET + 38
		fx.shake(6, 0.22)
		_block_send(1 - attacker, start, Vector2(ax, ay), 30, 0.42, "Block!")
	elif r < Config.VB_BLOCK_GL_STUFF + Config.VB_BLOCK_GL_TOOL:
		_tool_out(attacker, start, ball.end.y)
	elif r < Config.VB_BLOCK_GL_STUFF + Config.VB_BLOCK_GL_TOOL + Config.VB_BLOCK_GL_SOFT:
		fx.shake(3, 0.16)
		_block_outcome(1 - attacker, false)
	elif (r < Config.VB_BLOCK_GL_STUFF + Config.VB_BLOCK_GL_TOOL + Config.VB_BLOCK_GL_SOFT
			+ Config.VB_BLOCK_GL_ROOF):
		fx.shake(4, 0.18)
		_block_outcome(1 - attacker, true)
	else:
		fx.shake(4, 0.18)
		_block_outcome(attacker, true)
	return true


func _tool_out(attacker: int, start: Vector2, ry: float) -> void:
	var defteam := 1 - attacker
	var side := _C_L - Config.VB_OUT_LAND if start.x < _CX else _C_R + Config.VB_OUT_LAND
	fx.shake(4, 0.18)
	ball.launch(start, Vector2(side, ry), 95, 0.8)
	ball.team = defteam
	_crossing = false
	_serve_fault = false
	_touches = 0
	_await = ["receive", _receiver(defteam)]


func _block_send(winner: int, start: Vector2, end: Vector2, peak: float, dur: float, msg: String) -> void:
	ball.launch(start, end, peak, dur)
	ball.team = winner
	_crossing = false
	_serve_fault = true
	_serve_outcome = ["block", winner, msg]


func _block_outcome(recv_team: int, deep: bool) -> void:
	var net_off := 90.0 if deep else 56.0
	var ty := _NET - net_off if recv_team == 1 else _NET + net_off
	var tx := clampf(ball.x + _rng.randf_range(-60, 60), _C_L + 16, _C_R - 16)
	var peak := 150.0 if deep else 125.0
	ball.launch(Vector2(ball.x, _NET), Vector2(tx, ty), peak, _hang(peak))
	ball.team = recv_team
	_crossing = false
	_await = ["receive", _receiver(recv_team)]


func _attackers(team: int, exclude: VBActor = null) -> Array:
	var atk := _team(team).filter(func(a): return a.role != SETTER and a != exclude)
	if not atk.is_empty():
		return atk
	return _team(team).filter(func(a): return a != exclude)


func _smart_hitter(team: int, exclude: VBActor = null) -> VBActor:
	var cands := _attackers(team, exclude)
	if team == 0:
		var human = _first(cands, func(h): return h.is_player)
		if human != null and _rng.randf() < Config.VB_SETTER_PLAYER_BIAS:
			return human
	if _rng.randf() < _opp["avoid_block"]:
		var bx := _player().x
		return _max_by(cands, func(h): return absf(h.x - bx))
	var opp := _team(1 - team)
	return _max_by(cands, func(h): return _min_dx(opp, h.x))


func _min_dx(opp: Array, hx: float) -> float:
	var best := INF
	for a in opp:
		best = minf(best, absf(a.x - hx))
	return best


func _emergency_setter(team: int) -> VBActor:
	var hitters := _team(team).filter(func(a): return a.role != SETTER)
	return _min_by(hitters, func(a): return absf(a.y - _NET) + absf(a.x - _CX))


func _spike_target_ai(team: int, perfect: bool) -> Vector2:
	var half := _opp_half(team)
	var x0: float = half[0]
	var x1: float = half[1]
	var y0: float = half[2]
	var y1: float = half[3]
	var opp := _team(1 - team)
	var best := Vector2(_CX, (y0 + y1) / 2.0)
	var best_d := -1.0
	for _i in 10:
		var tx := _rng.randf_range(x0 + 24, x1 - 24)
		var ty := _rng.randf_range(y0 + 16, y1 - 16)
		var d: float = _min_by(opp, func(a): return a.dist_to(tx, ty)).dist_to(tx, ty)
		if d > best_d:
			best_d = d
			best = Vector2(tx, ty)
	var sc: float = (8.0 if perfect else 18.0) * _opp["attack_spread"]
	return Vector2(
		clampf(best.x + _rng.randf_range(-sc, sc), x0, x1),
		clampf(best.y + _rng.randf_range(-sc, sc), y0, y1))


func _ai_tip(team: int, c: VBActor) -> void:
	var half := _opp_half(team)
	var x0: float = half[0]
	var x1: float = half[1]
	var front_y := _NET - 46 if team == 0 else _NET + 46
	var opp := _team(1 - team)
	var best_x := _CX
	var best_d := -1.0
	for _i in 6:
		var tx := _rng.randf_range(x0 + 24, x1 - 24)
		var d: float = _min_by(opp, func(a): return a.dist_to(tx, front_y)).dist_to(tx, front_y)
		if d > best_d:
			best_d = d
			best_x = tx
	ball.launch(Vector2(c.x, c.y), Vector2(best_x, front_y), Config.VB_TIP_PEAK, Config.VB_TIP_DUR)


# ── Receive quality (clean / shank / error) ──────────────────────────────────
func _difficulty() -> float:
	var dist := (ball.end - ball.start).length()
	var speed := dist / maxf(0.05, ball.duration)
	return clampf((speed - 180.0) / (430.0 - 180.0), 0.0, 1.0)


func _team_diff(team: int) -> Dictionary:
	return _opp if team == 1 else Config.VB_DIFFICULTY["hard"]


func _dig_timing_factor(rem: float) -> float:
	var off := absf(rem - Config.VB_DIG_IDEAL)
	if off <= Config.VB_DIG_GOOD_TOL:
		return 1.0
	return clampf(1.0 - (off - Config.VB_DIG_GOOD_TOL) / Config.VB_DIG_TOL,
		Config.VB_DIG_TIME_FLOOR, 1.0)


func _dig_feedback(rem: float, outcome: String, late: bool) -> void:
	var label: String
	if late:
		label = "LATE!"
	elif rem - Config.VB_DIG_IDEAL > Config.VB_DIG_GOOD_TOL:
		label = "EARLY"
	elif rem - Config.VB_DIG_IDEAL < -Config.VB_DIG_GOOD_TOL:
		label = "LATE"
	elif outcome == "clean":
		label = "PERFECT"
	else:
		label = "SHANK"
	_hit_feedback = [label, 0.7]


func _player_dig_quality(c: VBActor) -> float:
	var spd := _vel.length() / Config.VB_TOP_SPEED
	var offset := c.dist_to(ball.end.x, ball.end.y) / maxf(1.0, _player_radius())
	var q := (1.0 - Config.VB_DIG_MOVE_PEN * clampf(spd, 0.0, 1.0)
		- Config.VB_DIG_OFFSET_PEN * clampf(offset, 0.0, 1.0)
		- Config.VB_DIG_DIFF_PEN * _difficulty())
	return clampf(q, 0.0, 1.0)


func _ai_receive(c: VBActor) -> void:
	var diff := _difficulty()
	var params := _team_diff(c.team)
	var p_good: float = lerpf(params["dig_base"], params["dig_hard"], diff)
	var err: float = params["error_frac"]
	var r := _rng.randf()
	var outcome: String
	if r < p_good:
		outcome = "clean"
	elif r < p_good + (1.0 - p_good) * err:
		outcome = "error"
	else:
		outcome = "shank"
	_do_receive(c, outcome)


func _shank_target(c: VBActor, team: int) -> Vector2:
	var y: float
	if team == 0:
		y = clampf(c.y + _rng.randf_range(-30, 30), _NET + 40, _C_B - 30)
	else:
		y = clampf(c.y + _rng.randf_range(-30, 30), _C_T + 30, _NET - 40)
	var side := -1.0 if c.x > _CX else 1.0
	var x := clampf(c.x + side * _rng.randf_range(50, 110), _C_L + 20, _C_R - 20)
	return Vector2(x, y)


func _rebound_target(c: VBActor) -> Vector2:
	var team := c.team
	var side := -1.0 if _rng.randf() < 0.5 else 1.0
	var dist := _rng.randf_range(40, 95)
	var x := clampf(c.x + side * dist, _C_L + 12, _C_R - 12)
	var y: float
	if team == 0:
		y = clampf(c.y + _rng.randf_range(-20, 50), _NET + 28, _C_B - 18)
	else:
		y = clampf(c.y + _rng.randf_range(-50, 20), _C_T + 18, _NET - 28)
	return Vector2(x, y)


func _rebound(c: VBActor) -> void:
	var team := c.team
	_last_contact = c
	_touches += 1
	_rally_touches += 1
	if _touches >= 3 or _rally_touches >= Config.VB_RALLY_MAX:
		fx.emit_dust(c.x, c.y)
		_point(1 - team)
		return
	_in_system = false
	c.set_pose(P_DIG)
	Audio.sfx("dig")
	fx.emit_dust(c.x, c.y)
	var tgt := _rebound_target(c)
	ball.launch(Vector2(c.x, c.y), tgt, _REBOUND.x, _REBOUND.y)
	ball.team = team
	var mates := _team(team).filter(func(a): return a != c)
	if mates.is_empty():
		mates = [c]
	_await = ["receive", _min_by(mates, func(a): return a.dist_to(tgt.x, tgt.y))]


func _do_receive(c: VBActor, outcome: String) -> void:
	var team := c.team
	_last_contact = c
	if outcome == "error":
		_rebound(c)
		return
	_touches += 1
	_rally_touches += 1
	if c.is_player:
		_tut_player_action("dig")
	if _touches >= 3:
		_dump_over(c)
		return
	c.set_pose(P_DIG)
	Audio.sfx("dig")
	fx.emit_burst(c.x, c.y - 8, Color8(180, 220, 255), 6, 90)
	if c.role == SETTER:
		_in_system = false
		var em := _emergency_setter(team)
		ball.launch(Vector2(c.x, c.y), Vector2(em.x, em.y), 150, _hang(150))
		ball.team = team
		_await = ["set", em]
		return
	var setter := _role(team, SETTER)
	if outcome == "clean":
		_in_system = true
		var spot := Vector2(_CX, _NET + 54 if team == 0 else _NET - 54)
		var handler := _second_handler(team, c, spot)
		ball.launch(Vector2(c.x, c.y), spot, _DIG.x, _DIG.y)
		ball.team = team
		_await = ["set", handler]
		return
	_in_system = false
	var st := _shank_target(c, team)
	ball.launch(Vector2(c.x, c.y), st, 150, _hang(150))
	ball.team = team
	_await = ["set", setter]


func _second_handler(team: int, digger: VBActor, spot: Vector2) -> VBActor:
	var cands := _team(team).filter(func(a): return a != digger)
	var reach: float = Config.VB_ACTOR_SPEED * _DIG.y + Config.VB_CONTACT_RADIUS
	var able := cands.filter(func(a): return a.dist_to(spot.x, spot.y) <= reach)
	var pool := able if not able.is_empty() else cands
	return _min_by(pool, func(a): return a.dist_to(spot.x, spot.y))


func _ball_to_side(team: int) -> bool:
	var ey := ball.end.y
	return ey > _NET if team == 0 else ey < _NET


func _read_block(c: VBActor) -> bool:
	var bt = _block_target
	if bt == null or bt.get("late"):
		return false
	var squareness := clampf(1.0 - absf(float(bt["lane_x"]) - c.x) / (Config.VB_BLOCK_REACH * 4.0), 0.0, 1.0)
	return _rng.randf() < _opp.get("read", 0.0) * (0.5 + 0.5 * squareness)


func _contact_success(kind: String, c: VBActor, perfect: bool) -> void:
	var team := c.team
	_last_contact = c
	_touches += 1
	_rally_touches += 1
	if kind == "set" and _touches >= 3:
		_dump_over(c)
		return
	Audio.sfx("set" if kind == "set" else "spike")
	if kind == "set":
		c.set_pose(P_READY)
		var hitter := _smart_hitter(team, c)
		ball.launch(Vector2(c.x, c.y), _net_point(team, hitter.x), _SET.x, _SET.y)
		ball.team = team
		_await = ["spike", hitter]
		_commit_block(hitter)
	else:
		c.set_pose(P_JUMP)
		var err: float = _team_diff(team)["attack_err"]
		if not _in_system:
			err *= Config.VB_OOS_ERROR_MULT
		if _rally_touches >= Config.VB_RALLY_MAX or _rng.randf() < err:
			_ai_attack_error(team, c)
			return
		if _read_block(c):
			if _rng.randf() < Config.VB_AI_TIP_BIAS:
				_ai_tip(team, c)
			else:
				var tgt = _planned_spike if _planned_spike != null else _spike_target_ai(team, perfect)
				ball.launch(Vector2(c.x, c.y), tgt, _SPIKE_AI.x, _SPIKE_AI.y)
				fx.shake(2, 0.12)
		elif _in_system and _rng.randf() < _opp["tip_chance"]:
			_ai_tip(team, c)
		elif _in_system:
			var tgt = _planned_spike if _planned_spike != null else _spike_target_ai(team, perfect)
			ball.launch(Vector2(c.x, c.y), tgt, _SPIKE_AI.x, _SPIKE_AI.y)
			fx.shake(3, 0.14)
		else:
			var tgt := _spike_target_ai(team, false)
			ball.launch(Vector2(c.x, c.y), tgt, 76, 0.88)
			fx.shake(2, 0.12)
		ball.team = team
		_await = null
		_crossing = true
		_ai_setter_block(team)


func _ai_setter_block(attacker: int) -> void:
	var rsetter := _role(1 - attacker, SETTER)
	if rsetter.is_player or not _at_net(rsetter):
		return
	rsetter.set_pose(P_BLOCK)
	_ai_block_jump = Config.VB_BLOCK_DURATION


func _ai_attack_error(team: int, c: VBActor) -> void:
	var msg: String
	if _rng.randf() < 0.20:
		var ny := _NET - 8 if team == 0 else _NET + 8
		ball.launch(Vector2(c.x, c.y), Vector2(c.x, ny), 44, 0.5)
		msg = "Into the net!"
	else:
		var cx := clampf(c.x + _rng.randf_range(-50, 50), _C_L, _C_R)
		var base := _C_T - Config.VB_OUT_LAND if team == 0 else _C_B + Config.VB_OUT_LAND
		var ol := _out_landing(cx, base, team)
		ball.launch(Vector2(c.x, c.y), ol, 72, 0.8)
		msg = "Out!"
	ball.team = team
	_await = null
	_crossing = false
	_serve_fault = true
	_serve_outcome = ["fault", 1 - team, msg]


# ── Aim-step (player spike) ──────────────────────────────────────────────────
func _set_quality(hitter: VBActor) -> float:
	var base := 1.0 if _in_system else 0.5
	if hitter.is_player:
		var spd := _vel.length() / Config.VB_TOP_SPEED
		var offset := hitter.dist_to(ball.end.x, ball.end.y) / maxf(1.0, _player_radius())
		base -= 0.30 * clampf(spd, 0.0, 1.0) + 0.30 * clampf(offset, 0.0, 1.0)
	return clampf(base, 0.0, 1.0)


func _enter_aimstep(c: VBActor) -> void:
	_ai_block_jump = 0.0
	var half := _opp_half(c.team)
	var y0: float = half[2]
	var y1: float = half[3]
	var sq := _set_quality(c)
	var hw := (_C_W / 2.0) * lerpf(Config.VB_OOS_RANGE, 1.0, sq) + Config.VB_AIM_OUT
	var block_x = null
	var blocker := _role(1 - c.team, SETTER)
	if not blocker.is_player and _at_net(blocker):
		block_x = blocker.x
		blocker.set_pose(P_BLOCK)
	_aimstep = {
		"contactor": c, "power_cap": lerpf(Config.VB_OOS_POWER_CAP, 1.0, sq),
		"sq": sq, "xmin": _CX - hw, "xmax": _CX + hw, "block_x": block_x,
		"timer": Config.VB_AIMSTEP_WINDOW, "rx": _CX, "ry": (y0 + y1) / 2.0,
		"meter": 0.0,
	}
	_time_target = Config.VB_AIMSTEP_SLOWMO
	c.set_pose(P_JUMP)
	ball.hold_at(c.x, c.y)
	ball.z = 30.0
	_rally_touches += 1
	_action = false


func _update_aimstep(raw_dt: float) -> void:
	var a = _aimstep
	var c: VBActor = a["contactor"]
	a["rx"] = clampf(a["rx"] + _move.x * Config.VB_RETICLE_SPEED * raw_dt, a["xmin"], a["xmax"])
	if c.team == 0:
		a["ry"] = clampf(a["ry"] + _move.y * Config.VB_RETICLE_SPEED * raw_dt, _C_T - 30, _NET - 2)
	else:
		a["ry"] = clampf(a["ry"] + _move.y * Config.VB_RETICLE_SPEED * raw_dt, _NET + 2, _C_B + 30)
	a["meter"] += Config.VB_SPIKE_METER_SPEED * raw_dt
	if a["meter"] >= 1.0:
		a["meter"] -= 1.0
	a["timer"] -= raw_dt
	if _tip_pressed:
		_fire_tip()
	elif _action:
		_fire_spike()
	elif a["timer"] <= 0:
		_fire_spike(true)


func _hit_quality(meter: float) -> Array:
	if Config.VB_SPIKE_SWEET_LO <= meter and meter <= Config.VB_SPIKE_SWEET_HI:
		return ["PERFECT", 1.0]
	if meter < Config.VB_SPIKE_SWEET_LO:
		var frac := (Config.VB_SPIKE_SWEET_LO - meter) / maxf(1e-6, Config.VB_SPIKE_SWEET_LO)
		return ["EARLY", lerpf(0.85, Config.VB_SPIKE_MIN_POWER, frac)]
	var frac := (meter - Config.VB_SPIKE_SWEET_HI) / maxf(1e-6, 1.0 - Config.VB_SPIKE_SWEET_HI)
	return ["LATE", lerpf(0.85, Config.VB_SPIKE_MIN_POWER, frac)]


func _spike_zone(target: Vector2, team: int) -> String:
	var tx := target.x
	var ty := target.y
	if team == 0:
		if ty >= _NET - 6:
			return "net"
		if ty < _C_T:
			return "out"
	else:
		if ty <= _NET + 6:
			return "net"
		if ty > _C_B:
			return "out"
	if tx < _C_L or tx > _C_R:
		return "out"
	return "in"


func _out_landing(rx: float, ry: float, team: int) -> Vector2:
	var ox := rx
	var oy := ry
	if rx < _C_L:
		ox = _C_L - Config.VB_OUT_LAND
	elif rx > _C_R:
		ox = _C_R + Config.VB_OUT_LAND
	if team == 0 and ry < _C_T:
		oy = _C_T - Config.VB_OUT_LAND
	elif team == 1 and ry > _C_B:
		oy = _C_B + Config.VB_OUT_LAND
	return Vector2(clampf(ox, _H_L + 6, _H_R - 6), clampf(oy, _H_T + 4, _H_B - 4))


func _in_landing(tx: float, ty: float, team: int) -> Vector2:
	var ix := clampf(tx, _C_L + 6, _C_R - 6)
	var iy: float
	if team == 0:
		iy = clampf(ty, _C_T + 6, _NET - 8)
	else:
		iy = clampf(ty, _NET + 8, _C_B - 6)
	return Vector2(ix, iy)


func _fire_spike(timed_out := false) -> void:
	var a = _aimstep
	_aimstep = null
	_time_target = 1.0
	var c: VBActor = a["contactor"]
	var label: String
	var power: float
	if timed_out:
		label = "LATE"
		power = Config.VB_SPIKE_MIN_POWER
	else:
		var hq := _hit_quality(float(a["meter"]))
		label = hq[0]
		power = hq[1]
	power = minf(power, float(a["power_cap"]))
	_hit_feedback = [label, 0.7]
	var zone := _spike_zone(Vector2(a["rx"], a["ry"]), c.team)
	var scatter := 6.0 + 18.0 * (1.0 - power)
	var tx: float = a["rx"] + _rng.randf_range(-scatter, scatter)
	var ty: float = a["ry"] + _rng.randf_range(-scatter, scatter)
	ball.team = c.team
	c.set_pose(P_JUMP)
	fx.emit_burst(c.x, c.y - 24, Color8(255, 240, 150), 14, 210)
	if label == "PERFECT":
		fx.emit_burst(c.x, c.y - 24, Color8(255, 255, 215), 12, 300)
	fx.shake(6.0 if label == "PERFECT" else 3.0, 0.20)
	Audio.sfx("perfect" if label == "PERFECT" else "spike")
	var over := false
	if zone == "net":
		ball.launch(Vector2(c.x, c.y), Vector2(tx, _NET), 60, 0.55)
		_crossing = false
		_serve_fault = true
		_serve_outcome = ["fault", 1 - c.team, "Into the net!"]
	elif zone == "out":
		var ol := _out_landing(a["rx"], a["ry"], c.team)
		ball.launch(Vector2(c.x, c.y), ol, 80, 0.7)
		_crossing = false
		_serve_fault = true
		_serve_outcome = ["fault", 1 - c.team, "Out!"]
	elif _spike_blocked(a, c):
		pass
	else:
		var peak := 82.0 - 46.0 * power
		var dur := 0.84 - 0.46 * power
		var land := _in_landing(tx, ty, c.team)
		ball.launch(Vector2(c.x, c.y), land, peak, dur)
		_await = null
		_crossing = true
		over = true
	_action = false
	if c.is_player:
		if _tut_is("spike"):
			_tut_player_action("spike", label == "PERFECT" and over)
		else:
			_tut_player_action("spike")


func _spike_blocked(a: Dictionary, c: VBActor) -> bool:
	var bx = a.get("block_x")
	if bx == null or absf(a["rx"] - float(bx)) > Config.VB_BLOCK_REACH:
		return false
	fx.emit_burst(float(bx), _NET, Color8(255, 240, 150), 12, 220)
	var start := Vector2(bx, _NET)
	var attacker := c.team
	var offset := absf(a["rx"] - float(bx))
	var stuff: float
	var tool: float
	var soft: float
	if offset <= Config.VB_BLOCK_REACH * Config.VB_BLOCK_SQUARE:
		stuff = Config.VB_BLOCK_SQ_STUFF
		tool = Config.VB_BLOCK_SQ_TOOL
		soft = Config.VB_BLOCK_SQ_SOFT
	else:
		stuff = Config.VB_BLOCK_GL_STUFF
		tool = Config.VB_BLOCK_GL_TOOL
		soft = Config.VB_BLOCK_GL_SOFT
	var r := _rng.randf()
	if r < stuff:
		fx.shake(7, 0.26)
		var px := clampf(c.x, _C_L + 16, _C_R - 16)
		var py := _NET + 40 if c.team == 0 else _NET - 40
		_block_send(1 - c.team, start, Vector2(px, py), 30, 0.42, "Stuffed!")
	elif r < stuff + tool:
		fx.shake(5, 0.20)
		_tool_out(attacker, start, a["ry"])
	elif r < stuff + tool + soft:
		_block_outcome(1 - attacker, false)
	else:
		_block_outcome(attacker, true)
	return true


func _fire_tip() -> void:
	var a = _aimstep
	_aimstep = null
	_time_target = 1.0
	var c: VBActor = a["contactor"]
	var tx := clampf(a["rx"], _C_L + 14, _C_R - 14)
	var ty := (_NET - Config.VB_TIP_DROP) if c.team == 0 else (_NET + Config.VB_TIP_DROP)
	ball.team = c.team
	c.set_pose(P_JUMP)
	fx.emit_burst(c.x, c.y - 22, Color8(200, 230, 255), 8, 120)
	Audio.sfx("tip")
	ball.launch(Vector2(c.x, c.y), Vector2(tx, ty), Config.VB_TIP_PEAK, Config.VB_TIP_DUR)
	_await = null
	_crossing = true
	_action = false
	_set_pressed = false
	_tip_pressed = false


# ── Set-step (player setter: choose side / dump, in slow-mo) ──────────────────
func _enter_setstep(c: VBActor) -> void:
	_time_target = Config.VB_AIMSTEP_SLOWMO
	ball.hold_at(c.x, c.y)
	ball.z = 28.0
	var attackers: Array
	if _tut_is("set"):
		attackers = _team(c.team).filter(func(a): return a != c)
	else:
		attackers = _attackers(c.team, c)
	_setstep = {"contactor": c, "attackers": attackers,
		"choice": _smart_hitter(c.team, c), "timer": Config.VB_AIMSTEP_WINDOW}
	c.set_pose(P_READY)
	_rally_touches += 1
	_action = false
	_set_pressed = false


func _update_setstep(raw_dt: float) -> void:
	var s = _setstep
	var atk: Array = s["attackers"].duplicate()
	atk.sort_custom(func(a, b): return a.x < b.x)
	var mx := _move.x
	if atk.size() >= 2:
		if mx <= -0.3:
			s["choice"] = atk[0]
		elif mx >= 0.3:
			s["choice"] = atk[-1]
	s["timer"] -= raw_dt
	if _tip_pressed:
		_setter_dump()
	elif _set_pressed or s["timer"] <= 0:
		_confirm_set()


func _confirm_set() -> void:
	var s = _setstep
	_setstep = null
	_time_target = 1.0
	var setter: VBActor = s["contactor"]
	var hitter: VBActor = s["choice"]
	ball.launch(Vector2(setter.x, setter.y), _net_point(hitter.team, hitter.x), _SET.x, _SET.y)
	ball.team = hitter.team
	_await = ["spike", hitter]
	_commit_block(hitter)
	Audio.sfx("set")
	_action = false
	_set_pressed = false
	if setter.is_player:
		_tut_player_action("set")


func _dump_over(c: VBActor) -> void:
	var tx := clampf(c.x, _C_L + 14, _C_R - 14)
	var ty := (_NET - Config.VB_TIP_DROP) if c.team == 0 else (_NET + Config.VB_TIP_DROP)
	ball.team = c.team
	c.set_pose(P_JUMP)
	fx.emit_burst(c.x, c.y - 20, Color8(200, 230, 255), 8, 120)
	Audio.sfx("tip")
	ball.launch(Vector2(c.x, c.y), Vector2(tx, ty), Config.VB_TIP_PEAK, Config.VB_TIP_DUR)
	_await = null
	_crossing = true


func _setter_dump() -> void:
	var c: VBActor = _setstep["contactor"]
	_setstep = null
	_time_target = 1.0
	_dump_over(c)
	_action = false
	_set_pressed = false
	_tip_pressed = false


func _quick_dump(c: VBActor) -> void:
	_rally_touches += 1
	_dump_over(c)
	_action = false
	_set_pressed = false
	_tip_pressed = false


# ── Block-step (player front-row setter: slow-mo slide + jump) ────────────────
func _start_block() -> void:
	var p := _player()
	p.set_pose(P_BLOCK)
	p.facing = "up"
	var dur := Config.VB_TUT_BLOCK_DURATION if _tut_is("block") else Config.VB_BLOCK_DURATION
	_block_jump = dur
	_block_cd = dur + Config.VB_BLOCK_COOLDOWN
	fx.emit_burst(p.x, p.y - 24, Color8(255, 240, 150), 8, 150)
	Audio.sfx("block")


func _can_block() -> bool:
	var p := _player()
	return (_block_cd <= 0 and _block_jump <= 0
		and absf(p.y - _NET) < Config.VB_BLOCK_ELIGIBLE
		and ball.team == 1 and ball.in_flight)


# ── Resolve ──────────────────────────────────────────────────────────────────
func _resolve(dt: float) -> void:
	var b := ball
	if _serve_fault:
		if not b.in_flight:
			var winner: int = _serve_outcome[1]
			var msg: String = _serve_outcome[2]
			fx.emit_dust(b.end.x, b.end.y)
			_point(winner)
			_banner = msg
			_serve_fault = false
		return
	if _crossing:
		if (b.in_flight and absf(b.y - _NET) <= Config.VB_BLOCK_Y_BAND and _check_block()):
			return
		var crossed := (_prev_y - _NET) * (b.y - _NET) <= 0
		if b.in_flight and crossed and absf(b.y - _NET) <= 80:
			_on_cross_net()
		elif not b.in_flight:
			_on_cross_net()
		return
	if _await == null:
		return
	var kind: String = _await[0]
	var c := _current_contactor()
	if (c != null and not c.is_player and b.in_flight and kind in ["receive", "set", "spike"]):
		var creach: float = Config.VB_ACTOR_SPEED * maxf(0.05, b.remaining()) + Config.VB_CONTACT_RADIUS
		if c.dist_to(b.end.x, b.end.y) > creach:
			var cands := _team(c.team).filter(func(a): return not a.is_player and a != _last_contact)
			if not cands.is_empty():
				var cand: VBActor = _min_by(cands, func(a): return a.dist_to(b.end.x, b.end.y))
				if cand != c and cand.dist_to(b.end.x, b.end.y) + 1.0 < c.dist_to(b.end.x, b.end.y):
					_await = [kind, cand]
					c = cand
	var radius := _player_radius()
	var in_range := c.dist_to(b.end.x, b.end.y) <= radius
	if c.is_player:
		if kind == "spike":
			if _action and b.in_flight and b.remaining() <= Config.VB_TIMING_WINDOW and in_range:
				_enter_aimstep(c)
			elif not b.in_flight:
				fx.emit_dust(b.end.x, b.end.y)
				_point(1 - c.team)
		elif kind == "set":
			if b.in_flight and b.remaining() <= Config.VB_TIMING_WINDOW and in_range:
				var third := _touches >= 2
				if _action:
					if _at_net(c):
						_enter_aimstep(c)
					elif third:
						_quick_dump(c)
					else:
						_enter_setstep(c)
				elif _set_pressed:
					if third:
						_quick_dump(c)
					else:
						_enter_setstep(c)
				elif _tip_pressed:
					_quick_dump(c)
			elif not b.in_flight:
				fx.emit_dust(b.end.x, b.end.y)
				_point(1 - c.team)
		else:  # receive (dig)
			if b.in_flight:
				_dig_grace = Config.VB_DIG_GRACE
				var rem := b.remaining()
				if _action and in_range and rem <= Config.VB_DIG_EARLY_EDGE:
					var q := _player_dig_quality(c) * _dig_timing_factor(rem)
					var outcome: String = ("clean" if q >= Config.VB_DIG_CLEAN
						else "shank" if q >= Config.VB_DIG_SHANK else "error")
					_dig_feedback(rem, outcome, false)
					_do_receive(c, outcome)
			elif _dig_grace > 0:
				if _action and in_range:
					var q := _player_dig_quality(c) * Config.VB_DIG_TIME_FLOOR
					var outcome: String = "shank" if q >= Config.VB_DIG_SHANK else "error"
					_dig_feedback(0.0, outcome, true)
					_do_receive(c, outcome)
					_dig_grace = 0.0
				else:
					_dig_grace -= dt
			else:
				if in_range:
					_rebound(c)
				else:
					if _action:
						_hit_feedback = ["LATE!", 0.8]
					fx.emit_dust(b.end.x, b.end.y)
					_point(1 - c.team)
	elif _tut != null:
		if (_tut_is("set") and kind == "spike" and b.in_flight
				and b.remaining() <= 0.05 and in_range):
			_contact_success(kind, c, true)
		elif not b.in_flight:
			fx.emit_dust(b.end.x, b.end.y)
			_point(1 - c.team)
	else:
		if b.in_flight and b.remaining() <= 0.05:
			var actor := c if in_range else null
			if actor == null:
				var mates := _team(c.team).filter(func(a): return not a.is_player and a != _last_contact)
				var mate = _min_by(mates, func(a): return a.dist_to(b.end.x, b.end.y)) if not mates.is_empty() else null
				if mate != null and mate.dist_to(b.end.x, b.end.y) <= Config.VB_CONTACT_RADIUS:
					actor = mate
			if actor != null:
				if kind == "receive":
					_ai_receive(actor)
				else:
					_contact_success(kind, actor, true)
		elif not b.in_flight:
			fx.emit_dust(b.end.x, b.end.y)
			_point(1 - c.team)


# ── Scoring / rotation ───────────────────────────────────────────────────────
func _point(winner: int) -> void:
	if _tut != null:
		_tut_miss()
		return
	score[winner] += 1
	_last_winner = winner
	_await = null
	_crossing = false
	_aimstep = null
	_setstep = null
	_block_jump = 0.0
	_ai_block_jump = 0.0
	_block_target = null
	_time_target = 1.0
	phase = PHASE_POINT
	_banner = "Your point!" if winner == 0 else "Their point"
	_timer = 0.9
	fx.emit_burst(ball.end.x, ball.end.y, Color8(250, 230, 120), 10, 140)
	Audio.sfx("whistle")                 # the unobtrusive synth whistle per point
	if winner == 0:
		Audio.sfx("cheer")
	for a in _team(winner):
		a.set_pose(P_CELEBRATE)


func _rotate(team_list: Array) -> void:
	for a in team_list:
		a.role = _CW[a.role]
		a.home = _HOME[a.team][a.role]


func _after_point() -> void:
	if maxf(score[0], score[1]) >= Config.VB_SCORE_TO_WIN and absf(score[0] - score[1]) >= 2:
		phase = PHASE_OVER
		_banner = "YOU WIN!" if score[0] > score[1] else "You lost"
		return
	if _last_winner != serving:
		serving = _last_winner
		_rotate(near)
		_rotate(far)
	_start_serve()


# ── Tutorial ─────────────────────────────────────────────────────────────────
func _tut_setup(step: int) -> void:
	_tut = {"step": step, "phase": "intro", "t": 0.0}
	_reset_for_tut()
	_tut_stage(step)


func _reset_for_tut() -> void:
	_await = null
	_crossing = false
	_aimstep = null
	_setstep = null
	_serve_fault = false
	_serve_outcome = null
	_block_jump = 0.0
	_block_cd = 0.0
	_ai_block_jump = 0.0
	_block_target = null
	_in_system = true
	_time_target = 1.0
	for a in near + far:
		a.x = a.home.x
		a.y = a.home.y
		a.set_pose(P_READY)
		a.z = 0.0


func _tut_stage(step: int) -> void:
	var p := _player()
	var mech: String = _TUT_STEPS[step][0]
	if mech == "serve":
		serving = 0
		phase = PHASE_SERVE
		_serve_meter = 0.0
		_serve_dir = 1
		_serve_stage = "power"
		_serve_lat = 0.0
		_serve_lat_dir = 1
		_serve_power = 0.5
		var srv := _server()
		srv.x = _SERVE_POS[0].x
		srv.y = _SERVE_POS[0].y
		ball.hold_at(_SERVE_POS[0].x, _SERVE_POS[0].y)
	elif mech == "dig":
		phase = PHASE_RALLY
		p.x = _CX
		p.y = _C_B - 70
		var srv := _role(1, HITTER_R)
		srv.x = _SERVE_POS[1].x
		srv.y = _SERVE_POS[1].y
		srv.set_pose(P_READY)
		ball.hold_at(_SERVE_POS[1].x, _SERVE_POS[1].y)
	elif mech == "set":
		phase = PHASE_RALLY
		p.x = _CX
		p.y = _NET + 58
		var hl := _role(0, HITTER_L)
		var st := _role(0, SETTER)
		hl.x = _CX - 74
		hl.y = _NET + 46
		st.x = _CX + 74
		st.y = _NET + 46
		ball.hold_at(_C_R - 46, _C_B - 44)
	elif mech == "spike":
		phase = PHASE_RALLY
		p.x = _CX - 70
		p.y = _C_B - 64
		var st := _role(0, SETTER)
		st.x = _CX + 16
		st.y = _NET + 48
		st.set_pose(P_READY)
		var hl := _role(0, HITTER_L)
		hl.x = _CX + 70
		hl.y = _C_B - 60
		ball.hold_at(st.x, st.y - 6)
	else:  # block
		phase = PHASE_RALLY
		p.x = _CX
		p.y = _NET + 22
		var nst := _role(0, SETTER)
		nst.x = _CX + 72
		nst.y = _NET + 128
		var nhl := _role(0, HITTER_L)
		nhl.x = _CX - 72
		nhl.y = _NET + 128
		var setter := _role(1, SETTER)
		setter.x = _CX - 40
		setter.y = _NET - 42
		setter.set_pose(P_READY)
		var atk := _role(1, HITTER_R)
		atk.x = _CX + 70
		atk.y = _NET - 112
		atk.set_pose(P_READY)
		ball.hold_at(_CX - 96, _NET - 150)
	_separate()


func _tut_begin() -> void:
	var t = _tut
	t["phase"] = "active"
	var p := _player()
	var mech: String = _TUT_STEPS[t["step"]][0]
	if mech == "serve":
		return
	if mech == "dig":
		ball.launch(_SERVE_POS[1], Vector2(p.x, p.y), 178, 1.6)
		ball.team = 0
		_await = ["receive", p]
	elif mech == "set":
		ball.launch(Vector2(_C_R - 46, _C_B - 44), Vector2(p.x, p.y), 178, 1.45)
		ball.team = 0
		_await = ["set", p]
	elif mech == "spike":
		var st := _role(0, SETTER)
		st.set_pose(P_DIG)
		ball.launch(Vector2(st.x, st.y - 6), _net_point(0, p.x), 150, 1.35)
		ball.team = 0
		_await = ["spike", p]
	else:  # block
		t["bseq"] = 0
		var setter := _role(1, SETTER)
		ball.launch(Vector2(_CX - 96, _NET - 150), Vector2(setter.x, setter.y - 6), 150, 1.1)
		ball.team = 1
		_crossing = false


func _tut_block_lead(dt: float) -> void:
	var t = _tut
	var atk := _role(1, HITTER_R)
	ball.update(dt)
	if t["bseq"] == 1 and ball.in_flight:
		var to: Vector2 = t["atk_to"]
		atk.x += (to.x - atk.x) * minf(1.0, 6.0 * dt)
		atk.y += (to.y - atk.y) * minf(1.0, 6.0 * dt)
		atk.set_pose(P_RUN)
		return
	if ball.in_flight:
		return
	if t["bseq"] == 0:
		var setter := _role(1, SETTER)
		setter.set_pose(P_DIG)
		t["atk_to"] = Vector2(atk.x, _NET - 44)
		ball.launch(Vector2(setter.x, setter.y), Vector2(atk.x, _NET - 48), 130, 0.9)
		ball.team = 1
		t["bseq"] = 1
	else:
		atk.x = t["atk_to"].x
		atk.y = t["atk_to"].y
		atk.set_pose(P_JUMP)
		atk.z = 26.0
		var start := Vector2(atk.x, _NET - 40)
		ball.launch(start, Vector2(atk.x - 12, _NET + 95), 54, 0.56)
		ball.team = 1
		_crossing = true
		t["bseq"] = 2


func _tut_is(mech: String) -> bool:
	return _tut != null and _TUT_STEPS[_tut["step"]][0] == mech


func _tut_player_action(mech: String, ok := true) -> void:
	var t = _tut
	if t == null or t["phase"] != "active" or _TUT_STEPS[t["step"]][0] != mech:
		return
	t["phase"] = "resolve"
	t["t"] = Config.VB_TUT_RESOLVE
	t["ok"] = ok


func _tut_miss() -> void:
	var t = _tut
	if t != null and t["phase"] == "active":
		t["phase"] = "fail"
		t["t"] = Config.VB_TUT_FAIL


func _tut_meta(raw_dt: float) -> bool:
	var t = _tut
	var ph: String = t["phase"]
	if ph == "intro":
		if _action:
			_tut_begin()
		return true
	if ph == "resolve":
		t["t"] -= raw_dt
		var landed := not ball.in_flight
		if t["t"] <= 0 or (landed and t["t"] < Config.VB_TUT_RESOLVE - 0.3):
			if t.get("ok", true):
				t["phase"] = "success"
				t["t"] = Config.VB_TUT_SUCCESS
			else:
				t["phase"] = "fail"
				t["t"] = Config.VB_TUT_FAIL
		return false
	if ph == "success":
		t["t"] -= raw_dt
		if t["t"] <= 0:
			if t["step"] + 1 >= _TUT_STEPS.size():
				_banner = "Tutorial complete!"
				phase = PHASE_OVER
				_tut = null
			else:
				_tut_setup(t["step"] + 1)
		return true
	if ph == "fail":
		t["t"] -= raw_dt
		if t["t"] <= 0:
			t["phase"] = "intro"
			_reset_for_tut()
			_tut_stage(t["step"])
		return true
	if _TUT_STEPS[t["step"]][0] == "block" and t.get("bseq", 2) < 2:
		_update_timers(raw_dt)
		_move_player(raw_dt)
		if _action and _can_block():
			_start_block()
		_tut_block_lead(raw_dt)
		return true
	return false


# ── Update ───────────────────────────────────────────────────────────────────
func _approach(v: float, target: float, dt: float) -> float:
	var rate: float
	if target == 0.0 or (v != 0.0 and (target > 0) != (v > 0)) or absf(target) < absf(v):
		rate = Config.VB_DECEL
	else:
		rate = Config.VB_ACCEL
	if v < target:
		return minf(target, v + rate * dt)
	return maxf(target, v - rate * dt)


func _update_timers(dt: float) -> void:
	if _block_jump > 0:
		_block_jump -= dt
	if _block_cd > 0:
		_block_cd -= dt
	if _ai_block_jump > 0:
		_ai_block_jump -= dt


func _move_player(dt: float) -> void:
	if phase != PHASE_SERVE and phase != PHASE_RALLY:
		return
	var p := _player()
	if phase == PHASE_SERVE and p == _server():
		p.x = _SERVE_POS[serving].x
		p.y = _SERVE_POS[serving].y
		return
	var ty_target := _move.y * Config.VB_TOP_SPEED
	if ty_target > 0:
		ty_target *= Config.VB_BACKPEDAL_FACTOR
	_vel.x = _approach(_vel.x, _move.x * Config.VB_TOP_SPEED, dt)
	_vel.y = _approach(_vel.y, ty_target, dt)
	if p.pose == P_READY or p.pose == P_RUN:
		var spd := absf(_vel.x) + absf(_vel.y)
		p.set_pose(P_RUN if spd > 24 else P_READY)
	var fx_ := _face.x
	var fy := _face.y
	if absf(fx_) >= absf(fy):
		p.facing = "right" if fx_ > 0 else "left"
	else:
		p.facing = "down" if fy > 0 else "up"
	p.x = clampf(p.x + _vel.x * dt, _X_MIN, _X_MAX)
	p.y = clampf(p.y + _vel.y * dt, _NEAR_MIN_Y, _NEAR_MAX_Y)


func _defense_base(d_team: int, hitter: VBActor) -> Array:
	var dig_y := _NET + 138 if d_team == 0 else _NET - 138
	var line_x := clampf(hitter.x, _C_L + 34, _C_R - 34)
	var cross_x := clampf(2 * _CX - hitter.x, _C_L + 34, _C_R - 34)
	if absf(line_x - cross_x) < 80:
		line_x = clampf(_CX - 62, _C_L + 34, _C_R - 34)
		cross_x = clampf(_CX + 62, _C_L + 34, _C_R - 34)
	return [Vector2(line_x, dig_y), Vector2(cross_x, dig_y)]


func _defend_zone(a: VBActor, recv: int) -> Vector2:
	if a.role == SETTER:
		var side := -1.0 if ball.end.x > _CX else 1.0
		return Vector2(clampf(_CX + side * 46, _C_L + 18, _C_R - 18),
			_NET + 48 if recv == 0 else _NET - 48)
	var wing := 1.0 if a.home.x >= _CX else -1.0
	return Vector2(clampf(_CX + wing * 104, _C_L + 30, _C_R - 30),
		_NET + 138 if recv == 0 else _NET - 138)


func _attack_wing(a: VBActor) -> Vector2:
	var wing := 1.0 if a.home.x >= _CX else -1.0
	return Vector2(clampf(_CX + wing * 96, _C_L + 24, _C_R - 24),
		_NET + 44 if a.team == 0 else _NET - 44)


func _crossing_receiver(recv_team: int) -> VBActor:
	var key := [ball.start, ball.end]
	if _recv_cache == null or _recv_cache[0] != key:
		_recv_cache = [key, _receiver(recv_team)]
	return _recv_cache[1]


func _ball_player() -> VBActor:
	if _await != null and _await[0] in ["receive", "set", "spike"]:
		var c = _await[1]
		if c == null and _await[0] == "receive":
			c = _nearest_defender(ball.team, ball.end)
		return c if (c != null and not c.is_player) else null
	if _crossing and ball.in_flight:
		var c := _crossing_receiver(1 - ball.team)
		return c if not c.is_player else null
	return null


func _separate(dt = null) -> void:
	var min_d := 42.0
	var cap: float = Config.VB_ACTOR_SPEED * dt if dt != null else min_d
	var protected := _ball_player()
	for team in [near, far]:
		for i in team.size():
			var a: VBActor = team[i]
			for j in range(i + 1, team.size()):
				var b: VBActor = team[j]
				if protected != null and ((a.is_player and b == protected) or (b.is_player and a == protected)):
					continue
				var dx := b.x - a.x
				var dy := b.y - a.y
				var d2 := dx * dx + dy * dy
				if d2 >= min_d * min_d or d2 < 1e-6:
					continue
				var d := sqrt(d2)
				var shove: float = minf(min_d - d, cap)
				var ux := dx / d
				var uy := dy / d
				if a.is_player:
					b.x += ux * shove
					b.y += uy * shove
				elif b.is_player:
					a.x -= ux * shove
					a.y -= uy * shove
				else:
					a.x -= ux * shove * 0.5
					a.y -= uy * shove * 0.5
					b.x += ux * shove * 0.5
					b.y += uy * shove * 0.5
		for a in team:
			if a.is_player:
				continue
			a.x = clampf(a.x, _X_MIN, _X_MAX)
			a.y = (clampf(a.y, _NET + 10, _NEAR_MAX_Y) if a.team == 0
				else clampf(a.y, _FAR_MIN_Y, _NET - 10))


func _ai_step(a: VBActor, tx: float, ty: float, dt: float) -> void:
	var dx := tx - a.x
	var dy := ty - a.y
	var d := sqrt(dx * dx + dy * dy)
	if d <= 1.0:
		a.x = tx
		a.y = ty
		a.vx = 0.0
		a.vy = 0.0
		return
	var vmax: float = minf(Config.VB_TOP_SPEED, sqrt(2.0 * Config.VB_DECEL * d))
	var tvx := dx / d * vmax
	var tvy := dy / d * vmax
	if (tvy > 0 if a.team == 0 else tvy < 0):
		tvy *= Config.VB_BACKPEDAL_FACTOR
	a.vx = _approach(a.vx, tvx, dt)
	a.vy = _approach(a.vy, tvy, dt)
	a.x += a.vx * dt
	a.y += a.vy * dt


func _move_ai(dt: float) -> void:
	_react_t = maxf(0.0, _react_t - dt)
	if _crossing and not _was_crossing:
		_react_t = _team_diff(1 - ball.team).get("reaction", 0.25)
	_was_crossing = _crossing
	var recv = null
	var receiver: VBActor = null
	if _await != null and _await[0] == "receive":
		recv = ball.team
		receiver = _await[1]
	elif _crossing and ball.in_flight:
		recv = 1 - ball.team
		receiver = _crossing_receiver(recv)
	if receiver != null and recv != null and ball.in_flight:
		var best := _best_digger(recv)
		if (best != null and best != receiver
				and receiver.dist_to(ball.end.x, ball.end.y) > best.dist_to(ball.end.x, ball.end.y) + Config.VB_DIG_SWITCH_MARGIN):
			receiver = best
			if _await != null and _await[0] == "receive":
				_await = ["receive", best]
			else:
				_recv_cache = [[ball.start, ball.end], best]
	var stored: VBActor = _await[1] if (_await != null and _await[0] in ["set", "spike"]) else null
	var aim_block := (_aimstep != null and _aimstep.get("block_x") != null)
	var bt = _block_target
	var base := {}
	if _await != null and _await[0] == "spike":
		var hitter: VBActor = _await[1]
		var slots := _defense_base(1 - hitter.team, hitter)
		var defs := _team(1 - hitter.team).filter(func(a): return a.role != SETTER and not a.is_player)
		for d in defs:
			if slots.is_empty():
				break
			var slot = _min_by(slots, func(s): return (d.x - s.x) * (d.x - s.x) + (d.y - s.y) * (d.y - s.y))
			base[d] = slot
			slots.erase(slot)
	for a in near + far:
		if a.is_player:
			continue
		if a.role == SETTER and a.team == 0 and _ai_block_jump > 0:
			continue
		if aim_block and a.role == SETTER and a.team == 1:
			continue
		if bt != null and a == bt["blocker"]:
			var ny: float
			if bt.get("late"):
				var off := Config.VB_BLOCK_NET_DIST + 20
				ny = _NET - off if a.team == 1 else _NET + off
			else:
				ny = _NET - Config.VB_NET_CONTACT if a.team == 1 else _NET + Config.VB_NET_CONTACT
			a.move_toward_pt(float(bt["lane_x"]), ny, dt, Config.VB_ACTOR_SPEED)
			continue
		if base.has(a):
			_ai_step(a, base[a].x, base[a].y, dt)
			continue
		var target: Vector2
		if a == stored or (a == receiver and _react_t <= 0.0):
			target = ball.end
		elif a == receiver and a.dist_to(ball.end.x, ball.end.y) <= Config.VB_DIG_INSTANT_RADIUS:
			target = Vector2(a.x, a.y)
		elif recv != null and a.team == recv:
			target = _defend_zone(a, recv)
		elif (stored != null and _await[0] == "set" and a.team == stored.team and a.role != SETTER):
			target = _attack_wing(a)
		elif _tut != null:
			target = Vector2(a.x, a.y)
		elif (ball.in_flight and a.role != SETTER and _ball_to_side(a.team)
				and a.dist_to(ball.end.x, ball.end.y) <= Config.VB_DIG_INSTANT_RADIUS):
			target = ball.end
		else:
			target = a.home
		_ai_step(a, target.x, target.y, dt)
	_separate(dt)


func _process(delta: float) -> void:
	var raw_dt := delta
	_time_scale += (_time_target - _time_scale) * minf(1.0, 10.0 * raw_dt)
	var game_dt := raw_dt * _time_scale
	_prev_y = ball.y
	_move = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if _move != Vector2.ZERO:
		_face = _move

	fx.update(raw_dt)
	for a in near + far:
		a.update_anim(raw_dt)
	if _hit_feedback != null:
		var nt: float = _hit_feedback[1] - raw_dt
		_hit_feedback = [_hit_feedback[0], nt] if nt > 0 else null

	_step_logic(raw_dt, game_dt)

	# mirror sim -> nodes
	_world.position = fx.offset()
	_apply_layering()
	_ballnode.queue_redraw()
	_play.queue_redraw()
	_dim.queue_redraw()
	_top.queue_redraw()
	_hud.queue_redraw()


func _step_logic(raw_dt: float, game_dt: float) -> void:
	if _intro:
		if _action:
			_intro = false
		_clear_presses()
		return

	if _tut != null:
		if _tut_meta(raw_dt):
			_clear_presses()
			return

	if phase == PHASE_OVER:
		if _action and on_finish.is_valid():
			on_finish.call()
		_clear_presses()
		return
	if phase == PHASE_POINT:
		ball.update(game_dt)
		if _timer > 0:
			_timer -= raw_dt
		elif _action:
			_after_point()
		_clear_presses()
		return

	if _aimstep != null:
		_update_aimstep(raw_dt)
		_move_ai(game_dt)
		_clear_presses()
		return

	if _setstep != null:
		_update_setstep(raw_dt)
		_move_ai(game_dt)
		_clear_presses()
		return

	_update_timers(game_dt)
	_move_player(game_dt)
	if _action and _can_block():
		_start_block()
	ball.update(game_dt)
	_move_ai(game_dt)

	if phase == PHASE_SERVE:
		if _server().is_player:
			if _serve_stage == "power":
				_serve_meter += Config.VB_SERVE_METER_SPEED * game_dt * _serve_dir
				if _serve_meter >= 1.0:
					_serve_meter = 1.0
					_serve_dir = -1
				elif _serve_meter <= 0.0:
					_serve_meter = 0.0
					_serve_dir = 1
				if _action:
					_serve_power = _serve_meter
					_serve_stage = "lateral"
			else:
				_serve_lat += Config.VB_SERVE_LAT_SPEED * game_dt * _serve_lat_dir
				if _serve_lat >= 1.0:
					_serve_lat = 1.0
					_serve_lat_dir = -1
				elif _serve_lat <= 0.0:
					_serve_lat = 0.0
					_serve_lat_dir = 1
				if _action:
					_execute_serve(_serve_power, _serve_lat)
		else:
			_serve_timer -= game_dt
			if _serve_timer <= 0:
				_do_serve()
	else:
		_resolve(game_dt)
	_clear_presses()


func _clear_presses() -> void:
	_action = false
	_set_pressed = false
	_tip_pressed = false


func _apply_layering() -> void:
	for a in near + far:
		a.z_index = clampi(int(round(a.y)), -4096, 480)
	_ballnode.z_index = 1000
	if _aimstep != null:
		var c: VBActor = _aimstep["contactor"]
		c.z_index = 1600
		_ballnode.z_index = 1600
	elif _setstep != null:
		_setstep["contactor"].z_index = 1600
		for h in _setstep["attackers"]:
			h.z_index = 1600
		_ballnode.z_index = 1600


# ── Math helpers ──────────────────────────────────────────────────────────────
func _hang(peak: float) -> float:
	return 0.45 + 0.072 * sqrt(peak)


# ── Draw: court layer (z -10) — surface + net + ref stool + landing targets ───
func _draw_court(c: CanvasItem) -> void:
	c.draw_rect(Rect2(0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), _CLAD)
	c.draw_rect(Rect2(_H_L, _H_T, 340, 468), _FLOOR_EDGE)
	c.draw_rect(Rect2(_H_L + 5, _H_T + 5, 330, 458), _FLOOR)
	c.draw_rect(Rect2(_C_L, _C_T, _C_W, 428), _FLOOR_CT)
	for top in [_NET - _ATTACK, _NET]:
		c.draw_rect(Rect2(_C_L, top, _C_W, _ATTACK), _FLOOR_ATK)
	c.draw_rect(Rect2(_C_L, _C_T, _C_W, 428), _LINE, false, 2)
	for dy in [-_ATTACK, _ATTACK]:
		c.draw_line(Vector2(_C_L, _NET + dy), Vector2(_C_R, _NET + dy), _LINE, 1)
	var bl := _C_L - 6
	var br := _C_R + 6
	c.draw_rect(Rect2(bl, _NET - 6, _C_W + 12, 12), _NET_BG)
	var mx := int(bl)
	while mx < br:
		c.draw_line(Vector2(mx, _NET - 4), Vector2(mx, _NET + 4), _NET_MESH, 1)
		mx += 7
	c.draw_line(Vector2(bl, _NET - 6), Vector2(br, _NET - 6), _NET_W, 2)
	c.draw_line(Vector2(bl, _NET + 6), Vector2(br, _NET + 6), _NET_W, 2)
	for px in [_C_L - 6, _C_R + 6]:
		c.draw_rect(Rect2(px - 2, _NET - 20, 4, 40), _POST)
	# the ref's stool (the ref sprite is a node above)
	c.draw_rect(Rect2(_ref.position.x - 7, _ref.position.y + 6, 14, 6), Color8(60, 50, 40))
	# serve aim preview + ball landing target (under the actors)
	if phase == PHASE_SERVE and _server().is_player:
		var power := _serve_meter if _serve_stage == "power" else _serve_power
		var lat := 0.5 if _serve_stage == "power" else _serve_lat
		var res := _serve_target(power, lat, serving)
		_draw_target(c, res[0], _GREEN if res[1] == "in" else _RED, 0.0)
		if _serve_stage == "lateral":
			var half := _opp_half(serving)
			var lx := lerpf(half[0] + 10, half[1] - 10, _serve_lat)
			var base_y := _C_T + 16 if serving == 0 else _C_B - 16
			c.draw_line(Vector2(lx, _NET), Vector2(lx, base_y), Color8(255, 240, 150), 1)
			c.draw_circle(Vector2(lx, base_y), 5, Color8(255, 240, 150))
	if ball.in_flight and (_await != null or _crossing or _serve_fault):
		var fault: bool = (_serve_fault and _serve_outcome != null and _serve_outcome[0] == "fault")
		_draw_target(c, ball.end, _RED if fault else _MARK, ball.remaining())


func _draw_target(c: CanvasItem, pt: Vector2, col: Color, rem: float) -> void:
	var mx := pt.x
	var my := pt.y
	var r: float = 7 + 20 * minf(1.0, rem / 0.9)
	_ell_out(c, mx - r, my - r / 2.0, r * 2, r, col, 1)
	_ell_out(c, mx - 9, my - 5, 18, 10, col, 2)
	c.draw_line(Vector2(mx - 12, my), Vector2(mx + 12, my), col, 1)
	c.draw_line(Vector2(mx, my - 7), Vector2(mx, my + 7), col, 1)


# ── Draw: dim layer (z 1500) — darkens the court during aim/set steps ─────────
func _draw_dim(c: CanvasItem) -> void:
	if _aimstep != null or _setstep != null:
		c.draw_rect(Rect2(0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT),
			Color(6.0 / 255, 8.0 / 255, 24.0 / 255, 120.0 / 255))


# ── Draw: top layer (z 2000) — guides, reticle, contact ring, block bar, fx ───
func _draw_top(c: CanvasItem) -> void:
	var cc := _current_contactor()
	if (phase == PHASE_RALLY and cc != null and cc.is_player and ball.in_flight
			and _aimstep == null):
		var rem := ball.remaining()
		if rem <= Config.VB_TIMING_WINDOW:
			var r := 10 + 26 * (rem / Config.VB_TIMING_WINDOW)
			var col := Color8(250, 240, 140) if rem <= Config.VB_PERFECT_WINDOW else Color8(240, 250, 250)
			c.draw_arc(Vector2(cc.x, cc.y), r, 0, TAU, 24, col, 2)
	if _aimstep != null:
		_draw_aim_guides(c)
	if _setstep != null:
		_draw_set_guides(c)
	if _block_jump > 0:
		var p := _player()
		c.draw_line(Vector2(p.x - Config.VB_BLOCK_REACH, _NET),
			Vector2(p.x + Config.VB_BLOCK_REACH, _NET), _GREEN, 3)
	fx.draw(c)


func _draw_aim_guides(c: CanvasItem) -> void:
	var a = _aimstep
	var ct: VBActor = a["contactor"]
	var deep_y := _C_T + 30 if ct.team == 0 else _C_B - 30
	var line_x := clampf(ct.x, _C_L + 26, _C_R - 26)
	var cross_x := clampf(2 * _CX - ct.x, _C_L + 26, _C_R - 26)
	for pair in [[line_x, "LINE"], [cross_x, "CROSS"]]:
		var gx: float = pair[0]
		var reachable: bool = a["xmin"] <= gx and gx <= a["xmax"]
		var col := _GUIDE if reachable else Color8(78, 88, 104)
		c.draw_line(Vector2(ct.x, ct.y), Vector2(gx, deep_y), col, 1)
		c.draw_arc(Vector2(gx, deep_y), 9, 0, TAU, 18, col, 1)
		var ly := deep_y + 12 if ct.team == 0 else deep_y - 24
		_text(c, gx, ly, pair[1], 11, col, true)
	var bx = a.get("block_x")
	var in_block: bool = bx != null and absf(a["rx"] - float(bx)) <= Config.VB_BLOCK_REACH
	if bx != null:
		var top := _C_T if ct.team == 0 else _NET
		c.draw_rect(Rect2(bx - Config.VB_BLOCK_REACH, minf(_NET, top),
			Config.VB_BLOCK_REACH * 2, absf(_NET - top) + 4),
			Color(235.0 / 255, 80.0 / 255, 70.0 / 255, 70.0 / 255))
		c.draw_line(Vector2(bx - Config.VB_BLOCK_REACH, _NET),
			Vector2(bx + Config.VB_BLOCK_REACH, _NET), _RED, 3)
	var zone := _spike_zone(Vector2(a["rx"], a["ry"]), ct.team)
	var col2 := _RED if (in_block or zone != "in") else _GREEN
	var rx: float = a["rx"]
	var ry: float = a["ry"]
	c.draw_arc(Vector2(rx, ry), 16, 0, TAU, 24, col2, 2)
	c.draw_line(Vector2(rx - 22, ry), Vector2(rx + 22, ry), col2, 1)
	c.draw_line(Vector2(rx, ry - 22), Vector2(rx, ry + 22), col2, 1)
	var pw: float = _hit_quality(float(a["meter"]))[1]
	c.draw_rect(Rect2(rx - 18, ry + 22, 36, 5), Color8(40, 40, 50))
	c.draw_rect(Rect2(rx - 18, ry + 22, 36 * pw, 5), Color8(250, 220, 90))


func _draw_set_guides(c: CanvasItem) -> void:
	var s = _setstep
	var atk: Array = s["attackers"].duplicate()
	atk.sort_custom(func(a, b): return a.x < b.x)
	var labels := ["LEFT", "RIGHT"] if atk.size() >= 2 else ["SET"]
	for i in atk.size():
		var h: VBActor = atk[i]
		var chosen: bool = h == s["choice"]
		var col := _GREEN if chosen else _GUIDE
		c.draw_arc(Vector2(h.x, h.y), 20, 0, TAU, 24, col, 2 if chosen else 1)
		if i < labels.size():
			_text(c, h.x, h.y + 18, labels[i], 11, col, true)


# ── Draw: HUD layer (z 3000), screen-space ────────────────────────────────────
func _draw_overlay(c: CanvasItem) -> void:
	if _intro:
		_draw_intro(c)
		return
	var sw := Config.SCREEN_WIDTH
	var score_str := "%d  -  %d" % [score[0], score[1]]
	var sbw := _text_w(score_str, 22)
	_panel(c, sw / 2.0 - sbw / 2.0 - 16, 6, sbw + 32, 38)
	_text(c, sw / 2.0, 10, score_str, 22, Color8(245, 248, 255), true)
	if _tut != null:
		_draw_tut(c)
	_draw_left_hud(c)
	_draw_now(c)
	_draw_legend(c)
	_draw_right_hud(c)
	if phase == PHASE_SERVE and _server().is_player:
		_draw_serve_meter(c)
	if _aimstep != null:
		_draw_spike_meter(c)
	if _hit_feedback != null:
		_draw_hit_feedback(c)
	if (phase == PHASE_POINT or phase == PHASE_OVER) and _banner != "":
		var bw := _text_w(_banner, 22)
		var bx := sw / 2.0 - bw / 2.0
		var by := Config.SCREEN_HEIGHT / 2.0 - 20
		c.draw_rect(Rect2(bx - 16, by - 8, bw + 32, 38), _BANNER)
		_text(c, bx, by, _banner, 22, Color8(255, 255, 255))
		if phase == PHASE_OVER or (phase == PHASE_POINT and _timer <= 0):
			var label: String = "press Z" if phase == PHASE_OVER else "press Z for next point"
			_text(c, sw / 2.0, by + 40, label, 13, Color8(220, 220, 220), true)


func _draw_tut(c: CanvasItem) -> void:
	var t = _tut
	var step: int = t["step"]
	var ph: String = t["phase"]
	var keys := {"hit": "Z", "set": "X", "move": "arrows"}
	var head := "Tutorial  %d/%d" % [step + 1, _TUT_STEPS.size()]
	var instr: String = (_TUT_STEPS[step][1] as String).format(keys)
	var status := ""
	var col := Color8(250, 245, 200)
	if ph == "success":
		status = "Nice!"
		col = Color8(170, 255, 185)
	elif ph == "fail":
		status = ("Needs a PERFECT hit over — going again..."
			if _TUT_STEPS[step][0] == "spike" else "Just missed — going again...")
		col = Color8(255, 190, 170)
	elif ph == "intro":
		status = "Press Z to start"
		col = Color8(255, 230, 140)
	var sw := Config.SCREEN_WIDTH
	var cx := sw / 2.0
	# Wrap to a capped width so the panel sits between the side HUD columns and below
	# the score box, instead of spanning the screen and overlapping them.
	var maxw := 300.0
	var instr_lines := _wrap(instr, maxw, 13)
	var status_lines: Array = _wrap(status, maxw, 13) if status != "" else []
	var w := _text_w(head, 11)
	for ln in instr_lines:
		w = maxf(w, _text_w(ln, 13))
	for ln in status_lines:
		w = maxf(w, _text_w(ln, 13))
	w += 36
	var y0 := 48.0
	var h := 22.0 + instr_lines.size() * 16 + (status_lines.size() * 16 + 6 if status != "" else 0)
	_panel(c, cx - w / 2.0, y0, w, h)
	_text(c, cx, y0 + 6, head, 11, Color8(180, 200, 230), true)
	var yy := y0 + 22
	for ln in instr_lines:
		_text(c, cx, yy, ln, 13, Color8(245, 242, 212), true)
		yy += 16
	yy += 6
	for ln in status_lines:
		_text(c, cx, yy, ln, 13, col, true)
		yy += 16


func _draw_left_hud(c: CanvasItem) -> void:
	_panel(c, 6, 50, 140, 46)
	var rn: int = _player().role
	var role: String = {SETTER: "Setter", HITTER_L: "Hitter L", HITTER_R: "Hitter R"}.get(rn, "?")
	_text(c, 16, 56, "YOU · " + role, 10, Color8(150, 200, 255))
	_text(c, 16, 74, "Your serve" if serving == 0 else "Their serve", 11, Color8(205, 210, 220))


func _draw_now(c: CanvasItem) -> void:
	var prompt := _prompt()
	if prompt == "":
		return
	var lines := _wrap(prompt, 124, 11)
	_panel(c, 6, 104, 140, 24 + lines.size() * 15)
	_text(c, 16, 108, "NOW", 10, Color8(150, 200, 255))
	for i in lines.size():
		_text(c, 16, 122 + i * 15, lines[i], 11, Color8(245, 240, 200))


func _draw_right_hud(c: CanvasItem) -> void:
	if phase == PHASE_RALLY:
		_panel(c, 494, 50, 140, 30)
		_text(c, 504, 56, "Rally · %d touches" % _rally_touches, 11, Color8(220, 225, 235))


func _draw_legend(c: CanvasItem) -> void:
	var ctrls := [["Arrows", "Move"], ["Z", "Hit"], ["X", "Set"],
		["C", "Tip / dump"], ["Esc", "Pause"]]
	var row := 18
	var h := 24 + ctrls.size() * row
	var y0 := Config.SCREEN_HEIGHT - 8 - h
	_panel(c, 6, y0, 140, h)
	_text(c, 16, y0 + 6, "CONTROLS", 10, Color8(150, 180, 225))
	for i in ctrls.size():
		var yy := y0 + 24 + i * row
		var kw := _text_w(ctrls[i][0], 10) + 10
		c.draw_rect(Rect2(16, yy, kw, 15), Color8(205, 214, 230))
		_text(c, 21, yy + 1, ctrls[i][0], 10, Color8(20, 24, 32))
		_text(c, 16 + kw + 8, yy, ctrls[i][1], 11, Color8(220, 225, 235))


func _draw_intro(c: CanvasItem) -> void:
	var w := 404
	var h := 322
	var sw := Config.SCREEN_WIDTH
	var x := sw / 2.0 - w / 2.0
	var y := Config.SCREEN_HEIGHT / 2.0 - h / 2.0
	c.draw_rect(Rect2(x, y, w, h), Color8(16, 20, 28))
	c.draw_rect(Rect2(x, y, w, h), Color8(90, 150, 220), false, 2)
	_text(c, sw / 2.0, y + 12, "HOW TO PLAY", 22, Color8(255, 255, 255), true)
	var lines := [
		"You control the highlighted player",
		"(bright ring + marker). 3 vs 3.",
		"",
		"Rally:  serve  ->  dig  ->  set  ->  spike",
		"",
		"Arrows : move (run under the ball)",
		"Z : dig / attack / serve / block",
		"X : set     C : tip / dump",
		"",
		"At the net: Z to leap into slow-mo, aim,",
		"then Z to spike or C to tip.",
		"",
		"On ball 2 at the net: Z attack /",
		"X set / C dump.  On D: Z to block.",
		"Serve: Z for power, then Z to aim L/R.",
		"",
		"First to 7, win by 2.",
	]
	var ly := y + 50
	for ln in lines:
		_text(c, x + 20, ly, ln, 11, Color8(220, 224, 230))
		ly += 14
	_text(c, sw / 2.0, y + h - 24, "press Z to start", 13, Color8(250, 240, 160), true)


func _draw_serve_meter(c: CanvasItem) -> void:
	var bx := 506.0
	var by := 130.0
	var bw := 16.0
	var bh := 220.0
	c.draw_rect(Rect2(bx - 2, by - 2, bw + 4, bh + 4), Color8(24, 26, 34))
	var nm: float = Config.VB_SERVE_NET_MAX
	var om: float = Config.VB_SERVE_OUT_MIN
	var glo: float = Config.VB_SERVE_GREEN.x
	var ghi: float = Config.VB_SERVE_GREEN.y
	var segs := [[0.0, nm, Color8(150, 50, 46)], [nm, glo, Color8(208, 132, 52)],
		[glo, ghi, Color8(70, 200, 110)], [ghi, om, Color8(208, 132, 52)],
		[om, 1.0, Color8(150, 50, 46)]]
	for s in segs:
		var y0: float = by + bh * (1.0 - s[1])
		c.draw_rect(Rect2(bx, y0, bw, by + bh * (1.0 - s[0]) - y0), s[2])
	var val := _serve_meter if _serve_stage == "power" else _serve_power
	var my := by + bh * (1.0 - val)
	var locked := _serve_stage != "power"
	c.draw_rect(Rect2(bx - 4, my - 2, bw + 8, 4),
		Color8(110, 200, 130) if locked else Color8(255, 240, 150))
	_text(c, bx - 6, by - 20, "PWR", 11, Color8(220, 220, 220))


func _draw_spike_meter(c: CanvasItem) -> void:
	var bx := 506.0
	var by := 130.0
	var bw := 16.0
	var bh := 220.0
	c.draw_rect(Rect2(bx - 2, by - 2, bw + 4, bh + 4), Color8(24, 26, 34))
	var lo: float = Config.VB_SPIKE_SWEET_LO
	var hi: float = Config.VB_SPIKE_SWEET_HI
	var ow := 0.17
	var segs := [[0.0, lo - ow, Color8(172, 56, 50)], [lo - ow, lo, Color8(208, 132, 52)],
		[lo, hi, Color8(70, 200, 110)], [hi, hi + ow, Color8(208, 132, 52)],
		[hi + ow, 1.0, Color8(172, 56, 50)]]
	for s in segs:
		var y0: float = by + bh * (1.0 - s[1])
		c.draw_rect(Rect2(bx, y0, bw, by + bh * (1.0 - s[0]) - y0), s[2])
	var my := by + bh * (1.0 - float(_aimstep["meter"]))
	c.draw_rect(Rect2(bx - 4, my - 2, bw + 8, 4), Color8(255, 255, 255))
	_text(c, bx - 6, by - 20, "HIT", 11, Color8(220, 220, 220))


func _draw_hit_feedback(c: CanvasItem) -> void:
	var label: String = _hit_feedback[0]
	var t: float = _hit_feedback[1]
	var col: Color
	if label == "PERFECT":
		col = Color8(255, 224, 90)
	elif label in ["SHANK", "LATE", "LATE!", "EARLY"]:
		col = Color8(240, 150, 150)
	else:
		col = Color8(245, 180, 120)
	var txt := label + ("!" if label == "PERFECT" else "")
	var a: float = clampf(t / 0.7, 0.0, 1.0)
	var y := Config.SCREEN_HEIGHT * 0.30 - (1.0 - a) * 10
	_text(c, Config.SCREEN_WIDTH / 2.0, y, txt, 30, col, true)


func _prompt() -> String:
	if phase == PHASE_SERVE and _server().is_player:
		if _serve_stage == "power":
			return "Z: set power (green = fast)"
		return "Z: aim left / right"
	if _aimstep != null:
		return "Aim · Z spike · C tip"
	if _setstep != null:
		return "Pick side · X set · C dump"
	if _block_jump > 0:
		return "BLOCK!"
	if _can_block():
		return "At the net — Z to block"
	var cc := _current_contactor()
	if phase == PHASE_RALLY and cc != null and cc.is_player:
		var kind: String = _await[0]
		if kind == "receive":
			return "Get under it — Z to dig"
		if kind == "set":
			if _at_net(cc):
				return "Z hit · X set · C dump"
			return "X to set · C dump"
		if kind == "spike":
			return "Run in — Z to leap & aim"
	return ""


# ── Draw primitives ───────────────────────────────────────────────────────────
func _panel(c: CanvasItem, x: float, y: float, w: float, h: float) -> void:
	c.draw_rect(Rect2(x, y, w, h), _PANEL)
	c.draw_rect(Rect2(x, y, w, h), _PANEL_BD, false, 1)


func _ell_out(c: CanvasItem, x: float, y: float, w: float, h: float, col: Color, width: float) -> void:
	c.draw_set_transform(Vector2(x + w / 2.0, y + h / 2.0), 0, Vector2(w / 2.0, h / 2.0))
	c.draw_arc(Vector2.ZERO, 1.0, 0, TAU, 24, col, width / maxf(w, h) * 2.0)
	c.draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


func _text(c: CanvasItem, x: float, y: float, s: String, size: int, col: Color, center := false) -> void:
	var px := x
	if center:
		px -= _text_w(s, size) / 2.0
	c.draw_string(_font, Vector2(px, y + size), s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


func _text_w(s: String, size: int) -> float:
	return _font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x


func _wrap(text: String, maxw: float, size: int) -> Array:
	var lines := []
	var cur := ""
	for word in text.split(" "):
		var trial := word if cur == "" else cur + " " + word
		if _text_w(trial, size) <= maxw or cur == "":
			cur = trial
		else:
			lines.append(cur)
			cur = word
	if cur != "":
		lines.append(cur)
	return lines
