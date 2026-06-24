# Leonard — slightly taller build, messy brown hair, white tee.
# Ported from entities/characters/leonard.py.
class_name Leonard
extends Npc

var _HAIR := Color8(90, 58, 30)
var _HAIR_LT := Color8(125, 85, 48)
var _HAIR_DK := Color8(60, 35, 16)
var _EYE := Color8(50, 35, 25)
var _LASH := Color8(25, 12, 3)
var _LIP := Color8(190, 120, 110)
var _CHEEK := Color8(210, 155, 130)
var _GLINT := Color8(240, 245, 235)


func _init(tx := 0, ty := 0) -> void:
	super(tx, ty)
	display_name = "Leonard"
	p_skin = Color8(200, 160, 120)
	p_skin_sh = Color8(175, 138, 100)
	p_tee = Color8(238, 236, 230)
	p_tee_sh = Color8(210, 208, 200)
	p_shoe = Color8(60, 40, 25)
	p_sole = Color8(42, 28, 16)
	interaction_text = ["Alles klar, alles klar.", "Ordnung muss sein."]


func _head_down() -> void:
	_r(-7, -16, 14, 5, _HAIR)
	_r(-4, -17, 4, 2, _HAIR)
	_r(2, -17, 4, 2, _HAIR)
	_r(-1, -18, 3, 2, _HAIR)
	_r(-3, -17, 3, 1, _HAIR_LT)
	_r(3, -17, 2, 1, _HAIR_LT)
	_r(-1, -18, 2, 1, _HAIR_LT)

	_r(-7, -11, 2, 5, _HAIR)
	_r(5, -11, 2, 5, _HAIR)
	_r(-7, -11, 1, 3, _HAIR_DK)
	_r(6, -11, 1, 3, _HAIR_DK)

	_el(-5, -11, 10, 10, p_skin)

	_r(-5, -11, 10, 2, _HAIR)
	_r(-3, -11, 4, 1, _HAIR_LT)

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
	_rf(-7, -16, 13, 5, _HAIR, flip)              # messy back + tuft up top
	_rf(-3, -18, 4, 3, _HAIR, flip)
	_rf(1, -17, 3, 2, _HAIR, flip)
	_rf(-2, -18, 2, 1, _HAIR_LT, flip)
	_rf(-5, -16, 3, 1, _HAIR_LT, flip)
	_rf(-7, -12, 3, 9, _HAIR, flip)
	_rf(-7, -12, 1, 6, _HAIR_DK, flip)
	_rf(-7, -4, 2, 2, _HAIR, flip)

	_elf(-2, -12, 8, 10, p_skin, flip)            # face
	_rf(-2, -10, 2, 6, p_skin_sh, flip)

	_rf(-2, -12, 7, 2, _HAIR, flip)               # fringe
	_rf(0, -12, 3, 1, _HAIR_LT, flip)
	_rf(5, -12, 1, 3, _HAIR, flip)

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
	_r(-3, -18, 5, 3, _HAIR)                      # messy tuft
	_r(-8, -11, 16, 9, _HAIR)
	_r(-9, -10, 2, 4, _HAIR)
	_r(7, -10, 2, 4, _HAIR)
	_r(-2, -11, 5, 7, _HAIR_LT)
	_r(-8, -11, 2, 7, _HAIR_DK)
	_r(6, -11, 2, 7, _HAIR_DK)


func _body() -> void:
	# taller torso + longer legs than the standard Humanoid body
	_r(-2, -1, 4, 2, p_skin)
	_r(-7, 1, 3, 3, p_tee)
	_r(4, 1, 3, 3, p_tee)
	_r(-7, 4, 3, 2, p_skin)
	_r(4, 4, 3, 2, p_skin)
	_r(-5, 1, 10, 7, p_tee)
	_r(-5, 1, 1, 7, p_tee_sh)
	_r(-2, 1, 4, 1, p_tee_sh)
	_r(-4, 8, 8, 1, p_short_sh)
	_r(-4, 9, 3, 3, p_short)
	_r(1, 9, 3, 3, p_short)
	_r(-4, 9, 3, 1, p_short_sh)
	_r(1, 9, 3, 1, p_short_sh)
	_r(-4, 12, 3, 3, p_skin)
	_r(1, 12, 3, 3, p_skin)
	_r(-4, 12, 1, 3, p_skin_sh)
	_r(1, 12, 1, 3, p_skin_sh)
	_r(-5, 15, 5, 2, p_shoe)
	_r(1, 15, 5, 2, p_shoe)
	_r(-5, 16, 5, 1, p_sole)
	_r(1, 16, 5, 1, p_sole)
