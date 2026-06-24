# Wallace — short neat black hair, glasses, wide friendly face, teal tee.
# Ported from entities/characters/wallace.py.
class_name Wallace
extends Npc

var _HAIR := Color8(34, 32, 40)
var _HAIR_LT := Color8(60, 56, 68)
var _HAIR_DK := Color8(20, 18, 26)
var _EYE := Color8(44, 34, 30)
var _LIP := Color8(182, 122, 112)
var _CHEEK := Color8(208, 162, 132)
var _GLINT := Color8(240, 244, 242)
var _FRAME := Color8(98, 98, 114)         # light enough to read as thin wire, not a mask


func _init(tx := 0, ty := 0) -> void:
	super(tx, ty)
	display_name = "Wallace"
	p_skin = Color8(212, 176, 140)
	p_skin_sh = Color8(186, 152, 120)
	p_tee = Color8(66, 118, 118)
	p_tee_sh = Color8(48, 92, 92)
	interaction_text = ["Helloooo what's up"]


func _glasses_down() -> void:
	_ro(-5, -8, 3, 3, _FRAME, 1)              # hollow lenses, clear gap
	_ro(2, -8, 3, 3, _FRAME, 1)
	_r(-2, -7, 4, 1, _FRAME)                  # bridge
	_r(-6, -7, 1, 1, _FRAME)                  # temples
	_r(5, -7, 1, 1, _FRAME)


func _head_down() -> void:
	_r(-7, -15, 14, 4, _HAIR)                 # short neat crop (wide)
	_r(-4, -16, 8, 1, _HAIR)
	_r(-7, -13, 2, 4, _HAIR)
	_r(5, -13, 2, 4, _HAIR)
	_r(-3, -15, 5, 1, _HAIR_LT)

	_el(-6, -11, 12, 10, p_skin)              # wider face
	_r(-6, -11, 12, 2, _HAIR)                 # hairline

	_r(-4, -7, 1, 1, _EYE)                    # small eyes, clear behind glasses
	_r(3, -7, 1, 1, _EYE)
	_glasses_down()
	_r(-4, -4, 1, 1, _CHEEK)
	_r(3, -4, 1, 1, _CHEEK)
	_r(-1, -3, 2, 1, _LIP)


func _head_side(flip: bool) -> void:
	_rf(-6, -15, 13, 4, _HAIR, flip)          # short crop, turned
	_rf(-3, -16, 5, 1, _HAIR, flip)
	_rf(-6, -12, 3, 8, _HAIR, flip)
	_rf(-6, -12, 1, 6, _HAIR_DK, flip)

	_elf(-3, -12, 9, 10, p_skin, flip)        # wider profile
	_rf(-3, -10, 2, 6, p_skin_sh, flip)
	_rf(-3, -12, 8, 2, _HAIR, flip)
	_rf(5, -12, 1, 3, _HAIR, flip)

	_rf(1, -7, 1, 1, _EYE, flip)
	_rof(1, -8, 3, 3, _FRAME, flip, 1)        # front lens
	_rf(-1, -7, 1, 1, _FRAME, flip)           # temple to the back

	_rf(6, -7, 1, 2, p_skin, flip)
	_rf(7, -6, 1, 1, p_skin_sh, flip)
	_rf(3, -4, 2, 1, _CHEEK, flip)
	_rf(2, -3, 3, 1, _LIP, flip)


func _head_up() -> void:
	_r(-7, -15, 14, 4, _HAIR)
	_r(-4, -16, 8, 1, _HAIR)
	_r(-8, -11, 16, 9, _HAIR)
	_r(-8, -11, 2, 8, _HAIR_DK)
	_r(6, -11, 2, 8, _HAIR_DK)
	_r(-2, -11, 4, 6, _HAIR_LT)
