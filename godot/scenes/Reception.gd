# Scene 6 — sports-centre reception lobby. Ported from scenes/reception.py.
# Wide, shallow room: corridor door (left), passage door (right), stairs up on
# the left, sofas + glass partition in the middle, reception desk with windows
# on the right. Replaces the old Promenade scroll-demo placeholder.
class_name Reception
extends GameScene

const _TS := 32

# scenes/palette.py
var _WALL := Color8(185, 162, 120)
var _FLOOR := Color8(146, 144, 140)
var _DOOR_FR := Color8(80, 75, 90)
# reception-local palette
var _DESK := Color8(105, 78, 48)
var _DESK_LT := Color8(128, 98, 62)
var _DESK_TOP := Color8(148, 118, 78)
var _GLASS := Color8(155, 175, 190)
var _GLASS_HI := Color8(180, 200, 215)
var _GLASS_FR := Color8(85, 100, 115)
var _SOFA := Color8(58, 62, 68)
var _SOFA_CUSH := Color8(72, 78, 88)
var _SOFA_ARM := Color8(48, 52, 58)
var _STAIR_DK := Color8(135, 130, 125)
var _STAIR_NOSE := Color8(175, 170, 165)
var _RAIL := Color8(85, 85, 90)
var _RAIL_LT := Color8(110, 110, 115)
var _MAT := Color8(65, 85, 55)
var _MONITOR := Color8(60, 60, 65)
var _SCREEN := Color8(80, 120, 180)
var _WIN_FRAME := Color8(178, 172, 162)


func _init() -> void:
	bg_texture = "res://assets/baked/reception_bg.png"   # native backdrop; _draw() is now the re-bake seed
	walkable_cols = Vector2i(1, 14)
	walkable_rows = Vector2i(5, 10)
	exits = {
		"left": {"scene": 5, "rows": Vector2i(6, 7)},
		"right": {"scene": 8, "rows": Vector2i(6, 7)},   # -> passage (not ported yet)
	}
	entry_points = {"right": Vector2i(2, 7), "left": Vector2i(14, 7)}

	var blocked: Array = []
	for c in range(1, 4):                     # stairs
		blocked.append(Vector2i(c, 9))
		blocked.append(Vector2i(c, 10))
	blocked.append(Vector2i(6, 9))            # sofa
	blocked.append(Vector2i(6, 10))
	for r in range(8, 11):                    # glass partition
		blocked.append(Vector2i(7, r))
	for c in range(10, 14):                   # desk
		blocked.append(Vector2i(c, 9))
		blocked.append(Vector2i(c, 10))

	grid = TileGrid.new(
		walkable_cols, walkable_rows,
		Config.MAP_COLS, Config.MAP_ROWS,
		blocked, [])

	# Bright lobby: near-neutral ambient with warm ceiling pools across the room
	# and cool daylight spilling in at the two glass doors and the desk windows.
	ambient_color = Color(0.62, 0.62, 0.66)
	var warm := Color8(255, 246, 220)
	for c in [4, 8, 12]:
		lights.append({"pos": Vector2(c * _TS + _TS / 2, 6 * _TS), "radius": 110.0, "color": warm, "energy": 0.85})
	var day := Color8(205, 222, 238)
	lights.append({"pos": Vector2(_TS / 2, 7 * _TS), "radius": 96.0, "color": day, "energy": 0.9})       # corridor door
	lights.append({"pos": Vector2(15 * _TS + _TS / 2, 7 * _TS), "radius": 96.0, "color": day, "energy": 0.9})  # passage door
	lights.append({"pos": Vector2(11 * _TS + _TS, 11 * _TS + _TS / 2), "radius": 80.0, "color": day, "energy": 0.75})  # desk windows


func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _outline(x, y, w, h, c, width := 1.0) -> void:
	draw_rect(Rect2(x, y, w, h), c, false, width)


func _ln(x0, y0, x1, y1, c, w := 1.0) -> void:
	draw_line(Vector2(x0, y0), Vector2(x1, y1), c, w)


func _draw() -> void:
	if use_baked_bg:        # live path renders the baked Sprite2D; _draw() is the bake seed
		return
	draw_rect(Rect2(0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), Color(0, 0, 0))  # black off-plan
	_draw_walls()
	_draw_floor()
	_draw_glass_door(0)            # corridor door (west)
	_draw_glass_door(15 * _TS)     # passage door (east)
	_draw_stairs()
	_draw_sofas()
	_draw_glass_partition()
	_draw_desk()
	_draw_windows()


func _draw_walls() -> void:
	for b in [[0, 16, 4, 5], [0, 16, 11, 12], [0, 1, 5, 11], [15, 16, 5, 11]]:
		_r(b[0] * _TS, b[2] * _TS, (b[1] - b[0]) * _TS, (b[3] - b[2]) * _TS, _WALL)


func _draw_floor() -> void:
	_r(1 * _TS, 5 * _TS, 14 * _TS, 6 * _TS, _FLOOR)
	_r(1 * _TS, 7 * _TS, 2 * _TS, _TS, _MAT)


