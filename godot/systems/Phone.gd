# A scrolling iMessage-style text thread, revealed one bubble per confirm (Z).
# Port of systems/screens.py::Phone. Bubble kinds (dicts in the thread array):
#   {"who": "James"|"Dan"|..., "text": str}            plain bubble (right if "me")
#   {"sep": str}                                       centred date pill
#   {..., "react": "❤"}                                reaction badge on the bubble
#   {..., "notif": {"app","title","body"}}             notification card
#   {..., "shot": [[sender,line],...], "caption": str} screenshot-of-a-chat bubble
# Emoji render natively via a system font fallback (the pygame build hand-drew vector
# glyphs only because SDL couldn't render colour emoji — Godot can, so we don't).
class_name Phone
extends Control

const _BG := Color(0.024, 0.027, 0.039)        # (6,7,10) backdrop behind the shell
const _PHONE_BG := Color8(18, 20, 28)
const _SHELL_EDGE := Color8(60, 64, 78)
const _HEADER := Color8(30, 32, 42)
const _BUB_ME := Color8(58, 122, 246)          # right-aligned (the "me" side)
const _BUB_THEM := Color8(58, 60, 70)          # left-aligned (the other person)
const _BUB_TEXT := Color8(240, 242, 248)
const _SEP_BG := Color8(40, 42, 52)
const _SEP_TEXT := Color8(150, 154, 162)
const _NOTIF_BG := Color8(244, 246, 250)
const _NOTIF_EDGE := Color8(210, 214, 222)
const _SHOT_BG := Color8(236, 238, 242)
const _SHOT_EDGE := Color8(200, 204, 210)
const _SHOT_ME := Color8(52, 199, 89)
const _SHOT_THEM := Color8(228, 230, 234)
const _MUTED := Color8(150, 154, 162)

const _F := 15      # body
const _S := 12      # small (date pills, notif body, screenshot text)
const _T := 16      # header title

var _thread: Array = []
var _me := "James"
var _other := "Dan"
var shown := 1

var _font: SystemFont
var _bold: SystemFont
var _area: _ThreadArea


# The clipped scroll viewport: its own canvas item so older bubbles slide up under
# the header instead of over it (clip_contents masks them to the area rect).
class _ThreadArea extends Control:
	var phone: Phone
	func _draw() -> void:
		phone._draw_messages(self)


func setup(thread: Array, other := "", me := "James") -> void:
	_thread = thread
	_me = me
	_other = other if other != "" else ("Dan" if me == "James" else "James")
	shown = 1


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_font = _make_font(400)
	_bold = _make_font(700)
	var pw := 360
	var ph := Config.SCREEN_HEIGHT - 24
	var px := (Config.SCREEN_WIDTH - pw) / 2
	_area = _ThreadArea.new()
	_area.phone = self
	_area.clip_contents = true
	_area.position = Vector2(px, 12 + 48)
	_area.size = Vector2(pw, ph - 48)
	_area.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_area)


func _make_font(weight: int) -> SystemFont:
	var f := SystemFont.new()
	f.font_names = PackedStringArray(["Helvetica Neue", "Arial", "Sans-Serif"])
	f.font_weight = weight
	f.allow_system_fallback = true   # falls back to Apple Color Emoji for emoji glyphs
	return f


func done() -> bool:
	return shown >= _thread.size()


# Reveal the next bubble; returns false once the whole thread is shown.
func advance() -> bool:
	if shown < _thread.size():
		shown += 1
		queue_redraw()
		_area.queue_redraw()
		return true
	return false


# ── width / text helpers ────────────────────────────────────────────────────────
func _tw(s: String, size: int) -> float:
	return _font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x


