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
var _SEL := Color8(255, 50, 50)

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
var _on_done := Callable()    # invoked when the last page closes (cutscene advance)
var _on_choice := Callable()  # invoked with the selected label on a choice page
var _choosing := false
var _choice_keys: Array = []
var _choice_index := 0


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_font = ThemeDB.fallback_font
	visible = false


func start(pages: Array, speaker := "", on_done := Callable(), on_choice := Callable()) -> void:
	_pages = pages.duplicate()
	_index = 0
	_speaker = speaker
	_on_done = on_done
	_on_choice = on_choice
	active = true
	visible = true
	_begin_page()


func _begin_page() -> void:
	if _index >= _pages.size():
		active = false
		visible = false
		_choosing = false
		queue_redraw()
		var cb := _on_done
		_on_done = Callable()
		if cb.is_valid():
			cb.call()
		return
	var page = _pages[_index]
	if page is Dictionary:                # a choice page: {text, choices: [labels]}
		_full = str(page["text"])
		_choosing = true
		_choice_keys = page["choices"]
		_choice_index = 0
	else:
		_full = str(page)
		_choosing = false
	_shown = 0.0
	_typing = _full.length() > 0
	queue_redraw()


func is_choosing() -> bool:
	return _choosing and not _typing


# The name tag currently showing ("" when idle) — drives the speaker's music theme.
func current_speaker() -> String:
	return _speaker if active else ""


func move_choice(delta: int) -> void:
	if not is_choosing() or delta == 0:
		return
	_choice_index = wrapi(_choice_index + delta, 0, _choice_keys.size())
	queue_redraw()


func advance() -> void:
	if _typing:  # confirm waits for the line; only cancel (X) rushes it
		return
	if _choosing:
		var sel: String = _choice_keys[_choice_index]
		_choosing = false
		if _on_choice.is_valid():
			_on_choice.call(sel)
		_index = _pages.size()    # a choice page is terminal -> finish (fires on_done)
		_begin_page()
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
	var prev := int(_shown)
	_shown += cps * delta
	if _shown >= _full.length():
		_shown = float(_full.length())
		_typing = false
	var now := int(_shown)
	# blip on each fresh (every other, non-space) glyph — but not while fast-forwarding
	if not fast and now > prev and now % 2 == 0 and not _full[now - 1].strip_edges().is_empty():
		Audio.sfx("blip")
	queue_redraw()


func _draw() -> void:
	if not active:
		return
	var sw := Config.SCREEN_WIDTH
	var sh := Config.SCREEN_HEIGHT
	var show_choices := _choosing and not _typing
	var h := _BOX_H
	if show_choices:
		h += _choice_keys.size() * 24
	var box := Rect2(_MARGIN, sh - h - _MARGIN, sw - _MARGIN * 2, h)
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

	if show_choices:
		var cy := box.position.y + _PAD + 24 + _font.get_ascent(_FONT_SIZE)
		for i in range(_choice_keys.size()):
			if i == _choice_index:
				draw_string(_font, Vector2(tx, cy), ">", HORIZONTAL_ALIGNMENT_LEFT, -1, _FONT_SIZE, _SEL)
			draw_string(_font, Vector2(tx + 18, cy), str(_choice_keys[i]),
				HORIZONTAL_ALIGNMENT_LEFT, -1, _FONT_SIZE, _TEXT)
			cy += 24
