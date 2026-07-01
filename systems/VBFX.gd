# Lightweight visual juice — particles + screen-shake. Port of systems/fx.py.
# Cosmetic only; uses its own seeded RNG so the gameplay RNG stays independent.
class_name VBFX
extends RefCounted

class Particle:
	var x: float
	var y: float
	var vx: float
	var vy: float
	var life: float
	var max_life: float
	var size: float
	var color: Color
	var gravity: float

	func _init(px, py, pvx, pvy, l, sz, c, g) -> void:
		x = px
		y = py
		vx = pvx
		vy = pvy
		life = l
		max_life = l
		size = sz
		color = c
		gravity = g

	func update(dt: float) -> void:
		vy += gravity * dt
		x += vx * dt
		y += vy * dt
		life -= dt


var _rng := RandomNumberGenerator.new()
var particles: Array[Particle] = []
var _shake_mag := 0.0
var _shake_t := 0.0
var _shake_dur := 0.0
var _ox := 0.0
var _oy := 0.0


func _init() -> void:
	_rng.seed = 20260531


func emit_burst(x: float, y: float, color: Color, count := 12, speed := 160.0) -> void:
	for _i in count:
		var ang := _rng.randf_range(0, TAU)
		var spd := _rng.randf_range(0.35, 1.0) * speed
		particles.append(Particle.new(
			x, y, cos(ang) * spd, sin(ang) * spd,
			_rng.randf_range(0.25, 0.5), _rng.randf_range(2, 4), color, 320.0))


func emit_dust(x: float, y: float, count := 8) -> void:
	for _i in count:
		var ang := _rng.randf_range(-PI, 0)        # upward fan
		var spd := _rng.randf_range(20, 70)
		particles.append(Particle.new(
			x, y, cos(ang) * spd, sin(ang) * spd,
			_rng.randf_range(0.3, 0.6), _rng.randf_range(2, 3),
			Color8(210, 214, 220), 120.0))


func shake(mag: float, dur: float) -> void:
	if mag > _shake_mag:
		_shake_mag = mag
	_shake_dur = max(_shake_dur, dur)
	_shake_t = _shake_dur


func update(dt: float) -> void:
	for p in particles:
		p.update(dt)
	particles = particles.filter(func(p): return p.life > 0)
	if _shake_t > 0:
		_shake_t -= dt
		var k: float = max(0.0, _shake_t / _shake_dur) if _shake_dur else 0.0
		var amp := _shake_mag * k
		_ox = _rng.randf_range(-amp, amp)
		_oy = _rng.randf_range(-amp, amp)
	else:
		_shake_mag = 0.0
		_ox = 0.0
		_oy = 0.0


func offset() -> Vector2:
	return Vector2(int(_ox), int(_oy))


func draw(canvas: CanvasItem) -> void:
	for p in particles:
		var a: float = clampf(p.life / p.max_life, 0.0, 1.0)
		var s: float = max(1, int(p.size * (0.4 + 0.6 * a)))
		canvas.draw_circle(Vector2(p.x, p.y), s, p.color)
