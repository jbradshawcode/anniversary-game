# Scene 8 — underground passage. Ported from scenes/passage.py.
# Narrow outdoor alley alongside the sports centre (enter left, from reception) ->
# stairs down -> a tunnel running east -> stairs up and right (exit to the courts).
# The walkable box (1..18, 5..12) is carved by static_blocked into a backwards-L:
# tunnel along rows 5-7, alley + down-stairs in cols 1-3.
class_name Passage
extends GameScene

const _TS := 32

# scenes/palette.py
var _DOOR := Color8(120, 82, 48)
var _DOOR_DK := Color8(90, 60, 32)
var _DOOR_FR := Color8(80, 75, 90)
# passage-local palette
var _BRICK := Color8(155, 68, 48)
var _BRICK_DK := Color8(130, 52, 35)
var _BRICK_GR := Color8(118, 112, 105)
var _BRICK_GDK := Color8(98, 92, 85)
var _CONCRETE := Color8(165, 160, 155)
var _TUNNEL_W := Color8(92, 90, 88)
var _TUNNEL_WLT := Color8(105, 102, 98)
var _TUNNEL_FL := Color8(108, 105, 100)
var _PIPE := Color8(95, 100, 108)
var _PIPE_DK := Color8(78, 82, 90)
var _STAIR := Color8(155, 150, 145)
var _STAIR_DK := Color8(135, 130, 125)
var _STAIR_NOSE := Color8(175, 170, 165)
var _RAIL := Color8(85, 85, 90)
var _RAIL_LT := Color8(110, 110, 115)
var _LIGHT := Color8(235, 225, 195)
var _LIGHT_FR := Color8(85, 85, 90)
var _GLASS := Color8(155, 175, 190)
var _GLASS_HI := Color8(180, 200, 215)
var _DRAIN := Color8(70, 68, 65)
var _DRAIN_DK := Color8(55, 53, 50)
var _SKY := Color8(165, 185, 210)
var _WALL_CAP := Color8(178, 172, 162)


func _init() -> void:
	bg_texture = "res://assets/baked/passage_bg.png"   # native backdrop; _draw() is now the re-bake seed
	walkable_cols = Vector2i(1, 18)
	walkable_rows = Vector2i(5, 12)
	exits = {
		"left": {"scene": 6, "rows": Vector2i(11, 11)},                              # -> reception
		"right": {"scene": 9, "target": Vector2i(3, 3), "rows": Vector2i(5, 7)},      # -> courts
	}
	entry_points = {"right": Vector2i(1, 11), "left": Vector2i(17, 6)}

	var blocked: Array = []
	for r in range(8, 13):
		for c in range(4, 19):
			blocked.append(Vector2i(c, r))

	grid = TileGrid.new(
		walkable_cols, walkable_rows,
		Config.MAP_COLS, Config.MAP_ROWS,
		blocked, [])

	# Subterranean mood: dark, cool ambient lit by warm strip-lights down the tunnel
	# ceiling, with cool daylight spilling in at the alley mouth (left) and the
	# ascending exit stairs (right). Real PointLight2Ds replace the pygame glow blits.
	ambient_color = Color(0.40, 0.40, 0.47)
	var warm := Color8(255, 244, 210)
	for c in [4, 8, 12, 16]:
		lights.append({"pos": Vector2(c * _TS, 6 * _TS + 4), "radius": 76.0, "color": warm, "energy": 1.05})
	var day := Color8(200, 218, 236)
	lights.append({"pos": Vector2(2 * _TS, 10 * _TS), "radius": 104.0, "color": day, "energy": 1.0})   # alley mouth
	lights.append({"pos": Vector2(18 * _TS, 6 * _TS), "radius": 92.0, "color": day, "energy": 0.9})    # exit stairs


func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _outline(x, y, w, h, c, width := 1.0) -> void:
	draw_rect(Rect2(x, y, w, h), c, false, width)


func _ln(x0, y0, x1, y1, c, w := 1.0) -> void:
	draw_line(Vector2(x0, y0), Vector2(x1, y1), c, w)


func _shade(base: Color, factor: float) -> Color:
	return Color8(int(base.r8 * factor), int(base.g8 * factor), int(base.b8 * factor))


func _draw() -> void:
	if use_baked_bg:        # live path renders the baked Sprite2D; _draw() is the bake seed
		return
	draw_rect(Rect2(0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), Color(0, 0, 0))  # black off-plan
	_draw_walls()
	_draw_tunnel()
	_draw_tunnel_pipes()
	_draw_tunnel_lights()
	_draw_alley()
	_draw_stairs_down()
	_draw_stairs_right()
	_draw_reception_door()


# Flat brick fill with offset courses + mortar lines (pygame's _brick_rect).
func _brick_rect(x: int, y: int, w: int, h: int, color: Color, dark: Color) -> void:
	_r(x, y, w, h, color)
	var offset := 0
	for gy in range(y, y + h, 4):
		for gx in range(x + offset, x + w, 8):
			_ln(gx, gy, gx, gy + 4, dark, 1)
		offset = 4 - offset
		_ln(x, gy, x + w, gy, dark, 1)


func _draw_walls() -> void:
	_brick_rect(0, 5 * _TS - 6, 1 * _TS, 3 * _TS + 6 + 6, _BRICK, _BRICK_DK)
	_brick_rect(4 * _TS, 5 * _TS - 6, 16 * _TS, 3 * _TS + 12, _BRICK_GR, _BRICK_GDK)
	_brick_rect(0, 8 * _TS, 1 * _TS, 5 * _TS, _BRICK, _BRICK_DK)
	_brick_rect(4 * _TS, 8 * _TS, 16 * _TS, 5 * _TS, _BRICK, _BRICK_DK)
	_brick_rect(0, 13 * _TS, 4 * _TS, 2 * _TS, _BRICK, _BRICK_DK)


