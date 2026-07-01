# Scene 2 — King Street, Hammersmith. Ported from scenes/king_st.py at recognisable
# fidelity: a 180-tile scrolling street — named shopfronts + awnings along the north
# pavement, buildings to the south, the carriageway (rows 6-8) crossable only on the
# zebra crossings, evening lamplight. (Condensed from the original: per-shop style
# variants -> one generic shopfront; live traffic -> a few parked cars; the green-man
# timing -> crossings always passable.)
#
# Bake captures the street surface only: pavements, carriageway + lane markings, side
# roads, and the zebra crossings (surface markings). Every feature is its own node:
# the north shops and south buildings sit Z_BACK (the player walks the pavement in
# front of them, never behind), as do the parked cars (in the non-walkable road). The
# streetlamps are the lone Y->z occluders — the player walks the pavement behind their
# bases, so each lamp group sorts at its base row.
class_name KingSt
extends GameScene

const _TS := 32

var _ROAD := Color8(90, 92, 95)
var _ROAD_LINE := Color8(220, 220, 215)
var _CURB := Color8(155, 150, 142)
var _PAVE := Color8(188, 183, 175)
var _PAVE_EDGE := Color8(172, 167, 160)
var _GLASS := Color8(162, 182, 198)
var _GLASS_HI := Color8(192, 208, 218)
var _DOOR_WOOD := Color8(82, 58, 38)
var _SIDE_RD := Color8(100, 102, 105)
var _ZEBRA := Color8(236, 236, 230)
var _LAMP := Color8(255, 238, 182)
var _CAR_GLASS := Color8(150, 175, 190)

