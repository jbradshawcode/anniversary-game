# Story state — the single source of truth for beats, flags and movement gating.
# Faithful port of systems/story.py: the weeks are flattened to an ordered beat
# list, advanced by flags; this manager is consulted at a few hook points (exit
# gating in SceneManager; interaction/reach/talk in Main) and is bound once to the
# DialogueBox / SceneManager / Player / Party / Cutscene so it can drive dialogue,
# scene jumps and the follower crew. Minigame launches, phone interludes and the
# week/chapter/end-game cards are delegated to host callbacks (stubbed in Main
# until those systems land).
#
# A beat is a Dictionary; the fields the screenplay uses:
#   name / objective / advance_when
#   cutscene        : [steps]                run on beat-enter (its ['flag',...] advances)
#   checklist       : {Vector2i: item}       "check N things in any order" beat
#   goto            : {scene:int, tile:Vector2i}   relocate the player on enter
#   party           : "form" | {"form":[names]}    summon the crew (optionally excluding)
#   settle_party    : bool                   crew stays put as you leave
#   absent          : [names]                crew not present this chapter (week-level)
#   locked_exits    : {scene_id: "all"|[dirs]}     blocked edges (+ locked_msg)
#   door_block      : {dest_scene_id: [lines]}     one barred door
#   advance_on_enter: scene_id               entering it sets advance_when
#   end_week        : direction              leaving that way ends the chapter
#   end_chapter / end_game : bool            straight to the results / closing card
#   launch_volleyball / launch_dive : bool   hand off to a minigame
#   phone / phone_with / card_date           a texts-only interlude
#   hide_player     : bool                   hide Sarah's sprite (someone else's POV)
#   talk            : {name: [lines]}        speak to a seated follower
#   interact_ask    : {who, steps}           talk to a named NPC to fire a choice cutscene
class_name StoryManager
extends RefCounted

# Pub seats: two rows of four facing each other across the Ch1 left booth, in
# WEEK1_CREW order [James, Dan, Matt, Nat, Bailey, Mayu, Wallace] — so a load into
# a seated beat restores the same table the queue cutscene leaves behind.
const PUB_SEATS := [Vector2i(11, 9), Vector2i(12, 11), Vector2i(13, 11), Vector2i(13, 9),
	Vector2i(10, 9), Vector2i(11, 11), Vector2i(10, 11)]
const SARAH_PUB_SEAT := Vector2i(12, 9)
const _SEATED_BEATS := ["pub_queue", "gifts", "where_from", "wind_down"]
const PUB_DRINKS := {"James": "beer", "Dan": "beer", "Matt": "beer", "Wallace": "beer",
	"Nat": "white_wine", "Bailey": "cider", "Mayu": "white_wine"}

var flags := {}
var vb_attempts := 0           # volleyball matches played this chapter -> results-card stars

# Host callbacks (set by Main); stubbed until the real systems land. Each is a
# Callable; the host reads beat() for the details it needs and sets the beat's
# advance flag when its placeholder finishes.
var on_launch_vb := Callable()
var on_launch_dive := Callable()
var on_week_end := Callable()
var on_phone := Callable()
var on_chapter_start := Callable()   # (week:int, title:String, first:bool)

var _beats: Array = []
var _beat := 0
var _fired := {}
var _cur_week = null                 # last week entered, to spot chapter changes
var _dialogue
var _sm
var _player
var _party
var _cutscene


func _init(weeks: Array) -> void:
	_beats = _flatten(weeks)


func _flatten(weeks: Array) -> Array:
	var out: Array = []
	for w in weeks:
		for b in w["beats"]:
			var beat: Dictionary = b.duplicate()
			beat["week"] = w["week"]
			beat["week_title"] = w["title"]
			beat["absent"] = w.get("absent", [])
			out.append(beat)
	return out


func bind(dialogue, scene_manager, player, party, cutscene) -> void:
	_dialogue = dialogue
	_sm = scene_manager
	_player = player
	_party = party
	_cutscene = cutscene


func beat() -> Dictionary:
	return _beats[_beat]


func index_of(name: String) -> int:
	for i in range(_beats.size()):
		if _beats[i].get("name", "") == name:
			return i
	return -1


func week_title():
	return beat().get("week_title", null)


func stars() -> int:
	return Config.stars_for_attempts(maxi(1, vb_attempts))


