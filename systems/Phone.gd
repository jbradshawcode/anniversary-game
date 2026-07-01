# A scrolling WhatsApp-style text thread, revealed one bubble per confirm (Z).
# Port of systems/screens.py::Phone, restyled to the WhatsApp dark theme: doodle
# wallpaper, green (outgoing) / grey (incoming) bubbles with tails, a header with a
# back chevron + avatar + name + call icons, per-message timestamps and blue double
# read-ticks on outgoing messages, and centred date pills.
# Bubble kinds (dicts in the thread array):
#   {"who": "James"|"Dan"|..., "text": str}            plain bubble (right if "me")
#   {"sep": str}                                       centred date pill
#   {..., "react": "❤"}                                reaction badge on the bubble
#   {..., "notif": {"app","title","body"}}             notification card
#   {..., "shot": [[sender,line],...], "caption": str} screenshot-of-a-chat bubble
#   {..., "time": "14:58"}                             explicit time (else synthesised)
# Emoji render natively via a system font fallback (Godot renders colour emoji).
class_name Phone
extends Control

# ── WhatsApp dark palette ────────────────────────────────────────────────────────
const _BG := Color(0.0, 0.0, 0.0)              # letterbox behind the shell
const _WALL := Color8(11, 20, 26)              # #0b141a chat wallpaper
const _WALL_DOODLE := Color8(20, 32, 40)       # faint doodle ink over the wallpaper
const _HEADER := Color8(32, 44, 51)            # #202c33 top bar
const _BUB_ME := Color8(0, 92, 75)             # #005c4b outgoing (right)
const _BUB_THEM := Color8(32, 44, 51)          # #202c33 incoming (left)
const _BUB_TEXT := Color8(233, 237, 239)       # #e9edef
const _META := Color8(134, 150, 160)           # #8696a0 timestamps / muted
const _META_ME := Color8(173, 200, 194)        # lighter meta on the green bubble
const _TICK := Color8(83, 189, 235)            # #53bdeb read receipts
const _SEP_BG := Color8(24, 34, 41)            # #182229 date pill
const _SEP_TEXT := Color8(140, 155, 164)
const _AVATAR := Color8(102, 122, 138)
const _ICON := Color8(200, 214, 220)
const _NOTIF_BG := Color8(244, 246, 250)
const _NOTIF_EDGE := Color8(210, 214, 222)
const _SHOT_BG := Color8(236, 238, 242)
const _SHOT_EDGE := Color8(200, 204, 210)
const _SHOT_ME := Color8(0, 92, 75)
const _SHOT_THEM := Color8(228, 230, 234)

const _F := 15      # body
const _S := 12      # small (date pills, notif body, screenshot text)
const _T := 16      # header title
const _M := 10      # timestamp

const _PW := 360    # phone shell width
const _HEAD_H := 54

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
	var ph := Config.SCREEN_HEIGHT - 24
	var px := (Config.SCREEN_WIDTH - _PW) / 2
	_area = _ThreadArea.new()
	_area.phone = self
	_area.clip_contents = true
	_area.position = Vector2(px, 12 + _HEAD_H)
	_area.size = Vector2(_PW, ph - _HEAD_H)
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


# A plausible clock time for message #idx (WhatsApp shows one per bubble). Data may
# override with an explicit "time"; otherwise step a minute per message from a base.
func _time_for(idx: int) -> String:
	var base := 14 * 60 + 52          # 14:52
	var t := base + idx
	return "%02d:%02d" % [(t / 60) % 24, t % 60]


# ── the shell (wallpaper + header + footer), drawn behind the clipped scroll area ──
func _draw() -> void:
	var sw := Config.SCREEN_WIDTH
	var sh := Config.SCREEN_HEIGHT
	draw_rect(Rect2(0, 0, sw, sh), _BG)
	var ph := sh - 24
	var px := (sw - _PW) / 2
	var py := 12

	# Chat wallpaper: dark base + a faint scattered doodle pattern (masked to the shell
	# by a nested clip control so the doodles don't spill past the rounded corners).
	_round(self, Rect2(px, py, _PW, ph), _WALL, 26)
	_draw_header(px, py)
	draw_string(_font, Vector2(0, sh - 14 + _font.get_ascent(_S)), "Z to continue",
		HORIZONTAL_ALIGNMENT_CENTER, sw, _S, _META)


