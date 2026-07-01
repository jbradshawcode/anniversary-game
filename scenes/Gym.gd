# Scene 1 — Latymer sports hall (volleyball). Ported from scenes/gym.py.
# Structures via _draw() (1:1 with the pygame draw_structures); walls + walkable
# bounds feed the TileGrid; owns the referee Matúš and the scene's 2D lighting.
class_name Gym
extends GameScene

const _TS := 32
const _SW := 640
const _SH := 480

var _CLAD := Color8(202, 182, 142)
var _CLAD_DK := Color8(184, 163, 122)
var _FLOOR := Color8(66, 130, 180)
var _FLOOR_SHEEN := Color8(78, 143, 192)
var _VB := Color8(248, 248, 248)
var _ORANGE := Color8(228, 128, 52)
var _YELLOW := Color8(232, 198, 72)
var _NET_FILL := Color8(230, 232, 236)
var _NET_MESH := Color8(198, 202, 208)
var _NET_TAPE := Color8(250, 250, 250)
var _POLE := Color8(180, 180, 190)
var _ANT_R := Color8(212, 64, 52)
var _ANT_W := Color8(240, 240, 240)
var _CURT := Color8(44, 92, 172)
var _CURT_DK := Color8(32, 68, 132)
var _CURT_LT := Color8(78, 130, 206)
var _RAIL := Color8(120, 124, 132)
var _CURT_SH := Color8(40, 74, 124)
var _CORR := Color8(180, 174, 164)
var _CORR_DK := Color8(66, 62, 56)
var _DOOR_PLY := Color8(196, 176, 136)
var _DOOR_RV := Color8(150, 128, 92)
var _GLASS_PN := Color8(58, 70, 78)
var _EXIT_GRN := Color8(46, 158, 74)
var _EXIT_LT := Color8(210, 238, 215)
var _HOOP_OR := Color8(230, 120, 40)
var _BACKBOARD := Color8(240, 240, 238)
var _BB_DK := Color8(200, 200, 198)
# Wall benches (entities/bench.py) and ball baskets (entities/ball_basket.py) —
# factory props in scene_configs['gym'], drawn here + blocked in _init.
var _BENCH_SEAT := Color8(148, 108, 58)
var _BENCH_LITE := Color8(168, 128, 72)
var _BENCH_EDGE := Color8(88, 60, 32)
var _BK_BOX := Color8(35, 85, 185)
var _BK_BOX_DK := Color8(20, 60, 145)
var _BK_BOX_LT := Color8(65, 115, 220)
var _BK_BALL := Color8(240, 195, 20)
var _BK_BALL_HI := Color8(255, 235, 100)
var _BK_OUTLINE := Color8(20, 20, 20)
var _BK_STILT := Color8(170, 170, 185)
var _BK_STILT_DK := Color8(120, 120, 135)
var _BK_WHEEL := Color8(45, 45, 52)

const _BENCH_H := 5
const _BENCHES := [Vector2i(1, 2), Vector2i(1, 8), Vector2i(18, 2), Vector2i(18, 8)]
const _BASKETS := [Vector2i(2, 7), Vector2i(17, 7)]

var _HALL := Rect2(24, 24, _SW - 48, _SH - 48)
var _LEFT := Rect2(2 * _TS, 3 * _TS, 7 * _TS, 10 * _TS)
var _RIGHT := Rect2(11 * _TS, 3 * _TS, 7 * _TS, 10 * _TS)
var _NET_Y := 8 * _TS
var _CURT_X := 10 * _TS
var _NETB := Rect2(54, 86, 532, 308)


func _init() -> void:
	bg_texture = "res://assets/baked/gym_bg.png"   # native backdrop; _draw() is now the re-bake seed
	walkable_cols = Vector2i(1, 18)
	walkable_rows = Vector2i(1, 13)
	exits = {"up": {"scene": 5, "cols": Vector2i(8, 11)}}
	entry_points = {"down": Vector2i(9, 1)}
	var blocked: Array = []
	for b in _BENCHES:                    # each bench blocks its column for _BENCH_H tiles
		for i in _BENCH_H:
			blocked.append(Vector2i(b.x, b.y + i))
	for k in _BASKETS:                    # baskets block their single tile
		blocked.append(k)
	grid = TileGrid.new(
		walkable_cols, walkable_rows,
		Config.MAP_COLS, Config.MAP_ROWS,
		blocked, _build_walls())

	# Cool overhead light pools — a lit sports hall (gym.py `lighting`).
	ambient_color = Color(0.56, 0.59, 0.65)
	var pool := Color8(232, 240, 255)
	for y in [90, 250]:
		for x in [160, 320, 480]:
			lights.append({"pos": Vector2(x, y), "radius": 128.0, "color": pool, "energy": 0.85})