# col, width, wall, awning, label
var _SHOPS := [
	[0, 5, Color8(148, 145, 140), Color8(42, 68, 135), "POSK"],
	[5, 5, Color8(45, 45, 48), Color8(35, 55, 35), "SAFFRON"],
	[13, 4, Color8(235, 230, 225), Color8(180, 60, 65), "ASK"],
	[17, 3, Color8(225, 222, 218), Color8(30, 30, 32), "LILLY'S\nNAILS"],
	[20, 2, Color8(180, 200, 40), Color8(145, 168, 30), "THYME"],
	[22, 3, Color8(228, 225, 218), Color8(55, 50, 45), "MISTER CUT"],
	[28, 4, Color8(232, 228, 222), Color8(200, 30, 30), "KFH"],
	[32, 4, Color8(235, 235, 230), Color8(180, 180, 185), "PRIMA\nBRITANNIA"],
	[36, 3, Color8(80, 45, 70), Color8(60, 32, 52), "SHILPA"],
	[39, 3, Color8(195, 150, 155), Color8(180, 140, 120), "PATISSERIE\nSAINTE-ANNE"],
	[45, 4, Color8(232, 228, 222), Color8(70, 100, 160), "THE ITALIAN\nBREAK"],
	[49, 4, Color8(220, 215, 205), Color8(55, 55, 58), "BOHEMIA"],
	[53, 4, Color8(235, 232, 228), Color8(190, 25, 25), "W LOCAL"],
	[57, 4, Color8(195, 125, 110), Color8(180, 45, 35), "SANBAO\nKITCHEN"],
	[64, 3, Color8(220, 218, 212), Color8(75, 78, 72), "PORTICO"],
	[67, 3, Color8(48, 42, 45), Color8(35, 30, 38), "MOOBOO"],
	[70, 3, Color8(230, 228, 225), Color8(35, 35, 38), "CURTIS &\nPARKS"],
	[73, 3, Color8(225, 220, 212), Color8(90, 40, 70), "HORTON &\nGARTON"],
	[76, 2, Color8(230, 225, 218), Color8(190, 35, 30), "POST\nOFFICE"],
	[81, 3, Color8(235, 235, 232), Color8(30, 60, 120), "DEXTERS"],
	[84, 3, Color8(225, 222, 218), Color8(0, 95, 115), "CO-OP"],
	[87, 3, Color8(195, 180, 165), Color8(75, 110, 105), "CREDIT\nMUNCH"],
	[90, 3, Color8(220, 215, 210), Color8(68, 68, 72), "HAIR WORKS"],
	[93, 2, Color8(225, 222, 218), Color8(40, 40, 45), "MR ADAM'S"],
	[95, 5, Color8(155, 75, 55), Color8(85, 75, 130), "THE\nSALUTATION"],
	[100, 3, Color8(228, 224, 218), Color8(205, 70, 120), "BEAUTY BY\nHONEY"],
	[103, 2, Color8(235, 232, 225), Color8(210, 55, 50), "99P STORE"],
	[105, 3, Color8(235, 232, 225), Color8(40, 150, 70), "SIMPLY\nFRESH"],
	[108, 3, Color8(235, 235, 232), Color8(20, 50, 120), "DOMINO'S"],
	[111, 3, Color8(200, 178, 150), Color8(60, 110, 70), "PINOCCHIO'S"],
	[114, 3, Color8(60, 50, 48), Color8(190, 85, 40), "BRIM\nBURGERS"],
	[117, 2, Color8(58, 58, 66), Color8(120, 60, 150), "MSP VAPE"],
	[119, 2, Color8(235, 235, 225), Color8(35, 120, 55), "SUBWAY"],
	[121, 2, Color8(58, 58, 66), Color8(215, 30, 40), "TCG"],
	[123, 5, Color8(155, 80, 60), Color8(75, 95, 78), "PLOUGH &\nHARROW"],
	[128, 3, Color8(235, 235, 230), Color8(20, 120, 55), "PADDY\nPOWER"],
	[131, 3, Color8(40, 55, 95), Color8(210, 170, 40), "H&T"],
	[134, 3, Color8(235, 232, 225), Color8(230, 120, 30), "TAPI\nCARPETS"],
	[137, 3, Color8(235, 232, 225), Color8(40, 135, 150), "CRISIS"],
	[140, 3, Color8(55, 48, 48), Color8(35, 60, 45), "HEYTEA"],
	[143, 3, Color8(45, 38, 55), Color8(170, 30, 95), "CASINO"],
	[146, 3, Color8(235, 232, 228), Color8(110, 45, 130), "TACO BELL"],
	[149, 3, Color8(45, 42, 45), Color8(200, 30, 40), "GDK"],
	[152, 3, Color8(225, 222, 215), Color8(70, 105, 90), "HOME\nSTORE"],
	[155, 3, Color8(235, 232, 225), Color8(210, 40, 40), "MERKUR"],
	[158, 3, Color8(235, 228, 228), Color8(200, 150, 160), "SERAPHINE"],
	[161, 4, Color8(180, 185, 190), Color8(90, 95, 100), "LIVAT"],
	[165, 3, Color8(20, 80, 170), Color8(235, 200, 40), "IKEA"],
	[168, 3, Color8(235, 235, 232), Color8(210, 30, 40), "H&M"],
	[171, 3, Color8(60, 52, 48), Color8(210, 95, 40), "TORTILLA"],
	[174, 6, Color8(140, 95, 65), Color8(45, 65, 55), "WETHERSPOONS"],
]

# col, width, wall (south-side buildings)
var _BUILDINGS := [
	[0, 10, Color8(155, 75, 55)], [13, 5, Color8(160, 85, 60)], [18, 7, Color8(165, 80, 55)],
	[28, 7, Color8(165, 160, 152)], [35, 7, Color8(140, 130, 110)], [45, 5, Color8(160, 75, 55)],
	[50, 5, Color8(135, 115, 95)], [55, 6, Color8(168, 185, 202)], [64, 7, Color8(185, 180, 172)],
	[71, 7, Color8(158, 155, 150)], [81, 9, Color8(170, 168, 162)], [90, 10, Color8(160, 80, 55)],
	[100, 8, Color8(165, 80, 55)], [108, 7, Color8(172, 168, 160)], [115, 6, Color8(160, 85, 60)],
	[121, 7, Color8(170, 145, 110)], [128, 10, Color8(165, 80, 55)], [138, 9, Color8(172, 168, 160)],
	[147, 10, Color8(158, 155, 150)], [157, 11, Color8(175, 178, 182)], [168, 12, Color8(160, 82, 56)],
]

