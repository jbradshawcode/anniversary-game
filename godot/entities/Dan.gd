# Dan — organizes the 3v3; tall messy quiff, light stubble, red tee.
# Ported from entities/characters/dan.py.
class_name Dan
extends Npc

var _STUBBLE := Color8(195, 180, 155)
var _HAIR := Color8(140, 120, 60)
var _HAIR_LT := Color8(175, 155, 85)
var _HAIR_DK := Color8(105, 88, 40)
var _EYE := Color8(50, 35, 25)
var _LASH := Color8(40, 28, 15)
var _LIP := Color8(190, 125, 110)
var _CHEEK := Color8(210, 155, 130)
var _GLINT := Color8(240, 245, 235)


func _init(tx := 0, ty := 0) -> void:
	super(tx, ty)
	display_name = "Dan"
	p_skin = Color8(205, 165, 125)
	p_skin_sh = Color8(180, 140, 105)
	p_tee = Color8(205, 55, 45)
	p_tee_sh = Color8(165, 38, 32)
	interaction_text = ["What's uuuup"]


func _head_down() -> void:
	_r(-6, -16, 12, 6, _HAIR)
	_r(-3, -17, 6, 2, _HAIR)
	_r(-7, -14, 2, 3, _HAIR)
	_r(5, -15, 2, 3, _HAIR)
	_r(-2, -17, 4, 2, _HAIR_LT)
	_r(-5, -16, 3, 3, _HAIR_LT)
	_r(3, -15, 2, 2, _HAIR_LT)
	_r(-6, -14, 1, 4, _HAIR_DK)
	_r(5, -13, 1, 3, _HAIR_DK)

	_r(-7, -11, 2, 4, _HAIR)
	_r(5, -11, 2, 4, _HAIR)

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

	_r(-4, -4, 2, 1, _STUBBLE)
	_r(2, -4, 2, 1, _STUBBLE)
	_r(-3, -3, 6, 1, _STUBBLE)
	_r(-2, -2, 4, 1, _STUBBLE)

	_r(-1, -4, 2, 1, _LIP)


func _head_side(flip: bool) -> void:
	_rf(-6, -15, 12, 4, _HAIR, flip)              # quiff stacked up and swept forward
	_rf(-6, -18, 5, 4, _HAIR, flip)
	_rf(-3, -19, 6, 3, _HAIR, flip)
	_rf(1, -20, 5, 3, _HAIR, flip)
	_rf(0, -19, 3, 2, _HAIR_LT, flip)
	_rf(-4, -17, 3, 2, _HAIR_LT, flip)
	_rf(-6, -12, 4, 8, _HAIR, flip)
	_rf(-6, -12, 1, 6, _HAIR_DK, flip)

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

	_rf(2, -4, 3, 1, _LIP, flip)                  # mouth + stubble
	_rf(3, -5, 2, 1, _STUBBLE, flip)
	_rf(2, -3, 3, 1, _STUBBLE, flip)
	_rf(0, -3, 2, 1, _STUBBLE, flip)


func _head_up() -> void:
	_r(-6, -16, 12, 5, _HAIR)
	_r(-3, -19, 7, 4, _HAIR)                      # quiff from behind
	_r(-1, -20, 5, 2, _HAIR_LT)
	_r(-7, -11, 14, 9, _HAIR)
	_r(-8, -10, 2, 4, _HAIR)
	_r(6, -10, 2, 4, _HAIR)
	_r(-2, -11, 5, 6, _HAIR_LT)
	_r(-7, -11, 2, 6, _HAIR_DK)
	_r(5, -11, 2, 6, _HAIR_DK)
