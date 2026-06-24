# Undertale-style typewriter dialogue box. Scoped port of systems/dialogue.py:
# bottom panel, speaker name tag, char-by-char reveal, X to speed/skip, Z to advance.
# (Choices + portrait busts are deferred — the original supports both.)
# Lives in a CanvasLayer so the world's 2D lighting never dims the UI.
class_name DialogueBox
extends Control

var _BG := Color8(0, 0, 0)
var _BORDER := Color8(255, 255, 255)
var _TEXT := Color8(255, 255, 255)
var _NAME := Color8(255, 210, 80)

const _MARGIN := 16
const _BOX_H := 96
const _BORDER_W := 3
const _PAD := 16
const _FONT_SIZE := 16

var active := false
var _pages: Array = []
var _index := 0
var _speaker := ""
var _full := ""
var _shown := 0.0
var _typing := false
var _font: Font
var _on_done := Callable()  # invoked when the last page closes (cutscene advance)


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_font = ThemeDB.fallback_font
	visible = false


func start(pages: Array, speaker := "", on_done := Callable()) -> void:
	_pages = pages.duplicate()
	_index = 0
	_speaker = speaker
	_on_done = on_done
	active = true
	visible = true
	_begin_page()


func _begin_page() -> void:
	if _index >= _pages.size():
		active = false
		visible = false
		queue_redraw()
		var cb := _on_done
		_on_done = Callable()
		if cb.is_valid():
			cb.call()
		return
	_full = str(_pages[_index])
	_shown = 0.0
	_typing = _full.length() > 0
	queue_redraw()


func advance() -> void:
	if _typing:  # confirm waits for the line; only cancel (X) rushes it
		return
	_index += 1
	_begin_page()


func skip() -> void:
	if _typing:
		_shown = float(_full.length())
		_typing = false
		queue_redraw()


func _process(delta: float) -> void:
	if not active or not _typing:
		return
	var fast := Input.is_key_pressed(KEY_X)
	var cps: float = Config.DIALOGUE_CPS * (Config.DIALOGUE_FAST if fast else 1.0)
	_shown += cps * delta
	if _shown >= _full.length():
		_shown = float(_full.length())
		_typing = false
	queue_redraw()


func _draw() -> void:
	if not active:
		return
	var sw := Config.SCREEN_WIDTH
	var sh := Config.SCREEN_HEIGHT
	var box := Rect2(_MARGIN, sh - _BOX_H - _MARGIN, sw - _MARGIN * 2, _BOX_H)
	draw_rect(box, _BG)
	draw_rect(box, _BORDER, false, _BORDER_W)

	if _speaker != "":
		var ns := _font.get_string_size(_speaker, HORIZONTAL_ALIGNMENT_LEFT, -1, _FONT_SIZE)
		var tag := Rect2(box.position.x + 18, box.position.y - 26, ns.x + 24, 24)
		draw_rect(tag, _BG)
		draw_rect(tag, _BORDER, false, _BORDER_W)
		draw_string(_font, Vector2(tag.position.x + 12, tag.position.y + 17),
			_speaker, HORIZONTAL_ALIGNMENT_LEFT, -1, _FONT_SIZE, _NAME)

	var shown_text := _full.substr(0, int(_shown))
	var tx := box.position.x + _PAD
	var ty := box.position.y + _PAD + _font.get_ascent(_FONT_SIZE)
	var tw := box.size.x - _PAD * 2
	draw_multiline_string(_font, Vector2(tx, ty), "* " + shown_text,
		HORIZONTAL_ALIGNMENT_LEFT, tw, _FONT_SIZE, -1, _TEXT)
