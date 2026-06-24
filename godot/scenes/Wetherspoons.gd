# Scene 10 — The William Morris (Wetherspoons). Ported from scenes/wetherspoons.py.
# Single-screen pub: the famous floral carpet, dark mahogany panelling with gilt
# William Morris prints + a mirror, an L of cask pumps along the front-room bar
# (gantry/optics/fridge above), a glazed partition with an open archway dividing
# the front room from the snug, green + mustard wall banquettes, poseur high-tables
# by the bar, dining tables + a snug, a teal-tiled fireplace, and the street doors.
# Banquettes/bar/tables/partition/fireplace are all SOLID. Exit: down -> King St (2).
class_name Wetherspoons
extends GameScene

const _TS := 32

# ── Layout (tile positions; everything here is SOLID / non-walkable) ──────────
const _HIGH := [[3, 4], [5, 4], [7, 4], [9, 4]]
const _DINING := [[3, 7], [6, 7], [9, 7], [3, 10], [6, 10], [9, 10]]
const _SNUG := [[13, 5], [16, 5], [13, 8], [16, 8], [13, 11], [16, 11]]

# Chair-back arc per facing: [a0, a1, dx, dy] — pygame arc bbox offset from the
# seat centre; centre = (cx+dx+9, cy+dy+9), r=9. pygame angles are CCW with +Y up,
# so the Godot draw_arc (CW, +Y down) sweep is [-a1, -a0].
const _CHAIR_ARCS := {
	"up": [3.6, 5.8, -9, -12], "down": [0.5, 2.7, -9, -4],
	"left": [2.1, 4.2, -12, -9], "right": [-1.0, 1.1, -4, -9],
}

# ── Palette (scenes/wetherspoons.py) ─────────────────────────────────────────
var _PANEL := Color8(76, 51, 32)
var _PANEL_DK := Color8(52, 34, 20)
var _PANEL_LT := Color8(100, 70, 46)
var _CARPET := Color8(36, 66, 62)
var _CARPET_R := Color8(132, 58, 46)
var _CARPET_GD := Color8(158, 132, 78)
var _CARPET_LF := Color8(48, 90, 72)
var _CARPET_CR := Color8(150, 150, 128)
var _SHADOW := Color8(28, 52, 49)
var _BAR_WOOD := Color8(74, 36, 28)
var _BAR_TOP := Color8(52, 26, 20)
var _BAR_HI := Color8(110, 60, 46)
var _BAR_DK := Color8(40, 22, 14)
var _BRASS := Color8(206, 174, 98)
var _GANTRY := Color8(46, 30, 18)
var _GANTRY_DK := Color8(32, 20, 12)
var _OPTIC := Color8(190, 205, 210)
var _FRIDGE := Color8(150, 178, 192)
var _FRIDGE_FR := Color8(90, 110, 120)
var _GREEN := Color8(44, 82, 60)
var _GREEN_DK := Color8(30, 60, 44)
var _GREEN_HI := Color8(78, 120, 92)
var _MUST := Color8(190, 150, 70)
var _MUST_DK := Color8(150, 116, 48)
var _MUST_HI := Color8(214, 180, 104)
var _CHAIR := Color8(120, 80, 46)
var _CHAIR_DK := Color8(78, 50, 28)
var _SEAT := Color8(176, 142, 78)
var _TABLE := Color8(92, 58, 34)
var _TABLE_DK := Color8(60, 36, 20)
var _TABLE_HI := Color8(120, 82, 52)
var _POSEUR := Color8(60, 38, 24)
var _STOOL := Color8(40, 26, 18)
var _STOOL_TOP := Color8(150, 110, 60)
var _BOTTLE_G := Color8(44, 96, 62)
var _BOTTLE_A := Color8(170, 116, 52)
var _BOTTLE_C := Color8(182, 204, 214)
var _BOTTLE_R := Color8(170, 60, 60)
var _GLASS := Color8(156, 182, 192)
var _GLASS_HI := Color8(198, 214, 220)
var _MIRROR := Color8(176, 192, 200)
var _FRAME := Color8(170, 134, 74)
var _FRAME_DK := Color8(118, 92, 50)
var _WMP_BG := Color8(78, 96, 78)
var _WMP_FG := Color8(150, 120, 70)
var _PUMP_CHR := Color8(208, 210, 212)
var _PRICE := Color8(24, 24, 26)
var _PRICE_TX := Color8(235, 235, 200)
var _LIGHT := Color8(252, 242, 208)
var _GLOW := Color8(255, 246, 214)
var _FITTING := Color8(54, 38, 24)
var _PART_GLASS := Color8(150, 170, 175)
var _FIRE := Color8(235, 150, 60)
var _FIRE_DK := Color8(180, 90, 35)
var _HEARTH := Color8(40, 38, 40)
var _CADDY := Color8(70, 70, 76)
var _PUMP_CLIP := [Color8(180, 50, 55), Color8(210, 178, 92), Color8(70, 110, 150),
	Color8(90, 60, 130), Color8(60, 130, 90)]