func _draw_glass_door(dx: int) -> void:
	var dy := 6 * _TS + 2
	var dw := _TS
	var dh := 2 * _TS - 4
	_r(dx, dy - 2, dw, dh + 4, _DOOR_FR)
	_r(dx + 2, dy, dw - 4, dh, _GLASS)
	_r(dx + 2, dy, (dw - 4) / 2, dh / 2, _GLASS_HI)
	_outline(dx + 2, dy, dw - 4, dh, _GLASS_FR)
	_ln(dx + dw / 2, dy, dx + dw / 2, dy + dh, _GLASS_FR)


func _draw_stairs() -> void:
	var x0 := 1 * _TS
	var y0 := 9 * _TS
	var w := 3 * _TS
	var h := 2 * _TS
	var num_steps := 10
	var step_w := w / num_steps

	_r(x0 - 4, y0, 4, h, _WALL)

	for i in range(num_steps):
		var sx := x0 + (num_steps - 1 - i) * step_w
		var t := float(i) / float(maxi(1, num_steps - 1))
		var shade := int(155 * (1 - t * 0.25))
		var c := Color8(maxi(110, shade), maxi(105, shade - 5), maxi(100, shade - 10))
		_r(sx, y0, step_w, h, c)
		_outline(sx, y0, step_w, h, _STAIR_DK)
		_ln(sx, y0, sx, y0 + h, _STAIR_NOSE)

	for ry in [y0 + 2, y0 + h - 4]:
		_r(x0 - 6, ry, w + 8, 2, _RAIL)
		_r(x0 - 6, ry, w + 8, 1, _RAIL_LT)
		_r(x0 - 8, ry - 1, 3, 4, _RAIL)
		_r(x0 + w + 4, ry - 1, 3, 4, _RAIL)


func _draw_sofas() -> void:
	var sx := 6 * _TS
	var sy := 9 * _TS
	var sw := _TS
	var sh := 2 * _TS

	_r(sx + 1, sy + 1, sw - 2, sh - 2, _SOFA)

	var back_w := 7
	_r(sx + sw - back_w - 1, sy + 1, back_w, sh - 2, _SOFA_ARM)

	var arm_h := 6
	_r(sx + 1, sy + 1, sw - 2, arm_h, _SOFA_ARM)
	_r(sx + 1, sy + sh - arm_h - 1, sw - 2, arm_h, _SOFA_ARM)

	var cush_x := sx + 2
	var cush_w := sw - back_w - 4
	var cush_top := sy + arm_h + 2
	var cush_h := (sh - 2 * arm_h - 6) / 2
	for i in range(2):
		var cy := cush_top + i * (cush_h + 2)
		_r(cush_x, cy, cush_w, cush_h, _SOFA_CUSH)
		_outline(cush_x, cy, cush_w, cush_h, _SOFA)


func _draw_glass_partition() -> void:
	var gx := 7 * _TS
	var gy := 8 * _TS
	var gw := _TS
	var gh := 3 * _TS

	_r(gx, gy, gw, gh, _GLASS_FR)
	_r(gx + 2, gy + 2, gw - 4, gh - 4, _GLASS)
	_r(gx + 2, gy + 2, (gw - 4) / 2, (gh - 4) / 2, _GLASS_HI)

	for py in range(gy + _TS, gy + gh, _TS):
		_ln(gx + 2, py, gx + gw - 2, py, _GLASS_FR)
	_ln(gx + gw / 2, gy + 2, gx + gw / 2, gy + gh - 2, _GLASS_FR)

	_outline(gx, gy, gw, gh, _GLASS_FR)


func _draw_desk() -> void:
	var x0 := 10 * _TS
	var y0 := 9 * _TS
	var w := 4 * _TS
	var h := 2 * _TS

	_r(x0, y0, w, h, _DESK)
	_r(x0 + 2, y0 + 2, w - 4, h - 4, _DESK_LT)
	_r(x0 + 4, y0 + 4, w - 8, 6, _DESK_TOP)
	_outline(x0, y0, w, h, _DESK)

	_r(x0 + 8, y0 + 14, 14, 10, _MONITOR)
	_r(x0 + 9, y0 + 15, 12, 7, _SCREEN)
	_r(x0 + 13, y0 + 24, 6, 3, _MONITOR)

	_r(x0 + w - 22, y0 + 14, 14, 10, _MONITOR)
	_r(x0 + w - 21, y0 + 15, 12, 7, _SCREEN)
	_r(x0 + w - 19, y0 + 24, 6, 3, _MONITOR)


func _draw_windows() -> void:
	var wy := 11 * _TS
	var wh := _TS
	for col in [11, 12]:
		var wx: int = col * _TS + 4
		var ww := _TS - 8
		_r(wx - 2, wy, ww + 4, wh, _WIN_FRAME)
		_r(wx, wy + 2, ww, wh - 4, _GLASS)
		_r(wx, wy + 2, ww / 2, (wh - 4) / 2, _GLASS_HI)
		_outline(wx, wy + 2, ww, wh - 4, _GLASS_FR)
		_ln(wx + ww / 2, wy + 2, wx + ww / 2, wy + wh - 2, _GLASS_FR)
