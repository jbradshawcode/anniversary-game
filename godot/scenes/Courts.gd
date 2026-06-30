# Scene 9 — Netball courts. Ported from scenes/courts.py.
# Single court behind the sports centre, enclosed by wire fence on three sides
# (open to the walkway at top). Stairs run up at top-left; a two-wide gate at the
# bottom-left (cols 3,4) lets the court out to the bottom walkway, and the left
# pathway runs alongside down to the same walkway.
# Edge-walls (not blocked tiles) carve the fence/stair lines; the walkable box is
# (2..16, 2..14) minus those edges. Exits: left -> passage (8), down -> courtyard (7).
#
# Bake captures the room only: sky, brick walls, concrete walkways, stairs, the tarmac
# court surface and its painted line-markings (surface markings stay baked). The two
# floor-standing features are nodes: the goal hoops and the wire fence both ring the
# court boundary with the player always on the inner/court side in front of them -> Z_BACK.
class_name Courts
extends GameScene

const _TS := 32

# courts-local palette (scenes/courts.py)
var _TARMAC := Color8(62, 65, 68)
var _TARMAC_ALT := Color8(58, 61, 64)
var _LINE := Color8(235, 235, 230)
var _FENCE_POST := Color8(42, 42, 40)
var _MESH := Color8(130, 133, 128)
var _MESH_DK := Color8(100, 103, 98)
var _BRICK := Color8(155, 68, 48)
var _BRICK_DK := Color8(130, 52, 35)
var _CONCRETE := Color8(175, 170, 165)
var _HOOP_OR := Color8(230, 120, 40)
var _HOOP_DK := Color8(200, 95, 25)
var _POLE := Color8(140, 142, 145)
var _POLE_DK := Color8(110, 112, 115)
var _SKY := Color8(165, 185, 210)
var _LIGHT := Color8(240, 238, 230)
var _STAIR := Color8(155, 150, 145)
var _STAIR_DK := Color8(135, 130, 125)
var _STAIR_NOSE := Color8(175, 170, 165)
var _RAIL := Color8(85, 85, 90)
var _RAIL_LT := Color8(110, 110, 115)

var _FW := 6

# Court rectangle (pixel coords for line markings) — courts.py _COURT.
var _COURT := Rect2(3 * _TS + 10, 6 * _TS, 14 * _TS - 20, 6 * _TS)


func _init() -> void:
	bg_texture = "res://assets/baked/courts_bg.png"   # native backdrop; _draw() is now the re-bake seed
	walkable_cols = Vector2i(2, 16)
	walkable_rows = Vector2i(2, 14)
	exits = {
		"left": {"scene": 8, "rows": Vector2i(2, 3), "target": Vector2i(17, 6)},   # -> passage
		# Bottom-left gate (cols 3,4) drops you at the foot of the courtyard's
		# central path (col 9), one column off its return-door.
		"down": {"scene": 7, "cols": Vector2i(3, 4), "target": Vector2i(9, 12)},   # -> courtyard
	}
	entry_points = {"right": Vector2i(3, 3), "down": Vector2i(10, 13)}

	grid = TileGrid.new(
		walkable_cols, walkable_rows,
		Config.MAP_COLS, Config.MAP_ROWS,
		[], _build_walls())

	# Open-air court: bright neutral daylight, with two floodlight pools warming
	# the tarmac where the pygame fill was flat. Real PointLight2Ds give the
	# court surface a soft gradient under the masts on the back wall.
	ambient_color = Color(0.82, 0.83, 0.86)
	var flood := Color8(255, 252, 240)
	for fx in [5 * _TS, 14 * _TS]:
		lights.append({"pos": Vector2(fx, 6 * _TS), "radius": 300.0, "color": flood, "energy": 0.34})
	var sky := Color8(210, 222, 240)
	lights.append({"pos": Vector2(10 * _TS, 3 * _TS), "radius": 200.0, "color": sky, "energy": 0.3})  # open top


func _build_walls() -> Array:
	var w: Array = []
	# Stair bottom wall — blocks north/south between stairs and walkway.
	for c in range(2, 4):
		w.append([Vector2i(c, 3), Vector2i(c, 4)])
		w.append([Vector2i(c, 4), Vector2i(c, 3)])
	# Left fence (col 2 <-> 3, rows 5..12).
	for r in range(5, 13):
		w.append([Vector2i(2, r), Vector2i(3, r)])
		w.append([Vector2i(3, r), Vector2i(2, r)])
	# Bottom fence — two-wide exit at far-left (cols 3,4 stay open).
	for c in range(5, 17):
		w.append([Vector2i(c, 12), Vector2i(c, 13)])
		w.append([Vector2i(c, 13), Vector2i(c, 12)])
	return w


# Draw target: the scene's own canvas while baking the room, or a Fixture node while it
# paints its feature. Every draw helper routes through this.
var _cv: CanvasItem