var _SIDE_ROADS := [[10, 3], [25, 3], [42, 3], [61, 3], [78, 3]]
var _CROSSINGS := [[10, 11], [25, 26], [42, 43], [61, 62], [78, 79], [96, 97], [129, 130], [157, 158]]
# North-pavement lamps (base at the curb, row 6) vs south-pavement lamps (row 11).
var _NORTH_LAMP_COLS := [4, 19, 35, 53, 71, 90, 106, 123, 142, 161, 176]
var _SOUTH_LAMP_COLS := [11, 27, 46, 64, 83, 100, 119, 135, 153, 171]
var _PARKED := [[8, 0], [33, 1], [55, 0], [88, 1], [115, 0], [145, 1], [167, 0]]

var _SIGN_COLORS := {
	"SAFFRON": Color8(50, 185, 65), "SHILPA": Color8(255, 215, 100),
	"SANBAO\nKITCHEN": Color8(255, 50, 40), "THE\nSALUTATION": Color8(255, 215, 100),
	"PRIMA\nBRITANNIA": Color8(55, 75, 135), "LILLY'S\nNAILS": Color8(240, 160, 60),
}
var _CAR_COLORS := [Color8(190, 60, 55), Color8(70, 90, 150), Color8(210, 200, 90),
	Color8(70, 120, 90), Color8(210, 215, 220), Color8(50, 52, 58)]
var _font: Font

# ── live traffic (port of king_st.py) ───────────────────────────────────────────
const _CAR_LEN := 52
const _CAR_W := 24
const _WALK_TIME := 6.0          # green-man window
const _WAIT_TIME := 7.0          # red-man (traffic flows)
const _CROSS_OFFSET := 3.1       # stagger neighbouring lights
# lane centre-y + travel direction: north lane westbound, south lane eastbound
var _LANES := [[6 * _TS + _TS - 2, -1], [8 * _TS + 2, 1]]
var _t := 0.0
var _cars: Array = []            # [{x, y, dir, lane, speed, color}]
var _spawn := [1.0, 2.4]         # per-lane spawn countdown
var _rng := RandomNumberGenerator.new()
var _car_fix: Fixture
var _sig_fix: Fixture


func _init() -> void:
	bg_texture = "res://assets/baked/kingst_bg.png"   # native backdrop; _draw() is now the re-bake seed
	world_cols = 180
	walkable_cols = Vector2i(0, 179)
	walkable_rows = Vector2i(4, 10)
	exits = {"up": {"scene": 3, "cols": Vector2i(95, 99), "target": Vector2i(2, 9)}}
	entry_points = {"down": Vector2i(4, 10)}
	grid = TileGrid.new(walkable_cols, walkable_rows, world_cols, Config.MAP_ROWS, [], [])

	# Golden-hour evening: warm ambient + a pool under each streetlamp.
	ambient_color = Color(0.74, 0.60, 0.46)
	for c in _NORTH_LAMP_COLS:
		lights.append({"pos": Vector2(c * _TS + 16, 6 * _TS), "radius": 78.0,
			"color": Color8(255, 214, 150), "energy": 1.0})
	for c in _SOUTH_LAMP_COLS:
		lights.append({"pos": Vector2(c * _TS + 16, 11 * _TS), "radius": 78.0,
			"color": Color8(255, 214, 150), "energy": 1.0})


# Draw target: the scene's own canvas while baking the street surface, or a Fixture
# node while it paints its feature. Every draw helper routes through this.
var _cv: CanvasItem


func _ready() -> void:
	_font = ThemeDB.fallback_font
	super._ready()


func _on_ready() -> void:
	# North shops + south buildings: the player walks the pavement in front of them and
	# never behind (their rows aren't walkable) -> Z_BACK. Parked cars sit in the
	# non-walkable carriageway, never walked behind -> Z_BACK. The streetlamps are the
	# walk-behind occluders: the player passes the pavement behind each base -> Y->z,
	# grouped by base row (all north bases at row 6, all south at row 11).
	add_fixture(Fixture.Z_BACK, _paint_shops)
	add_fixture(Fixture.Z_BACK, _paint_buildings)
	# Cars drive in the carriageway (never walked behind) -> Z_BACK, but they move, so
	# their fixture is redrawn each frame; the signal heads cycle red/green likewise.
	_car_fix = add_fixture(Fixture.Z_BACK, _paint_cars)
	_sig_fix = add_fixture(Fixture.Z_BACK, _paint_signals)
	add_fixture(6 * _TS, _paint_north_lamps)
	add_fixture(11 * _TS, _paint_south_lamps)
	_prime_traffic()


