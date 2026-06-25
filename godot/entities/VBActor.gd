# Volleyball player — free pixel movement, drawn with the game's real characters.
# Port of entities/volleyball/actor.py. Each actor wraps a real character node
# (Player / James / Dan / ...) added as a `bare` child for the head+body art; this
# node draws the team ground ring + (for the controlled actor) a bright ring and a
# chevron marker. Pose / z / lean are purely cosmetic (driven by update_anim) and
# never feed the contact maths, so gameplay stays deterministic.
class_name VBActor
extends Node2D

enum Role { SETTER, HITTER_L, HITTER_R }
enum Pose { READY, RUN, DIG, JUMP, BLOCK, CELEBRATE, PRONE }

const _SHADOW := Color8(40, 70, 96)
const _RING_YOU := Color8(250, 228, 120)
const _RING_NEAR := Color8(70, 140, 240)
const _RING_FAR := Color8(232, 96, 82)
const _MARK_YOU := Color8(255, 240, 120)

var x := 0.0
var y := 0.0
var team := 0
var role: Role = Role.SETTER
var sprite: Node2D = null
var is_player := false
var facing := "down"
var home := Vector2.ZERO
var vx := 0.0
var vy := 0.0
var pose: Pose = Pose.READY
var anim_t := 0.0
var z := 0.0                     # cosmetic jump height
var lean := 0.0                  # cosmetic lateral lean (px)


func _init(px := 0.0, py := 0.0, t := 0, r: Role = Role.SETTER,
		spr: Node2D = null, player := false) -> void:
	x = px
	y = py
	team = t
	role = r
	sprite = spr
	is_player = player
	home = Vector2(px, py)


func _ready() -> void:
	if sprite != null:
		sprite.bare = true
		add_child(sprite)


func _process(_delta: float) -> void:
	position = Vector2(x, y)            # VolleyCourt owns z_index (the y-sort + aim-step bump)
	if sprite != null:
		sprite.position = Vector2(lean, -z)
		sprite.facing = facing
		sprite.queue_redraw()
	queue_redraw()


func move_toward_pt(tx: float, ty: float, dt: float, speed: float) -> void:
	var dx := tx - x
	var dy := ty - y
	var d := sqrt(dx * dx + dy * dy)
	if d <= 1.0:
		x = tx
		y = ty
		return
	var step: float = min(d, speed * dt)
	x += dx / d * step
	y += dy / d * step


func dist_to(tx: float, ty: float) -> float:
	return sqrt((x - tx) * (x - tx) + (y - ty) * (y - ty))


func set_pose(p: Pose) -> void:
	if p != pose:
		pose = p
		anim_t = 0.0


func update_anim(dt: float) -> void:
	anim_t += dt
	var t := anim_t
	if pose == Pose.JUMP:
		z = max(0.0, 26.0 * (1.0 - pow(2.4 * t - 1.0, 2)))
		lean = 0.0
		if t > 0.85:
			set_pose(Pose.READY)
	elif pose == Pose.BLOCK:
		z = min(18.0, 90.0 * t)
		if t > 0.6:
			set_pose(Pose.READY)
	elif pose == Pose.DIG:
		z = 0.0
		if t > 0.4:
			set_pose(Pose.READY)
	elif pose == Pose.CELEBRATE:
		z = max(0.0, 10.0 * abs(sin(t * 9.0)))
		lean = 0.0
	elif pose == Pose.PRONE:
		z = 0.0
		if t > 0.5:
			set_pose(Pose.READY)
	else:
		z *= max(0.0, 1.0 - 12.0 * dt)
		lean *= max(0.0, 1.0 - 12.0 * dt)


func _draw() -> void:
	var prone := pose == Pose.PRONE
	var sw := 22.0 if prone else 16.0
	# shadow + team ring on the floor (centred at the feet, local origin)
	_fill_ellipse(0, 15, sw, 6, _SHADOW)
	var ring := _RING_NEAR if team == 0 else _RING_FAR
	_ring_ellipse(0, 15, sw + 4, 8, ring, 2)
	if is_player:
		_ring_ellipse(0, 15, sw + 8, 10, _RING_YOU, 2)
		var my := -26.0 - z
		draw_colored_polygon(PackedVector2Array([
			Vector2(-5, my - 5), Vector2(5, my - 5), Vector2(0, my)]), _MARK_YOU)


# pygame ellipse(top-left x,y,w,h): here the caller gives the CENTRE (cx,cy) + size.
func _fill_ellipse(cx: float, cy: float, w: float, h: float, c: Color) -> void:
	draw_set_transform(Vector2(cx, cy), 0, Vector2(w / 2.0, h / 2.0))
	draw_circle(Vector2.ZERO, 1.0, c)
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


func _ring_ellipse(cx: float, cy: float, w: float, h: float, c: Color, width: float) -> void:
	draw_set_transform(Vector2(cx, cy), 0, Vector2(w / 2.0, h / 2.0))
	draw_arc(Vector2.ZERO, 1.0, 0, TAU, 28, c, width / max(w, h) * 2.0)
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)
