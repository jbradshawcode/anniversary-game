# Milla — blonde woman behind the Salutation bar; wine top.
# Ported from entities/characters/milla.py. Her tile is a counter tile (already
# solid), so she's drawn a tile back and the player talks to her THROUGH the bar.
class_name Milla
extends Npc

var _HAIR := Color8(224, 188, 104)
var _HAIR_LT := Color8(244, 214, 140)
var _HAIR_DK := Color8(188, 150, 78)
var _EYE := Color8(80, 120, 150)
var _LASH := Color8(40, 28, 20)
var _LIP := Color8(200, 120, 120)
var _CHEEK := Color8(235, 180, 165)
var _GLINT := Color8(245, 248, 240)


func _init(tx := 0, ty := 0) -> void:
	super(tx, ty)
	display_name = "Milla"
	p_skin = Color8(238, 205, 178)
	p_skin_sh = Color8(214, 178, 150)
	p_tee = Color8(125, 55, 65)
	p_tee_sh = Color8(98, 42, 50)
	interaction_text = ["What'll it be?"]


func _ready() -> void:
	super()
	position.y -= Config.TILE_SIZE   # stand a tile back, behind the bar


func _head_down() -> void:
	# blonde fringe + shoulder-length sides
	_r(-7, -15, 14, 5, _HAIR)
	_r(-4, -16, 5, 2, _HAIR)
	_r(4, -16, 3, 2, _HAIR)
	_r(-3, -16, 3, 1, _HAIR_LT)
	_r(5, -16, 1, 1, _HAIR_LT)

	_r(-8, -11, 3, 8, _HAIR)
	_r(5, -11, 3, 8, _HAIR)
	_r(-9, -10, 2, 4, _HAIR)
	_r(7, -10, 2, 4, _HAIR)
	_r(-8, -11, 1, 6, _HAIR_DK)
	_r(7, -11, 1, 6, _HAIR_DK)

	_el(-5, -11, 10, 10, p_skin)

	_r(-5, -11, 4, 2, _HAIR)
	_r(1, -11, 4, 2, _HAIR)
	_r(-3, -11, 2, 1, _HAIR_LT)
	_r(2, -11, 2, 1, _HAIR_LT)

	_r(-4, -8, 3, 1, _LASH)
	_r(1, -8, 3, 1, _LASH)
	_r(-4, -7, 3, 2, _EYE)
	_r(-4, -7, 1, 1, _GLINT)
	_r(1, -7, 3, 2, _EYE)
	_r(1, -7, 1, 1, _GLINT)

	_r(-4, -5, 2, 1, _CHEEK)
	_r(2, -5, 2, 1, _CHEEK)

	_r(-1, -4, 2, 1, _LIP)