# Road rows (6-8): crossable only on a zebra crossing, and only on the green man
# (or to finish a crossing already begun); pavements are free.
func is_walkable(tx: int, ty: int) -> bool:
	if ty >= 6 and ty <= 8:
		var ci := _crossing_index(tx)
		if ci == -1:
			return false                              # no jaywalking
		if _walk_now(ci):
			return true
		# red man: only let a pedestrian already on the road step off it
		return player != null and player.tile_y >= 6 and player.tile_y <= 8
	return grid.is_walkable(tx, ty)


# ── traffic lights / crossings ──────────────────────────────────────────────────
func _crossing_index(tx: int) -> int:
	for i in range(_CROSSINGS.size()):
		if _CROSSINGS[i][0] <= tx and tx <= _CROSSINGS[i][1]:
			return i
	return -1


func _ped_on_crossing(i: int) -> bool:
	var c0: int = _CROSSINGS[i][0]
	var c1: int = _CROSSINGS[i][1]
	var peds: Array = []
	if player != null:
		peds.append(Vector2i(player.tile_x, player.tile_y))
	if party != null:
		for f in party.followers:
			peds.append(Vector2i(int(f.position.x / _TS), int(f.position.y / _TS)))
	for p in peds:
		if c0 <= p.x and p.x <= c1 and p.y >= 6 and p.y <= 8:
			return true
	return false


func _walk_now(i: int) -> bool:
	var period := _WALK_TIME + _WAIT_TIME
	var green: bool = fmod(_t + i * _CROSS_OFFSET, period) < _WALK_TIME
	return green or _ped_on_crossing(i)               # never go red while someone's on it


# ── cars ─────────────────────────────────────────────────────────────────────────
func _new_car(lane: int, x: float) -> Dictionary:
	return {"x": x, "y": float(_LANES[lane][0]), "dir": _LANES[lane][1], "lane": lane,
		"speed": _rng.randf_range(110.0, 170.0), "color": _CAR_COLORS[_rng.randi() % _CAR_COLORS.size()]}


func _spawn_car(lane: int) -> void:
	var d: int = _LANES[lane][1]
	var x: float = -_CAR_LEN if d > 0 else world_width() + _CAR_LEN
	_cars.append(_new_car(lane, x))


func _x_off_crossing(x: float) -> bool:
	for i in range(_CROSSINGS.size()):
		if _walk_now(i):
			var lo: float = _CROSSINGS[i][0] * _TS - _CAR_LEN
			var hi: float = (_CROSSINGS[i][1] + 1) * _TS + _CAR_LEN
			if lo <= x and x <= hi:
				return false
	return true


func _prime_traffic() -> void:
	_cars = []
	_spawn = [_rng.randf_range(1.8, 4.2), _rng.randf_range(1.8, 4.2)]
	for lane in range(_LANES.size()):
		var x := _rng.randf_range(0.0, 200.0)
		while x < world_width():
			if _x_off_crossing(x):
				_cars.append(_new_car(lane, x))
			x += _rng.randf_range(150.0, 280.0)


# Furthest a car may advance: the stop line of the next green crossing, or the back
# of the car ahead in its lane (whichever it reaches first).
func _car_stop_x(car: Dictionary) -> float:
	var d: int = car["dir"]
	var x: float = car["x"]
	var limit: float = d * 1e9
	for i in range(_CROSSINGS.size()):
		if not _walk_now(i):
			continue
		var line: float = (_CROSSINGS[i][0] * _TS - _CAR_LEN / 2.0 - 2) if d > 0 \
			else ((_CROSSINGS[i][1] + 1) * _TS + _CAR_LEN / 2.0 + 2)
		if (line - x) * d >= 0:
			limit = minf(limit, line) if d > 0 else maxf(limit, line)
	for o in _cars:
		if o == car or o["lane"] != car["lane"]:
			continue
		if (o["x"] - x) * d > 0:
			var gap: float = o["x"] - d * (_CAR_LEN + 6)
			limit = minf(limit, gap) if d > 0 else maxf(limit, gap)
	return limit


