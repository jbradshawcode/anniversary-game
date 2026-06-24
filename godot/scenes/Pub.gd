# Scene 3 — The Salutation pub interior (154 King Street). Ported from
# scenes/salutation.py at recognisable fidelity: a wide scrolling room with the
# L-peninsula bar + back-bar gantry across the top, tartan banquettes + long
# tables + chair rows along the bottom wall flanking the teal fireplace, a slate
# conservatory wing to the east, and stained-glass street doors west.
# Banquettes stay WALKABLE (the crew sit ON them); bar/tables/fireplaces are solid.
class_name Pub
extends GameScene

const _TS := 32

var _PINE := Color8(172, 140, 92)
var _PINE_ALT := Color8(162, 130, 82)
var _PINE_SEAM := Color8(146, 116, 70)
var _SLATE := Color8(96, 102, 108)
var _GROUT := Color8(74, 80, 86)
var _SAGE := Color8(58, 90, 94)
var _SAGE_DK := Color8(42, 70, 74)
var _CREAM := Color8(238, 230, 214)
var _CREAM_DK := Color8(226, 217, 200)
var _FLAG := Color8(150, 145, 132)
var _FLAG_DK := Color8(126, 121, 110)
var _BAR_WOOD := Color8(74, 50, 30)
var _BAR_DK := Color8(50, 33, 18)
var _BAR_TOP := Color8(104, 76, 48)
var _BRASS := Color8(206, 184, 122)
var _BRASS_DK := Color8(168, 148, 92)
var _MIRROR := Color8(180, 194, 202)
var _FRIDGE := Color8(150, 170, 182)
var _BACKBAR := Color8(52, 84, 92)
var _BACKBAR_DK := Color8(38, 64, 70)
var _FIRE := Color8(46, 70, 60)
var _FIRE_DK := Color8(32, 52, 44)
var _FIRE_CR := Color8(224, 214, 196)
var _IRON := Color8(45, 45, 48)
var _TABLE := Color8(174, 138, 90)
var _TABLE_DK := Color8(144, 110, 66)
var _CHAIR := Color8(120, 90, 56)
var _SEATPAD := Color8(196, 200, 196)
var _TARTAN := Color8(140, 58, 56)
var _TARTAN_DK := Color8(108, 42, 42)
var _TARTAN_LN := Color8(196, 120, 90)
var _MUST := Color8(196, 156, 74)
var _MUST_DK := Color8(162, 124, 52)
var _CHECK := Color8(118, 150, 140)
var _CHECK_DK := Color8(88, 116, 106)
var _DOOR_DK := Color8(40, 28, 18)
var _DOOR_WOOD := Color8(74, 50, 30)
var _GLASS := Color8(168, 188, 200)
var _GLASS_HI := Color8(196, 212, 220)
var _STAIN_R := Color8(180, 45, 55)
var _STAIN_G := Color8(55, 135, 85)
var _STAIN_B := Color8(65, 95, 160)
var _BOTTLE := [Color8(40, 92, 60), Color8(162, 110, 48), Color8(188, 202, 212), Color8(150, 60, 60), Color8(70, 100, 150)]

var _BAR_PTS := PackedVector2Array([
	Vector2(10 * 32, 32), Vector2(21 * 32, 32), Vector2(21 * 32, 3 * 32),
	Vector2(20 * 32, 4 * 32), Vector2(12 * 32, 4 * 32), Vector2(10 * 32, 3 * 32)])


func _init() -> void:
	world_cols = 34
	walkable_cols = Vector2i(1, 32)
	walkable_rows = Vector2i(1, 11)
	exits = {                                                  # west to King St, east to the garden
		"left": {"scene": 2, "target": Vector2i(97, 5)},
		"right": {"scene": 4, "target": Vector2i(2, 7)},
	}
	entry_points = {"right": Vector2i(2, 9), "left": Vector2i(32, 5)}
	grid = TileGrid.new(walkable_cols, walkable_rows, world_cols, Config.MAP_ROWS, _blocked(), [])

	# Warm pub interior: dim amber ambient with a pool under each pendant.
	ambient_color = Color(0.50, 0.46, 0.42)
	var glow := Color8(255, 214, 150)
	for p in [[4, 8], [8, 9], [12, 9], [16, 9], [20, 9], [16, 2]]:
		lights.append({"pos": Vector2(p[0] * _TS + 16, p[1] * _TS + 16), "radius": 92.0, "color": glow, "energy": 1.0})
	lights.append({"pos": Vector2(27 * _TS, 5 * _TS), "radius": 88.0, "color": glow, "energy": 0.9})


