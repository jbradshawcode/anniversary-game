# Scene 7 — school courtyard. Ported from scenes/courtyard.py.
# Long brick-paved avenue from the King Street gates (north) to the sports-centre
# glass entrance (south), flanked by Victorian school buildings (west) and the
# modern wing (east). Narrows at the gates, widens into a piazza near the glass.
# The walkable box (3..16, 2..12) is carved by static_blocked: planted borders and
# building edges down both sides, leaving the central path + piazza navigable.
#
# Bake captures the room only: the flanking buildings, gate walls + posts, south walls,
# the paved floor and the glass entrance. Every courtyard feature is its own node. The
# planted borders, benches and cafe tables are low -> Z_BACK (faithful player-on-top).
# The trees and cypresses are tall: the player walks behind them, so each is a Y->z
# node anchored at its trunk base.
class_name Courtyard
extends GameScene

const _TS := 32

# courtyard-local palette (scenes/courtyard.py)
var _VIC := Color8(155, 68, 48)
var _VIC_DK := Color8(130, 52, 35)
var _STONE := Color8(195, 188, 175)
var _STONE_DK := Color8(175, 168, 155)
var _MOD := Color8(165, 95, 58)
var _MOD_DK := Color8(142, 78, 45)
var _MOD_UPPER := Color8(175, 175, 178)
var _MOD_UP_DK := Color8(155, 155, 158)
var _MOD_ACCENT := Color8(215, 195, 135)
var _PATH := Color8(205, 178, 148)
var _PATH_ALT := Color8(198, 170, 140)
var _PATH_BRICK := Color8(180, 120, 82)
var _PATH_BR_DK := Color8(155, 98, 65)
var _GLASS := Color8(155, 175, 190)
var _GLASS_HI := Color8(180, 200, 215)
var _GLASS_FR := Color8(85, 100, 115)
var _SLATE := Color8(85, 90, 100)
var _SLATE_DK := Color8(72, 78, 88)
var _IRON := Color8(42, 40, 38)
var _IRON_LT := Color8(62, 60, 58)
var _PLANT_BG := Color8(45, 72, 38)
var _PLANT_BOX := Color8(55, 108, 48)
var _PLANT_BX_D := Color8(42, 85, 35)
var _PLANT_COV := Color8(68, 95, 55)
var _BENCH := Color8(110, 95, 72)
var _BENCH_DK := Color8(85, 72, 52)
var _BENCH_SLAT := Color8(125, 108, 82)
var _TREE_TRUNK := Color8(95, 65, 35)
var _TREE_LEAF := Color8(65, 135, 55)
var _TREE_LF_DK := Color8(48, 110, 42)
var _TREE_LF_LT := Color8(78, 150, 65)
var _CYPRESS := Color8(52, 90, 52)
var _CYPRESS_LT := Color8(68, 110, 62)
var _CHIMNEY := Color8(142, 58, 40)
var _CAFE_METAL := Color8(85, 85, 88)
var _CAFE_TOP := Color8(195, 192, 188)
var _SHADOW := Color8(178, 152, 122)
var _WINDOW_SIL := Color8(185, 178, 165)

# (c0, c1, r0, r1) paved zones, half-open in tiles (courtyard.py _FLOOR_ZONES)
var _FLOOR_ZONES := [
	[3, 17, 2, 13],
	[8, 12, 0, 2],
	[6, 14, 13, 15],
]


