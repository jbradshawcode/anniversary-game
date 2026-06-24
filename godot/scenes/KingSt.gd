# Scene 2 — King Street, Hammersmith. Ported from scenes/king_st.py at recognisable
# fidelity: a 180-tile scrolling street — named shopfronts + awnings along the north
# pavement, buildings to the south, the carriageway (rows 6-8) crossable only on the
# zebra crossings, evening lamplight. (Condensed from the original: per-shop style
# variants -> one generic shopfront; live traffic -> a few parked cars; the green-man
# timing -> crossings always passable.)
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
var _LAMP_COLS := [4, 19, 35, 53, 71, 90, 106, 123, 142, 161, 176, 11, 27, 46, 64, 83, 100, 119, 135, 153, 171]
var _PARKED := [[8, 0], [33, 1], [55, 0], [88, 1], [115, 0], [145, 1], [167, 0]]

var _SIGN_COLORS := {
	"SAFFRON": Color8(50, 185, 65), "SHILPA": Color8(255, 215, 100),
	"SANBAO\nKITCHEN": Color8(255, 50, 40), "THE\nSALUTATION": Color8(255, 215, 100),
	"PRIMA\nBRITANNIA": Color8(55, 75, 135), "LILLY'S\nNAILS": Color8(240, 160, 60),
}
var _CAR_COLORS := [Color8(190, 60, 55), Color8(70, 90, 150), Color8(210, 200, 90),
	Color8(70, 120, 90), Color8(210, 215, 220), Color8(50, 52, 58)]
var _font: Font


func _init() -> void:
	world_cols = 180
	walkable_cols = Vector2i(0, 179)
	walkable_rows = Vector2i(4, 10)
	exits = {"up": {"scene": 3, "cols": Vector2i(95, 99), "target": Vector2i(2, 9)}}
	entry_points = {"down": Vector2i(4, 10)}
	grid = TileGrid.new(walkable_cols, walkable_rows, world_cols, Config.MAP_ROWS, [], [])

	# Golden-hour evening: warm ambient + a pool under each streetlamp.
	ambient_color = Color(0.74, 0.60, 0.46)
	for c in _LAMP_COLS:
		var by := 6 * _TS if c in [4, 19, 35, 53, 71, 90, 106, 123, 142, 161, 176] else 11 * _TS
		lights.append({"pos": Vector2(c * _TS + 16, by), "radius": 78.0,
			"color": Color8(255, 214, 150), "energy": 1.0})


func _ready() -> void:
	_font = ThemeDB.fallback_font
	super._ready()


# Road rows (6-8) are crossable only on a zebra crossing; pavements free.
func is_walkable(tx: int, ty: int) -> bool:
	if ty >= 6 and ty <= 8:
		for cr in _CROSSINGS:
			if cr[0] <= tx and tx <= cr[1]:
				return grid.is_walkable(tx, ty)
		return false
	return grid.is_walkable(tx, ty)


func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _ln(x0, y0, x1, y1, c, w := 1.0) -> void:
	draw_line(Vector2(x0, y0), Vector2(x1, y1), c, w)


func _dk(c: Color, n := 0.12) -> Color:
	return c.darkened(n)


func _draw() -> void:
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
	for shop in _SHOPS:
		_draw_shop(shop)
	for b in _BUILDINGS:
		_draw_building(b)
	for cr in _CROSSINGS:
		_draw_crossing(cr[0], cr[1])
	for car in _PARKED:
		_draw_car(car[0], car[1])
	for c in _LAMP_COLS:
		var by := 6 * _TS if c in [4, 19, 35, 53, 71, 90, 106, 123, 142, 161, 176] else 11 * _TS
		_draw_lamp(c, by)


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
	draw_rect(Rect2(x + 4, 2 * _TS + 12, pw - 8, h - (2 * _TS + 14)), _dk(wall, 0.2), false, 1.0)
	_r(x + pw / 2 - 9, h - 22, 18, 22, _DOOR_WOOD)
	# Awning.
	var ay := 2 * _TS - 12
	_r(x + 2, ay, pw - 4, 20, awning)
	_r(x + 2, ay + 18, pw - 4, 3, _dk(awning, 0.12))
	draw_rect(Rect2(x, 0, pw, h), _dk(wall, 0.08), false, 1.0)
	# Sign text on the awning.
	var sc: Color = _SIGN_COLORS.get(label, Color8(35, 32, 28) if _brightness(awning) >= 0.5 else Color8(252, 252, 245))
	var lines := label.split("\n")
	var ty := ay + 8 - (lines.size() - 1) * 5
	for ln in lines:
		draw_string(_font, Vector2(x + 2, ty), ln, HORIZONTAL_ALIGNMENT_CENTER, pw - 4, 9, sc)
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
	draw_rect(Rect2(x, y, pw, h), _dk(wall, 0.08), false, 1.0)


func _draw_crossing(c0: int, c1: int) -> void:
	var x0 := c0 * _TS
	var x1 := (c1 + 1) * _TS
	for bx in range(x0 + 3, x1 - 3, 10):        # zebra stripes
		_r(bx, 6 * _TS + 2, 6, 3 * _TS - 4, _ZEBRA)
	for ky in [6 * _TS - 7, 9 * _TS + 6]:       # signal heads
		_r(x0 - 9, ky - 7, 7, 14, Color8(30, 30, 34))
		draw_circle(Vector2(x0 - 5, ky - 3), 2, Color8(225, 60, 45))
		draw_circle(Vector2(x0 - 5, ky + 3), 2, Color8(70, 215, 95))


func _draw_car(col: int, lane: int) -> void:
	var cx := col * _TS + 16
	var cy := 6 * _TS + _TS - 2 if lane == 0 else 8 * _TS + 2
	var c: Color = _CAR_COLORS[(col + lane) % _CAR_COLORS.size()]
	_r(cx - 26, cy - 12, 52, 24, _dk(c, 0.12))
	_r(cx - 24, cy - 8, 48, 16, c)
	_r(cx - 8, cy - 8, 16, 16, _CAR_GLASS)


func _draw_lamp(col: int, base_y: int) -> void:
	var x := col * _TS + 16
	var h := 42
	_r(x - 2, base_y - h, 4, h, Color8(48, 50, 58))
	_r(x - 6, base_y - h - 4, 12, 5, Color8(48, 50, 58))
	_r(x - 4, base_y - h - 3, 8, 4, _LAMP)
