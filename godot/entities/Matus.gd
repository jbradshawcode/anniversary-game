# Matúš — the referee. Reddish stubble, dark sunglasses, tank top, whistle.
# Ported from entities/characters/matus.py (head art + interaction lines).
class_name Matus
extends Npc

var _HAIR := Color8(150, 92, 52)
var _HAIR_LT := Color8(180, 118, 70)
var _HAIR_DK := Color8(110, 64, 34)
var _STUBBLE := Color8(158, 110, 82)
var _SHADE := Color8(26, 28, 34)
var _SHADE_HI := Color8(96, 102, 116)
var _MOUTH := Color8(170, 110, 100)
var _WHISTLE := Color8(236, 232, 224)
var _LANYARD := Color8(200, 70, 60)


func _init(tx := 0, ty := 0) -> void:
	super(tx, ty)
	display_name = "Matúš"
	p_skin = Color8(210, 158, 120)
	p_skin_sh = Color8(182, 132, 98)
	p_tee = Color8(52, 56, 64)
	p_tee_sh = Color8(38, 41, 48)
	interaction_text = [
		"FWEEEEEET!!",
		"I listen to lonely people music.",
		"Which means you all have to listen to lonely people music.",
	]


func _head_down() -> void:
	draw_circle(Vector2(0, -6), 5, p_skin)        # face
	_oval(0, -10.5, 6, 3.5, _HAIR)                # short messy cap
	_oval(-1, -11.5, 3, 1.5, _HAIR_LT)
	_r(-6, -9, 2, 3, _HAIR)                       # sideburns
	_r(4, -9, 2, 3, _HAIR)
	_r(-6, -8, 1, 2, _HAIR_DK)
	_r(-5, -8, 10, 3, _SHADE)                     # sunglasses bar
	_r(-5, -8, 10, 1, _SHADE_HI)
	_r(-3, -8, 1, 3, _SHADE_HI)                   # lens glints
	_r(3, -8, 1, 3, _SHADE_HI)
	_r(-4, -4, 8, 1, _STUBBLE)                    # stubble jaw
	_r(-3, -3, 6, 1, _STUBBLE)
	_r(-2, -3, 4, 1, _MOUTH)                      # grin
	_r(-3, 0, 6, 1, _LANYARD)                     # whistle lanyard
	_r(1, 1, 2, 2, _WHISTLE)                      # whistle at chest


func _head_up() -> void:
	_oval(0, -10, 6, 4, _HAIR)
	_oval(-1, -11.5, 3, 1.5, _HAIR_LT)
	_r(-6, -6, 2, 3, _HAIR_DK)
	_r(4, -6, 2, 3, _HAIR_DK)