func _init() -> void:
	bg_texture = "res://assets/baked/courtyard_bg.png"   # native backdrop; _draw() is now the re-bake seed
	walkable_cols = Vector2i(3, 16)
	walkable_rows = Vector2i(2, 12)
	exits = {
		"up": {"scene": 2, "cols": Vector2i(9, 10), "target": Vector2i(4, 10)},   # -> King Street
		"down": {"scene": 9, "cols": Vector2i(10, 10), "target": Vector2i(5, 13)},  # -> courts
	}
	entry_points = {"up": Vector2i(10, 11), "down": Vector2i(10, 3)}

	var blocked: Array = []
	for r in range(2, 9):
		blocked.append(Vector2i(3, r))
		blocked.append(Vector2i(16, r))
	for r in range(2, 5):
		blocked.append(Vector2i(4, r))
		blocked.append(Vector2i(15, r))
	for t in [
		Vector2i(5, 2), Vector2i(14, 4), Vector2i(5, 10),
		Vector2i(3, 10), Vector2i(3, 11),
		Vector2i(5, 6), Vector2i(14, 7),
		Vector2i(15, 10), Vector2i(16, 10), Vector2i(15, 11), Vector2i(16, 11),
	]:
		blocked.append(t)

	grid = TileGrid.new(
		walkable_cols, walkable_rows,
		Config.MAP_COLS, Config.MAP_ROWS,
		blocked, [])

	# Open-air daytime: bright warm ambient (no night-darkening), with soft sun
	# pools warming the central piazza and the gate gap. Real PointLight2Ds give
	# the paving a gentle gradient the flat pygame fill never had.
	ambient_color = Color(0.88, 0.87, 0.83)
	var sun := Color8(255, 250, 236)
	lights.append({"pos": Vector2(9 * _TS + _TS, 6 * _TS), "radius": 280.0, "color": sun, "energy": 0.32})
	lights.append({"pos": Vector2(9 * _TS + _TS, 12 * _TS), "radius": 230.0, "color": sun, "energy": 0.34})  # piazza
	var sky := Color8(214, 226, 240)
	lights.append({"pos": Vector2(9 * _TS + _TS, 1 * _TS), "radius": 160.0, "color": sky, "energy": 0.4})    # gate gap


# Draw target: the scene's own canvas while baking the room, or a Fixture node while it
# paints its feature. Every draw helper routes through this.
var _cv: CanvasItem


func _on_ready() -> void:
	# Low features the player never visibly stands behind -> Z_BACK (faithful player-on-top).
	add_fixture(Fixture.Z_BACK, _paint_planters)
	add_fixture(Fixture.Z_BACK, _paint_benches)
	add_fixture(Fixture.Z_BACK, _paint_cafe_tables)
	# Tall vegetation the player rounds from the north -> Y->z, anchored at the trunk base.
	for t in [[5, 2], [14, 4], [5, 10]]:
		add_fixture(t[1] * _TS + 22, _paint_tree.bind(t[0], t[1]))
	for cp in [[3, 10], [3, 11]]:
		add_fixture(cp[1] * _TS + 24, _paint_cypress.bind(cp[0], cp[1]))


func _r(x, y, w, h, c) -> void:
	_cv.draw_rect(Rect2(x, y, w, h), c)


func _outline(x, y, w, h, c, width := 1.0) -> void:
	_cv.draw_rect(Rect2(x, y, w, h), c, false, width)


func _ln(x0, y0, x1, y1, c, w := 1.0) -> void:
	_cv.draw_line(Vector2(x0, y0), Vector2(x1, y1), c, w)


func _circ(cx, cy, r, c) -> void:
	_cv.draw_circle(Vector2(cx, cy), r, c)


func _circ_outline(cx, cy, r, c, w := 1.0) -> void:
	_cv.draw_arc(Vector2(cx, cy), r, 0, TAU, 24, c, w)


func _poly(pts: Array, c) -> void:
	_cv.draw_colored_polygon(PackedVector2Array(pts), c)


func _poly_outline(pts: Array, c, w := 1.0) -> void:
	var closed := pts.duplicate()
	closed.append(pts[0])
	_cv.draw_polyline(PackedVector2Array(closed), c, w)


# pygame.draw.ellipse bounding-box semantics: (x, y) top-left, (w, h) box size.
func _ellipse(x, y, w, h, c) -> void:
	var rx: float = w / 2.0
	var ry: float = h / 2.0
	_cv.draw_set_transform(Vector2(x + rx, y + ry), 0, Vector2(rx, ry))
	_cv.draw_circle(Vector2.ZERO, 1.0, c)
	_cv.draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


# Flat brick fill with offset courses + mortar lines (courtyard.py's inline pattern).
func _brick_rect(x: int, y: int, w: int, h: int, color: Color, dark: Color) -> void:
	_r(x, y, w, h, color)
	var offset := 0
	for gy in range(y, y + h, 4):
		for gx in range(x + offset, x + w, 8):
			_ln(gx, gy, gx, gy + 4, dark, 1)
		offset = 4 - offset
		_ln(x, gy, x + w, gy, dark, 1)


func _draw() -> void:
	if use_baked_bg:        # live path renders the baked Sprite2D; _draw() is the bake seed
		return
	_cv = self
	_cv.draw_rect(Rect2(0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), Color(0, 0, 0))  # black off-plan
	_draw_vic_building()
	_draw_mod_building()
	_draw_gate_walls()
	_draw_south_walls()
	_draw_floor()
	_draw_gateposts()
	_draw_glass_entrance()


func _paint_planters(c: CanvasItem) -> void:
	_cv = c
	_draw_planted_borders()