func _on_ready() -> void:
	# The hoops and the wire fence ring the court boundary; the player is always on the
	# inner/court side, in front of them, never behind -> Z_BACK (the baked player-on-top
	# look). They are nodes for interact/collision ownership (the fence already owns its
	# wall-edges in the grid).
	add_fixture(Fixture.Z_BACK, _paint_hoops)
	add_fixture(Fixture.Z_BACK, _paint_fence)


func _r(x, y, w, h, c) -> void:
	_cv.draw_rect(Rect2(x, y, w, h), c)


func _outline(x, y, w, h, c, width := 1.0) -> void:
	_cv.draw_rect(Rect2(x, y, w, h), c, false, width)


func _ln(x0, y0, x1, y1, c, w := 1.0) -> void:
	_cv.draw_line(Vector2(x0, y0), Vector2(x1, y1), c, w)


func _circ_outline(cx, cy, r, c, w := 1.0) -> void:
	_cv.draw_arc(Vector2(cx, cy), r, 0, TAU, 24, c, w)


# pygame.draw.ellipse bounding-box semantics: (x, y) top-left, (w, h) box size.
func _ellipse(x, y, w, h, c) -> void:
	var rx: float = w / 2.0
	var ry: float = h / 2.0
	_cv.draw_set_transform(Vector2(x + rx, y + ry), 0, Vector2(rx, ry))
	_cv.draw_circle(Vector2.ZERO, 1.0, c)
	_cv.draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


func _shade(c: Color, f: float) -> Color:
	return Color(c.r * f, c.g * f, c.b * f)


# Liang–Barsky line clip to a rect — Godot has no immediate-mode clip, and the
# fence mesh diagonals must stay inside their thin strips.
func _ln_clipped(x0: float, y0: float, x1: float, y1: float, rect: Rect2, c: Color, w := 1.0) -> void:
	var dx := x1 - x0
	var dy := y1 - y0
	var p := [-dx, dx, -dy, dy]
	var q := [x0 - rect.position.x, rect.position.x + rect.size.x - x0,
			y0 - rect.position.y, rect.position.y + rect.size.y - y0]
	var u0 := 0.0
	var u1 := 1.0
	for i in range(4):
		var pi: float = p[i]
		var qi: float = q[i]
		if pi == 0.0:
			if qi < 0.0:
				return
		else:
			var t: float = qi / pi
			if pi < 0.0:
				u0 = max(u0, t)
			else:
				u1 = min(u1, t)
	if u0 > u1:
		return
	_ln(x0 + u0 * dx, y0 + u0 * dy, x0 + u1 * dx, y0 + u1 * dy, c, w)


func _brick_rect(x: int, y: int, w: int, h: int) -> void:
	_r(x, y, w, h, _BRICK)
	var offset := 0
	for gy in range(y, y + h, 4):
		for gx in range(x + offset, x + w, 8):
			_ln(gx, gy, gx, gy + 4, _BRICK_DK, 1)
		offset = 4 - offset
		_ln(x, gy, x + w, gy, _BRICK_DK, 1)


func _draw_mesh(rect: Rect2) -> void:
	var left := int(rect.position.x)
	var top := int(rect.position.y)
	var right := int(rect.position.x + rect.size.x)
	var bottom := int(rect.position.y + rect.size.y)
	for y in range(top - 8, bottom + 8, 8):
		for x in range(left - 8, right + 8, 8):
			_ln_clipped(x, y, x + 8, y + 8, rect, _MESH, 1)
			_ln_clipped(x + 8, y, x, y + 8, rect, _MESH_DK, 1)


func _draw() -> void:
	if use_baked_bg:        # live path renders the baked Sprite2D; _draw() is the bake seed
		return
	_cv = self
	_cv.draw_rect(Rect2(0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), Color(0, 0, 0))  # black off-plan
	_draw_sky_strip()
	_draw_back_wall()
	_draw_side_walls()
	_draw_walkway()
	_draw_stairs()
	_draw_court_surface()
	_draw_left_pathway()
	_draw_court_lines()
	_draw_bottom_walkway()


func _paint_hoops(c: CanvasItem) -> void:
	_cv = c
	_draw_hoops()


func _paint_fence(c: CanvasItem) -> void:
	_cv = c
	_draw_fence()


func _draw_sky_strip() -> void:
	_r(0, 0, 20 * _TS, _TS, _SKY)
	for cx in [5 * _TS, 14 * _TS]:
		_ellipse(cx - 14, _TS - 10, 28, 10, _LIGHT)


func _draw_back_wall() -> void:
	_brick_rect(0, _TS, 20 * _TS, _TS)


func _draw_side_walls() -> void:
	_brick_rect(0, 2 * _TS, 2 * _TS, 13 * _TS)
	_brick_rect(17 * _TS, 2 * _TS, 3 * _TS, 13 * _TS)


func _draw_walkway() -> void:
	_r(2 * _TS, 2 * _TS, 15 * _TS, 3 * _TS, _CONCRETE)


