# Mayu — chin-length brown bob with a fringe, fair skin, olive hoodie.
# Ported from entities/characters/mayu.py.
class_name Mayu
extends Npc

var _HAIR := Color8(70, 48, 35)
var _HAIR_LT := Color8(102, 74, 54)
var _HAIR_DK := Color8(48, 32, 22)
var _EYE := Color8(60, 42, 30)
var _LASH := Color8(30, 18, 8)
var _LIP := Color8(205, 120, 118)
var _CHEEK := Color8(228, 170, 150)
var _GLINT := Color8(245, 248, 240)


func _init(tx := 0, ty := 0) -> void:
	super(tx, ty)
	display_name = "Mayu"
	p_skin = Color8(236, 206, 182)
	p_skin_sh = Color8(214, 182, 158)
	p_tee = Color8(96, 99, 72)
	p_tee_sh = Color8(72, 76, 54)
	interaction_text = ["Hey! How are you!"]


func _head_down() -> void:
	_r(-7, -16, 14, 5, _HAIR)                  # rounded top
	_r(-7, -16, 4, 2, _HAIR_LT)
	_r(-8, -13, 3, 12, _HAIR)                  # straight bob, down to the jaw
	_r(5, -13, 3, 12, _HAIR)
	_r(-8, -13, 1, 11, _HAIR_DK)
	_r(7, -13, 1, 11, _HAIR_DK)
	_r(-6, -3, 2, 2, _HAIR)
	_r(4, -3, 2, 2, _HAIR)

	_el(-5, -11, 10, 10, p_skin)

	_r(-6, -12, 12, 3, _HAIR)                  # blunt fringe across the brow
	_r(-5, -12, 4, 1, _HAIR_LT)
	_r(0, -11, 3, 1, _HAIR_DK)

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
	_rf(-7, -16, 13, 5, _HAIR, flip)           # top
	_rf(-7, -16, 4, 2, _HAIR_LT, flip)
	_rf(-7, -13, 3, 13, _HAIR, flip)           # bob length down the back
	_rf(-7, -13, 1, 12, _HAIR_DK, flip)

	_elf(-2, -12, 8, 10, p_skin, flip)
	_rf(-2, -10, 2, 6, p_skin_sh, flip)

	_rf(-2, -12, 8, 3, _HAIR, flip)            # fringe sweeping to the front
	_rf(0, -12, 3, 1, _HAIR_LT, flip)
	_rf(5, -12, 1, 4, _HAIR, flip)

	_rf(1, -8, 3, 1, _LASH, flip)
	_rf(1, -7, 2, 2, _EYE, flip)
	_rf(1, -7, 1, 1, _GLINT, flip)
	_rf(5, -7, 1, 2, p_skin, flip)
	_rf(6, -6, 1, 1, p_skin_sh, flip)
	_rf(3, -5, 2, 1, _CHEEK, flip)
	_rf(2, -4, 3, 1, _LIP, flip)
	_rf(2, -3, 2, 1, p_skin_sh, flip)


func _head_up() -> void:
	_r(-7, -16, 14, 5, _HAIR)
	_r(-7, -16, 4, 2, _HAIR_LT)
	_r(-8, -11, 16, 11, _HAIR)                 # bob from behind, to the nape
	_r(-8, -11, 2, 10, _HAIR_DK)
	_r(6, -11, 2, 10, _HAIR_DK)
	_r(-1, -11, 2, 9, _HAIR_LT)                # centre parting hint
