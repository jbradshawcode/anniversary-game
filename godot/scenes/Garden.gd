# Scene 4 — The Salutation beer garden (scrolling). Ported from scenes/garden.py
# at recognisable fidelity: york paving, a brick perimeter with the pub's glazed
# doors west + dense planting at the deep east end, three pillared U-bench booths
# along each of the top/bottom walls, a central communal table with loose folding
# chairs, hanging baskets, and warm festoon lighting. Booth benches are walkable
# (step on to sit); planters/tables/pillars are solid.
class_name Garden
extends GameScene

const _TS := 32
var _BOOTHS := [5, 9, 13]
var _PILLARS := [4, 8, 12, 16]

var _YORK := Color8(178, 172, 162)
var _YORK_ALT := Color8(168, 162, 152)
var _YORK_DK := Color8(155, 148, 138)
var _BRICK := Color8(155, 85, 65)
var _BRICK_ALT := Color8(142, 78, 58)
var _MORTAR := Color8(185, 178, 168)
var _IVY := Color8(58, 108, 52)
var _IVY_DK := Color8(42, 85, 38)
var _IVY_LT := Color8(72, 128, 65)
var _OAK := Color8(128, 98, 62)
var _OAK_DK := Color8(105, 78, 48)
var _OAK_LT := Color8(148, 118, 78)
var _TEAL := Color8(58, 108, 118)
var _GLASS := Color8(162, 182, 198)
var _GLASS_HI := Color8(192, 208, 218)
var _DOOR_DK := Color8(52, 35, 18)
var _BRASS := Color8(200, 180, 120)
var _FOLD := Color8(200, 193, 172)
var _FOLD_DK := Color8(166, 158, 138)
var _BASKET := Color8(125, 95, 65)
var _FLOWER := [Color8(210, 65, 75), Color8(195, 85, 165), Color8(245, 242, 235)]


func _init() -> void:
	world_cols = 20
	walkable_cols = Vector2i(1, 18)
	walkable_rows = Vector2i(1, 13)
	exits = {"left": {"scene": 3}}                  # back into the pub conservatory
	entry_points = {"right": Vector2i(2, 7)}
	grid = TileGrid.new(walkable_cols, walkable_rows, world_cols, Config.MAP_ROWS, _blocked(), [])

	ambient_color = Color(0.58, 0.52, 0.45)         # dusk; the festoon bulbs warm it back
	for c in [3, 6, 9, 12, 15]:
		for ry in [6, 9]:
			lights.append({"pos": Vector2(c * _TS + 16, ry * _TS), "radius": 56.0,
				"color": Color8(255, 236, 170), "energy": 0.85})


func _blocked() -> Array:
	var b: Array = []
	for c in [17, 18]:
		for r in range(1, 14):
			b.append(Vector2i(c, r))
	for pc in _PILLARS:
		for r in range(1, 5):
			b.append(Vector2i(pc, r))
		for r in range(10, 14):
			b.append(Vector2i(pc, r))
	for i in _BOOTHS:
		for t in [[i, 1], [i + 1, 1], [i + 2, 1], [i + 1, 3], [i + 1, 4],
				[i, 13], [i + 1, 13], [i + 2, 13], [i + 1, 10], [i + 1, 11]]:
			b.append(Vector2i(t[0], t[1]))
	for c in [8, 9, 10, 11]:
		for r in [6, 7, 8]:
			b.append(Vector2i(c, r))
	b.append(Vector2i(2, 4))
	b.append(Vector2i(2, 11))
	return b


func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _brick(x, y, w, h) -> void:
	_r(x, y, w, h, _BRICK)
	var by := int(y)
	while by < y + h:
		draw_line(Vector2(x, by), Vector2(x + w, by), _MORTAR, 1.0)
		by += 8