func _process(dt: float) -> void:
	_t += dt
	for lane in range(_LANES.size()):
		_spawn[lane] -= dt
		if _spawn[lane] <= 0.0:
			_spawn_car(lane)
			_spawn[lane] = _rng.randf_range(1.8, 4.2)
	for car in _cars:
		var nx: float = car["x"] + car["dir"] * car["speed"] * dt
		var stop := _car_stop_x(car)
		car["x"] = minf(nx, stop) if car["dir"] > 0 else maxf(nx, stop)
	var kept: Array = []
	for c in _cars:
		if c["x"] >= -_CAR_LEN * 2 and c["x"] <= world_width() + _CAR_LEN * 2:
			kept.append(c)
	_cars = kept
	if _car_fix != null:
		_car_fix.queue_redraw()
	if _sig_fix != null:
		_sig_fix.queue_redraw()


func _r(x, y, w, h, c) -> void:
	_cv.draw_rect(Rect2(x, y, w, h), c)


func _ln(x0, y0, x1, y1, c, w := 1.0) -> void:
	_cv.draw_line(Vector2(x0, y0), Vector2(x1, y1), c, w)


func _dk(c: Color, n := 0.12) -> Color:
	return c.darkened(n)


func _draw() -> void:
	if use_baked_bg:        # live path renders the baked Sprite2D; _draw() is the bake seed
		return
	_cv = self
	var ww := world_width()
	_r(0, 0, ww, Config.SCREEN_HEIGHT, _PAVE)
	# Road + lane markings.
	_r(0, 6 * _TS, ww, 3 * _TS, _ROAD)
	_ln(0, 6 * _TS, ww, 6 * _TS, _CURB, 2)
	_ln(0, 9 * _TS - 1, ww, 9 * _TS - 1, _CURB, 2)
	var cy := 7 * _TS + 16
	for x in range(0, int(ww), 40):
		_r(x, cy - 1, 20, 2, _ROAD_LINE)
	for sr in _SIDE_ROADS:
		_draw_side_road(sr[0], sr[1])
	for cr in _CROSSINGS:
		_draw_crossing(cr[0], cr[1])


func _paint_shops(c: CanvasItem) -> void:
	_cv = c
	for shop in _SHOPS:
		_draw_shop(shop)


func _paint_buildings(c: CanvasItem) -> void:
	_cv = c
	for b in _BUILDINGS:
		_draw_building(b)


func _paint_cars(c: CanvasItem) -> void:
	_cv = c
	for car in _cars:
		_render_car(car)


# Live signal heads on each crossing kerb — the lit lamp follows the green-man timing.
func _paint_signals(c: CanvasItem) -> void:
	_cv = c
	for i in range(_CROSSINGS.size()):
		var walk := _walk_now(i)
		var x0: int = _CROSSINGS[i][0] * _TS
		var red := Color8(80, 30, 28) if walk else Color8(225, 60, 45)
		var grn := Color8(70, 215, 95) if walk else Color8(28, 70, 40)
		for ky in [6 * _TS - 7, 9 * _TS + 6]:
			_r(x0 - 9, ky - 7, 7, 14, Color8(30, 30, 34))
			_cv.draw_circle(Vector2(x0 - 5, ky - 3), 2, red)
			_cv.draw_circle(Vector2(x0 - 5, ky + 3), 2, grn)


func _paint_north_lamps(c: CanvasItem) -> void:
	_cv = c
	for col in _NORTH_LAMP_COLS:
		_draw_lamp(col, 6 * _TS)


func _paint_south_lamps(c: CanvasItem) -> void:
	_cv = c
	for col in _SOUTH_LAMP_COLS:
		_draw_lamp(col, 11 * _TS)


func _draw_side_road(col: int, w: int) -> void:
	var x := col * _TS
	var pw := w * _TS
	_r(x, 0, pw, 6 * _TS, _SIDE_RD)
	_r(x, 9 * _TS, pw, 6 * _TS, _SIDE_RD)


