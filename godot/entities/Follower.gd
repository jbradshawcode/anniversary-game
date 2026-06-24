# A crew member that walks — extends the static Npc with a walk bob + a simple
# generic head (the real crew's bespoke art is a later content port). The Party
# drives its position/facing/walking each frame; logic mirrors humanoid.py's mover.
class_name Follower
extends Npc

var walking := false
var walk_phase := 0.0
var _hair := Color8(58, 44, 34)
var _eye := Color8(40, 30, 25)


func _init(tx := 0, ty := 0, tee := Color8(70, 90, 150)) -> void:
	super(tx, ty)
	p_tee = tee
	p_tee_sh = tee.darkened(0.18)


func _draw() -> void:
	draw_set_transform(Vector2(0, 14), 0, Vector2(1, 0.4))
	draw_circle(Vector2.ZERO, 9, Color(0, 0, 0, 0.27))
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)

	var bob := 0.0
	if walking:
		bob = 3.0 * abs(sin(walk_phase))
	draw_set_transform(Vector2(0, -bob), 0, Vector2.ONE)
	if facing == "up":
		_head_up()
	else:
		_head_down()
	_body()
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


func _head_down() -> void:
	_r(-5, -13, 10, 4, _hair)
	_r(-6, -10, 2, 6, _hair)
	_r(4, -10, 2, 6, _hair)
	draw_circle(Vector2(0, -6), 5, p_skin)
	_r(-5, -10, 10, 2, _hair)
	_r(-3, -7, 2, 2, _eye)
	_r(1, -7, 2, 2, _eye)


func _head_up() -> void:
	_r(-6, -13, 12, 9, _hair)