func _draw_header(px: int, py: int) -> void:
	var h := _HEAD_H
	_round(self, Rect2(px, py, _PW, h), _HEADER, 26)
	draw_rect(Rect2(px, py + h - 20, _PW, 20), _HEADER)   # square off the header's bottom
	var cy := py + h / 2.0
	# Back chevron.
	var bx := px + 14.0
	draw_polyline(PackedVector2Array([Vector2(bx + 5, cy - 6), Vector2(bx, cy),
		Vector2(bx + 5, cy + 6)]), _ICON, 2.0)
	# Avatar circle with the contact's initial.
	var ax := px + 40.0
	draw_circle(Vector2(ax, cy), 15, _AVATAR)
	var initial := _other.substr(0, 1).to_upper()
	var iw := _bold.get_string_size(initial, HORIZONTAL_ALIGNMENT_LEFT, -1, 15).x
	_text(self, initial, ax - iw / 2.0, cy - 9, 15, Color8(20, 28, 34), _bold)
	# Contact name + presence line.
	_text(self, _other, px + 64, py + 10, _T, _BUB_TEXT, _bold)
	_text(self, "online", px + 64, py + 30, _S, _META)
	# Video + voice call icons on the right.
	var vx := px + _PW - 40.0
	_outline(self, Rect2(vx, cy - 7, 20, 14), _ICON, 4, 2)
	draw_colored_polygon(PackedVector2Array([Vector2(vx + 20, cy - 4),
		Vector2(vx + 26, cy - 7), Vector2(vx + 26, cy + 7), Vector2(vx + 20, cy + 4)]), _ICON)
	# Voice-call handset: a thick rounded diagonal with an ear/mouth knob at each end.
	var hx := px + _PW - 68.0
	var a := Vector2(hx - 5, cy - 5)
	var b := Vector2(hx + 5, cy + 5)
	draw_line(a, b, _ICON, 4.0)
	draw_circle(a, 2.5, _ICON)
	draw_circle(b, 2.5, _ICON)


# Messages laid bottom-up in the clipped area so the newest sits near the bottom and
# older ones scroll up under the header. Drawn in area-local coords.
func _draw_messages(area: CanvasItem) -> void:
	var ph := Config.SCREEN_HEIGHT - 24
	var inner_w := _PW - 28
	_draw_wallpaper(area, inner_w, ph)
	var blocks: Array = []
	var total_h := 0.0
	var msg_idx := 0
	for i in range(min(shown, _thread.size())):
		var m: Dictionary = _thread[i]
		var b := _measure(m, inner_w, msg_idx)
		if not m.has("sep"):
			msg_idx += 1
		blocks.append(b)
		total_h += b["h"] + 10
	var y := (ph - _HEAD_H) - 16 - total_h    # bottom-anchored within the area
	for b in blocks:
		b["draw"].call(area, 14.0, y, float(inner_w))
		y += b["h"] + 10


# Faint WhatsApp-style doodle pattern over the wallpaper — a scattered set of simple
# outlined glyphs on a fixed lattice so it reads as the printed pattern, not noise.
func _draw_wallpaper(area: CanvasItem, inner_w: int, ph: int) -> void:
	var w := float(inner_w + 28)
	var h := float(ph - _HEAD_H)
	var col := _WALL_DOODLE
	var step := 46.0
	var row := 0
	var y := 8.0
	while y < h:
		var x := 12.0 + (23.0 if row % 2 == 1 else 0.0)
		var k := row
		while x < w - 8:
			match k % 5:
				0:   # heart
					area.draw_circle(Vector2(x - 3, y - 2), 3, col)
					area.draw_circle(Vector2(x + 3, y - 2), 3, col)
					area.draw_colored_polygon(PackedVector2Array([Vector2(x - 6, y - 1),
						Vector2(x + 6, y - 1), Vector2(x, y + 6)]), col)
				1:   # ring
					area.draw_arc(Vector2(x, y), 5, 0, TAU, 16, col, 1.5)
				2:   # star (plus)
					area.draw_line(Vector2(x - 5, y), Vector2(x + 5, y), col, 1.5)
					area.draw_line(Vector2(x, y - 5), Vector2(x, y + 5), col, 1.5)
				3:   # little cup
					area.draw_rect(Rect2(x - 4, y - 3, 8, 7), col)
					area.draw_arc(Vector2(x + 4, y), 3, -PI / 2, PI / 2, 8, col, 1.5)
				4:   # dots
					area.draw_circle(Vector2(x - 3, y - 3), 1.5, col)
					area.draw_circle(Vector2(x + 3, y + 2), 1.5, col)
			x += step
			k += 1
		y += step
		row += 1


# Each _measure returns {h: float, draw: Callable(ci, x, y, w)}.
func _measure(m: Dictionary, w: int, idx: int) -> Dictionary:
	if m.has("sep"):
		return _measure_sep(m, w)
	var mine: bool = m.get("who", "") == _me
	var time: String = m.get("time", _time_for(idx))
	if m.has("shot"):
		return _measure_shot(m, w, mine)
	if m.has("notif"):
		return _measure_notif(m, w, mine)
	return _measure_text(m, w, mine, time)