func _draw_shop(shop: Array) -> void:
	var x: int = shop[0] * _TS
	var pw: int = shop[1] * _TS
	var h := 4 * _TS
	var wall: Color = shop[2]
	var awning: Color = shop[3]
	var label: String = shop[4]
	_r(x, 0, pw, h, wall)
	# Window strip + a door.
	_r(x + 4, 2 * _TS + 12, pw - 8, h - (2 * _TS + 14), _GLASS)
	_r(x + 5, 2 * _TS + 12, (pw - 8) / 2, 8, _GLASS_HI)
	_cv.draw_rect(Rect2(x + 4, 2 * _TS + 12, pw - 8, h - (2 * _TS + 14)), _dk(wall, 0.2), false, 1.0)
	_r(x + pw / 2 - 9, h - 22, 18, 22, _DOOR_WOOD)
	# Awning.
	var ay := 2 * _TS - 12
	_r(x + 2, ay, pw - 4, 20, awning)
	_r(x + 2, ay + 18, pw - 4, 3, _dk(awning, 0.12))
	_cv.draw_rect(Rect2(x, 0, pw, h), _dk(wall, 0.08), false, 1.0)
	# Sign text on the awning.
	var sc: Color = _SIGN_COLORS.get(label, Color8(35, 32, 28) if _brightness(awning) >= 0.5 else Color8(252, 252, 245))
	var lines := label.split("\n")
	var ty := ay + 8 - (lines.size() - 1) * 5
	for ln in lines:
		_cv.draw_string(_font, Vector2(x + 2, ty), ln, HORIZONTAL_ALIGNMENT_CENTER, pw - 4, 9, sc)
		ty += 10


func _brightness(c: Color) -> float:
	return (c.r + c.g + c.b) / 3.0


func _draw_building(b: Array) -> void:
	var x: int = b[0] * _TS
	var pw: int = b[1] * _TS
	var y := 11 * _TS
	var h := 4 * _TS
	var wall: Color = b[2]
	_r(x, y, pw, h, wall)
	for i in range(0, b[1], 2):                 # window pairs
		var wx := x + i * _TS + 6
		_r(wx, y + 8, _TS * 2 - 12, 20, _GLASS)
		_r(wx, y + 8, (_TS * 2 - 12) / 2, 10, _GLASS_HI)
	_cv.draw_rect(Rect2(x, y, pw, h), _dk(wall, 0.08), false, 1.0)


func _draw_crossing(c0: int, c1: int) -> void:
	# Zebra stripes only — a baked surface marking. The signal heads are a live
	# fixture (_paint_signals) so they can cycle red/green.
	var x0 := c0 * _TS
	var x1 := (c1 + 1) * _TS
	for bx in range(x0 + 3, x1 - 3, 10):
		_r(bx, 6 * _TS + 2, 6, 3 * _TS - 4, _ZEBRA)


func _render_car(car: Dictionary) -> void:
	var cx: float = car["x"]
	var cy: float = car["y"]
	var col: Color = car["color"]
	var d: int = car["dir"]
	var hl := _CAR_LEN / 2.0
	var hw := _CAR_W / 2.0
	_r(cx - hl, cy - hw, _CAR_LEN, _CAR_W, _dk(col, 0.30))             # shadow base
	_r(cx - hl + 1, cy - hw + 2, _CAR_LEN - 2, _CAR_W - 4, col)       # body
	_cv.draw_rect(Rect2(cx - hl + 1, cy - hw + 2, _CAR_LEN - 2, _CAR_W - 4), _dk(col, 0.18), false, 1.0)
	_r(cx - _CAR_LEN / 6.0, cy - hw + 4, _CAR_LEN / 3.0, _CAR_W - 8, _CAR_GLASS)   # windscreen band
	var fx := cx + d * (hl - 3)                                       # headlights lead the way
	_r(fx - 1, cy - hw + 2, 2, 3, Color8(255, 240, 190))
	_r(fx - 1, cy + hw - 5, 2, 3, Color8(255, 240, 190))


func _draw_lamp(col: int, base_y: int) -> void:
	var x := col * _TS + 16
	var h := 42
	_r(x - 2, base_y - h, 4, h, Color8(48, 50, 58))
	_r(x - 6, base_y - h - 4, 12, 5, Color8(48, 50, 58))
	_r(x - 4, base_y - h - 3, 8, 4, _LAMP)