func _paint_benches(c: CanvasItem) -> void:
	_cv = c
	_draw_bench(5, 6, "east")
	_draw_bench(14, 7, "west")


func _paint_cafe_tables(c: CanvasItem) -> void:
	_cv = c
	_draw_cafe_tables()


func _paint_tree(c: CanvasItem, col: int, row: int) -> void:
	_cv = c
	_draw_tree(col, row)


func _paint_cypress(c: CanvasItem, col: int, row: int) -> void:
	_cv = c
	_draw_cypress(col, row)


func _draw_vic_building() -> void:
	var w := 3 * _TS
	var h := 15 * _TS
	_brick_rect(0, 0, w, h, _VIC, _VIC_DK)

	var gable_h := 2 * _TS
	for i in range(6):
		var gy := 2 * _TS + i * gable_h
		var peak_y := gy + gable_h / 2
		_poly([Vector2(w - 2, gy + 2), Vector2(w + 6, peak_y), Vector2(w - 2, gy + gable_h - 2)], _SLATE)
		_poly_outline([Vector2(w - 2, gy + 2), Vector2(w + 6, peak_y), Vector2(w - 2, gy + gable_h - 2)], _SLATE_DK, 1)
		_r(w + 3, peak_y - 3, 5, 6, _STONE)

	for i in range(6):
		var wy := 2 * _TS + i * gable_h + (gable_h - 20) / 2
		var wx := w - 16
		_r(wx - 2, wy - 2, 16, 22, _STONE)
		_poly([Vector2(wx, wy), Vector2(wx + 6, wy - 5), Vector2(wx + 12, wy)], _STONE)
		_poly([Vector2(wx + 2, wy), Vector2(wx + 6, wy - 3), Vector2(wx + 10, wy)], _GLASS)
		_r(wx, wy, 12, 18, _GLASS)
		_r(wx, wy, 6, 9, _GLASS_HI)
		_ln(wx + 6, wy - 3, wx + 6, wy + 18, _STONE_DK, 1)
		_outline(wx, wy, 12, 18, _STONE_DK, 1)
		_r(wx - 2, wy + 18, 16, 2, _WINDOW_SIL)

	for cx in [_TS - 4, 2 * _TS - 6]:
		_r(cx, 0, 8, 6, _CHIMNEY)
		_outline(cx, 0, 8, 6, _VIC_DK, 1)
		_r(cx - 1, 0, 10, 2, _STONE)


func _draw_mod_building() -> void:
	var x := 17 * _TS
	var w := 3 * _TS
	var h := 15 * _TS
	_brick_rect(x, 0, w, h, _MOD, _MOD_DK)

	for r in range(0, 15, 3):
		var uy := r * _TS
		_r(x + 2, uy, w - 4, _TS, _MOD_UPPER)
		_r(x + 4, uy + 4, w - 8, _TS - 8, _GLASS)
		_r(x + 4, uy + 4, (w - 8) / 2, (_TS - 8) / 2, _GLASS_HI)
		_outline(x + 4, uy + 4, w - 8, _TS - 8, _MOD_UP_DK, 1)

	_r(x, 0, 3, h, _MOD_ACCENT)


func _draw_gate_walls() -> void:
	for z in [[3, 8, 0, 2], [12, 17, 0, 2]]:
		var x: int = z[0] * _TS
		var y: int = z[2] * _TS
		var w: int = (z[1] - z[0]) * _TS
		var h: int = (z[3] - z[2]) * _TS
		_brick_rect(x, y, w, h, _VIC, _VIC_DK)

	for s in [[3 * _TS, 5 * _TS], [12 * _TS, 5 * _TS]]:
		var section_x: int = s[0]
		var section_w: int = s[1]
		var arch_w := 32
		var num := section_w / arch_w
		for i in range(num):
			var ax := section_x + i * arch_w + 4
			var ay := 6
			var aw := arch_w - 8
			var ah := 2 * _TS - 10
			_r(ax - 1, ay - 1, aw + 2, ah + 2, _STONE)
			_poly([Vector2(ax, ay), Vector2(ax + aw / 2, ay - 6), Vector2(ax + aw, ay)], _STONE)
			_r(ax + 1, ay + 1, aw - 2, ah - 2, _IRON)
			_poly([Vector2(ax + 1, ay + 1), Vector2(ax + aw / 2, ay - 4), Vector2(ax + aw - 1, ay + 1)], _IRON)
			for rx in range(ax + 4, ax + aw - 2, 4):
				_ln(rx, ay, rx, ay + ah, _IRON_LT, 1)
			_ln(ax + 1, ay + ah / 2, ax + aw - 1, ay + ah / 2, _IRON_LT, 1)


