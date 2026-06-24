# Scene 5 — sports-centre corridor (L-shaped). Ported from scenes/corridor.py.
# Connects the gym (down) to reception (right, not ported yet). Walkable bounds
# minus static_blocked carve the L; pool windows + doors + fountain are the art.
class_name Corridor
extends GameScene

const _TS := 32
const _SW := 640
const _SH := 480

# scenes/palette.py
var _WALL := Color8(185, 162, 120)
var _WALL_DK := Color8(162, 140, 102)
var _FLOOR := Color8(146, 144, 140)
# corridor-local palette
var _DOOR := Color8(175, 135, 82)
var _DOOR_DK := Color8(148, 112, 65)
var _DOOR_FR := Color8(135, 102, 58)
var _GLASS := Color8(155, 175, 190)
var _GLASS_HI := Color8(180, 200, 215)
var _CEIL_LIGHT := Color8(242, 232, 205)
var _POOL := Color8(70, 145, 190)
var _POOL_DK := Color8(55, 128, 172)
var _LANE_RED := Color8(200, 65, 55)
var _LANE_YEL := Color8(220, 195, 55)
var _LANE_WHT := Color8(230, 230, 225)
var _SILL := Color8(178, 172, 162)
var _CHROME := Color8(192, 195, 200)
var _CHROME_DK := Color8(158, 162, 168)

var _FLOOR_ZONES := [[1, 19, 4, 7], [1, 5, 7, 12], [8, 12, 7, 14]]
var _BUILDING := [[0, 20, 0, 12], [7, 13, 12, 15]]


func _init() -> void:
	walkable_cols = Vector2i(1, 18)
	walkable_rows = Vector2i(4, 13)
	exits = {
		"down": {"scene": 1, "cols": Vector2i(8, 11)},
		"right": {"scene": 6, "rows": Vector2i(4, 6)},
	}
	entry_points = {"up": Vector2i(10, 13), "left": Vector2i(18, 5)}

	var blocked: Array = []
	for r in range(7, 12):
		for c in range(5, 8):
			blocked.append(Vector2i(c, r))
		for c in range(12, 19):
			blocked.append(Vector2i(c, r))
	for r in range(12, 14):
		for c in range(1, 8):
			blocked.append(Vector2i(c, r))
		for c in range(12, 19):
			blocked.append(Vector2i(c, r))

	grid = TileGrid.new(
		walkable_cols, walkable_rows,
		Config.MAP_COLS, Config.MAP_ROWS,
		blocked, [])

	# Dim interior with warm pools under the ceiling strip-lights (drawn at row 5);
	# the side passages stay darker for depth.
	ambient_color = Color(0.52, 0.52, 0.58)
	var warm := Color8(255, 245, 215)
	for c in [3, 7, 11, 15]:
		lights.append({"pos": Vector2(c * 32 + 16, 176), "radius": 92.0, "color": warm, "energy": 0.95})
	lights.append({"pos": Vector2(80, 304), "radius": 80.0, "color": warm, "energy": 0.8})  # west spur


func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _outline(x, y, w, h, c, width := 1.0) -> void:
	draw_rect(Rect2(x, y, w, h), c, false, width)


func _ln(x0, y0, x1, y1, c, w := 1.0) -> void:
	draw_line(Vector2(x0, y0), Vector2(x1, y1), c, w)


func _draw() -> void:
	draw_rect(Rect2(0, 0, _SW, _SH), Color(0, 0, 0))  # black under off-plan areas
	_draw_walls()
	_draw_pool_windows()
	_draw_floor()
	_draw_ceiling_lights()
	_draw_doors()
	_draw_water_fountain()


func _draw_walls() -> void:
	for b in _BUILDING:
		_r(b[0] * _TS, b[2] * _TS, (b[1] - b[0]) * _TS, (b[3] - b[2]) * _TS, _WALL)


func _draw_floor() -> void:
	for z in _FLOOR_ZONES:
		_r(z[0] * _TS, z[2] * _TS, (z[1] - z[0]) * _TS, (z[3] - z[2]) * _TS, _FLOOR)