func _blocked() -> Array:
	var b: Array = []
	for c in range(34):                                 # top + bottom walls
		b.append(Vector2i(c, 0))
		b.append(Vector2i(c, 12))
	for r in range(1, 12):                              # west wall (front-door gap rows 8-10)
		if r < 8 or r > 10:
			b.append(Vector2i(0, r))
	for c in range(23, 33):                             # conservatory walls above/below
		for r in [1, 2, 10, 11]:
			b.append(Vector2i(c, r))
	for r in range(1, 12):                              # east wall (garden-door gap rows 3-5)
		if r < 3 or r > 5:
			b.append(Vector2i(33, r))
	for r in [1, 2]:                                    # the L-bar footprint
		for c in range(10, 21):
			b.append(Vector2i(c, r))
	for c in range(11, 20):
		b.append(Vector2i(c, 3))
	for t in [[4, 11], [5, 11], [14, 11], [15, 11], [16, 6]]:  # fireplaces + column
		b.append(Vector2i(t[0], t[1]))
	for c in [10, 11, 12, 13, 16, 17, 18, 19, 20]:     # bottom-wall long tables (row 10)
		b.append(Vector2i(c, 10))
	for t in [[2, 2], [2, 4], [2, 6], [4, 3], [6, 3], [8, 3], [5, 5], [7, 5], [6, 8]]:
		b.append(Vector2i(t[0], t[1]))                 # front-room tables
	for c in range(24, 31):                            # conservatory long table (row 4)
		b.append(Vector2i(c, 4))
	for t in [[26, 7], [29, 7]]:
		b.append(Vector2i(t[0], t[1]))
	return b


func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _ln(x0, y0, x1, y1, c, w := 1.0) -> void:
	draw_line(Vector2(x0, y0), Vector2(x1, y1), c, w)


func _draw() -> void:
	draw_rect(Rect2(0, 0, world_width(), Config.SCREEN_HEIGHT), Color(0, 0, 0))
	_draw_floor()
	_draw_walls()
	_draw_bar()
	_draw_fireplaces()
	_draw_seating()
	_draw_doors()


func _draw_floor() -> void:
	_r(_TS, _TS, 22 * _TS, 11 * _TS, _PINE)             # stripped-pine main room
	var i := 0
	var x := _TS
	while x < 23 * _TS:
		if i % 2:
			_r(x, _TS, 11, 11 * _TS, _PINE_ALT)
		_ln(x, _TS, x, 12 * _TS, _PINE_SEAM)
		x += 11
		i += 1
	_r(10 * _TS, 4 * _TS, 11 * _TS, _TS, _FLAG)         # flagstone apron along the bar
	for fx in range(10 * _TS, 21 * _TS, 26):
		_r(fx + 1, 4 * _TS + 1, 24, _TS - 2, _FLAG_DK)
	_r(23 * _TS, 3 * _TS, 10 * _TS, 7 * _TS, _SLATE)    # slate conservatory
	for gy in range(3 * _TS, 10 * _TS, 13):
		_ln(23 * _TS, gy, 33 * _TS, gy, _GROUT)