func _draw_tunnel() -> void:
	var x0 := 1 * _TS
	var y0 := 5 * _TS
	var w := 16 * _TS
	var h := 3 * _TS

	_r(x0, y0 - 6, w, 6, _TUNNEL_W)
	_ln(x0, y0 - 3, x0 + w, y0 - 3, _TUNNEL_WLT, 1)
	_ln(x0, y0 - 6, x0 + w, y0 - 6, _BRICK_GDK, 1)

	_r(x0, y0, w, h, _TUNNEL_FL)

	_r(x0, y0 + h, w, 6, _TUNNEL_W)
	_ln(x0, y0 + h + 2, x0 + w, y0 + h + 2, _TUNNEL_WLT, 1)


func _draw_tunnel_pipes() -> void:
	var x0 := 1 * _TS
	var y0 := 5 * _TS - 5
	var w := 16 * _TS
	_ln(x0, y0, x0 + w, y0, _PIPE, 3)
	_ln(x0, y0 + 2, x0 + w, y0 + 2, _PIPE_DK, 1)

	var y1 := y0 - 6
	_ln(x0, y1, x0 + w, y1, _PIPE_DK, 2)
	_ln(x0, y1 + 1, x0 + w, y1 + 1, _PIPE, 1)

	for bx in range(x0 + 3 * _TS, x0 + w, 5 * _TS):
		_r(bx, y1 - 2, 6, 10, _PIPE_DK)


func _draw_tunnel_lights() -> void:
	var y0 := 5 * _TS - 4
	for lx in range(4 * _TS, 17 * _TS, 4 * _TS):
		_r(lx - 10, y0 - 2, 20, 4, _LIGHT_FR)
		_r(lx - 8, y0 - 1, 16, 3, _LIGHT)


func _draw_alley() -> void:
	var x0 := 1 * _TS
	var y0 := 10 * _TS
	var w := 3 * _TS
	var h := 3 * _TS
	_r(x0, y0, w, h, _CONCRETE)

	_r(2 * _TS + 8, 11 * _TS + 8, 14, 14, _DRAIN)
	_r(2 * _TS + 9, 11 * _TS + 9, 12, 12, _DRAIN_DK)
	for dy in range(0, 12, 3):
		_ln(2 * _TS + 10, 11 * _TS + 10 + dy, 2 * _TS + 20, 11 * _TS + 10 + dy, _DRAIN, 1)

	_r(4 * _TS - 4, y0, 4, h, _WALL_CAP)

	_r(x0, y0 - _TS, w, _TS, _SKY)
	_ln(x0, y0 - 1, x0 + w, y0 - 1, _WALL_CAP, 2)


func _draw_stairs_down() -> void:
	var x0 := 1 * _TS
	var w := 3 * _TS
	var num_steps := 8
	var stair_top := 8 * _TS
	var total_h := 2 * _TS
	var step_h := total_h / num_steps

	for i in range(num_steps):
		var sy := stair_top + i * step_h
		var t := float(i) / float(maxi(1, num_steps - 1))
		_r(x0, sy, w, step_h, _shade(_STAIR, 1.0 - t * 0.35))
		_outline(x0, sy, w, step_h, _STAIR_DK)
		_ln(x0, sy, x0 + w, sy, _shade(_STAIR_NOSE, 1.0 - t * 0.3), 2)

	for rx in [x0 + 2, x0 + w - 4]:
		_r(rx, stair_top - 2, 2, total_h + 4, _RAIL)
		_r(rx, stair_top - 2, 1, total_h + 4, _RAIL_LT)
		_r(rx - 1, stair_top - 4, 4, 3, _RAIL)
		_r(rx - 1, stair_top + total_h + 1, 4, 3, _RAIL)


func _draw_stairs_right() -> void:
	var x0 := 17 * _TS
	var y0 := 5 * _TS
	var total_w := 2 * _TS
	var h := 3 * _TS
	var num_steps := 8
	var step_w := total_w / num_steps

	for i in range(num_steps):
		var sx := x0 + i * step_w
		var t := float(i) / float(maxi(1, num_steps - 1))
		_r(sx, y0, step_w, h, _shade(_STAIR, 1.0 - (1.0 - t) * 0.35))
		_outline(sx, y0, step_w, h, _STAIR_DK)
		_ln(sx, y0, sx, y0 + h, _shade(_STAIR_NOSE, 1.0 - (1.0 - t) * 0.3), 2)

	for ry in [y0 + 2, y0 + h - 4]:
		_r(x0 - 2, ry, total_w + 4, 2, _RAIL)
		_r(x0 - 2, ry, total_w + 4, 1, _RAIL_LT)
		_r(x0 - 4, ry - 1, 3, 4, _RAIL)
		_r(x0 + total_w + 1, ry - 1, 3, 4, _RAIL)


func _draw_reception_door() -> void:
	var dx := 1 * _TS - 4
	var dy := 11 * _TS + 2
	var dw := 6
	var dh := _TS - 4
	_r(dx - 2, dy - 2, dw + 4, dh + 4, _DOOR_FR)
	_r(dx, dy, dw, dh, _DOOR)
	_outline(dx, dy, dw, dh, _DOOR_DK)
	_r(dx + 1, dy + 3, dw - 2, dh - 6, _GLASS)
	_r(dx + 1, dy + 3, (dw - 2) / 2, (dh - 6) / 2, _GLASS_HI)
