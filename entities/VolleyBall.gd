# Volleyball with a deterministic parabolic arc (top-down + height z).
# Port of entities/volleyball/ball.py. An arc is fully determined at launch
# (start/end/peak/duration), so the landing point is known exactly. The node sits
# at the origin and draws everything in court-space coords (matching pygame).
class_name VolleyBall
extends Node2D

const _BALL := Color8(240, 228, 120)
const _BALL_SH := Color8(206, 188, 86)
const _BALL_HI := Color8(253, 250, 214)
const _BALL_LN := Color8(70, 60, 30)
const _TRAIL := Color8(252, 246, 196)

var x := 320.0
var y := 380.0
var z := 0.0
var start := Vector2(320, 380)
var end := Vector2(320, 380)
var peak := 0.0
var t := 1.0
var duration := 1.0
var team := 0
var in_flight := false
var spin := 0.0
var trail: Array[Vector2] = []          # most-recent first, capped at 8


func launch(s: Vector2, e: Vector2, pk: float, dur: float) -> void:
	start = s
	end = e
	peak = pk
	duration = max(0.05, dur)
	t = 0.0
	in_flight = true
	trail.clear()
	_recompute()


func hold_at(hx: float, hy: float) -> void:
	x = hx
	y = hy
	z = 0.0
	in_flight = false
	trail.clear()


func _recompute() -> void:
	x = start.x + (end.x - start.x) * t
	y = start.y + (end.y - start.y) * t
	z = 4.0 * peak * t * (1.0 - t)


func update(dt: float) -> void:
	if not in_flight:
		return
	trail.push_front(Vector2(x, y - z))
	if trail.size() > 8:
		trail.resize(8)
	spin += dt * 14.0
	t += dt / duration
	if t >= 1.0:
		t = 1.0
		in_flight = false
	_recompute()


func landing_point() -> Vector2:
	return end


# Seconds until the ball reaches its landing point.
func remaining() -> float:
	return max(0.0, (1.0 - t) * duration)


func _draw() -> void:
	# soft shadow on the floor — wider + fainter the higher the ball is
	var sr := 7.0 + z / 10.0
	var alpha := maxf(40.0, 120.0 - z / 2.0) / 255.0
	_ellipse(x, y - sr / 4.0, sr, sr / 2.0, Color(18.0 / 255, 40.0 / 255, 58.0 / 255, alpha))
	if in_flight:
		var n: int = max(1, trail.size())
		for i in trail.size():
			var p: Vector2 = trail[i]
			var r: float = max(1, 5 - i)
			var a := 130.0 * (1.0 - float(i) / n) / 255.0
			draw_circle(p, r, Color(_TRAIL.r, _TRAIL.g, _TRAIL.b, a))
	var bx := x
	var by := y - z
	draw_circle(Vector2(bx, by), 7, _BALL_SH)
	draw_circle(Vector2(bx, by), 6, _BALL)
	draw_circle(Vector2(bx - 2, by - 2), 3, _BALL_HI)
	var ca := cos(spin)
	var sa := sin(spin)
	draw_line(Vector2(bx - 5 * ca, by - 5 * sa), Vector2(bx + 5 * ca, by + 5 * sa), _BALL_LN, 1)
	draw_arc(Vector2(bx, by), 7, 0, TAU, 20, _BALL_LN, 1)


# pygame ellipse: centre (cx,cy), half-extents (rx,ry).
func _ellipse(cx: float, cy: float, rx: float, ry: float, c: Color) -> void:
	draw_set_transform(Vector2(cx, cy), 0, Vector2(rx, ry))
	draw_circle(Vector2.ZERO, 1.0, c)
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)