func _draw_walls() -> void:
	# Two-band wall (cream rail over sage dado) along top/bottom + the side walls.
	_r(_TS, 0, 22 * _TS, 12, _CREAM_DK)
	_r(_TS, 12, 22 * _TS, _TS - 12, _SAGE)
	_r(_TS, 12 * _TS, 22 * _TS, Config.SCREEN_HEIGHT - 12 * _TS, _SAGE)
	_r(_TS, 12 * _TS, 22 * _TS, 10, _CREAM_DK)
	_r(0, _TS, _TS, 11 * _TS, _SAGE)
	_r(0, _TS, _TS, 14, _CREAM)
	_r(23 * _TS, 0, 10 * _TS, 3 * _TS, _SAGE)
	_r(23 * _TS, 0, 10 * _TS, 12, _CREAM_DK)
	_r(23 * _TS, 10 * _TS, 10 * _TS, Config.SCREEN_HEIGHT - 10 * _TS, _SAGE)
	_r(33 * _TS, 3 * _TS, _TS, 7 * _TS, _SAGE)
	for r in [2, 4, 6]:                                 # leaded bay windows, west wall
		_r(4, r * _TS + 4, _TS - 6, _TS - 8, _GLASS)
		_r(4, r * _TS + 4, (_TS - 6) / 2, (_TS - 8) / 2, _GLASS_HI)


func _draw_bar() -> void:
	draw_colored_polygon(_BAR_PTS, _BAR_WOOD)
	draw_polyline(_BAR_PTS + PackedVector2Array([_BAR_PTS[0]]), _BAR_DK, 2.0)
	_ln(12 * _TS, 4 * _TS - 6, 19 * _TS, 4 * _TS - 6, _BRASS, 2)   # foot rail
	var gx := 10 * _TS
	var gw := 11 * _TS
	_r(gx, _TS, gw, 2 * _TS, _BACKBAR)                  # back-bar gantry panel
	_r(gx, _TS, gw, 5, _BAR_DK)
	for sy in [_TS + 7, _TS + 16]:                      # two bottle shelves
		_r(gx + 4, sy, gw - 8, 2, _BAR_TOP)
		var bi := 0
		for bx in range(gx + 6, gx + gw - 6, 6):
			_r(bx, sy - 6, 3, 6, _BOTTLE[bi % 5])
			bi += 1
	_r(gx + gw / 2 - 25, _TS + 25, 50, 10, _MIRROR)     # central mirror
	for fx in [gx + 8, gx + gw - 48]:                   # glass-front fridges
		_r(fx, _TS + 38, 40, 22, _FRIDGE)
	_r(gx + gw / 2 - 24, _TS + 9, 48, 7, _BAR_DK)       # SALUTATION sign
	for lx in range(gx + gw / 2 - 20, gx + gw / 2 + 20, 5):
		_r(lx, _TS + 11, 2, 3, _BRASS)
	for i in range(7):                                  # cask pump taps along the servery
		var hx := (12 + i) * _TS + 16
		if hx > 19 * _TS:
			break
		_r(hx - 2, 3 * _TS + 2, 4, 12, _BRASS_DK)
		_r(hx - 2, 3 * _TS + 5, 4, 5, [_STAIN_R, _STAIN_G, _STAIN_B, _BRASS][i % 4])


func _draw_fireplaces() -> void:
	_r(4 * _TS, 11 * _TS, 2 * _TS, _TS, _FIRE_CR)       # cream cast-iron f/p
	_r(4 * _TS + 23, 11 * _TS + 10, 18, _TS - 12, _IRON)
	var tx := 14 * _TS
	_r(tx, 11 * _TS, 2 * _TS, _TS, _FIRE_DK)            # teal "Salutation" f/p
	_r(tx + 2, 11 * _TS + 2, 2 * _TS - 4, _TS - 4, _FIRE)
	_r(tx + 7, 11 * _TS + 6, 2 * _TS - 14, 9, _MIRROR)  # over-mantel mirror
	draw_rect(Rect2(tx + 6, 11 * _TS + 5, 2 * _TS - 12, 11), _BRASS, false, 2.0)


