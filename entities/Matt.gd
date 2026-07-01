# Matt — round afro, beard, green tee, friendly smile.
# Ported from entities/characters/matt.py.
class_name Matt
extends Npc

var _HAIR := Color8(70, 45, 25)
var _HAIR_LT := Color8(100, 65, 38)
var _HAIR_DK := Color8(45, 28, 15)
var _BEARD := Color8(65, 42, 25)
var _TEETH := Color8(240, 235, 225)
var _EYE := Color8(50, 35, 25)
var _LASH := Color8(25, 12, 3)
var _GLINT := Color8(240, 245, 235)


func _init(tx := 0, ty := 0) -> void:
	super(tx, ty)
	display_name = "Matt"
	p_skin = Color8(165, 120, 80)
	p_skin_sh = Color8(140, 100, 65)
	p_tee = Color8(75, 160, 100)
	p_tee_sh = Color8(55, 130, 75)
	interaction_text = ["Hey! Great to see you out here!"]


func _head_down() -> void:
	_el(-11, -17, 22, 16, _HAIR)
	_el(-6, -16, 10, 5, _HAIR_LT)
	_r(-10, -11, 2, 5, _HAIR_DK)
	_r(8, -11, 2, 5, _HAIR_DK)

	_el(-5, -11, 10, 10, p_skin)

	_r(-5, -11, 10, 2, _HAIR)
	_r(-3, -11, 4, 1, _HAIR_LT)

	_r(-4, -8, 3, 1, _LASH)
	_r(1, -8, 3, 1, _LASH)
	_r(-4, -7, 3, 2, _EYE)
	_r(-4, -7, 1, 1, _GLINT)
	_r(1, -7, 3, 2, _EYE)
	_r(1, -7, 1, 1, _GLINT)

	_r(-4, -5, 2, 3, _BEARD)
	_r(2, -5, 2, 3, _BEARD)
	_r(-3, -3, 6, 2, _BEARD)

	_r(-2, -4, 4, 1, _TEETH)


func _head_side(flip: bool) -> void:
	_elf(-10, -18, 19, 16, _HAIR, flip)           # round afro mass
	_elf(-9, -17, 9, 5, _HAIR_LT, flip)
	_rf(-10, -8, 3, 5, _HAIR, flip)
	_rf(-9, -3, 3, 3, _HAIR_DK, flip)

	_elf(-2, -12, 8, 10, p_skin, flip)            # face
	_rf(-2, -10, 2, 6, p_skin_sh, flip)
	_elf(-3, -13, 8, 4, _HAIR, flip)              # hairline over brow

	_rf(1, -8, 3, 1, _LASH, flip)                 # eye
	_rf(1, -7, 2, 2, _EYE, flip)
	_rf(1, -7, 1, 1, _GLINT, flip)

	_rf(5, -7, 1, 2, p_skin, flip)                # nose
	_rf(6, -6, 1, 1, p_skin_sh, flip)

	_rf(2, -5, 3, 1, _BEARD, flip)                # beard along jaw + smile
	_rf(1, -4, 4, 2, _BEARD, flip)
	_rf(-1, -3, 4, 1, _BEARD, flip)
	_rf(3, -4, 2, 1, _TEETH, flip)


func _head_up() -> void:
	_el(-11, -17, 22, 16, _HAIR)
	_el(-6, -16, 10, 5, _HAIR_LT)
	_r(-10, -6, 3, 4, _HAIR_DK)
	_r(7, -6, 3, 4, _HAIR_DK)
