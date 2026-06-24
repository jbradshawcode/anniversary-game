# Base for static talkable NPCs — the Godot mirror of entities/humanoid.py +
# the GameObject interaction hooks. Subclasses set the palette + interaction lines
# and override the head art. Shadow + shared body + the seated pose + held/rested
# drinks live here. The seating rule (a drink belongs in hand only between the bar
# and a seat) is owned by sit()/stand()/carry().
class_name Npc
extends Node2D

var tile_x: int
var tile_y: int
var facing := "down"
var display_name := ""
var interaction_text: Array = []

var sitting := false
var holding := ""               # "" or a Drinks.KINDS value
var _drink_off := Vector2(0, 32)

# Body palette (humanoid.py Palette defaults; subclass overrides skin/tee).
var p_skin := Color8(210, 158, 120)
var p_skin_sh := Color8(182, 132, 98)
var p_tee := Color8(52, 56, 64)
var p_tee_sh := Color8(38, 41, 48)
var p_short := Color8(35, 35, 38)
var p_short_sh := Color8(25, 25, 28)
var p_shoe := Color8(65, 42, 28)
var p_sole := Color8(45, 30, 18)


func _init(tx := 0, ty := 0) -> void:
	tile_x = tx
	tile_y = ty


func _ready() -> void:
	var ts := Config.TILE_SIZE
	position = Vector2(tile_x * ts + ts / 2, tile_y * ts + ts / 2)


func interaction_lines() -> Array:
	return interaction_text


# ── seating / drink state (owns the "drink in hand only in transit" rule) ──────
func sit(face := "") -> void:
	sitting = true
	if face != "":
		facing = face
	if holding != "":
		place_drink()
	queue_redraw()


func stand() -> void:
	if sitting:                 # a drink left on the table stays behind
		holding = ""
	sitting = false
	queue_redraw()


func carry(kind: String) -> void:
	holding = kind
	if kind != "" and sitting:
		place_drink()
	queue_redraw()


func place_drink() -> void:
	var off := {"up": Vector2(0, -22), "down": Vector2(0, 32),
		"left": Vector2(-28, 4), "right": Vector2(28, 4)}
	var o: Vector2 = off.get(facing, Vector2(0, 32))
	_drink_off = o + Vector2(randf_range(-3.5, 3.5), randf_range(-2.0, 2.0))


# ── drawing ───────────────────────────────────────────────────────────────────
func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _oval(cx, cy, rx, ry, c) -> void:
	draw_set_transform(Vector2(cx, cy), 0, Vector2(rx, ry))
	draw_circle(Vector2.ZERO, 1.0, c)
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


# pygame.draw.ellipse form: top-left (x,y) + size (w,h), to match the source art.
func _el(x, y, w, h, c) -> void:
	_oval(x + w / 2.0, y + h / 2.0, w / 2.0, h / 2.0, c)


# Outline rect (pygame rect with a width arg) — used for the wire-frame glasses.
func _ro(x, y, w, h, c, width := 1.0) -> void:
	draw_rect(Rect2(x, y, w, h), c, false, width)


# Mirrored draw for the side heads: the source flips x by -(x+w) when `flip`,
# so left/right share one profile (left = flip true, matching humanoid.py).
func _rf(x, y, w, h, c, flip) -> void:
	var x0 = (-(x + w)) if flip else x
	draw_rect(Rect2(x0, y, w, h), c)


func _elf(x, y, w, h, c, flip) -> void:
	var x0 = (-(x + w)) if flip else x
	_oval(x0 + w / 2.0, y + h / 2.0, w / 2.0, h / 2.0, c)


func _rof(x, y, w, h, c, flip, width := 1.0) -> void:
	var x0 = (-(x + w)) if flip else x
	draw_rect(Rect2(x0, y, w, h), c, false, width)


func _shadow() -> void:
	draw_set_transform(Vector2(0, 14), 0, Vector2(1, 0.4))
	draw_circle(Vector2.ZERO, 9, Color(0, 0, 0, 0.27))
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