func _init() -> void:
	walkable_cols = Vector2i(1, 18)
	walkable_rows = Vector2i(3, 13)
	exits = {
		"down": {"scene": 2, "cols": Vector2i(8, 11), "target": Vector2i(177, 4)},  # -> King St
	}
	entry_points = {"up": Vector2i(9, 13)}

	grid = TileGrid.new(
		walkable_cols, walkable_rows,
		Config.MAP_COLS, Config.MAP_ROWS,
		_blocked(), [])

	# Cosy Spoons interior: dim warm ambient with a real pool under each pendant
	# (pygame faked these with soft-glow circles; here they're PointLight2Ds).
	ambient_color = Color(0.52, 0.47, 0.42)
	for p in [[4, 5], [7, 5], [4, 9], [7, 9], [14, 6], [16, 10]]:
		lights.append({"pos": Vector2(p[0] * _TS, p[1] * _TS), "radius": 96.0, "color": _GLOW, "energy": 1.05})
	lights.append({"pos": Vector2(6 * _TS, 12 * _TS), "radius": 84.0, "color": _GLOW, "energy": 0.9})  # ceiling rose


func _blocked() -> Array:
	var b: Array = []
	for r in range(3, 13):
		b.append(Vector2i(1, r))       # green banquette, left wall
		b.append(Vector2i(18, r))      # mustard banquette, right wall
	for r in range(3, 9):
		b.append(Vector2i(11, r))      # glazed partition (archway open rows 9-12)
	for t in _HIGH + _DINING + _SNUG:
		b.append(Vector2i(t[0], t[1]))
	return b


# ── draw helpers (pygame.draw.* mirrors) ─────────────────────────────────────

func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _outline(x, y, w, h, c, width := 1.0) -> void:
	draw_rect(Rect2(x, y, w, h), c, false, width)


func _ln(x0, y0, x1, y1, c, w := 1.0) -> void:
	draw_line(Vector2(x0, y0), Vector2(x1, y1), c, w)


func _circ(cx, cy, r, c) -> void:
	draw_circle(Vector2(cx, cy), r, c)


func _circ_o(cx, cy, r, c, w := 1.0) -> void:
	draw_arc(Vector2(cx, cy), r, 0, TAU, 24, c, w)


func _poly(pts: Array, c: Color) -> void:
	draw_colored_polygon(PackedVector2Array(pts), c)


# pygame.draw.ellipse bounding-box semantics: (x, y) top-left, (w, h) box size.
func _ellipse(x, y, w, h, c) -> void:
	var rx: float = w / 2.0
	var ry: float = h / 2.0
	draw_set_transform(Vector2(x + rx, y + ry), 0, Vector2(rx, ry))
	draw_circle(Vector2.ZERO, 1.0, c)
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


func _dk(c: Color, n := 22) -> Color:
	var d := n / 255.0
	return Color(max(0.0, c.r - d), max(0.0, c.g - d), max(0.0, c.b - d))


func _draw() -> void:
	draw_rect(Rect2(0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), Color(0, 0, 0))
	_draw_carpet()
	_draw_walls()
	_draw_fireplace()
	_draw_bar()
	_draw_partition()
	_draw_banquettes()
	_draw_high_tables(_HIGH)
	_draw_dining(_DINING, ["up", "down", "left", "right"])
	_draw_dining(_SNUG, ["up", "down", "left"])
	_draw_doors()
	_draw_lights()


# ── Floor: the famous Wetherspoons floral carpet ─────────────────────────────