func _draw_ceiling_lights() -> void:
	for c in range(3, 18, 4):
		var x := c * _TS + _TS / 2
		var y := 5 * _TS + _TS / 2
		_r(x - 12, y - 2, 24, 4, _CEIL_LIGHT)
		_outline(x - 12, y - 2, 24, 4, _WALL_DK)
	for r in range(8, 11):
		var x := 2 * _TS + _TS / 2
		var y := r * _TS + _TS / 2
		_r(x - 2, y - 8, 4, 16, _CEIL_LIGHT)
		_outline(x - 2, y - 8, 4, 16, _WALL_DK)


func _draw_doors() -> void:
	for c in [6, 13, 16]:
		var x: int = c * _TS + 4
		var y := 7 * _TS - 2
		var w := _TS - 8
		_r(x - 2, y - 2, w + 4, 6, _DOOR_FR)
		_r(x, y, w, 4, _DOOR)
		_outline(x, y, w, 4, _DOOR_DK)
	for c in [9, 10]:
		var x: int = c * _TS
		var y := 14 * _TS - 6
		_r(x, y, _TS, 6, _DOOR_FR)
		_r(x + 4, y + 1, _TS - 8, 4, _GLASS)
		_outline(x + 4, y + 1, _TS - 8, 4, _DOOR_DK)

	var dx := 5 * _TS - 2
	var dy := 10 * _TS + 2
	var dh := 2 * _TS - 4
	_r(dx - 2, dy - 2, 6, dh + 4, _DOOR_FR)
	for i in range(2):
		var py := dy + i * (dh / 2)
		var ph := dh / 2
		_r(dx, py, 4, ph, _DOOR)
		_outline(dx, py, 4, ph, _DOOR_DK)
		_r(dx + 1, py + 4, 2, ph - 8, _GLASS)
	_ln(dx, dy + dh / 2, dx + 4, dy + dh / 2, _DOOR_FR)


func _draw_water_fountain() -> void:
	var fx := 5 * _TS - 10
	var fy := 9 * _TS
	var fw := 14
	var fh := _TS - 2
	_r(fx, fy, fw, fh, _CHROME_DK)
	_r(fx + 1, fy + 1, fw - 2, fh - 2, _CHROME)
	_r(fx + 2, fy + 2, fw - 4, 8, _CHROME_DK)
	_r(fx + 3, fy + 3, fw - 6, 6, Color8(85, 145, 190))
	_r(fx + 5, fy + 4, 4, 2, Color8(65, 125, 170))
	_ln(fx, fy + 11, fx + fw, fy + 11, _CHROME_DK)
	_r(fx + 2, fy + 14, fw - 4, 12, _CHROME_DK)
	_r(fx + 3, fy + 15, fw - 6, 10, _CHROME)
	_r(fx + 4, fy + 17, fw - 8, 6, Color8(110, 165, 200))
	_outline(fx + 4, fy + 17, fw - 8, 6, _CHROME_DK)
	_outline(fx, fy, fw, fh, _CHROME_DK)


func _draw_pool_windows() -> void:
	var sections := [[1 * _TS, 6 * _TS], [8 * _TS, 5 * _TS], [14 * _TS, 5 * _TS]]
	var wy := 1 * _TS
	var wh := 3 * _TS
	for s in sections:
		var wx: int = s[0]
		var ww: int = s[1]
		var pad := 3
		var gx := wx + pad
		var gy := wy + pad
		var gw := ww - pad * 2
		var gh := wh - pad * 2

		_r(wx, wy, ww, wh, _SILL)
		_r(gx, gy, gw, gh, _POOL)
		for ry in range(gy + 6, gy + gh, 8):
			_ln(gx, ry, gx + gw, ry, _POOL_DK)

		var num_lanes := clampi(gw / 30, 3, 8)
		var lane_w := gw / num_lanes
		for i in range(1, num_lanes):
			var lx := gx + i * lane_w
			for dy in range(0, gh, 5):
				var seg := (dy / 5) % 4
				var c := _LANE_WHT
				if seg < 2:
					c = _LANE_RED
				elif seg == 2:
					c = _LANE_YEL
				_r(lx - 1, gy + dy, 3, 3, c)

		_r(gx, gy, gw, 6, _GLASS_HI)
		var num_panes := maxi(2, gw / 48)
		var pane_w := gw / num_panes
		for i in range(1, num_panes):
			var mx := gx + i * pane_w
			_ln(mx, gy, mx, gy + gh, _SILL, 2)
		_ln(gx, gy + gh / 2, gx + gw, gy + gh / 2, _SILL, 2)
		_outline(gx, gy, gw, gh, _WALL_DK)
