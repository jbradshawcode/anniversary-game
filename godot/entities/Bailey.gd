# Bailey — big round curly afro, round glasses, black/white striped tee.
# Ported from entities/characters/bailey.py.
class_name Bailey
extends Npc

var _HAIR := Color8(78, 52, 32)
var _HAIR_LT := Color8(112, 78, 46)
var _HAIR_DK := Color8(52, 34, 20)
var _TEE := Color8(238, 238, 238)
var _STRIPE := Color8(40, 40, 46)         # the dark bands of the striped tee
var _EYE := Color8(50, 35, 25)
var _LIP := Color8(190, 120, 110)
var _CHEEK := Color8(210, 155, 130)
var _FRAME := Color8(70, 64, 78)          # light enough to read as thin wire, not a blob


func _init(tx := 0, ty := 0) -> void:
	super(tx, ty)
	display_name = "Bailey"
	p_skin = Color8(205, 165, 125)
	p_skin_sh = Color8(180, 140, 105)
	p_tee = _TEE
	p_tee_sh = Color8(205, 205, 205)
	interaction_text = ["Um hello"]


func _glasses_down() -> void:
	_ro(-4, -8, 3, 3, _FRAME, 1)              # hollow lenses
	_ro(1, -8, 3, 3, _FRAME, 1)
	_r(-1, -7, 2, 1, _FRAME)                  # bridge


func _head_down() -> void:
	_el(-12, -20, 24, 17, _HAIR)              # big round afro
	_el(-10, -15, 8, 9, _HAIR)                # rounded lobes (not drooping)
	_el(2, -15, 8, 9, _HAIR)
	_el(-8, -19, 16, 6, _HAIR_LT)             # top sheen
	_r(-6, -18, 2, 2, _HAIR_DK)
	_r(4, -18, 2, 2, _HAIR_DK)
	_r(-9, -11, 2, 3, _HAIR_DK)
	_r(7, -11, 2, 3, _HAIR_DK)

	_el(-5, -11, 10, 10, p_skin)
	_r(-5, -11, 10, 2, _HAIR)                 # hairline over brow

	_r(-3, -7, 1, 1, _EYE)                    # small eyes, clear behind glasses
	_r(2, -7, 1, 1, _EYE)
	_glasses_down()
	_r(-4, -4, 1, 1, _CHEEK)
	_r(3, -4, 1, 1, _CHEEK)
	_r(-1, -3, 2, 1, _LIP)


func _head_side(flip: bool) -> void:
	_elf(-11, -20, 22, 17, _HAIR, flip)       # round afro, turned
	_elf(-10, -15, 8, 9, _HAIR, flip)
	_elf(-8, -19, 14, 6, _HAIR_LT, flip)
	_rf(-9, -11, 2, 3, _HAIR_DK, flip)

	_elf(-2, -12, 8, 10, p_skin, flip)
	_rf(-2, -10, 2, 6, p_skin_sh, flip)
	_elf(-3, -13, 8, 4, _HAIR, flip)          # curls over brow

	_rf(1, -7, 1, 1, _EYE, flip)
	_rof(1, -8, 3, 3, _FRAME, flip, 1)        # front lens
	_rf(-1, -7, 1, 1, _FRAME, flip)           # temple to the back

	_rf(5, -7, 1, 2, p_skin, flip)
	_rf(6, -6, 1, 1, p_skin_sh, flip)
	_rf(3, -4, 2, 1, _CHEEK, flip)
	_rf(2, -3, 3, 1, _LIP, flip)


func _head_up() -> void:
	_el(-12, -20, 24, 17, _HAIR)              # round afro from behind
	_el(-8, -19, 16, 6, _HAIR_LT)
	_r(-6, -10, 3, 4, _HAIR_DK)
	_r(5, -10, 3, 4, _HAIR_DK)
	_r(-4, -16, 2, 2, _HAIR_DK)
	_r(2, -15, 2, 2, _HAIR_DK)


func _body() -> void:
	# horizontal black/white striped tee
	_r(-2, -1, 4, 2, p_skin)                  # neck
	var bands := [_TEE, _STRIPE, _TEE, _STRIPE, _TEE]
	for i in range(bands.size()):             # striped torso
		_r(-5, 1 + i, 10, 1, bands[i])
	_r(-7, 1, 3, 1, _TEE)                     # striped sleeve caps
	_r(-7, 2, 3, 1, _STRIPE)
	_r(4, 1, 3, 1, _TEE)
	_r(4, 2, 3, 1, _STRIPE)
	_r(-7, 3, 3, 2, p_skin)                   # forearms
	_r(4, 3, 3, 2, p_skin)
	_r(-4, 6, 8, 1, p_short_sh)               # shorts + legs + shoes (standard)
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