func _measure_sep(m: Dictionary, _w: int) -> Dictionary:
	var label: String = m["sep"]
	var bw := _tw(label, _S) + 20
	var draw := func(ci: CanvasItem, x: float, y: float, ww: float) -> void:
		var bx := x + (ww - bw) / 2.0
		_round(ci, Rect2(bx, y, bw, 22), _SEP_BG, 8)
		_text(ci, label, bx + 10, y + 5, _S, _SEP_TEXT)
	return {"h": 22.0, "draw": draw}


func _measure_text(m: Dictionary, w: int, mine: bool, time: String) -> Dictionary:
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
	# Meta = "HH:MM" (+ space for read-ticks on my messages). It tucks onto the last
	# line's right if it fits, else drops to its own row bottom-right.
	var meta_w := _tw(time, _M) + (16.0 if mine else 4.0)
	var last_w := _tw(lines[-1], _F) if not lines.is_empty() and not preformatted else 1e9
	var inline: bool = (last_w + 10 + meta_w) <= cap and not preformatted
	var bw: float
	var bh: float
	if inline:
		bw = maxf(maxw, last_w + 10 + meta_w) + 22
		bh = lines.size() * 20 + 14
	else:
		bw = maxf(maxw, meta_w) + 22
		bh = lines.size() * 20 + 14 + 12
	var react: String = m.get("react", "")
	var draw := func(ci: CanvasItem, x: float, y: float, ww: float) -> void:
		var bx := (x + ww - bw) if mine else x
		var rect := Rect2(bx, y, bw, bh)
		_round(ci, rect, _BUB_ME if mine else _BUB_THEM, 12)
		_tail(ci, rect, mine, _BUB_ME if mine else _BUB_THEM)
		for i in range(lines.size()):
			var ln: String = lines[i]
			var lx := (bx + (bw - _tw(ln, _F)) / 2.0) if preformatted else (bx + 11)
			_text(ci, ln, lx, y + 7 + i * 20, _F, _BUB_TEXT)
		_draw_meta(ci, rect, time, mine)
		if react != "":
			_reaction(ci, rect, react)
	return {"h": bh + (16.0 if react != "" else 0.0), "draw": draw}


# Timestamp (+ blue double-tick for my messages) at the bubble's bottom-right.
func _draw_meta(ci: CanvasItem, rect: Rect2, time: String, mine: bool) -> void:
	var tw := _tw(time, _M)
	var meta_col := _META_ME if mine else _META
	var ty := rect.position.y + rect.size.y - 15
	var right := rect.position.x + rect.size.x - 10
	if mine:
		_draw_ticks(ci, right - 13, ty + 5)
		right -= 17
	_text(ci, time, right - tw, ty, _M, meta_col)


# WhatsApp read receipt: two overlapping blue check-marks.
func _draw_ticks(ci: CanvasItem, x: float, y: float) -> void:
	for off in [0.0, 4.0]:
		ci.draw_polyline(PackedVector2Array([Vector2(x + off, y),
			Vector2(x + off + 2.5, y + 3), Vector2(x + off + 7, y - 4)]), _TICK, 1.3)


# A small tail at the bubble's top-outer corner (right for me, left for them).
func _tail(ci: CanvasItem, rect: Rect2, mine: bool, col: Color) -> void:
	var ty := rect.position.y
	if mine:
		var rx := rect.position.x + rect.size.x
		ci.draw_colored_polygon(PackedVector2Array([Vector2(rx - 6, ty),
			Vector2(rx + 5, ty), Vector2(rx - 6, ty + 8)]), col)
	else:
		var lx := rect.position.x
		ci.draw_colored_polygon(PackedVector2Array([Vector2(lx + 6, ty),
			Vector2(lx - 5, ty), Vector2(lx + 6, ty + 8)]), col)


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
			var tc := Color8(233, 237, 239) if smine else Color8(28, 30, 36)
			for i in range(wl.size()):
				_text(ci, wl[i], sx + 7, cy + 4 + i * 15, _S, tc)
			cy += th + 12
		if caption != "":
			_text(ci, caption, bx + 8, y + bh - 16, _S, Color8(120, 124, 132))
	return {"h": bh, "draw": draw}


# The reaction badge hangs off the bubble's bottom-right, below the timestamp so the
# two don't collide (WhatsApp floats reactions on the bubble's lower edge).
func _reaction(ci: CanvasItem, rect: Rect2, react: String) -> void:
	var pw := _tw(react, _S) + 12
	var bx := rect.position.x + rect.size.x - pw + 4
	var pr := Rect2(bx, rect.position.y + rect.size.y - 3, pw, 18)
	_round(ci, pr, _SEP_BG, 9)
	_text(ci, react, bx + 6, rect.position.y + rect.size.y - 1, _S, Color8(250, 250, 250))
