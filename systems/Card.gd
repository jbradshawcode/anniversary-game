# Full-screen story cards: the end-of-week star results, the between-chapters
# chapter/interlude title cards, and the closing "The End" card. One Control hosted
# on a CanvasLayer above the overworld (like Phone); Z confirms, running on_confirm.
# Port of systems/screens.py — draw_results/Results, draw_chapter_card,
# draw_interlude_card, draw_the_end — over the shared title_backdrop look.
class_name Card
extends Control

enum Kind { RESULTS, CHAPTER, INTERLUDE, THE_END }

const _BG_TOP := Color8(24, 26, 51)            # dusk indigo (title_backdrop gradient)
const _BG_BOT := Color8(46, 26, 49)            # ...to plum
const _INK := Color8(236, 233, 244)
const _MUTED := Color8(151, 150, 172)
const _RULE := Color8(150, 154, 162)
const _SHADOW := Color8(0, 0, 0)
const _STAR_GOLD := Color8(245, 196, 70)
const _STAR_DARK := Color8(70, 64, 92)
const _STAR_GOLD_EDGE := Color8(255, 255, 255)
const _STAR_DARK_EDGE := Color8(110, 104, 132)

var kind := Kind.RESULTS
var on_confirm := Callable()
var loaded := false                            # THE_END: a completed-save prompt vs. the finale

# Per-kind params.
var _title := "Week Complete"
var _stars := 5
var _attempts := 1
var _completed := 0
var _starting := 0
var _kicker := ""
var _name := ""
var _date := ""

var _body: SystemFont
var _disp: SystemFont
var _disp_b: SystemFont


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_body = _mk(["Avenir Next", "Avenir", "Helvetica Neue", "Arial"], 400)
	_disp = _mk(["Futura", "Gill Sans", "Avenir Next", "Trebuchet MS", "Arial"], 400)
	_disp_b = _mk(["Futura", "Gill Sans", "Avenir Next", "Trebuchet MS", "Arial"], 700)


func _mk(names: Array, weight: int) -> SystemFont:
	var f := SystemFont.new()
	f.font_names = PackedStringArray(names)
	f.font_weight = weight
	f.allow_system_fallback = true
	return f


func setup_results(stars: int, attempts: int, title := "Week Complete") -> void:
	kind = Kind.RESULTS
	_stars = clampi(stars, 1, 5)
	_attempts = attempts
	_title = title


func setup_chapter(completed: int, starting: int) -> void:
	kind = Kind.CHAPTER
	_completed = completed
	_starting = starting


func setup_interlude(kicker: String, name: String, date := "") -> void:
	kind = Kind.INTERLUDE
	_kicker = kicker
	_name = name
	_date = date


func setup_the_end(is_loaded := false) -> void:
	kind = Kind.THE_END
	loaded = is_loaded


func confirm() -> void:
	if on_confirm.is_valid():
		on_confirm.call()


# ── drawing ──────────────────────────────────────────────────────────────────────
func _draw() -> void:
	_backdrop()
	var cx := Config.SCREEN_WIDTH / 2.0
	var sh := Config.SCREEN_HEIGHT
	match kind:
		Kind.RESULTS:
			_draw_results(cx, sh)
		Kind.CHAPTER:
			_draw_chapter(cx, sh)
		Kind.INTERLUDE:
			_draw_interlude(cx, sh)
		Kind.THE_END:
			_draw_the_end(cx, sh)


func _draw_results(cx: float, sh: int) -> void:
	_ctext(_title, cx, 70, 40, _disp_b, _INK, true)
	var gap := 78.0
	var r := 30.0
	var x0 := cx - 2 * gap
	for i in range(5):
		_draw_star(Vector2(x0 + i * gap, 200), r, i < _stars)
	var tries := "1 try" if _attempts == 1 else "%d tries" % _attempts
	_ctext("Volleyball won in %s" % tries, cx, 268, 18, _body, _INK)
	_ctext("Z to continue", cx, sh - 56, 15, _body, _MUTED)


