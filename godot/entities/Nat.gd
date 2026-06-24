# Nat — voluminous curly bob, golden eyes, deep purple tee.
# Ported from entities/characters/nat.py.
class_name Nat
extends Npc

var _HAIR := Color8(55, 35, 20)
var _HAIR_LT := Color8(85, 58, 35)
var _HAIR_DK := Color8(35, 20, 10)
var _EYE := Color8(195, 155, 45)
var _LASH := Color8(25, 12, 3)
var _GLINT := Color8(240, 245, 235)
var _LIP := Color8(200, 110, 120)
var _CHEEK := Color8(175, 125, 90)


func _init(tx := 0, ty := 0) -> void:
	super(tx, ty)
	display_name = "Nat"
	p_skin = Color8(165, 120, 80)
	p_skin_sh = Color8(140, 100, 65)
	p_tee = Color8(80, 30, 110)
	p_tee_sh = Color8(58, 20, 82)
	p_shoe = Color8(55, 35, 22)
	p_sole = Color8(38, 25, 15)
	interaction_text = ["Dawg I'm getting changed, can I have a minute?"]


func _head_down() -> void:
	_el(-9, -17, 18, 13, _HAIR)
	_el(-5, -16, 8, 4, _HAIR_LT)

	_r(-8, -11, 3, 10, _HAIR)
	_r(-9, -10, 2, 6, _HAIR)
	_r(-8, -11, 1, 8, _HAIR_DK)
	_r(-7, -8, 1, 3, _HAIR_LT)
	_r(-9, -7, 1, 2, _HAIR_LT)

	_r(5, -11, 3, 10, _HAIR)
	_r(7, -10, 2, 6, _HAIR)
	_r(7, -11, 1, 8, _HAIR_DK)
	_r(6, -8, 1, 3, _HAIR_LT)
	_r(8, -7, 1, 2, _HAIR_LT)

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
	_elf(-9, -17, 17, 14, _HAIR, flip)            # voluminous bob mass
	_elf(-7, -16, 8, 4, _HAIR_LT, flip)
	_rf(-9, -8, 4, 6, _HAIR, flip)                # length down the back
	_rf(-9, -8, 1, 6, _HAIR_DK, flip)
	_rf(-7, -4, 3, 3, _HAIR, flip)
	_rf(-6, -2, 2, 2, _HAIR_LT, flip)

	_elf(-2, -12, 8, 10, p_skin, flip)            # face
	_rf(-2, -10, 2, 6, p_skin_sh, flip)
	_elf(-3, -13, 8, 4, _HAIR, flip)              # hairline
	_rf(0, -13, 3, 1, _HAIR_LT, flip)
	_rf(5, -12, 2, 4, _HAIR, flip)                # front curl

	_rf(1, -8, 3, 1, _LASH, flip)                 # eye (golden)
	_rf(1, -7, 2, 2, _EYE, flip)
	_rf(1, -7, 1, 1, _GLINT, flip)

	_rf(5, -7, 1, 2, p_skin, flip)                # nose
	_rf(6, -6, 1, 1, p_skin_sh, flip)

	_rf(3, -5, 2, 1, _CHEEK, flip)                # cheek + lip
	_rf(2, -4, 3, 1, _LIP, flip)
	_rf(2, -3, 2, 1, p_skin_sh, flip)


func _head_up() -> void:
	_el(-9, -17, 18, 14, _HAIR)
	_el(-5, -16, 8, 4, _HAIR_LT)
	_r(-9, -7, 3, 5, _HAIR)
	_r(6, -7, 3, 5, _HAIR)
	_r(-9, -7, 1, 5, _HAIR_DK)
	_r(8, -7, 1, 5, _HAIR_DK)
