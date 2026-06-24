# Scene 6 — camera-demo placeholder: a wide street the camera scrolls across.
# Stands in for the real wide scenes (King St = 180 cols, the pub = 34) whose
# faithful art is a content port; this proves the scrolling MECHANIC with a
# 40-col (1280px) map and a few landmarks so the scroll is obvious.
class_name Promenade
extends GameScene

const _TS := 32
const _ROWS := 15

var _SKY := Color8(150, 170, 190)
var _PAVE := Color8(168, 166, 160)
var _PAVE_LN := Color8(150, 148, 143)
var _CURB := Color8(120, 122, 128)
var _ROAD := Color8(66, 68, 74)
var _ROAD_LN := Color8(196, 190, 120)
var _POLE := Color8(88, 90, 96)
var _POLE_DK := Color8(70, 72, 78)
var _LAMP := Color8(250, 240, 180)
var _BENCH := Color8(140, 98, 60)
var _BENCH_DK := Color8(112, 78, 46)


func _init() -> void:
	world_cols = 40
	walkable_cols = Vector2i(0, 39)
	walkable_rows = Vector2i(4, 10)
	exits = {"left": {"scene": 5}, "right": {"scene": 3}}   # left to corridor, right to the pub
	entry_points = {"right": Vector2i(1, 7), "left": Vector2i(38, 7)}
	grid = TileGrid.new(
		walkable_cols, walkable_rows,
		world_cols, Config.MAP_ROWS,
		[], [])

	# Dusk: cool-blue ambient with a warm pool of light under each lamp post.
	ambient_color = Color(0.42, 0.46, 0.60)
	var lamp := Color8(255, 216, 150)
	for c in range(3, world_cols, 6):
		lights.append({"pos": Vector2(c * _TS + _TS / 2, 5 * _TS), "radius": 96.0, "color": lamp, "energy": 1.15})


func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _draw() -> void:
	var ww := world_width()
	_r(0, 0, ww, _ROWS * _TS, _SKY)
	_r(0, 3 * _TS, ww, 8 * _TS, _PAVE)               # pavement band (rows 3-10)
	for c in range(0, world_cols + 1):               # paving slab lines
		_r(c * _TS, 3 * _TS, 1, 8 * _TS, _PAVE_LN)
	_r(0, 11 * _TS - 3, ww, 3, _CURB)                # curb
	_r(0, 11 * _TS, ww, 4 * _TS, _ROAD)              # road
	var x := _TS
	while x < ww:                                    # centre line dashes
		_r(x, 13 * _TS, 18, 4, _ROAD_LN)
		x += 48

	for c in range(3, world_cols, 6):                # lamp posts along the pavement
		var px := c * _TS + _TS / 2
		_r(px - 2, 4 * _TS, 4, 6 * _TS, _POLE)
		_r(px - 2, 4 * _TS, 1, 6 * _TS, _POLE_DK)
		_r(px - 7, 4 * _TS - 6, 14, 7, _LAMP)        # lantern head

	for c in range(6, world_cols, 11):               # the odd bench
		var bx := c * _TS
		_r(bx, 9 * _TS, 3 * _TS, 5, _BENCH)
		_r(bx, 9 * _TS + 5, 3 * _TS, 3, _BENCH_DK)
		_r(bx + 2, 9 * _TS + 8, 4, 10, _BENCH_DK)
		_r(bx + 3 * _TS - 6, 9 * _TS + 8, 4, 10, _BENCH_DK)
