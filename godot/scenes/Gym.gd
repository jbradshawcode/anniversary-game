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

var _HALL := Rect2(24, 24, _SW - 48, _SH - 48)
var _LEFT := Rect2(2 * _TS, 3 * _TS, 7 * _TS, 10 * _TS)
var _RIGHT := Rect2(11 * _TS, 3 * _TS, 7 * _TS, 10 * _TS)
var _NET_Y := 8 * _TS
var _CURT_X := 10 * _TS
var _NETB := Rect2(54, 86, 532, 308)


func _init() -> void:
	walkable_cols = Vector2i(1, 18)
	walkable_rows = Vector2i(1, 13)
	exits = {"up": {"scene": 5, "cols": Vector2i(8, 11)}}
	entry_points = {"down": Vector2i(9, 1)}
	grid = TileGrid.new(
		walkable_cols, walkable_rows,
		Config.MAP_COLS, Config.MAP_ROWS,
		[], _build_walls())

	# Cool overhead light pools — a lit sports hall (gym.py `lighting`).
	ambient_color = Color(0.56, 0.59, 0.65)
	var pool := Color8(232, 240, 255)
	for y in [90, 250]:
		for x in [160, 320, 480]:
			lights.append({"pos": Vector2(x, y), "radius": 128.0, "color": pool, "energy": 0.85})


func _on_ready() -> void:
	var matus := Matus.new(8, 6)
	add_child(matus)
	npcs.append(matus)
	grid.set_blockers([Vector2i(matus.tile_x, matus.tile_y)])


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
	_draw_walls()
	_draw_floor()
	_draw_badminton()
	_draw_netball()
	_draw_court(_LEFT)
	_draw_court(_RIGHT)
	_draw_hoops()
	_draw_entrance()
	_draw_curtain()
	_draw_net(_LEFT)
	_draw_net(_RIGHT)


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


func _draw_curtain() -> void:
	var x := _CURT_X
	var y0 := 2 * _TS
	var y1 := 13 * _TS
	_r(x - 8, y0 + 2, 16, y1 - y0, _CURT_SH)
	_r(x - 5, y0, 10, y1 - y0, _CURT)
	_ln(x - 4, y0, x - 4, y1, _CURT_DK)
	_ln(x - 1, y0, x - 1, y1, _CURT_LT)
	_ln(x + 2, y0, x + 2, y1, _CURT_DK)
	_r(x - 7, y0 - 3, 14, 4, _RAIL)


func _draw_net(court: Rect2) -> void:
	var ny := _NET_Y
	var left := court.position.x
	var right := court.position.x + court.size.x
	for px in [left - 2, right + 2]:
		_r(px - 2, ny - 22, 4, 44, _POLE)
	_r(left, ny - 6, court.size.x, 12, _NET_FILL)
	var x := left
	while x <= right:
		_ln(x, ny - 6, x, ny + 6, _NET_MESH)
		x += 6
	_ln(left, ny - 6, right, ny - 6, _NET_TAPE, 2)
	_ln(left, ny + 6, right, ny + 6, _NET_TAPE, 2)
	for ax in [left, right]:
		_r(ax - 1, ny - 16, 3, 32, _ANT_W)
		_r(ax - 1, ny - 16, 3, 8, _ANT_R)
		_r(ax - 1, ny + 8, 3, 8, _ANT_R)
