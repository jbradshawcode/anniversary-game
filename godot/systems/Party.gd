# Follower party — the crew trailing the player two-abreast. Ported from
# systems/party.py: a breadcrumb trail of real tiles; followers target staggered
# points along it, the flanking column stepping onto a perpendicular tile (or
# falling into single file where that's blocked). Followers obey the same solid
# tiles the player does but are never in any scene's tile map, so they can't jam it.
class_name Party
extends RefCounted

var followers: Array = []
var _trail: Array = []          # Array[Vector2i] of real tiles the player walked
var _last_tile: Vector2i
var _following := false
var _sm                         # SceneManager (walkability source)
var _layer: Node2D              # parent for the follower nodes (persists across scenes)


func _init(layer: Node2D, scene_manager) -> void:
	_layer = layer
	_sm = scene_manager


func active() -> bool:
	return not followers.is_empty()


# roster: Array of {tee: Color, name: String}
func form(player, roster: Array) -> void:
	for spec in roster:
		var f := Follower.new(player.tile_x, player.tile_y, spec["tee"])
		f.display_name = spec.get("name", "")
		_layer.add_child(f)
		f.position = player.position
		followers.append(f)
	_seed(player)
	_following = true


func on_scene_change(player) -> void:
	if followers.is_empty():
		return
	for f in followers:
		f.position = player.position
		f.tile_x = player.tile_x
		f.tile_y = player.tile_y
		f.queue_redraw()
	_seed(player)
	_following = true


func _seed(player) -> void:
	_trail = [Vector2i(player.tile_x, player.tile_y)]
	_last_tile = Vector2i(player.tile_x, player.tile_y)


func update(dt: float, player) -> void:
	if not _following or followers.is_empty():
		return
	var cur := Vector2i(player.tile_x, player.tile_y)
	if cur != _last_tile:
		_trail.append(cur)
		_last_tile = cur
		var ranks := (followers.size() - 1) / 2 + 1
		var cap := ranks + 3
		if _trail.size() > cap:
			_trail = _trail.slice(_trail.size() - cap)

	for i in range(followers.size()):
		var f = followers[i]
		var rank := i / 2          # two abreast: a trail column + a flank
		var member := i % 2
		var idx := _trail.size() - 2 - rank
		if idx < 0:
			idx = 0
		var target: Vector2i = _trail[idx]
		if member == 1:
			var perp := _perp_tile(idx)
			var cand := target + perp
			if _walkable_tile(cand):
				target = cand
			else:
				target = _trail[maxi(0, idx - 1)]
		_step(f, _tile_center(target), dt)
		f.queue_redraw()


func _tile_center(t: Vector2i) -> Vector2:
	var ts := Config.TILE_SIZE
	return Vector2(t.x * ts + ts / 2, t.y * ts + ts / 2)


func _perp_tile(idx: int) -> Vector2i:
	var a: Vector2i = _trail[idx]
	var b: Vector2i
	if idx > 0:
		b = _trail[idx - 1]
	elif idx + 1 < _trail.size():
		b = _trail[idx + 1]
	else:
		b = a
	var d := a - b
	if d.x != 0 and d.y == 0:
		return Vector2i(0, 1)   # heading horizontally -> flank vertically
	if d.y != 0 and d.x == 0:
		return Vector2i(1, 0)   # heading vertically -> flank horizontally
	return Vector2i(0, 1)


func _walkable_tile(t: Vector2i) -> bool:
	var sc = _sm.current
	return sc == null or sc.is_walkable(t.x, t.y)


func _walkable_px(px: float, py: float) -> bool:
	var sc = _sm.current
	if sc == null:
		return true
	return sc.is_walkable(int(px) / Config.TILE_SIZE, int(py) / Config.TILE_SIZE)


func _step(f: Follower, target: Vector2, dt: float) -> void:
	var d := target - f.position
	var dist := d.length()
	if dist < 0.5:                         # arrived -> rest exactly on the tile
		f.position = target
		f.tile_x = int(f.position.x) / Config.TILE_SIZE
		f.tile_y = int(f.position.y) / Config.TILE_SIZE
		f.walking = false
		return

	if absf(d.x) >= absf(d.y):             # face the way we're walking
		f.facing = "right" if d.x > 0 else "left"
	else:
		f.facing = "down" if d.y > 0 else "up"

	# Catch up when lagging (e.g. after waiting at a crossing).
	var speed := Config.TILE_MOVE_SPEED * (1.7 if dist > Config.TILE_SIZE * 2.2 else 1.0)
	var step := speed * dt
	var nx: float
	var ny: float
	var moved: float
	if step >= dist:
		nx = target.x
		ny = target.y
		moved = dist
	else:
		nx = f.position.x + d.x / dist * step
		ny = f.position.y + d.y / dist * step
		moved = step

	# Never step from valid ground into a solid tile; slide along the free axis.
	if not _walkable_px(nx, ny) and _walkable_px(f.position.x, f.position.y):
		if _walkable_px(nx, f.position.y):
			ny = f.position.y
		elif _walkable_px(f.position.x, ny):
			nx = f.position.x
		else:
			nx = f.position.x
			ny = f.position.y
			moved = 0.0

	f.position = Vector2(nx, ny)
	f.tile_x = int(f.position.x) / Config.TILE_SIZE
	f.tile_y = int(f.position.y) / Config.TILE_SIZE
	f.walking = moved > 0
	f.walk_phase += moved * 0.2