func objective():
	var text = beat().get("objective", null)
	var checklist = beat().get("checklist", null)
	if text != null and checklist != null:
		var done := 0
		for it in checklist.values():
			if flags.has(it["flag"]):
				done += 1
		return "%s (%d/%d)" % [text, done, checklist.size()]
	return text


func has(flag: String) -> bool:
	return flags.has(flag)


func can_talk() -> bool:
	return not beat().get("talk", {}).is_empty()


func interactable_at(tx: int, ty: int) -> bool:
	var cl = beat().get("checklist", null)
	return cl != null and cl.has(Vector2i(tx, ty))


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


# New game: reset to the first beat with no week entered yet, so begin() fires the
# opening chapter card (restore() deliberately syncs _cur_week, suppressing it).
func start_new() -> void:
	restore(0, [])
	vb_attempts = 0
	_cur_week = null
	_enter_beat()


func _enter_beat() -> void:
	var b := beat()
	# A drink lives in hand only between the bar and a seat: a beat that isn't a
	# seated pub beat means Sarah isn't carrying one (e.g. a new chapter).
	if _player != null and not (b.get("name", "") in _SEATED_BEATS):
		_player.carry("")
	if _player != null:
		_player.visible = not b.get("hide_player", false)

	var goto = b.get("goto", null)
	if goto != null and _sm != null and _player != null:
		_sm.go_to(int(goto["scene"]), _player, goto.get("tile", Vector2i(_player.tile_x, _player.tile_y)))
	_remove_absent()
	_apply_party(b.get("party", null))
	if b.get("settle_party", false) and _party != null:
		_party.stop_following()

	var week = b.get("week", null)
	if week != null and week != _cur_week:
		var first := _cur_week == null
		_cur_week = week
		if on_chapter_start.is_valid():
			on_chapter_start.call(week, b.get("title", b.get("week_title", "")), first)

	if b.get("launch_volleyball", false) and on_launch_vb.is_valid():
		on_launch_vb.call()
		return
	if b.get("launch_dive", false) and on_launch_dive.is_valid():
		on_launch_dive.call()
		return
	if b.get("end_chapter", false) and on_week_end.is_valid():
		on_week_end.call()                       # straight to the results card
		return
	if b.get("phone", null) != null and on_phone.is_valid():   # end_game flows through here too
		on_phone.call(b["phone"], b.get("phone_with", "Sarah"),
			b.get("advance_when", ""), b.get("week_title", "Interlude"), b.get("card_date", ""))
		return
	var cutscene = b.get("cutscene", null)
	if cutscene != null and _cutscene != null:
		_cutscene.start(cutscene)
		return
	if _sm != null:
		notify_enter(_sm.current_id())


func _remove_absent() -> void:
	if _sm == null:
		return
	var absent = beat().get("absent", [])
	if absent.is_empty():
		return
	var gym = _sm.get_scene(1)
	if gym != null and gym.has_method("remove_named"):
		gym.remove_named(absent)


func _apply_party(directive) -> void:
	if _party == null or directive == null:
		return
	if directive is String and directive == "form":
		_party.form(_player, Party.week1_crew())
	elif directive is Dictionary and directive.has("form"):
		_party.form(_player, Party.week1_crew(), directive["form"])


func gate_exit(scene_id, direction: String, dest_scene_id) -> String:
	var b := beat()
	var door = b.get("door_block", {}).get(dest_scene_id, null)
	if door != null:
		_say(door)
		return "block"
	var locked = b.get("locked_exits", {}).get(scene_id, null)
	if locked != null and ((locked is String and locked == "all") or (locked is Array and direction in locked)):
		_say(b.get("locked_msg", []))
		return "block"
	if b.get("end_week", "") == direction:
		return "end_week"
	return "pass"


func _say(lines) -> void:
	if lines and _dialogue != null and not _dialogue.active:
		_dialogue.start(lines)


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


func trigger_week_end() -> void:
	if on_week_end.is_valid():
		on_week_end.call()


# ── interaction (talk / check) ──────────────────────────────────────────────────
# What the player faced: a tile (for checklists, which key off the basket/crew tile)
# and the NPC display name there, if any (for interact_ask). Returns true if the
# interaction was consumed (a line shown / a cutscene started).
func interact(tx: int, ty: int, name := "") -> bool:
	var b := beat()
	var checklist = b.get("checklist", null)
	if checklist != null:
		return _interact_checklist(tx, ty, checklist)
	var ask = b.get("interact_ask", null)
	if (ask != null and _cutscene != null and name != ""
			and name.to_lower() == str(ask["who"]).to_lower()):
		_cutscene.start(ask["steps"])
		return true
	return false