func _draw() -> void:
	if sitting:
		draw_seated()
		return
	_shadow()
	if facing == "up":
		_head_up()
	elif facing == "left":
		_head_side(true)
	elif facing == "right":
		_head_side(false)
	else:
		_head_down()
	_body()
	_blit_drink()


# Shared seated render (reused by Follower._draw too).
func draw_seated() -> void:
	_shadow()
	draw_set_transform(Vector2(0, 4), 0, Vector2.ONE)
	if facing == "left" or facing == "right":
		_head_side(facing == "left")
		_seat_side(facing == "right")
	else:
		if facing == "up":
			_head_up()
		else:
			_head_down()
		_seat_front()
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)
	_blit_drink()


func _seat_front() -> void:
	_r(-5, 1, 10, 5, p_tee)
	_r(-5, 1, 1, 5, p_tee_sh)
	_r(-2, 1, 4, 1, p_tee_sh)
	_r(-5, 6, 10, 3, p_short)
	_r(-5, 6, 10, 1, p_short_sh)
	_r(-4, 9, 3, 2, p_skin)
	_r(1, 9, 3, 2, p_skin)
	_r(-4, 11, 3, 2, p_shoe)
	_r(1, 11, 3, 2, p_shoe)
	_r(-4, 12, 3, 1, p_sole)
	_r(1, 12, 3, 1, p_sole)


func _seat_side(right: bool) -> void:
	var sr := func(x, y, w, h, c):
		var x0 = x if right else -x - w
		draw_rect(Rect2(x0, y, w, h), c)
	sr.call(-5, 1, 10, 5, p_tee)
	sr.call(-5, 1, 1, 5, p_tee_sh)
	sr.call(-2, 1, 4, 1, p_tee_sh)
	sr.call(-4, 6, 5, 3, p_short)
	sr.call(-4, 6, 5, 1, p_short_sh)
	sr.call(0, 6, 7, 3, p_short)
	sr.call(0, 6, 7, 1, p_short_sh)
	sr.call(6, 9, 3, 3, p_skin)
	sr.call(6, 9, 1, 3, p_skin_sh)
	sr.call(6, 12, 5, 2, p_shoe)
	sr.call(6, 13, 5, 1, p_sole)


func _blit_drink() -> void:
	if holding == "":
		return
	if sitting:
		Drinks.draw(self, _drink_off.x, _drink_off.y, holding)
	else:
		Drinks.draw(self, 8, 6, holding)   # carried beside the body


func _head_down() -> void:
	draw_circle(Vector2(0, -6), 5, p_skin)


# left/right share one profile head (auto-mirrored via flip); characters without
# turned art fall back to the front head, as in humanoid.py.
func _head_side(_flip: bool) -> void:
	_head_down()


func _head_up() -> void:
	draw_circle(Vector2(0, -6), 5, p_skin)


func _body() -> void:
	_r(-2, -1, 4, 2, p_skin)
	_r(-7, 1, 3, 2, p_tee)
	_r(4, 1, 3, 2, p_tee)
	_r(-7, 3, 3, 2, p_skin)
	_r(4, 3, 3, 2, p_skin)
	_r(-5, 1, 10, 5, p_tee)
	_r(-5, 1, 1, 5, p_tee_sh)
	_r(-2, 1, 4, 1, p_tee_sh)
	_r(-4, 6, 8, 1, p_short_sh)
	_r(-4, 7, 3, 3, p_short)
	_r(1, 7, 3, 3, p_short)
	_r(-4, 7, 3, 1, p_short_sh)
	_r(1, 7, 3, 1, p_short_sh)
	_r(-4, 10, 3, 3, p_skin)
	_r(1, 10, 3, 3, p_skin)
	_r(-4, 10, 1, 3, p_skin_sh)
	_r(1, 10, 1, 3, p_skin_sh)
	_r(-5, 13, 5, 2, p_shoe)
	_r(1, 13, 5, 2, p_shoe)
	_r(-5, 14, 5, 1, p_sole)
	_r(1, 14, 5, 1, p_sole)