func _text(ci: CanvasItem, s: String, x: float, y_top: float, size: int, col: Color,
		font: SystemFont = null) -> void:
	var f: SystemFont = font if font != null else _font
	ci.draw_string(f, Vector2(x, y_top + f.get_ascent(size)), s,
		HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


func _round(ci: CanvasItem, rect: Rect2, col: Color, radius: int) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = col
	sb.set_corner_radius_all(radius)
	ci.draw_style_box(sb, rect)


func _outline(ci: CanvasItem, rect: Rect2, col: Color, radius: int, width: int) -> void:
	var sb := StyleBoxFlat.new()
	sb.draw_center = false
	sb.set_corner_radius_all(radius)
	sb.set_border_width_all(width)
	sb.border_color = col
	ci.draw_style_box(sb, rect)


func _wrap(text: String, size: int, max_w: float) -> Array:
	var out: Array = []
	var line := ""
	for word in text.split(" "):
		var trial := word if line == "" else line + " " + word
		if _tw(trial, size) <= max_w or line == "":
			line = trial
		else:
			out.append(line)
			line = word
	if line != "":
		out.append(line)
	return out


# ── the shell (header + footer), drawn unclipped behind the scroll area ──────────
func _draw() -> void:
	var sw := Config.SCREEN_WIDTH
	var sh := Config.SCREEN_HEIGHT
	draw_rect(Rect2(0, 0, sw, sh), _BG)
	var pw := 360
	var ph := sh - 24
	var px := (sw - pw) / 2
	var py := 12
	_round(self, Rect2(px, py, pw, ph), _PHONE_BG, 26)
	_outline(self, Rect2(px, py, pw, ph), _SHELL_EDGE, 26, 2)
	_round(self, Rect2(px, py, pw, 46), _HEADER, 26)
	var tw := _bold.get_string_size(_other, HORIZONTAL_ALIGNMENT_LEFT, -1, _T).x
	_text(self, _other, px + pw / 2.0 - tw / 2.0, py + 12, _T, _BUB_TEXT, _bold)
	draw_string(_font, Vector2(0, sh - 14 + _font.get_ascent(_S)), "Z to continue",
		HORIZONTAL_ALIGNMENT_CENTER, sw, _S, _MUTED)


# Messages laid bottom-up in the clipped area so the newest sits near the bottom and
# older ones scroll up under the header. Drawn in area-local coords (origin px, py+48).
func _draw_messages(area: CanvasItem) -> void:
	var pw := 360
	var ph := Config.SCREEN_HEIGHT - 24
	var inner_w := pw - 28
	var blocks: Array = []
	var total_h := 0.0
	for i in range(min(shown, _thread.size())):
		var b := _measure(_thread[i], inner_w)
		blocks.append(b)
		total_h += b["h"] + 12
	var y := (ph - 48) - 20 - total_h     # bottom-anchored within the area
	for b in blocks:
		b["draw"].call(area, 14.0, y, float(inner_w))
		y += b["h"] + 12


# Each _measure returns {h: float, draw: Callable(ci, x, y, w)}.
func _measure(m: Dictionary, w: int) -> Dictionary:
	if m.has("sep"):
		return _measure_sep(m, w)
	var mine: bool = m.get("who", "") == _me
	if m.has("shot"):
		return _measure_shot(m, w, mine)
	if m.has("notif"):
		return _measure_notif(m, w, mine)
	return _measure_text(m, w, mine)


func _measure_sep(m: Dictionary, _w: int) -> Dictionary:
	var label: String = m["sep"]
	var bw := _tw(label, _S) + 18
	var draw := func(ci: CanvasItem, x: float, y: float, ww: float) -> void:
		var bx := x + (ww - bw) / 2.0
		_round(ci, Rect2(bx, y, bw, 20), _SEP_BG, 10)
		_text(ci, label, bx + 9, y + 4, _S, _SEP_TEXT)
	return {"h": 20.0, "draw": draw}


func _measure_text(m: Dictionary, w: int, mine: bool) -> Dictionary:
	# Pre-formatted messages (their own \n line breaks, e.g. the emoji meme) take the
	# full bubble width and are centred; plain ones wrap at 66% and are left-padded.
	var preformatted: bool = "\n" in m["text"]
	var cap: float = (w - 24) if preformatted else int(w * 0.66)
	var lines: Array = []
	for seg in String(m["text"]).split("\n"):
		if seg == "":
			lines.append("")
		else:
			lines.append_array(_wrap(seg, _F, cap))
	var maxw := 0.0
	for ln in lines:
		maxw = maxf(maxw, _tw(ln, _F))
	var bw := maxw + 22
	var bh := lines.size() * 20 + 14
	var react: String = m.get("react", "")
	var draw := func(ci: CanvasItem, x: float, y: float, ww: float) -> void:
		var bx := (x + ww - bw) if mine else x
		var rect := Rect2(bx, y, bw, bh)
		_round(ci, rect, _BUB_ME if mine else _BUB_THEM, 14)
		for i in range(lines.size()):
			var ln: String = lines[i]
			var lx := (bx + (bw - _tw(ln, _F)) / 2.0) if preformatted else (bx + 11)
			_text(ci, ln, lx, y + 7 + i * 20, _F, _BUB_TEXT)
		if react != "":
			_reaction(ci, rect, react)
	return {"h": bh + (10.0 if react != "" else 0.0), "draw": draw}


func _measure_notif(m: Dictionary, w: int, _mine: bool) -> Dictionary:
	var n: Dictionary = m["notif"]
	var body_lines := _wrap(n["body"], _S, int(w * 0.74))
	var bw := int(w * 0.82)
	var bh := 30 + body_lines.size() * 16 + 12
	var draw := func(ci: CanvasItem, x: float, y: float, ww: float) -> void:
		var bx := x + (ww - bw) / 2.0
		var rect := Rect2(bx, y, bw, bh)
		_round(ci, rect, _NOTIF_BG, 14)
		_outline(ci, rect, _NOTIF_EDGE, 14, 1)
		_text(ci, n["app"], bx + 12, y + 7, _S, Color8(120, 124, 132))
		_text(ci, n["title"], bx + 12, y + 22, 13, Color8(20, 22, 28), _bold)
		for i in range(body_lines.size()):
			_text(ci, body_lines[i], bx + 12, y + 40 + i * 16, _S, Color8(60, 64, 72))
	return {"h": float(bh), "draw": draw}


func _measure_shot(m: Dictionary, w: int, mine: bool) -> Dictionary:
	var shot: Array = m["shot"]
	var caption: String = m.get("caption", "")
	var me_side: String = m.get("shot_me", "James")
	var bw := int(w * 0.8)
	var inner := bw - 20
	var name_h := _font.get_height(_S) - 1
	var rows: Array = []
	var prev := ""
	for pair in shot:
		var sender: String = pair[0]
		var wl := _wrap(pair[1], _S, int(inner * 0.7))
		var named: bool = sender != me_side and sender != prev   # label each 'them' group
		rows.append([sender, wl, named])
		prev = sender
	var rh := 16.0
	for r in rows:
		rh += r[1].size() * 15 + 12 + (name_h if r[2] else 0.0)
	var cap_h := 18.0 if caption != "" else 0.0
	var bh := rh + cap_h
	var draw := func(ci: CanvasItem, x: float, y: float, ww: float) -> void:
		var bx := (x + ww - bw) if mine else x
		_round(ci, Rect2(bx, y, bw, bh), _SHOT_BG, 12)
		_outline(ci, Rect2(bx, y, bw, bh), _SHOT_EDGE, 12, 1)
		var cy := y + 8
		for r in rows:
			var sender: String = r[0]
			var wl: Array = r[1]
			var smine: bool = sender == me_side
			if r[2]:
				_text(ci, sender, bx + 12, cy, _S, Color8(120, 124, 132))
				cy += name_h
			var tw := 0.0
			for ln in wl:
				tw = maxf(tw, _tw(ln, _S))
			tw += 14
			var th := wl.size() * 15 + 8
			var sx := (bx + bw - 10 - tw) if smine else (bx + 10)
			_round(ci, Rect2(sx, cy, tw, th), _SHOT_ME if smine else _SHOT_THEM, 9)
			var tc := Color8(255, 255, 255) if smine else Color8(28, 30, 36)
			for i in range(wl.size()):
				_text(ci, wl[i], sx + 7, cy + 4 + i * 15, _S, tc)
			cy += th + 12
		if caption != "":
			_text(ci, caption, bx + 8, y + bh - 16, _S, Color8(120, 124, 132))
	return {"h": bh, "draw": draw}


# The reaction badge sits at the bubble's bottom-right corner, whoever sent it.
func _reaction(ci: CanvasItem, rect: Rect2, react: String) -> void:
	var pw := _tw(react, _S) + 12
	var bx := rect.position.x + rect.size.x - pw + 8
	var pr := Rect2(bx, rect.position.y + rect.size.y - 9, pw, 18)
	_round(ci, pr, _SEP_BG, 9)
	_text(ci, react, bx + 6, rect.position.y + rect.size.y - 7, _S, Color8(250, 250, 250))