func _on_ready() -> void:
	# The Ch1 crew at their scene_configs tiles; Matúš the ref sits on the right bench.
	var crew: Array = [
		James.new(5, 7), Dan.new(14, 7), Matt.new(3, 4), Leonard.new(16, 7),
		Nat.new(8, 1), Bailey.new(6, 4), Mayu.new(15, 10), Wallace.new(8, 10),
	]
	var matus := Matus.new(18, 3)
	matus.sit("left")
	crew.append(matus)
	var blockers: Array = []
	for c in crew:
		add_child(c)
		npcs.append(c)
		blockers.append(Vector2i(c.tile_x, c.tile_y))
	grid.set_blockers(blockers)

	# Features as their own nodes (never baked). Carts and nets sort against movers by their
	# base-Y; the wall benches and the court-divider curtain sit at Z_BACK — nothing ever
	# stands behind them, so seated/standing crew (e.g. Matúš on the bench) render in front.
	for b in _BENCHES:
		var bench := Fixture.new()
		bench.setup(Fixture.Z_BACK, _draw_bench.bind(b.x, b.y, _BENCH_H))
		add_child(bench)
	for k in _BASKETS:
		var cart := Fixture.new()
		cart.setup((k.y + 1) * _TS, _draw_basket.bind(k.x, k.y))
		add_child(cart)
	for court in [_LEFT, _RIGHT]:
		var net := Fixture.new()
		net.setup(_NET_Y + 22, _draw_net.bind(court))
		add_child(net)
	var curtain := Fixture.new()
	curtain.setup(Fixture.Z_BACK, _draw_curtain)
	add_child(curtain)


func _build_walls() -> Array:
	var w: Array = []
	for c in range(2, 9):
		w.append([Vector2i(c, 7), Vector2i(c, 8)])
		w.append([Vector2i(c, 8), Vector2i(c, 7)])
	for c in range(11, 18):
		w.append([Vector2i(c, 7), Vector2i(c, 8)])
		w.append([Vector2i(c, 8), Vector2i(c, 7)])
	for r in range(2, 13):
		w.append([Vector2i(9, r), Vector2i(10, r)])
		w.append([Vector2i(10, r), Vector2i(9, r)])
	return w


func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _outline(rect: Rect2, c: Color, width: float) -> void:
	draw_rect(rect, c, false, width)


func _ln(x0, y0, x1, y1, c, w := 1.0) -> void:
	draw_line(Vector2(x0, y0), Vector2(x1, y1), c, w)


func _draw() -> void:
	if use_baked_bg:        # live path renders the baked Sprite2D; _draw() is the bake seed
		return
	_draw_walls()
	_draw_floor()
	_draw_badminton()
	_draw_netball()
	_draw_court(_LEFT)
	_draw_court(_RIGHT)
	_draw_hoops()
	_draw_entrance()
	# Bake = the room only (floor, walls, painted lines, wall-mounted hoops/doors). Every
	# floor-standing feature — benches, ball carts, the volleyball nets and the court-divider
	# curtain — is its own Fixture node (see _on_ready), so none of them are painted here.


func _draw_walls() -> void:
	_r(0, 0, _SW, _SH, _CLAD)
	for x in range(0, _SW, 9):
		_ln(x, 0, x, _SH, _CLAD_DK, 1)


func _draw_floor() -> void:
	draw_rect(_HALL, _FLOOR)
	var i := 0
	while i < int(_HALL.size.y):
		if (i / 14) % 3 == 0:
			_r(_HALL.position.x, _HALL.position.y + i, _HALL.size.x, 5, _FLOOR_SHEEN)
		i += 14


