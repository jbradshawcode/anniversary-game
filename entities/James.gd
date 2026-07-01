# James — one of the crew; wavy reddish-brown hair.
# Ported from entities/characters/james.py.
class_name James
extends Npc

var _HAIR := Color8(145, 75, 40)
var _HAIR_LT := Color8(185, 115, 65)
var _HAIR_DK := Color8(100, 45, 20)
var _EYE := Color8(50, 35, 25)
var _LASH := Color8(25, 12, 3)
var _LIP := Color8(195, 120, 110)
var _CHEEK := Color8(210, 155, 130)
var _GLINT := Color8(240, 245, 235)


func _init(tx := 0, ty := 0) -> void:
	super(tx, ty)
	display_name = "James"
	p_skin = Color8(200, 160, 120)
	p_skin_sh = Color8(175, 135, 100)
	p_tee = Color8(238, 236, 230)
	p_tee_sh = Color8(210, 208, 200)
	interaction_text = [
		"Heyyy there beautiful lady.",
		"(James was not actually brave enough to say this)",
	]


func _head_down() -> void:
	_r(-7, -15, 14, 5, _HAIR)
	_r(-4, -16, 5, 2, _HAIR)
	_r(4, -16, 3, 2, _HAIR)
	_r(-3, -16, 3, 1, _HAIR_LT)
	_r(5, -16, 1, 1, _HAIR_LT)

	_r(-8, -11, 3, 7, _HAIR)
	_r(5, -11, 3, 7, _HAIR)
	_r(-9, -10, 2, 3, _HAIR)
	_r(7, -10, 2, 3, _HAIR)
	_r(-8, -11, 1, 5, _HAIR_DK)
	_r(7, -11, 1, 5, _HAIR_DK)

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


func _head_side(flip: bool) -> void:
	_rf(-7, -15, 13, 4, _HAIR, flip)              # back + top, wavy tail
	_rf(-5, -15, 4, 2, _HAIR_LT, flip)
	_rf(-7, -12, 4, 9, _HAIR, flip)
	_rf(-5, -12, 2, 6, _HAIR_LT, flip)
	_rf(-8, -10, 2, 4, _HAIR, flip)
	_rf(-8, -6, 2, 3, _HAIR, flip)
	_rf(-7, -3, 2, 2, _HAIR_DK, flip)

	_elf(-2, -12, 8, 10, p_skin, flip)            # face, turned right
	_rf(-2, -10, 2, 6, p_skin_sh, flip)

	_rf(-2, -12, 8, 2, _HAIR, flip)               # fringe + front tuft
	_rf(0, -12, 3, 1, _HAIR_LT, flip)
	_rf(5, -12, 2, 4, _HAIR, flip)

	_rf(1, -8, 3, 1, _LASH, flip)                 # eye
	_rf(1, -7, 2, 2, _EYE, flip)
	_rf(1, -7, 1, 1, _GLINT, flip)

	_rf(5, -7, 1, 2, p_skin, flip)                # nose
	_rf(6, -6, 1, 1, p_skin_sh, flip)

	_rf(3, -5, 2, 1, _CHEEK, flip)                # cheek + lip
	_rf(2, -4, 3, 1, _LIP, flip)
	_rf(2, -3, 2, 1, p_skin_sh, flip)


func _head_up() -> void:
	_r(-7, -16, 14, 5, _HAIR)
	_r(-4, -16, 5, 2, _HAIR)
	_r(-8, -11, 16, 9, _HAIR)
	_r(-9, -10, 2, 4, _HAIR)
	_r(7, -10, 2, 4, _HAIR)
	_r(-5, -15, 4, 2, _HAIR_LT)
	_r(-2, -11, 5, 7, _HAIR_LT)
	_r(-8, -11, 2, 7, _HAIR_DK)
	_r(6, -11, 2, 7, _HAIR_DK)
