# Save slots — small JSON files under user://. Port of systems/save.py.
# A save holds where the player is (scene + tile + facing) and the story state
# (beat + flags), plus display labels for a slot menu.
class_name SaveManager
extends RefCounted

const SLOTS := [1, 2, 3]

var _story
var _sm
var _player

var _scene_names := {1: "Sports Hall", 5: "Corridor", 6: "King Street"}


func bind(story, scene_manager, player) -> void:
	_story = story
	_sm = scene_manager
	_player = player


func _path(slot: int) -> String:
	return "user://slot%d.json" % slot


func has(slot: int) -> bool:
	return FileAccess.file_exists(_path(slot))


func save(slot: int) -> void:
	var snap: Dictionary = _story.snapshot()
	var data := {
		"scene_id": _sm.current_id(),
		"tile": [_player.tile_x, _player.tile_y],
		"facing": _player.facing,
		"beat": snap["beat"],
		"flags": snap["flags"],
		"scene_name": _scene_names.get(_sm.current_id(), "?"),
		"beat_name": _story.beat().get("name", "?"),
		"saved_at": Time.get_datetime_string_from_system(false, true),
	}
	var f := FileAccess.open(_path(slot), FileAccess.WRITE)
	f.store_string(JSON.stringify(data, "\t"))
	f.close()


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
	_story.restore(int(data["beat"]), data["flags"])
	var tile: Array = data["tile"]
	_sm.go_to(int(data["scene_id"]), _player, Vector2i(int(tile[0]), int(tile[1])))
	_player.facing = data["facing"]
	_player.queue_redraw()
