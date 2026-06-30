# Menu navigation + save/load sub-state machine. Port of systems/menu_flow.py.
#
# Owns where you are in the title/pause menu tree and the slot save/load flow,
# rebuilding the shared Menu node as you navigate and firing terminal effects
# back through a context Dictionary of Callables.
#
# Roots:
#   "title" — New Game / Load Game / Quit
#   "pause" — Resume / Save Game / Quit to Title / Quit to Desktop
#
# ctx must provide Callables: start_new, load_slot(slot), save_to_slot(slot),
# resume, open_title, quit_game.
class_name MenuFlow
extends RefCounted

const _TITLE_HINT := "Arrows = move   Z = select   X = back"
const _PAUSE_HINT := "Z = select   X / Esc = back"

var _root: String                      # "title" or "pause"
var _ctx: Dictionary
var _menu: Menu
var _save: SaveManager
var _state := "root"                   # "root" | "save" | "load" | "slot_action"
var _slot_target := 0
var _slot_source := ""


func _init(root: String, ctx: Dictionary, menu: Menu, save_mgr: SaveManager) -> void:
	_root = root
	_ctx = ctx
	_menu = menu
	_save = save_mgr
	_open_root()


func at_root() -> bool:
	return _state == "root"


# ── input (driven by Main's _unhandled_input) ───────────────────────────────────
func move(delta: int) -> void:
	_menu.move(delta)


func select() -> void:
	_select(_menu.index)


func back() -> void:
	_back()


# ── navigation ──────────────────────────────────────────────────────────────────
func _select(i: int) -> void:
	if _state == "root":
		_select_root(i)
	elif _state == "save" or _state == "load":
		_select_slot(i)
	else:
		_select_slot_action(i)


func _select_root(i: int) -> void:
	if _root == "title":
		match i:
			0: _ctx["start_new"].call()
			1: _open_slots("load")
			2: _ctx["quit_game"].call()
	else:
		match i:
			0: _ctx["resume"].call()
			1: _open_slots("save")
			2: _ctx["open_title"].call()
			3: _ctx["quit_game"].call()


# Slots offered this screen: the autosave shows in Load only (never Save).
func _slot_ids() -> Array:
	if _state == "load" and _save.has(SaveManager.AUTOSAVE):
		return [SaveManager.AUTOSAVE] + SaveManager.SLOTS
	return SaveManager.SLOTS.duplicate()


func _select_slot(i: int) -> void:
	var ids := _slot_ids()
	if i >= ids.size():                  # the trailing "Back"
		_back()
		return
	var slot: int = ids[i]
	if _save.has(slot):
		_open_slot_action(slot, _state)
	elif _state == "save":               # empty slot: save straight in
		_ctx["save_to_slot"].call(slot)
		_open_root()


func _select_slot_action(i: int) -> void:
	var slot := _slot_target
	if i == 0:                           # Load / Overwrite
		if _slot_source == "load":
			_ctx["load_slot"].call(slot)
		else:
			_ctx["save_to_slot"].call(slot)
			_open_root()
	elif i == 1:                         # Delete
		_save.delete(slot)
		_open_slots(_slot_source)
	else:                                # Back
		_open_slots(_slot_source)


func _back() -> void:
	if _state == "save" or _state == "load":
		_open_root()
	elif _state == "slot_action":
		_open_slots(_slot_source)
	elif _root == "pause":               # at root
		_ctx["resume"].call()
	else:                                # title root
		_ctx["quit_game"].call()


# ── menu builders ────────────────────────────────────────────────────────────────
func _open_root() -> void:
	_state = "root"
	if _root == "title":
		_menu.open("The Story of Us", ["New Game", "Load Game", "Quit"], _select, _TITLE_HINT)
	else:
		_menu.open("Paused", ["Resume", "Save Game", "Quit to Title", "Quit to Desktop"],
			_select, _PAUSE_HINT)


func _open_slots(state: String) -> void:
	_state = state                       # "save" or "load"
	var title := "Save Game" if state == "save" else "Load Game"
	_menu.open(title, _slot_labels() + ["Back"], _select)


func _open_slot_action(slot: int, source: String) -> void:
	_slot_target = slot
	_slot_source = source
	_state = "slot_action"
	var verb := "Load" if source == "load" else "Overwrite"
	var nm := "Autosave" if slot == SaveManager.AUTOSAVE else "Slot %d" % slot
	_menu.open(nm, [verb, "Delete", "Back"], _select)


func _slot_labels() -> Array:
	var labels: Array = []
	for slot in _slot_ids():
		var nm := "Autosave" if slot == SaveManager.AUTOSAVE else "Slot %d" % slot
		var info = _save.slot_info(slot)
		if info != null:
			labels.append("%s: %s  %s" % [nm, info["scene_name"], info["saved_at"]])
		else:
			labels.append("%s: Empty" % nm)
	return labels