func _draw() -> void:
	# Paving.
	_r(_TS, _TS, 16 * _TS, 13 * _TS, _YORK)
	var tsz := 28
	for tx in range(_TS, 17 * _TS, tsz):
		for ty in range(_TS, 14 * _TS, tsz):
			if ((tx - _TS) / tsz + (ty - _TS) / tsz) % 2:
				_r(tx, ty, tsz, tsz, _YORK_ALT)
	# Perimeter brick + pub doors + deep planting.
	_brick(0, 0, 20 * _TS, _TS)
	_brick(0, 14 * _TS, 20 * _TS, _TS)
	_brick(0, _TS, _TS, 13 * _TS)
	_brick(19 * _TS, _TS, _TS, 13 * _TS)
	_r(0, 6 * _TS, _TS, 3 * _TS, _DOOR_DK)
	for i in range(3):
		_r(4, 6 * _TS + 3 + i * _TS, _TS - 8, _TS - 8, _GLASS)
		_r(4, 6 * _TS + 3 + i * _TS, (_TS - 8) / 2, (_TS - 8) / 2, _GLASS_HI)
	_r(_TS - 7, 7 * _TS + 13, 4, 6, _BRASS)
	for c in [17, 18]:                              # dense deep-end planting
		_r(c * _TS, _TS, _TS, 13 * _TS, _IVY_DK)
		for r in range(1, 14):
			draw_circle(Vector2(c * _TS + 16, r * _TS + 16), 5, _IVY_LT)
	# Booths (top + bottom) with dividing pillars.
	for pc in _PILLARS:
		_r(pc * _TS + 4, _TS, _TS - 8, 4 * _TS, _BRICK_ALT)
		_r(pc * _TS + 4, 10 * _TS, _TS - 8, 4 * _TS, _BRICK_ALT)
	for i in _BOOTHS:
		_booth(i, true)
		_booth(i, false)
	# Communal table + loose seating + baskets.
	_r(8 * _TS + 4, 6 * _TS + 3, 4 * _TS - 8, 3 * _TS - 6, _OAK_LT)
	draw_rect(Rect2(8 * _TS + 4, 6 * _TS + 3, 4 * _TS - 8, 3 * _TS - 6), _OAK_DK, false, 1.0)
	_r(8 * _TS + 6, 5 * _TS + 23, 4 * _TS - 12, 8, _TEAL)
	_r(8 * _TS + 6, 9 * _TS + 2, 4 * _TS - 12, 8, _TEAL)
	for spot in [[2, 4], [2, 11]]:
		_wood_table(spot[0], spot[1])
	for ch in [[7, 6], [7, 8], [12, 6], [12, 8], [3, 7]]:
		_fold_chair(ch[0] * _TS + 16, ch[1] * _TS + 16)
	for pc in [4, 12]:
		for hy in [5 * _TS, 9 * _TS + 4]:
			_basket(pc * _TS + 16, hy)


func _booth(i: int, top: bool) -> void:
	if top:
		_r(i * _TS, _TS, 3 * _TS, _TS, _IVY_DK)            # planter behind
		_r(i * _TS, 2 * _TS + 6, 3 * _TS, _TS - 10, _BRICK)  # back bench
		_r(i * _TS + _TS - 11, 2 * _TS + 6, 3 * _TS - (_TS - 11) - (_TS - 11), _TS - 12, _BRICK)
		_r((i + 1) * _TS + 4, 3 * _TS + 2, _TS - 8, 2 * _TS - 4, _OAK_LT)  # table
		_r(i * _TS + 6, 3 * _TS, _TS - 10, 2 * _TS, _BRICK)               # side benches
		_r((i + 2) * _TS + 6, 3 * _TS, _TS - 10, 2 * _TS, _BRICK)
	else:
		_r(i * _TS, 14 * _TS - _TS, 3 * _TS, _TS, _IVY_DK)
		_r(i * _TS, 12 * _TS + 6, 3 * _TS, _TS - 10, _BRICK)
		_r((i + 1) * _TS + 4, 10 * _TS + 2, _TS - 8, 2 * _TS - 4, _OAK_LT)
		_r(i * _TS + 6, 10 * _TS, _TS - 10, 2 * _TS, _BRICK)
		_r((i + 2) * _TS + 6, 10 * _TS, _TS - 10, 2 * _TS, _BRICK)


func _wood_table(col: int, row: int) -> void:
	var cx := col * _TS + 16
	var cy := row * _TS + 16
	_r(cx - 11, cy - 9, 22, 18, _OAK_LT)
	draw_rect(Rect2(cx - 11, cy - 9, 22, 18), _OAK_DK, false, 1.0)


func _fold_chair(cx: int, cy: int) -> void:
	_r(cx - 5, cy - 5, 10, 10, _FOLD)
	draw_rect(Rect2(cx - 5, cy - 5, 10, 10), _FOLD_DK, false, 1.0)


func _basket(x: int, hy: int) -> void:
	draw_line(Vector2(x, hy), Vector2(x, hy + 8), Color8(38, 36, 32), 2.0)
	draw_colored_polygon(PackedVector2Array([
		Vector2(x - 7, hy + 6), Vector2(x + 7, hy + 6),
		Vector2(x + 5, hy + 14), Vector2(x - 5, hy + 14)]), _BASKET)
	for fi in range(3):
		draw_circle(Vector2(x - 4 + fi * 4, hy + 12), 2, _FLOWER[fi])
