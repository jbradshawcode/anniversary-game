# Save slots — small JSON files under user://. Port of systems/save.py.
# A save holds where the player is (scene + tile + facing) and the story state
# (beat + flags), plus display labels for a slot menu.
class_name SaveManager
extends RefCounted

const SLOTS := [1, 2, 3]
const AUTOSAVE := 0           # written at each chapter start; load-only in the menu

var _story
var _sm
var _player

# Display labels for the slot menu, by Godot scene id (see Main's _sm.register order).
var _scene_names := {
	1: "Gym", 2: "King Street", 3: "The Salutation", 4: "Beer Garden",
	5: "Corridor", 6: "Reception", 7: "Courtyard", 8: "Passage",
	9: "Netball Courts", 10: "Wetherspoons", 11: "Volleyball", 12: "Diving",
}


func bind(story, scene_manager, player) -> void:
	_story = story
	_sm = scene_manager
	_player = player


func _path(slot: int) -> String:
	return "user://slot%d.json" % slot


func scene_title(scene_id: int) -> String:
	return _scene_names.get(scene_id, "Scene %d" % scene_id)


func has(slot: int) -> bool:
	return FileAccess.file_exists(_path(slot))


func save(slot: int, completed := false) -> void:
	var snap: Dictionary = _story.snapshot()
	var data := {
		"scene_id": _sm.current_id(),
		"tile": [_player.tile_x, _player.tile_y],
		"facing": _player.facing,
		"beat": snap["beat"],
		"flags": snap["flags"],
		"vb_attempts": snap.get("vb_attempts", 0),
		"scene_name": _scene_names.get(_sm.current_id(), "?"),
		"beat_name": _story.beat().get("name", "?"),
		"saved_at": Time.get_datetime_string_from_system(false, true),
	}
	if completed:
		data["completed"] = true
	var f := FileAccess.open(_path(slot), FileAccess.WRITE)
	f.store_string(JSON.stringify(data, "\t"))
	f.close()


# Delete a slot, keeping a timestamped backup under user://deleted/ (mirror of save.py).
func delete(slot: int) -> void:
	if not has(slot):
		return
	DirAccess.make_dir_recursive_absolute("user://deleted")
	var stamp := Time.get_datetime_string_from_system(false, false).replace(":", "").replace("-", "").replace("T", "-")
	var backup := "user://deleted/slot%d-%s.json" % [slot, stamp]
	DirAccess.rename_absolute(_path(slot), backup)


func load_slot(slot: int):
	if not has(slot):
		return null
	var f := FileAccess.open(_path(slot), FileAccess.READ)
	var txt := f.get_as_text()
	f.close()
	var data = JSON.parse_string(txt)
	return data if data is Dictionary else null


# Display summary for a slot menu, or null if empty.
func slot_info(slot: int):
	var data = load_slot(slot)
	if data == null:
		return null
	return {
		"scene_name": data.get("scene_name", "?"),
		"beat_name": data.get("beat_name", "?"),
		"saved_at": data.get("saved_at", ""),
	}


func apply(data: Dictionary) -> void:
	_story.restore(int(data["beat"]), data["flags"], int(data["scene_id"]))
	_story.vb_attempts = int(data.get("vb_attempts", 0))
	var tile: Array = data["tile"]
	_sm.go_to(int(data["scene_id"]), _player, Vector2i(int(tile[0]), int(tile[1])))
	_player.facing = data["facing"]
	_player.queue_redraw()
	if _story.has_method("sync_party"):   # rebuild the follower crew for this beat
		_story.sync_party(_player)