func _flower(cx, cy) -> void:
	for o in [[-7, 0], [7, 0], [0, -7], [0, 7]]:
		_circ(cx + o[0], cy + o[1], 3, _CARPET_LF)
	_circ(cx, cy, 4, _CARPET_R)
	_circ(cx, cy, 2, _CARPET_GD)


func _draw_carpet() -> void:
	var top := 3 * _TS
	var bottom := 15 * _TS
	var right := 20 * _TS
	_r(0, top, right, 12 * _TS, _CARPET)
	var step := 40
	var j := 0
	var gy := top + 8
	while gy < bottom:
		var off: int = step / 2 if j % 2 else 0
		var gx := 8 + off
		while gx < right:
			draw_arc(Vector2(gx, gy), 14, -2.9, -0.3, 16, _CARPET_CR, 1)
			_flower(gx, gy)
			gx += step
		gy += step
		j += 1


# ── Walls: dark mahogany panelling, gilt prints + mirror ─────────────────────

func _panel(x, y, w, h) -> void:
	_r(x, y, w, h, _PANEL)
	var sx: int = x + 6
	while sx < x + w - 4:
		_outline(sx, y + 4, 12, h - 8, _PANEL_DK, 1)
		_ln(sx, y + 4, sx + 12, y + 4, _PANEL_LT, 1)
		sx += 20


func _wm_print(x, y, w, h) -> void:
	_r(x - 2, y - 2, w + 4, h + 4, _FRAME_DK)
	_r(x - 1, y - 1, w + 2, h + 2, _FRAME)
	_r(x, y, w, h, _WMP_BG)
	var fy: int = y + 4
	while fy < y + h - 2:
		var fx: int = x + 4
		while fx < x + w - 2:
			_circ(fx, fy, 2, _WMP_FG)
			fx += 8
		fy += 7


func _draw_walls() -> void:
	_panel(0, 0, _TS, 15 * _TS)
	_panel(19 * _TS, 0, _TS, 15 * _TS)
	_panel(0, 14 * _TS, 20 * _TS, _TS)
	_panel(12 * _TS, 0, 7 * _TS, 3 * _TS)              # snug back wall
	for ty in [5, 8, 11]:
		_wm_print(5, ty * _TS + 5, _TS - 14, _TS - 12)
		_wm_print(19 * _TS + 7, ty * _TS + 5, _TS - 14, _TS - 12)
	# gilt mirror, left wall
	var mx := 4
	var my := 3 * _TS + 4
	_r(mx - 1, my - 1, _TS - 6, _TS + 6, _FRAME_DK)
	_r(mx, my, _TS - 8, _TS + 4, _FRAME)
	_r(mx + 3, my + 3, _TS - 14, _TS - 2, _MIRROR)
	_ln(mx + 5, my + 5, mx + 5, my + _TS - 6, _GLASS_HI, 2)
	# pump-clip bunting strung across the front room
	var i := 0
	var bx := _TS
	while bx < 11 * _TS:
		var c: Color = _PUMP_CLIP[i % _PUMP_CLIP.size()]
		_poly([Vector2(bx, 3 * _TS), Vector2(bx + 14, 3 * _TS), Vector2(bx + 7, 3 * _TS + 9)], c)
		bx += 26
		i += 1


# ── Bar sprite (front room): gantry, optics, fridge, cask pumps ──────────────

