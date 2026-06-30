# Owns the active scene and exit transitions — ported from systems/scene_manager.py.
# Scenes are persistent nodes; only the current one is parented under `_world`, so
# each scene's children (NPCs, lights) come and go with it. Exits are wired by id;
# scenes never reference each other.
class_name SceneManager
extends RefCounted

var current: GameScene
var story = null                 # optional StoryManager: gates exits + scene-enter
var party = null                 # optional Party: crew/followers block movement too
var _current_id: int = -1
var _scenes: Dictionary = {}
var _world: Node2D


func _init(world: Node2D) -> void:
	_world = world


func current_id() -> int:
	return _current_id


func register(scene_id: int, scene: GameScene) -> void:
	_scenes[scene_id] = scene


func get_scene(scene_id: int):
	return _scenes.get(scene_id, null)


func start(scene_id: int, player) -> void:
	_current_id = scene_id
	current = _scenes[scene_id]
	_world.add_child(current)
	player.scene = current


# One tile-step request: an exit step transitions scenes, otherwise a normal move.
func try_move(dtx: int, dty: int, player) -> void:
	if player.moving:
		return

	var exit_dir := ""
	if dtx == 1 and player.tile_x >= current.walkable_cols.y:
		exit_dir = "right"
	elif dtx == -1 and player.tile_x <= current.walkable_cols.x:
		exit_dir = "left"
	elif dty == 1 and player.tile_y >= current.walkable_rows.y:
		exit_dir = "down"
	elif dty == -1 and player.tile_y <= current.walkable_rows.x:
		exit_dir = "up"

	if exit_dir != "" and current.exits.has(exit_dir):
		var res := _resolve_exit(current.exits[exit_dir], player)
		if res[0] != null:
			if story != null:
				var verdict: String = story.gate_exit(_current_id, exit_dir, res[0])
				if verdict == "block":
					return
				if verdict == "end_week":
					story.trigger_week_end()   # leaving ends the chapter; no transition
					return
			_transition_to(res[0], player, exit_dir, res[1])
			return

	if _occupied(player.tile_x + dtx, player.tile_y + dty):
		return                         # a person is solid — can't walk through crew/NPCs
	player.try_move(dtx, dty, current)


# A crew member or scene NPC occupies this tile (solid whatever their state).
func _occupied(tx: int, ty: int) -> bool:
	if current != null:
		for o in current.npcs:
			if o.tile_x == tx and o.tile_y == ty:
				return true
	if party != null:
		for f in party.followers:
			if f.tile_x == tx and f.tile_y == ty:
				return true
	return false


# Hard jump to a scene + tile (load, chapter jump) — bypasses exit gating.
func go_to(scene_id: int, player, tile: Vector2i) -> void:
	if not _scenes.has(scene_id):
		return
	if current != null:
		_world.remove_child(current)
	_current_id = scene_id
	current = _scenes[scene_id]
	_world.add_child(current)
	player.scene = current
	player.place(tile.x, tile.y)


func _resolve_exit(exit_val, player) -> Array:
	if exit_val == null:
		return [null, null]
	if exit_val is Dictionary:
		if exit_val.has("cols"):
			var cols: Vector2i = exit_val["cols"]
			if not (cols.x <= player.tile_x and player.tile_x <= cols.y):
				return [null, null]
		if exit_val.has("rows"):
			var rows: Vector2i = exit_val["rows"]
			if not (rows.x <= player.tile_y and player.tile_y <= rows.y):
				return [null, null]
		return [exit_val["scene"], exit_val.get("target", null)]
	return [exit_val, null]


func _transition_to(new_id, player, exit_dir: String, entry_pos) -> void:
	if not _scenes.has(new_id):
		return  # neighbour not ported yet — stay put rather than crash

	_world.remove_child(current)
	_current_id = new_id
	current = _scenes[new_id]
	_world.add_child(current)
	player.scene = current

	var pos = entry_pos
	if pos == null:
		pos = current.entry_points.get(exit_dir, null)
	if pos == null:
		var mid_col := (current.walkable_cols.x + current.walkable_cols.y) / 2
		var mid_row := (current.walkable_rows.x + current.walkable_rows.y) / 2
		match exit_dir:
			"right":
				pos = Vector2i(current.walkable_cols.x, mid_row)
			"left":
				pos = Vector2i(current.walkable_cols.y, mid_row)
			"down":
				pos = Vector2i(mid_col, current.walkable_rows.x)
			"up":
				pos = Vector2i(mid_col, current.walkable_rows.y)
	player.place(pos.x, pos.y)
