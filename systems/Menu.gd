# Modal menu, styled after the pygame systems/menu.py: a full title screen (gradient
# backdrop + faint volleyball watermarks + big hero title) or a dimmed pause/sub-screen,
# with centred options and a rounded accent pill behind the selection. Driven by
# MenuFlow; lives in its own CanvasLayer so the world's 2D lighting can't dim it.
class_name Menu
extends Control

const _BG_TOP := Color8(24, 26, 51)
const _BG_BOT := Color8(46, 26, 49)
const _INK := Color8(236, 233, 244)
const _MUTED := Color8(151, 150, 172)
const _ACCENT := Color8(244, 179, 80)
const _SEL_TEXT := Color8(30, 24, 14)
const _DIM := Color(12.0 / 255, 12.0 / 255, 22.0 / 255, 165.0 / 255)

var title := ""
var subtitle := ""              # the bottom hint line ("" = none)
var options: Array = []
var on_select := Callable()
var index := 0
var backdrop := "dim"           # "gradient" (title screen) or "dim" (overlay the world)
var hero := false               # draw the big hero title vs. a smaller header
var _font: Font
var _grad: Texture2D


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_font = ThemeDB.fallback_font
	visible = false


func open(t: String, opts: Array, cb: Callable, sub := "") -> void:
	title = t
	options = opts
	on_select = cb
	subtitle = sub
	index = 0
	visible = true
	queue_redraw()


func close() -> void:
	visible = false
	queue_redraw()


func is_open() -> bool:
	return visible


func move(delta: int) -> void:
	if options.is_empty():
		return
	index = wrapi(index + delta, 0, options.size())
	queue_redraw()


func select() -> void:
	if on_select.is_valid():
		on_select.call(index)


func _draw() -> void:
	if not visible:
		return
	var sw := Config.SCREEN_WIDTH
	var sh := Config.SCREEN_HEIGHT
	var cx := sw / 2.0

	if backdrop == "gradient":
		draw_texture_rect(_grad_tex(), Rect2(0, 0, sw, sh), false)
		_ball(sw - 70, 70, 96, 16)                  # large faint ball, top-right
		_ball(60, sh - 40, 60, 12)                  # small one, lower-left
	else:
		draw_rect(Rect2(0, 0, sw, sh), _DIM)        # dim the world behind

	var start_y: float
	if hero:
		_ctext("The Story of Us", cx, 92, 50, _INK, true)
		draw_line(Vector2(cx - 130, 162), Vector2(cx + 130, 162), _ACCENT, 3.0)
		start_y = 248.0
	else:
		_ctext(title, cx, 84, 38, _INK, true)
		start_y = 188.0

	var oy := start_y
	for i in range(options.size()):
		_option(str(options[i]), cx, oy, i == index, 24)
		oy += 46.0

	if subtitle != "":
		_ctext(subtitle, cx, sh - 34, 14, _MUTED)


# A faint volleyball watermark — circle plus three curved seams (port of menu._ball).
func _ball(cx: float, cy: float, r: float, alpha: int) -> void:
	draw_circle(Vector2(cx, cy), r, Color(1, 1, 1, alpha / 255.0))
	draw_arc(Vector2(cx, cy), r, 0, TAU, 48, Color(1, 1, 1, minf(1.0, (alpha + 40) / 255.0)), 2.0)
	var seam := Color(1, 1, 1, minf(1.0, (alpha + 30) / 255.0))
	for s in [[-0.48, 0.42], [0.0, -0.42], [0.48, 0.42]]:
		var pts := PackedVector2Array()
		for j in range(17):
			var v := j / 16.0                       # 0 (top) .. 1 (bottom)
			var x: float = s[0] * r * 0.82 + s[1] * r * sin(PI * v)
			var y := (v * 2.0 - 1.0) * r * 0.92
			pts.append(Vector2(cx + x, cy + y))
		draw_polyline(pts, seam, 2.0)


# One option row: a rounded accent pill behind the selection, then centred text.
func _option(s: String, cx: float, top_y: float, selected: bool, size: int) -> void:
	var ts := _font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size)
	if selected:
		var bh := size + 18.0
		var bw := ts.x + 52.0
		var mid := top_y + ts.y / 2.0
		var r := bh / 2.0
		draw_rect(Rect2(cx - bw / 2.0 + r, mid - r, bw - 2.0 * r, bh), _ACCENT)
		draw_circle(Vector2(cx - bw / 2.0 + r, mid), r, _ACCENT)
		draw_circle(Vector2(cx + bw / 2.0 - r, mid), r, _ACCENT)
	_ctext(s, cx, top_y, size, _SEL_TEXT if selected else _INK)


# Centred text with an optional drop shadow; top_y is the top of the glyph box.
func _ctext(s: String, cx: float, top_y: float, size: int, col: Color, shadow := false) -> void:
	var w := _font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var x := cx - w / 2.0
	var base := top_y + _font.get_ascent(size)
	if shadow:
		draw_string(_font, Vector2(x + 2, base + 2), s, HORIZONTAL_ALIGNMENT_LEFT, -1, size,
			Color(0, 0, 0, 0.6))
	draw_string(_font, Vector2(x, base), s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


func _grad_tex() -> Texture2D:
	if _grad == null:
		var g := Gradient.new()
		g.set_color(0, _BG_TOP)
		g.set_color(1, _BG_BOT)
		var gt := GradientTexture2D.new()
		gt.gradient = g
		gt.width = 8
		gt.height = 256
		gt.fill_from = Vector2(0, 0)
		gt.fill_to = Vector2(0, 1)                   # vertical top->bottom
		_grad = gt
	return _grad