func _draw_gateposts() -> void:
	for px in [8 * _TS - 10, 12 * _TS]:
		_r(px, 0, 10, 2 * _TS, _VIC)
		var offset := 0
		for gy in range(0, 2 * _TS, 4):
			_ln(px, gy, px + 10, gy, _VIC_DK, 1)
			for gx in range(px + offset, px + 10, 8):
				_ln(gx, gy, gx, gy + 4, _VIC_DK, 1)
			offset = 4 - offset
		_r(px - 2, 0, 14, 4, _STONE)
		_outline(px - 2, 0, 14, 4, _STONE_DK, 1)
		_r(px + 1, _TS + 2, 8, 10, _STONE)
		_outline(px + 1, _TS + 2, 8, 10, _STONE_DK, 1)
		_poly([Vector2(px, 6), Vector2(px + 5, 0), Vector2(px + 10, 6)], _STONE)
		_poly_outline([Vector2(px, 6), Vector2(px + 5, 0), Vector2(px + 10, 6)], _STONE_DK, 1)


func _draw_south_walls() -> void:
	for c in [[3, 6], [14, 17]]:
		var x: int = c[0] * _TS
		var y := 13 * _TS
		var w: int = (c[1] - c[0]) * _TS
		var h := 2 * _TS
		_brick_rect(x, y, w, h, _VIC, _VIC_DK)


func _draw_glass_entrance() -> void:
	var gx := 6 * _TS
	var gy := 13 * _TS
	var gw := 8 * _TS
	var gh := 2 * _TS
	_r(gx - 6, gy - 2, 10, gh + 4, _VIC)
	_r(gx + gw - 4, gy - 2, 10, gh + 4, _VIC)
	_outline(gx - 6, gy - 2, 10, gh + 4, _VIC_DK, 1)
	_outline(gx + gw - 4, gy - 2, 10, gh + 4, _VIC_DK, 1)

	_r(gx, gy - 2, gw, gh + 4, _GLASS_FR)
	var pane_w := gw / 8
	for i in range(8):
		var px := gx + i * pane_w + 1
		var pw := pane_w - 2
		_r(px, gy, pw, gh - 2, _GLASS)
		_r(px, gy, pw / 2, gh / 3, _GLASS_HI)
		_outline(px, gy, pw, gh - 2, _GLASS_FR, 1)
	_ln(gx + gw / 2, gy, gx + gw / 2, gy + gh - 2, _GLASS_FR, 2)
	_ln(gx, gy + gh / 2, gx + gw, gy + gh / 2, _GLASS_FR, 1)


func _draw_floor() -> void:
	for z in _FLOOR_ZONES:
		var fx: int = z[0] * _TS
		var fy: int = z[2] * _TS
		var fw: int = (z[1] - z[0]) * _TS
		var fh: int = (z[3] - z[2]) * _TS
		_r(fx, fy, fw, fh, _PATH)
		for py in range(fy, fy + fh, _TS):
			for px in range(fx, fx + fw, _TS):
				if ((px - fx) / _TS + (py - fy) / _TS) % 3 == 0:
					_r(px, py, _TS, _TS, _PATH_ALT)

	var strip_x := 10 * _TS - 8
	var strip_w := 16
	for z in _FLOOR_ZONES:
		var fy: int = z[2] * _TS
		var fh: int = (z[3] - z[2]) * _TS
		_r(strip_x, fy, strip_w, fh, _PATH_BRICK)
		var bw := 8
		var bh := 4
		for row in range(fh / bh):
			var off := (bw / 2) if row % 2 else 0
			for col in range(-1, strip_w / bw + 2):
				var bx := strip_x + col * bw + off
				var by := fy + row * bh
				_outline(bx, by, bw, bh, _PATH_BR_DK, 1)


