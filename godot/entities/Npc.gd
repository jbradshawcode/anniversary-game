# Base for static talkable NPCs — the Godot mirror of entities/humanoid.py +
# the GameObject interaction hooks. Subclasses set the palette + interaction lines
# and override the head art. Shadow + shared body live here.
class_name Npc
extends Node2D

var tile_x: int
var tile_y: int
var facing := "down"
var display_name := ""
var interaction_text: Array = []

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


func _r(x, y, w, h, c) -> void:
	draw_rect(Rect2(x, y, w, h), c)


# Flattened circle ≈ a pygame ellipse centred at (cx,cy) with radii (rx,ry).
func _oval(cx, cy, rx, ry, c) -> void:
	draw_set_transform(Vector2(cx, cy), 0, Vector2(rx, ry))
	draw_circle(Vector2.ZERO, 1.0, c)
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


func _draw() -> void:
	draw_set_transform(Vector2(0, 14), 0, Vector2(1, 0.4))
	draw_circle(Vector2.ZERO, 9, Color(0, 0, 0, 0.27))
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)
	if facing == "up":
		_head_up()
	else:
		_head_down()
	_body()


func _head_down() -> void:
	draw_circle(Vector2(0, -6), 5, p_skin)


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