func _interact_checklist(tx: int, ty: int, checklist: Dictionary) -> bool:
	var key := Vector2i(tx, ty)
	var item = checklist.get(key, null)
	if item == null:
		return false
	var b := beat()
	var flag: String = item["flag"]
	var spk: String = item.get("speaker", "")
	var advance = b.get("advance_when", "")

	if flags.has(flag):                          # already ticked off
		var again = b.get("checked_again", item.get("lines", ["..."]))
		if _dialogue != null:
			_dialogue.start(again, spk)
		return true

	var steps = item.get("steps", null)          # a cutscene greet — can hold a choice
	if steps != null and _cutscene != null:
		var after := func():
			flags[flag] = true
			if _checklist_complete(checklist):
				set_flag(advance)
		_cutscene.start(steps + [["call", after]])
		return true

	if _dialogue == null:
		return false
	var last := _checklist_last(checklist, item)
	var suffix = b.get("check_done", []) if last else b.get("check_more", [])
	var lines: Array = item.get("lines", []) + suffix
	var done := func():
		flags[flag] = true
		if _checklist_complete(checklist):
			set_flag(advance)
	_dialogue.start(lines, spk, done)
	return true


func _checklist_complete(checklist: Dictionary) -> bool:
	for it in checklist.values():
		if not flags.has(it["flag"]):
			return false
	return true


# Whether every OTHER item is already ticked (so this one is the last to check).
func _checklist_last(checklist: Dictionary, item) -> bool:
	for it in checklist.values():
		if it != item and not flags.has(it["flag"]):
			return false
	return true


func talk(name) -> bool:
	if _dialogue == null or name == null or name == "":
		return false
	var lines = beat().get("talk", {}).get(str(name).to_lower(), null)
	if lines == null:
		return false
	_face_crew(name)
	_dialogue.start(lines, name)
	return true


func _face_crew(name: String) -> void:
	if _party == null or _player == null:
		return
	for f in _party.followers:
		if str(f.display_name).to_lower() == name.to_lower():
			_cutscene._face_actor(f, _player)
			_cutscene._face_actor(_player, f)
			f.queue_redraw()
			_player.queue_redraw()
			break


# ── party rebuild (new game / load) ─────────────────────────────────────────────
func sync_party(player) -> void:
	if _party == null:
		return
	_party.clear()
	var cur_week = beat().get("week", null)      # crew resets each chapter
	var directive = null
	for i in range(_beat + 1):
		var b: Dictionary = _beats[i]
		if b.get("week", null) == cur_week and b.get("party", null) != null:
			directive = b.get("party")
	if directive is String and directive == "form":
		_party.form(player, Party.week1_crew())
	elif directive is Dictionary and directive.has("form"):
		_party.form(player, Party.week1_crew(), directive["form"])

	# Loading into a seated Ch1 pub beat: park the crew at their queue-cutscene
	# seats (with their drinks on the table) and seat Sarah in her chair.
	if _party.active() and (beat().get("name", "") in _SEATED_BEATS):
		for f in _party.followers:
			f.carry(PUB_DRINKS.get(f.display_name, ""))
		_party.settle(3, PUB_SEATS)
		if player != null:
			player.place(SARAH_PUB_SEAT.x, SARAH_PUB_SEAT.y)
			var drink := "white_wine"
			if flags.has("sarah_cider"):
				drink = "cider"
			elif flags.has("sarah_red"):
				drink = "red_wine"
			elif not flags.has("sarah_wine"):
				drink = ""
			player.carry(drink)
			player.sit("up" if SARAH_PUB_SEAT.y >= 10 else "down")


# ── save / load ───────────────────────────────────────────────────────────────
func snapshot() -> Dictionary:
	return {"beat": _beat, "flags": flags.keys(), "vb_attempts": vb_attempts}


func restore(beat_i: int, flag_list, scene_id = null) -> void:
	_beat = clampi(beat_i, 0, _beats.size() - 1)
	flags = {}
	for fl in flag_list:
		flags[fl] = true
	_fired = {[_beat, scene_id]: true} if scene_id != null else {}
	_cur_week = _beats[_beat].get("week", null)   # a load never re-fires the chapter card