func _draw_badminton() -> void:
	for y in [54, 256]:
		for x in [44, 330]:
			var c := Rect2(x, y, 250, 142)
			_outline(c, _ORANGE, 1)
			var cx := c.position.x + c.size.x / 2
			for sx in [cx - 26, cx + 26]:
				_ln(sx, c.position.y, sx, c.position.y + c.size.y, _ORANGE)
			var cy := c.position.y + c.size.y / 2
			_ln(c.position.x, cy, c.position.x + c.size.x, cy, _ORANGE)
			for sy in [c.position.y + 12, c.position.y + c.size.y - 12]:
				_ln(c.position.x, sy, c.position.x + c.size.x, sy, _ORANGE)


func _draw_netball() -> void:
	var c := _NETB
	_outline(c, _YELLOW, 1)
	var third := c.size.x / 3
	for tx in [c.position.x + third, c.position.x + 2 * third]:
		_ln(tx, c.position.y, tx, c.position.y + c.size.y, _YELLOW)
	var cy := c.position.y + c.size.y / 2
	draw_arc(Vector2(c.position.x, cy), 84.0, -1.4, 1.4, 24, _YELLOW, 1)
	draw_arc(Vector2(c.position.x + c.size.x, cy), 84.0, 1.74, 4.54, 24, _YELLOW, 1)


func _draw_court(court: Rect2) -> void:
	_outline(court, _VB, 3)
	for ay in [_NET_Y - 2 * _TS, _NET_Y + 2 * _TS]:
		_ln(court.position.x, ay, court.position.x + court.size.x, ay, _VB, 2)


func _draw_hoops() -> void:
	var by := _HALL.position.y + _HALL.size.y / 2
	var bl := _HALL.position.x - 2
	_r(bl - 8, by - 16, 10, 32, _BACKBOARD)
	_outline(Rect2(bl - 8, by - 16, 10, 32), _BB_DK, 1)
	draw_arc(Vector2(bl + 8, by), 8, 0, TAU, 20, _HOOP_OR, 2)
	var br := _HALL.position.x + _HALL.size.x + 2
	_r(br - 2, by - 16, 10, 32, _BACKBOARD)
	_outline(Rect2(br - 2, by - 16, 10, 32), _BB_DK, 1)
	draw_arc(Vector2(br - 8, by), 8, 0, TAU, 20, _HOOP_OR, 2)


func _draw_entrance() -> void:
	var cx := _SW / 2
	var half := 2 * _TS
	var x0 := cx - half
	var x1 := cx + half
	var bot := _HALL.position.y + 2
	var top := 7
	_r(x0, top, x1 - x0, bot - top, _CORR)
	_r(x0, top, x1 - x0, 4, _CORR_DK)
	var lw := 12
	for lx in [x0 + 2, x1 - 2 - lw]:
		_r(lx, top, lw, bot - top, _DOOR_PLY)
		_outline(Rect2(lx, top, lw, bot - top), _DOOR_RV, 1)
		_r(lx + lw / 2 - 1, top + 3, 2, bot - top - 7, _GLASS_PN)
	for jx in [x0 - 1, x1 - 1]:
		_r(jx, top - 1, 2, bot - top + 1, _DOOR_RV)
	var sw := 14
	var sx := cx - sw / 2
	_r(sx, 1, sw, 5, _EXIT_GRN)
	_r(sx + sw - 4, 2, 2, 3, _EXIT_LT)
	_outline(Rect2(sx, 1, sw, 5), Color8(20, 80, 40), 1)
	var sdx := _HALL.position.x - 1
	var sdy := 10 * _TS + 2
	var sdh := 2 * _TS - 4
	_r(sdx, sdy, 4, sdh, _DOOR_PLY)
	_outline(Rect2(sdx, sdy, 4, sdh), _DOOR_RV, 1)


# Court-divider curtain (port of gym.py). Paints onto `c` (its own Fixture node).
func _draw_curtain(c: CanvasItem) -> void:
	var x := _CURT_X
	var y0 := 2 * _TS
	var y1 := 13 * _TS
	c.draw_rect(Rect2(x - 8, y0 + 2, 16, y1 - y0), _CURT_SH)
	c.draw_rect(Rect2(x - 5, y0, 10, y1 - y0), _CURT)
	c.draw_line(Vector2(x - 4, y0), Vector2(x - 4, y1), _CURT_DK)
	c.draw_line(Vector2(x - 1, y0), Vector2(x - 1, y1), _CURT_LT)
	c.draw_line(Vector2(x + 2, y0), Vector2(x + 2, y1), _CURT_DK)
	c.draw_rect(Rect2(x - 7, y0 - 3, 14, 4), _RAIL)


