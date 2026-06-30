# A simple modal menu — a centred bordered panel with a title and a vertical list
# of options (up/down to move, a red '>' cursor, Z to pick). Reused for the title
# screen and the pause menu. Lives in its own CanvasLayer so 2D lighting can't dim it.
class_name Menu
extends Control

var _BG := Color8(0, 0, 0)
var _BORDER := Color8(255, 255, 255)
var _TEXT := Color8(235, 235, 235)
var _SEL := Color8(255, 80, 80)
var _TITLE := Color8(255, 210, 80)

var title := ""
var subtitle := ""
var options: Array = []
var on_select := Callable()
var index := 0
var _font: Font


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
	draw_rect(Rect2(0, 0, sw, sh), Color(0, 0, 0, 0.62))   # dim the world behind

	var maxw := _font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, 24).x
	if subtitle != "":
		maxw = maxf(maxw, _font.get_string_size(subtitle, HORIZONTAL_ALIGNMENT_LEFT, -1, 14).x)
	for opt in options:
		maxw = maxf(maxw, _font.get_string_size("> " + str(opt), HORIZONTAL_ALIGNMENT_LEFT, -1, 18).x)
	var pw := int(maxf(300.0, maxw + 72.0))   # 44px left inset + right padding
	var ph := 64 + options.size() * 30 + (26 if subtitle != "" else 0)
	var px := (sw - pw) / 2.0
	var py := (sh - ph) / 2.0
	draw_rect(Rect2(px, py, pw, ph), _BG)
	draw_rect(Rect2(px, py, pw, ph), _BORDER, false, 3.0)

	draw_string(_font, Vector2(px + 16, py + 32), title, HORIZONTAL_ALIGNMENT_CENTER, pw - 32, 24, _TITLE)
	var oy := py + 60
	if subtitle != "":
		draw_string(_font, Vector2(px + 16, oy), subtitle, HORIZONTAL_ALIGNMENT_CENTER, pw - 32, 14, _TEXT)
		oy += 26
	for i in range(options.size()):
		var col := _SEL if i == index else _TEXT
		var prefix := "> " if i == index else "   "
		draw_string(_font, Vector2(px + 44, oy + 16), prefix + str(options[i]),
			HORIZONTAL_ALIGNMENT_LEFT, pw - 64, 18, col)
		oy += 30