func _draw_bar() -> void:
	var bx := 2 * _TS
	var bw := 11 * _TS
	var bw3: int = bw / 3
	_r(bx, 0, bw, 2 * _TS, _GANTRY_DK)
	_r(bx + 3, 3, bw - 6, 2 * _TS - 8, _GANTRY)
	# spirit optics (left third)
	for row in [10, 26]:
		_r(bx + 8, row + 12, bw3 - 8, 2, _BAR_DK)
		var ox := bx + 12
		while ox < bx + bw3:
			_r(ox, row, 5, 12, _OPTIC)
			_r(ox + 1, row + 12, 3, 3, _BRASS)
			ox += 11
	# bottle shelves (middle)
	var bshelf := [_BOTTLE_G, _BOTTLE_A, _BOTTLE_C]
	for row in [12, 30]:
		var ox := bx + bw3 + 6
		while ox < bx + 2 * bw3:
			_r(ox, row, 5, 11, bshelf[ox % 3])
			_outline(ox, row, 5, 11, _BAR_DK, 1)
			ox += 8
	# glass-front fridge (right third)
	var fx := bx + 2 * bw3 + 4
	var fw := bw - 2 * bw3 - 10
	var fridge := [_BOTTLE_R, _BOTTLE_G, _BOTTLE_C, _BOTTLE_A]
	_r(fx, 6, fw, 2 * _TS - 14, _FRIDGE_FR)
	_r(fx + 2, 8, fw - 4, 2 * _TS - 18, _FRIDGE)
	var gx := fx + 5
	while gx < fx + fw - 6:
		var gy := 12
		while gy < 2 * _TS - 16:
			_r(gx, gy, 5, 8, fridge[(gx + gy) % 4])
			gy += 11
		gx += 9
	_ln(fx + 4, 10, fx + 4, 2 * _TS - 12, _GLASS_HI, 2)
	# counter (row 2) — glossy mahogany, brass top + foot rail
	var cy := 2 * _TS
	_r(bx, cy, bw, _TS - 2, _BAR_WOOD)
	_r(bx, cy, bw, 6, _BAR_TOP)
	_ln(bx, cy + 7, bx + bw, cy + 7, _BAR_HI, 1)
	_r(bx, cy + _TS - 8, bw, 3, _BRASS)
	_outline(bx, cy, bw, _TS - 2, _BAR_DK, 1)
	# cask-ale pumps with round clips + LED price tags
	for i in range(8):
		var hx := bx + 20 + i * 40
		var clip: Color = _PUMP_CLIP[i % _PUMP_CLIP.size()]
		_r(hx, cy - 4, 5, 14, _PUMP_CHR)
		_circ(hx + 2, cy - 9, 6, clip)
		_circ_o(hx + 2, cy - 9, 6, _dk(clip), 1)
		_r(hx - 3, cy + 9, 12, 5, _PRICE)
		_r(hx - 1, cy + 10, 8, 1, _PRICE_TX)


# ── Glazed partition with archway ────────────────────────────────────────────

func _draw_partition() -> void:
	var px := 11 * _TS
	for ty in range(3, 9):
		var gy := ty * _TS + 3
		_r(px + 8, gy - 3, 16, _TS, _PANEL)
		_r(px + 5, gy, _TS - 10, _TS - 8, _PART_GLASS)
		_outline(px + 5, gy, _TS - 10, _TS - 8, _PANEL_DK, 2)
		_ln(px + 8, gy + 3, px + 8, gy + _TS - 11, _GLASS_HI, 1)
	for py in [3 * _TS - 4, 9 * _TS - 4]:               # newel posts
		_r(px + 10, py, 12, 8, _BAR_WOOD)
		_outline(px + 10, py, 12, 8, _BAR_DK, 1)


# ── Banquettes ───────────────────────────────────────────────────────────────

func _banquette(x, y, w, h, base, dark, hi) -> void:
	_r(x, y, w, h, dark)
	_r(x + 3, y + 2, w - 6, h - 4, base)
	_r(x + 3, y + 2, w - 6, 3, hi)
	var a := 10
	while a < h - 6:                                    # buttoning
		_circ(x + w / 2, y + a, 1, dark)
		a += 16


func _draw_banquettes() -> void:
	_banquette(_TS, 3 * _TS, _TS, 10 * _TS, _GREEN, _GREEN_DK, _GREEN_HI)
	_banquette(18 * _TS, 3 * _TS, _TS, 10 * _TS, _MUST, _MUST_DK, _MUST_HI)


# ── Furniture sprites: poseur table, dining table, bentwood chair ────────────

func _chair(cx, cy, face) -> void:
	_circ(cx, cy + 2, 8, _SHADOW)
	_circ(cx, cy, 8, _CHAIR_DK)
	_circ(cx, cy, 7, _CHAIR)
	_circ(cx, cy, 5, _SEAT)
	_circ_o(cx, cy, 5, _dk(_SEAT), 1)
	var a: Array = _CHAIR_ARCS[face]
	draw_arc(Vector2(cx + a[2] + 9, cy + a[3] + 9), 9, -a[1], -a[0], 12, _CHAIR_DK, 3)