# One court's volleyball net (poles + mesh + antennae). Paints onto `c` (its own Fixture node).
func _draw_net(c: CanvasItem, court: Rect2) -> void:
	var ny := _NET_Y
	var left := court.position.x
	var right := court.position.x + court.size.x
	for px in [left - 2, right + 2]:
		c.draw_rect(Rect2(px - 2, ny - 22, 4, 44), _POLE)
	c.draw_rect(Rect2(left, ny - 6, court.size.x, 12), _NET_FILL)
	var x := left
	while x <= right:
		c.draw_line(Vector2(x, ny - 6), Vector2(x, ny + 6), _NET_MESH)
		x += 6
	c.draw_line(Vector2(left, ny - 6), Vector2(right, ny - 6), _NET_TAPE, 2)
	c.draw_line(Vector2(left, ny + 6), Vector2(right, ny + 6), _NET_TAPE, 2)
	for ax in [left, right]:
		c.draw_rect(Rect2(ax - 1, ny - 16, 3, 32), _ANT_W)
		c.draw_rect(Rect2(ax - 1, ny - 16, 3, 8), _ANT_R)
		c.draw_rect(Rect2(ax - 1, ny + 8, 3, 8), _ANT_R)


# Multi-tile wooden wall bench (port of entities/bench.py Bench.draw). Paints onto
# `c` (its own Fixture node) in absolute scene coords.
func _draw_bench(c: CanvasItem, col: int, row: int, height: int) -> void:
	var bx := col * _TS + 6
	var by := row * _TS + 2
	var bw := _TS - 12
	var bh := height * _TS - 4
	c.draw_rect(Rect2(bx, by, bw, bh), _BENCH_SEAT)
	c.draw_rect(Rect2(bx, by, bw, maxi(bh / 6, 3)), _BENCH_LITE)
	var sy := by + _TS
	while sy < by + bh:                   # slat seams once per tile down the run
		c.draw_line(Vector2(bx + 1, sy), Vector2(bx + bw - 2, sy), _BENCH_EDGE, 1)
		sy += _TS
	c.draw_rect(Rect2(bx, by, bw, bh), _BENCH_EDGE, false, 1)


# Single-tile ball cart (port of entities/ball_basket.py BallBasket.draw). Paints onto
# `c` (its own Fixture node) in absolute scene coords.
func _draw_basket(c: CanvasItem, col: int, row: int) -> void:
	var cx := col * _TS + 16
	var cy := row * _TS + 16
	var bw := 26
	var bh := 11
	var bx := cx - bw / 2
	var by := cy - 5
	var leg_bot := cy + 11
	c.draw_line(Vector2(bx + 4, by + bh), Vector2(bx + 2, leg_bot), _BK_STILT, 2)            # splayed legs
	c.draw_line(Vector2(bx + bw - 4, by + bh), Vector2(bx + bw - 2, leg_bot), _BK_STILT, 2)
	var brace_y := by + bh + (leg_bot - by - bh) / 2
	c.draw_line(Vector2(bx + 3, brace_y), Vector2(bx + bw - 3, brace_y), _BK_STILT_DK, 1)
	for wx in [bx + 2, bx + bw - 2]:                              # caster wheels
		c.draw_circle(Vector2(wx, leg_bot + 2), 2, _BK_WHEEL)
		c.draw_arc(Vector2(wx, leg_bot + 2), 2, 0, TAU, 12, _BK_OUTLINE, 1)
	var ball_y := by - 2
	for offset in [-7, 0, 7]:                                     # balls peeking over the rim
		var bpx := cx + int(offset)
		c.draw_circle(Vector2(bpx, ball_y), 4, _BK_BALL)
		c.draw_circle(Vector2(bpx, ball_y - 1), 1, _BK_BALL_HI)
		c.draw_arc(Vector2(bpx, ball_y), 4, 0, TAU, 16, _BK_OUTLINE, 1)
	c.draw_rect(Rect2(bx, by, bw, bh), _BK_BOX)                   # fabric box covers ball bottoms
	c.draw_rect(Rect2(bx, by, bw, bh), _BK_BOX_DK, false, 1)
	c.draw_line(Vector2(bx + 1, by + 1), Vector2(bx + bw - 2, by + 1), _BK_BOX_LT, 1)