func _draw_planted_borders() -> void:
	for r in range(2, 9):
		var bx := 3 * _TS
		var by := r * _TS
		_r(bx, by, _TS, _TS, _PLANT_BG)
		_r(bx + 2, by + 2, _TS - 4, _TS - 4, _PLANT_COV)
		var cx := bx + _TS / 2
		var cy := by + _TS / 2
		_circ(cx, cy, 8, _PLANT_BX_D)
		_circ(cx - 1, cy - 1, 7, _PLANT_BOX)

	for r in range(2, 5):
		var bx := 4 * _TS
		var by := r * _TS
		_r(bx, by, _TS, _TS, _PLANT_BG)
		_r(bx + 4, by + 4, _TS - 8, _TS - 8, _PLANT_COV)
		for sx in range(bx + 8, bx + _TS - 4, 12):
			_circ(sx, by + _TS / 2, 5, _PLANT_BOX)
			_circ_outline(sx, by + _TS / 2, 5, _PLANT_BX_D, 1)

	for r in range(2, 9):
		var bx := 16 * _TS
		var by := r * _TS
		_r(bx, by, _TS, _TS, _PLANT_BG)
		_r(bx + 2, by + 2, _TS - 4, _TS - 4, _PLANT_COV)
		var cx := bx + _TS / 2
		var cy := by + _TS / 2
		_circ(cx, cy, 8, _PLANT_BX_D)
		_circ(cx - 1, cy - 1, 7, _PLANT_BOX)

	for r in range(2, 5):
		var bx := 15 * _TS
		var by := r * _TS
		_r(bx, by, _TS, _TS, _PLANT_BG)
		_r(bx + 4, by + 4, _TS - 8, _TS - 8, _PLANT_COV)
		for sx in range(bx + 8, bx + _TS - 4, 12):
			_circ(sx, by + _TS / 2, 5, _PLANT_BOX)
			_circ_outline(sx, by + _TS / 2, 5, _PLANT_BX_D, 1)


func _draw_tree(col: int, row: int) -> void:
	var cx := col * _TS + _TS / 2
	var cy := row * _TS + _TS / 2
	_ellipse(cx - 14, cy - 4, 28, 14, _SHADOW)
	_r(cx - 3, cy - 4, 6, 10, _TREE_TRUNK)
	_circ(cx, cy - 4, 13, _TREE_LF_DK)
	_circ(cx - 2, cy - 6, 11, _TREE_LEAF)
	_circ(cx - 4, cy - 8, 6, _TREE_LF_LT)


func _draw_cypress(col: int, row: int) -> void:
	var cx := col * _TS + _TS / 2
	var cy := row * _TS + _TS / 2
	_ellipse(cx - 5, cy + 4, 10, 6, _SHADOW)
	_r(cx - 1, cy + 2, 3, 6, _TREE_TRUNK)
	_ellipse(cx - 5, cy - 14, 10, 26, _CYPRESS)
	_ellipse(cx - 3, cy - 12, 6, 20, _CYPRESS_LT)


func _draw_bench(col: int, row: int, facing: String) -> void:
	var x := col * _TS
	var y := row * _TS
	if facing == "east" or facing == "west":
		_r(x + 8, y + 2, 16, 28, _BENCH)
		for sy in range(y + 3, y + 29, 4):
			_r(x + 9, sy, 14, 3, _BENCH_SLAT)
		for ly in [y + 4, y + 22]:
			_r(x + 7, ly, 2, 6, _BENCH_DK)
			_r(x + 23, ly, 2, 6, _BENCH_DK)
		var back_x := x + 5 if facing == "east" else x + 24
		_r(back_x, y + 2, 3, 28, _BENCH_DK)
	else:
		_r(x + 2, y + 8, 28, 16, _BENCH)
		for sx in range(x + 3, x + 29, 4):
			_r(sx, y + 9, 3, 14, _BENCH_SLAT)
		for lx in [x + 4, x + 22]:
			_r(lx, y + 7, 6, 2, _BENCH_DK)
			_r(lx, y + 23, 6, 2, _BENCH_DK)
		var back_y := y + 6 if facing == "south" else y + 24
		_r(x + 2, back_y, 28, 3, _BENCH_DK)


func _draw_cafe_tables() -> void:
	for tr in [10, 11]:
		for tc in [15, 16]:
			var tx: int = tc * _TS
			var ty: int = tr * _TS
			var cx := tx + _TS / 2
			var cy := ty + _TS / 2
			_r(cx - 6, cy - 6, 12, 12, _CAFE_TOP)
			_outline(cx - 6, cy - 6, 12, 12, _CAFE_METAL, 1)
			for d in [Vector2i(-9, 0), Vector2i(9, 0), Vector2i(0, -9), Vector2i(0, 9)]:
				var sx: int = cx + d.x
				var sy: int = cy + d.y
				if tx + 2 < sx and sx < tx + _TS - 2 and ty + 2 < sy and sy < ty + _TS - 2:
					_r(sx - 3, sy - 3, 6, 6, _CAFE_METAL)