func _draw_chapter(cx: float, sh: int) -> void:
	_ctext("CHAPTER %d COMPLETE" % _completed, cx, 150, 20, _body, _RULE)
	_ctext("Chapter %d" % _starting, cx, 188, 46, _disp_b, _INK, true)
	draw_rect(Rect2(cx - 40, 252, 80, 2), _RULE)
	_ctext("Z to continue", cx, sh - 56, 15, _body, _MUTED)


func _draw_interlude(cx: float, sh: int) -> void:
	_ctext(_kicker.to_upper(), cx, 150, 20, _body, _RULE)
	_ctext(_name, cx, 184, 46, _disp_b, _INK, true)
	draw_rect(Rect2(cx - 40, 250, 80, 2), _RULE)
	if _date != "":
		_ctext(_date, cx, 268, 16, _body, _RULE)
	_ctext("Z to read", cx, sh - 56, 15, _body, _MUTED)


func _draw_the_end(cx: float, sh: int) -> void:
	if loaded:
		_ctext("Complete", cx, 140, 46, _disp_b, _INK, true)
		_ctext("This save completed the game.", cx, 214, 18, _body, _INK)
		_ctext("Would you like to start from the beginning?", cx, 244, 18, _body, _INK)
		_ctext("Z — start over     X — back", cx, sh - 56, 15, _body, _MUTED)
	else:
		_ctext("The End", cx, 150, 50, _disp_b, _INK, true)
		var ded: Array = Config.END_DEDICATION
		for i in range(ded.size()):
			_ctext(ded[i], cx, 232 + i * 30, 18, _body, _INK)
		_ctext("Z — play again from the beginning", cx, sh - 56, 15, _body, _MUTED)


# Centred text with TOP at y_top (matches menu.text's top-anchored y), optional shadow.
func _ctext(s: String, cx: float, y_top: float, size: int, font: SystemFont, col: Color,
		shadow := false) -> void:
	var w := font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var x := cx - w / 2.0
	var base := y_top + font.get_ascent(size)
	if shadow:
		draw_string(font, Vector2(x + 2, base + 2), s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, _SHADOW)
	draw_string(font, Vector2(x, base), s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


# A five-pointed star; gold when earned, slate when not (screens._draw_star).
func _draw_star(c: Vector2, r: float, filled: bool) -> void:
	var pts := PackedVector2Array()
	for i in range(10):
		var ang := -PI / 2 + i * PI / 5
		var rad := r if i % 2 == 0 else r * 0.42
		pts.append(c + Vector2(cos(ang), sin(ang)) * rad)
	draw_colored_polygon(pts, _STAR_GOLD if filled else _STAR_DARK)
	var loop := pts.duplicate()
	loop.append(pts[0])
	draw_polyline(loop, _STAR_GOLD_EDGE if filled else _STAR_DARK_EDGE, 2.0)


# The shared title_backdrop: a vertical indigo->plum gradient plus two faint
# volleyball watermarks (top-right large, lower-left small).
func _backdrop() -> void:
	var sw := Config.SCREEN_WIDTH
	var sh := Config.SCREEN_HEIGHT
	for y in range(sh):
		draw_rect(Rect2(0, y, sw, 1), _BG_TOP.lerp(_BG_BOT, float(y) / float(sh - 1)))
	_ball(sw - 70, 70, 96, 16)
	_ball(60, sh - 40, 60, 12)


func _ball(cx: float, cy: float, r: float, alpha: int) -> void:
	var a := alpha / 255.0
	var fill := Color(1, 1, 1, a)
	var edge := Color(1, 1, 1, minf(1.0, a + 40.0 / 255.0))
	var seam := Color(1, 1, 1, minf(1.0, a + 30.0 / 255.0))
	var c := Vector2(cx, cy)
	draw_circle(c, r, fill)
	draw_arc(c, r, 0, TAU, 32, edge, 2.0)
	for bb in [[-0.48, 0.42], [0.0, -0.42], [0.48, 0.42]]:
		var base: float = bb[0]
		var bow: float = bb[1]
		var pts := PackedVector2Array()
		for j in range(17):
			var v := j / 16.0
			var x := base * r * 0.82 + bow * r * sin(PI * v)
			var yy := (v * 2 - 1) * r * 0.92
			pts.append(c + Vector2(x, yy))
		draw_polyline(pts, seam, 2.0)