func _draw_stairs() -> void:
	var x0 := 2 * _TS
	var y0 := 2 * _TS
	var w := 2 * _TS
	var h := 2 * _TS
	var num_steps := 8
	var step_w: int = w / num_steps

	for i in range(num_steps):
		var sx := x0 + i * step_w
		var t := i / float(max(1, num_steps - 1))
		_r(sx, y0, step_w, h, _shade(_STAIR, 1.0 - (1.0 - t) * 0.35))
		_outline(sx, y0, step_w, h, _STAIR_DK, 1)
		_ln(sx, y0, sx, y0 + h, _shade(_STAIR_NOSE, 1.0 - (1.0 - t) * 0.3), 2)

	_outline(x0, y0, w, h, _STAIR_DK, 1)

	for ry in [y0 + 2, y0 + h - 4]:
		_r(x0 - 2, ry, w + 4, 2, _RAIL)
		_r(x0 - 2, ry, w + 4, 1, _RAIL_LT)
		_r(x0 - 4, ry - 1, 3, 4, _RAIL)
		_r(x0 + w + 1, ry - 1, 3, 4, _RAIL)


func _draw_left_pathway() -> void:
	_r(2 * _TS, 5 * _TS, _TS, 8 * _TS, _CONCRETE)


func _draw_court_surface() -> void:
	var x0 := 3 * _TS
	var y0 := 5 * _TS
	var w := 14 * _TS
	var h := 8 * _TS
	_r(x0, y0, w, h, _TARMAC)
	for ty in range(y0, y0 + h, _TS):
		for tx in range(x0, x0 + w, _TS):
			if ((tx - x0) / _TS + (ty - y0) / _TS) % 5 == 0:
				_r(tx, ty, _TS, _TS, _TARMAC_ALT)


func _draw_court_lines() -> void:
	var ct := _COURT
	var left := ct.position.x
	var top := ct.position.y
	var right := ct.position.x + ct.size.x
	var bottom := ct.position.y + ct.size.y
	var cx := ct.position.x + ct.size.x / 2.0
	var cy := ct.position.y + ct.size.y / 2.0
	_outline(left, top, ct.size.x, ct.size.y, _LINE, 2)
	var third_w: float = ct.size.x / 3.0
	for i in [1, 2]:
		var lx: float = left + i * third_w
		_ln(lx, top, lx, bottom, _LINE, 2)
	_circ_outline(cx, cy, 22, _LINE, 2)
	var d_r := ct.size.y / 2.0
	_cv.draw_arc(Vector2(left, cy), d_r, -1.5708, 1.5708, 32, _LINE, 2)
	_cv.draw_arc(Vector2(right, cy), d_r, 1.5708, 4.7124, 32, _LINE, 2)


func _draw_hoops() -> void:
	var ct := _COURT
	var cy := ct.position.y + ct.size.y / 2.0
	for hx in [ct.position.x + 2, ct.position.x + ct.size.x - 2]:
		_r(hx - 2, cy - 3, 4, 6, _POLE)
		_outline(hx - 2, cy - 3, 4, 6, _POLE_DK, 1)
		_circ_outline(hx, cy, 6, _HOOP_OR, 2)
		_circ_outline(hx, cy, 6, _HOOP_DK, 1)


func _draw_fence() -> void:
	var fw := _FW
	var fence_top := 5 * _TS
	var fence_h := 8 * _TS

	# Left fence — thin strip on left edge of col 3.
	var lx := 3 * _TS
	var lf := Rect2(lx, fence_top, fw, fence_h)
	_draw_mesh(lf)
	for r in range(5, 13, 2):
		_r(lx, r * _TS, fw, 8, _FENCE_POST)
	_r(lx, fence_top, fw, 3, _FENCE_POST)
	_r(lx, fence_top + fence_h - 3, fw, 3, _FENCE_POST)

	# Right fence — thin strip on right edge of col 16.
	var rx := 17 * _TS - fw
	var rf := Rect2(rx, fence_top, fw, fence_h)
	_draw_mesh(rf)
	for r in range(5, 13, 2):
		_r(rx, r * _TS, fw, 8, _FENCE_POST)
	_r(rx, fence_top, fw, 3, _FENCE_POST)
	_r(rx, fence_top + fence_h - 3, fw, 3, _FENCE_POST)

	# Bottom fence — thin strip at bottom of row 12, two-wide exit at far-left
	# (cols 3,4 open), so the mesh runs from col 5 to col 16.
	var by := 13 * _TS - fw
	var bx := 5 * _TS
	var bw := 12 * _TS
	var bf := Rect2(bx, by, bw, fw)
	_draw_mesh(bf)
	for c in range(5, 17, 2):
		_r(c * _TS, by, 8, fw, _FENCE_POST)

	# Bottom-right corner post — seal where bottom fence meets the right fence.
	_r(rx, by, fw, fw, _FENCE_POST)

	# Exit jambs — left jamb is the bottom of the left fence; right jamb frames
	# the opening at the start of the bottom fence (col 5).
	_r(3 * _TS, by - 2, fw, fw + 4, _FENCE_POST)
	_r(5 * _TS - fw, by - 2, fw, fw + 4, _FENCE_POST)


func _draw_bottom_walkway() -> void:
	_r(2 * _TS, 13 * _TS, 15 * _TS, 2 * _TS, _CONCRETE)