func _banq_run(c0: int, c1: int, row: int, top_back: bool, col: Color, dk: Color) -> void:
	var x := c0 * _TS
	var w := (c1 - c0 + 1) * _TS
	var y := row * _TS
	if top_back:
		_r(x, y, w, 9, dk)
		_r(x + 2, y + 10, w - 4, _TS - 14, col)
	else:
		_r(x, y + _TS - 9, w, 9, dk)
		_r(x + 2, y + 4, w - 4, _TS - 14, col)
	for lx in range(x + 4, x + w, 7):
		_ln(lx, y + 5, lx, y + _TS - 6, _TARTAN_LN if col == _TARTAN else dk)


func _long_table(c0: int, c1: int, row: int) -> void:
	var x := c0 * _TS
	var y := row * _TS + 6
	var w := (c1 - c0 + 1) * _TS
	var h := _TS - 12
	_r(x + 2, y, w - 4, h, _TABLE)
	_r(x + 3, y + 1, w - 6, 3, Color8(196, 160, 112))
	draw_rect(Rect2(x + 2, y, w - 4, h), _TABLE_DK, false, 1.0)
	for gx in range(x + _TS, x + w, _TS):
		_ln(gx, y, gx, y + h, _TABLE_DK)


func _chair_at(col: int, row: int, facing_down: bool) -> void:
	var cx := col * _TS + 16
	var cy := row * _TS + 16
	_r(cx - 6, cy - 6, 12, 12, _CHAIR)
	_r(cx - 4, cy - 4, 8, 8, _SEATPAD)
	var by := cy - 7 if facing_down else cy + 4
	_r(cx - 6, by, 12, 3, _BAR_DK)


func _wood_table(col: int, row: int) -> void:
	var cx := col * _TS + 16
	var cy := row * _TS + 16
	_r(cx - 13, cy - 9, 26, 18, _TABLE)
	draw_rect(Rect2(cx - 13, cy - 9, 26, 18), _TABLE_DK, false, 1.0)
	_r(cx - 2, cy - 1, 4, 5, Color8(226, 222, 214))    # the ubiquitous flower vase


func _draw_seating() -> void:
	_banq_run(10, 13, 11, false, _TARTAN, _TARTAN_DK)
	_banq_run(16, 20, 11, false, _TARTAN, _TARTAN_DK)
	_long_table(10, 13, 10)
	_long_table(16, 20, 10)
	for c in [10, 11, 12, 13, 16, 17, 18, 19]:
		_chair_at(c, 9, true)
	_banq_run(1, 1, 7, true, _CHECK, _CHECK_DK)         # front-window bench (short stub)
	for t in [[2, 2], [2, 4], [2, 6], [4, 3], [6, 3], [8, 3], [5, 5], [7, 5], [6, 8]]:
		_wood_table(t[0], t[1])
	# conservatory: mustard banquette + long table + diners
	_banq_run(24, 30, 3, true, _MUST, _MUST_DK)
	_long_table(24, 30, 4)
	for c in range(24, 31):
		_chair_at(c, 5, false)
	_wood_table(26, 7)
	_wood_table(29, 7)
	# panelled structural column mid-room
	_r(16 * _TS + 8, 6 * _TS + 5, 16, 22, _BAR_WOOD)
	_r(16 * _TS + 12, 6 * _TS + 8, 8, 16, _BAR_DK)


func _draw_doors() -> void:
	# Street doors (west, stained glass) over the front-door gap.
	var dy := 8 * _TS
	var dh := 3 * _TS
	_r(0, dy, _TS, dh, _DOOR_DK)
	for ddy in [dy + 4, dy + dh / 2 + 2]:
		_r(3, ddy, _TS - 8, dh / 2 - 8, _STAIN_B)
		_r(3, ddy + (dh / 2 - 8) / 2, _TS - 8, (dh / 2 - 8) / 2, _STAIN_R)
	# Garden doors (east, glazed) over the garden-door gap.
	var gx := 33 * _TS
	var gdy := 3 * _TS
	var gdh := 3 * _TS
	_r(gx, gdy, _TS, gdh, _DOOR_DK)
	for i in range(3):
		_r(gx + 2, gdy + 1 + i * (gdh / 3), _TS - 4, gdh / 3 - 2, _GLASS)