func _draw_dining(positions: Array, faces: Array) -> void:
	var off := {"up": [0, -16], "down": [0, 16], "left": [-16, 0], "right": [16, 0]}
	var flip := {"up": "down", "down": "up", "left": "right", "right": "left"}
	for p in positions:
		var cx: int = p[0] * _TS + _TS / 2
		var cy: int = p[1] * _TS + _TS / 2
		for f in faces:
			_chair(cx + off[f][0], cy + off[f][1], flip[f])
		_ellipse(cx - 13, cy - 9, 26, 22, _SHADOW)
		_circ(cx, cy, 13, _TABLE_DK)
		_circ(cx, cy, 12, _TABLE)
		_circ_o(cx - 3, cy - 3, 8, _TABLE_HI, 1)
		_r(cx - 4, cy - 4, 8, 8, _CADDY)               # condiment caddy
		_r(cx - 2, cy - 3, 2, 4, _BOTTLE_R)


func _draw_high_tables(positions: Array) -> void:
	for p in positions:
		var cx: int = p[0] * _TS + _TS / 2
		var cy: int = p[1] * _TS + _TS / 2
		for o in [[-14, 0], [14, 0], [0, 14]]:          # tall stools
			_circ(cx + o[0], cy + o[1], 6, _STOOL)
			_circ(cx + o[0], cy + o[1], 4, _STOOL_TOP)
		_circ(cx, cy + 3, 11, _SHADOW)
		_circ(cx, cy, 4, _STOOL)                        # pedestal
		_circ(cx, cy, 10, _POSEUR)                      # tall round top
		_circ_o(cx, cy, 10, _dk(_POSEUR, 14), 1)
		_circ(cx - 3, cy - 3, 3, _BAR_HI)


# ── Fireplace, doors, lighting ───────────────────────────────────────────────

func _draw_fireplace() -> void:
	var fx := 14 * _TS
	var fy := 2 * _TS - 10
	var fw := 3 * _TS
	var fh := _TS + 8
	_r(fx - 4, fy - 4, fw + 8, fh + 4, _BAR_WOOD)
	_r(fx - 4, fy - 4, fw + 8, 5, _BAR_DK)
	_r(fx + 6, fy + 4, fw - 12, fh - 6, _HEARTH)
	for i in range(5):
		var gx: int = fx + 14 + i * ((fw - 28) / 4)
		_poly([Vector2(gx, fy + fh - 4), Vector2(gx - 5, fy + 12), Vector2(gx + 5, fy + 12)], _FIRE_DK)
		_poly([Vector2(gx, fy + fh - 6), Vector2(gx - 3, fy + 16), Vector2(gx + 3, fy + 16)], _FIRE)
	_r(fx + fw / 2 - 14, fy - 2, 28, 10, _FRAME)
	_r(fx + fw / 2 - 11, fy, 22, 6, _MIRROR)


func _draw_doors() -> void:
	var dxs := [9 * _TS, 10 * _TS]
	for i in range(dxs.size()):
		var dx: int = dxs[i]
		_r(dx, 14 * _TS, _TS, _TS, _PANEL_DK)
		_r(dx + 2, 14 * _TS + 2, _TS - 4, _TS - 4, _BAR_WOOD)
		_r(dx + 6, 14 * _TS + 5, _TS - 12, _TS / 2 + 2, _GLASS)
		_ln(dx + 8, 14 * _TS + 7, dx + 8, 14 * _TS + _TS / 2 + 3, _GLASS_HI, 2)
		var hx: int = dx + (_TS - 5 if i == 0 else 3)
		_r(hx, 14 * _TS + _TS / 2, 2, 9, _BRASS)


func _pendant(lx, ly) -> void:
	_ln(lx, ly - 22, lx, ly - 6, _FITTING, 1)
	_circ(lx, ly, 5, _LIGHT)
	_circ_o(lx, ly, 8, _FITTING, 1)


func _draw_lights() -> void:
	for lx in [4 * _TS, 7 * _TS]:
		_pendant(lx, 5 * _TS)
		_pendant(lx, 9 * _TS)
	_pendant(14 * _TS, 6 * _TS)
	_pendant(16 * _TS, 10 * _TS)
	var cx := 6 * _TS                                   # ceiling rose
	var cy := 12 * _TS
	_circ_o(cx, cy, 14, _PANEL_LT, 2)
	_circ(cx, cy, 4, _LIGHT)
