# Story state — ordered beats advanced by flags. Scoped port of systems/story.py:
# the core progression loop (beats, flags, advance_when), beat-enter cutscenes,
# scene-enter triggers, and exit gating. (Deferred from the original: minigame
# launches, phone interludes, week-end results, checklist beats, party directives,
# goto/jump, the seated-pub restore, dev jumps.)
#
# A beat is a Dictionary:
#   name           : String
#   cutscene       : [steps]            run on beat-enter (its ['flag', ...] advances)
#   advance_when   : flag that moves to the next beat
#   on_enter_scene : {scene_id: [lines]} one-shot line when that scene is entered
#   advance_on_enter: scene_id          entering it sets advance_when
#   door_block     : {dest_scene_id: [lines]}  one barred door (blocks + message)
#   locked_exits   : {scene_id: "all"|[dirs]}  blocked edges (+ locked_msg)
class_name StoryManager
extends RefCounted

var flags := {}

var _beats: Array
var _beat := 0
var _fired := {}
var _dialogue
var _sm
var _player
var _party
var _cutscene


func _init(beats: Array) -> void:
	_beats = beats


func bind(dialogue, scene_manager, player, party, cutscene) -> void:
	_dialogue = dialogue
	_sm = scene_manager
	_player = player
	_party = party
	_cutscene = cutscene


func beat() -> Dictionary:
	return _beats[_beat]


func has(flag: String) -> bool:
	return flags.has(flag)


func set_flag(name) -> void:
	if name == null or name == "":
		return
	flags[name] = true
	_check_advance()


func _check_advance() -> void:
	while _beat < _beats.size() - 1:
		var need = beat().get("advance_when", "")
		if need != "" and flags.has(need):
			_beat += 1
			_enter_beat()
		else:
			break


func begin() -> void:
	_enter_beat()


func _enter_beat() -> void:
	var b := beat()
	var cs = b.get("cutscene", null)
	if cs != null and _cutscene != null:
		_cutscene.start(cs)
		return
	notify_enter(_sm.current_id())


func notify_enter(scene_id: int) -> void:
	var b := beat()
	var lines = b.get("on_enter_scene", {}).get(scene_id, null)
	if lines != null:
		var key := [_beat, scene_id]
		if not _fired.has(key):
			_fired[key] = true
			if _dialogue != null:
				_dialogue.start(lines)
	if b.get("advance_on_enter", -1) == scene_id:
		set_flag(b.get("advance_when", ""))


func gate_exit(scene_id: int, direction: String, dest_scene_id) -> String:
	var b := beat()
	var door = b.get("door_block", {}).get(dest_scene_id, null)
	if door != null:
		_say(door)
		return "block"
	var locked = b.get("locked_exits", {}).get(scene_id, null)
	if locked != null and (locked == "all" or direction in locked):
		_say(b.get("locked_msg", []))
		return "block"
	return "pass"


func _say(lines) -> void:
	if lines and _dialogue != null and not _dialogue.active:
		_dialogue.start(lines)


# ── save / load ───────────────────────────────────────────────────────────────
func snapshot() -> Dictionary:
	return {"beat": _beat, "flags": flags.keys()}


func restore(beat: int, flag_list) -> void:
	_beat = clampi(beat, 0, _beats.size() - 1)
	flags = {}
	for fl in flag_list:
		flags[fl] = true
	_fired = {}
