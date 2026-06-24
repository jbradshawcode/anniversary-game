# Scripted cutscenes — interleave dialogue, scripted actor movement and fades.
# Scoped port of systems/cutscene.py: a flat list of steps run in order, blocking
# on the current step until it completes. Verbs supported here:
#   ["say", [lines]]              dialogue (no speaker tag)
#   ["say", [lines], "Name"]      dialogue with a speaker tag (turns to face listener)
#   ["walk", who, Vector2i]       tween one actor to a tile; wait until arrived
#   ["move", {who: Vector2i,...}] tween several actors in parallel; wait for all
#   ["face", who, "down"|...]     set facing
#   ["wait", seconds]             hold
#   ["fade_out"/"fade_in", secs]  ramp the black overlay (non-blocking)
#   ["flag", name]                set a story flag
#   ["call", Callable]            run a callable once
# ask/hub choices, walkto/moveto pathfind, vanish, hold, sit/settle/sit_all,
# if_flag and game_over (inside ask) are all supported. Only the sprawled `pose`
# ART is deferred (with the dive minigame) — the verb is consumed, not drawn.
# `who` is case-insensitive: sarah/player/you -> the player, else a party follower
# or current-scene NPC matched on display name.
class_name Cutscene
extends RefCounted

const _PLAYER_NAMES := ["sarah", "player", "you"]

var active := false
var flags := {}
var on_game_over := Callable()  # set by Main: fn(lines)

var _dialogue: DialogueBox
var _sm: SceneManager
var _player
var _party: Party
var _fade: ColorRect
var _story = null
var _gen := 0          # bumped on (re)start; guards against a flag restarting us mid-loop

var _steps: Array = []
var _i := 0
var _wait := 0.0
var _movers: Array = []        # [[actor, [Vector2 waypoints]], ...]
var _await_dialogue := false
var _last_speaker := ""
var _fade_to := 0.0
var _fade_rate := 0.0
var _fader = null               # [actor, alpha_rate] for a blocking 'vanish'
var _ask_outcomes := {}
var _ask_choice := ""
var _hub_outcomes := {}
var _hub_choice := ""
var _hub_explored := {}
var _hub_ref = null


func bind(dialogue: DialogueBox, scenes: SceneManager, player, party: Party, fade: ColorRect, story = null) -> void:
	_dialogue = dialogue
	_sm = scenes
	_player = player
	_party = party
	_fade = fade
	_story = story


func start(steps: Array) -> void:
	active = true
	_gen += 1
	_steps = steps.duplicate()
	_i = 0
	_wait = 0.0
	_movers = []
	_await_dialogue = false
	_last_speaker = ""
	_fader = null
	_begin_step()


func stop() -> void:
	active = false
	_steps = []
	_movers = []
	_await_dialogue = false
	_fader = null


func _finish() -> void:
	active = false
	_steps = []
	_movers = []


# ── actor lookup ──────────────────────────────────────────────────────────────
func _resolve(who: String):
	var key := who.to_lower()
	if key in _PLAYER_NAMES:
		return _player
	for f in _party.followers:
		if str(f.display_name).to_lower() == key:
			return f
	if _sm.current != null:
		for o in _sm.current.npcs:
			if str(o.display_name).to_lower() == key:
				return o
	return null


func _present_actors() -> Array:
	var out: Array = []
	if _player != null:
		out.append(_player)
	for f in _party.followers:
		out.append(f)
	if _sm.current != null:
		for o in _sm.current.npcs:
			out.append(o)
	return out


func _nearest_actor(a):
	var best = null
	var bd := -1
	for o in _present_actors():
		if o == a:
			continue
		var d: int = (o.tile_x - a.tile_x) ** 2 + (o.tile_y - a.tile_y) ** 2
		if bd < 0 or d < bd:
			bd = d
			best = o
	return best


# Project rule: people turn to face whoever they're addressing.
func _converse(speaker: String) -> void:
	if speaker == "":
		return
	var a = _resolve(speaker)
	if a == null:
		_last_speaker = speaker
		return
	var b = null
	if _last_speaker != "" and _last_speaker.to_lower() != speaker.to_lower():
		b = _resolve(_last_speaker)
	if b == null and _player != null and a != _player:
		b = _player
	if b == null:
		b = _nearest_actor(a)
	_face_actor(a, b)
	_face_actor(b, a)
	if a != null:
		a.queue_redraw()
	if b != null:
		b.queue_redraw()
	_last_speaker = speaker


func _face_actor(a, b) -> void:
	if a == null or b == null or a == b:
		return
	var dx: int = b.tile_x - a.tile_x
	var dy: int = b.tile_y - a.tile_y
	if dx == 0 and dy == 0:
		return
	if absi(dx) >= absi(dy):
		a.facing = "right" if dx > 0 else "left"
	else:
		a.facing = "down" if dy > 0 else "up"


# ── step dispatch ─────────────────────────────────────────────────────────────
func _begin_step() -> void:
	var gen := _gen
	while true:
		if _i >= _steps.size():
			_finish()
			return
		var step: Array = _steps[_i]
		var verb: String = step[0]
		match verb:
			"say":
				var lines: Array = step[1]
				var speaker: String = step[2] if step.size() > 2 else ""
				_converse(speaker)
				_i += 1
				_await_dialogue = true
				_dialogue.start(lines, speaker, _on_dialogue_done)
				return
			"ask":
				_begin_ask(step)
				return
			"hub":
				_begin_hub(step)
				return
			"walk", "move":
				_setup_move(step)
				if not _movers.is_empty():
					return
			"walkto", "moveto":
				_setup_move(step, true)        # pathfind round solids
				if not _movers.is_empty():
					return
			"if_flag":
				_i += 1
				if _has_flag(step[1]):
					_splice(step[2])
			"vanish":
				var va = _resolve(step[1])
				_i += 1
				if va != null:
					var secs := float(step[2]) if step.size() > 2 else 0.8
					_fader = [va, (1.0 / secs) if secs > 0.0 else 1e9]
					return                     # block until faded out
			"face":
				var a = _resolve(step[1])
				if a != null:
					a.facing = step[2]
					a.queue_redraw()
				_i += 1
			"pose":
				# The sprawled-on-the-floor pose art is deferred with the dive minigame;
				# for now consume the step (turning the actor if a direction is given).
				var pa = _resolve(step[1])
				if pa != null and step.size() > 2 and step[2] is String:
					pa.facing = step[2]
					pa.queue_redraw()
				_i += 1
			"sit":
				var a = _resolve(step[1])
				if a != null and a.has_method("sit"):
					a.sit(step[2] if step.size() > 2 else "")
				_i += 1
			"hold":
				var a = _resolve(step[1])
				if a != null and a.has_method("carry"):
					a.carry(step[2])
				_i += 1
			"sit_all":
				for f in _party.followers:
					f.sit("")
				if _player != null and _player.has_method("sit"):
					_player.sit("")
				_i += 1
			"settle":
				if _party != null:
					_party.stop_following()
				_i += 1
			"wait":
				_wait = float(step[1])
				_i += 1
				if _wait > 0:
					return
			"fade_out":
				_set_fade(1.0, float(step[1]))
				_i += 1
			"fade_in":
				_fade.color.a = 1.0
				_set_fade(0.0, float(step[1]))
				_i += 1
			"flag":
				_i += 1
				if _story != null:
					_story.set_flag(step[1])   # may advance a beat -> start a new cutscene
				else:
					flags[step[1]] = true
				if _gen != gen:                # we were restarted; abandon this stale loop
					return
			"call":
				_i += 1
				step[1].call()
				if _gen != gen:
					return
			_:
				push_warning("unknown cutscene verb: " + str(verb))
				_i += 1


# ── choices (ask) ─────────────────────────────────────────────────────────────
# An outcome is ["flag", name] / ["game_over", lines] (a String-led tuple), or a
# list of steps to splice in (Array of step-Arrays), or [] to just continue.
func _begin_ask(step: Array) -> void:
	var text: String = step[1]
	var outcomes: Dictionary = step[2]
	var speaker: String = step[3] if step.size() > 3 else ""
	_converse(speaker)
	_ask_outcomes = outcomes
	_ask_choice = ""
	_i += 1
	_await_dialogue = true
	_dialogue.start([{"text": text, "choices": outcomes.keys()}], speaker,
		_on_ask_done, _on_ask_choice)


func _on_ask_choice(label: String) -> void:
	_ask_choice = label


func _on_ask_done() -> void:
	_await_dialogue = false
	var outcome = _ask_outcomes.get(_ask_choice, null)
	if outcome == null or (outcome is Array and outcome.is_empty()):
		_begin_step()
		return
	if outcome[0] is String and outcome[0] in ["flag", "game_over"]:
		if outcome[0] == "flag":
			var gen := _gen
			if _story != null:
				_story.set_flag(outcome[1])
			else:
				flags[outcome[1]] = true
			if _gen != gen:
				return
			_begin_step()
		else:
			_finish()
			if on_game_over.is_valid():
				on_game_over.call(outcome[1])
	else:                               # a list of steps spliced in here
		_splice(outcome)
		_begin_step()


# ── hub (explore-all menu) ────────────────────────────────────────────────────
func _begin_hub(step: Array) -> void:
	var text: String = step[1]
	var outcomes: Dictionary = step[2]
	var speaker: String = step[3] if step.size() > 3 else ""
	if not is_same(outcomes, _hub_ref):     # a fresh hub -> reset exploration
		_hub_ref = outcomes
		_hub_explored = {}
	var remaining: Array = []
	for label in outcomes.keys():
		if not _hub_explored.has(label):
			remaining.append(label)
	if remaining.is_empty():                # every topic seen -> move on
		_i += 1
		_begin_step()
		return
	_hub_outcomes = outcomes
	_hub_choice = ""
	_await_dialogue = true
	_dialogue.start([{"text": text, "choices": remaining}], speaker,
		_on_hub_done, _on_hub_choice)


func _on_hub_choice(label: String) -> void:
	_hub_choice = label


func _on_hub_done() -> void:
	_await_dialogue = false
	_hub_explored[_hub_choice] = true
	# Run the chosen topic, then fall back into the hub (still ahead at _i).
	_splice(_hub_outcomes.get(_hub_choice, []))
	_begin_step()


func _splice(steps: Array) -> void:
	for j in range(steps.size()):
		_steps.insert(_i + j, steps[j])


func _setup_move(step: Array, pathfind := false) -> void:
	var verb: String = step[0]
	var targets: Dictionary = {step[1]: step[2]} if (verb == "walk" or verb == "walkto") else step[1]
	_movers = []
	for who in targets:
		var actor = _resolve(who)
		if actor == null:
			continue
		if actor.has_method("stand"):
			actor.stand()                  # standing up to move; a seated drink stays put
		var dest: Vector2i = targets[who]
		var waypts: Array = []
		if pathfind:
			for t in _bfs_path(actor, dest):
				waypts.append(_tile_center(t))
		else:
			waypts.append(_tile_center(dest))
		actor.tile_x = dest.x
		actor.tile_y = dest.y
		_movers.append([actor, waypts])
	_i += 1


func _has_flag(name: String) -> bool:
	return _story.has(name) if _story != null else flags.has(name)


func _bfs_path(actor, target: Vector2i) -> Array:
	var sc = _sm.current
	if sc == null:
		return [target]
	var ts := Config.TILE_SIZE
	var start := Vector2i(int(actor.position.x) / ts, int(actor.position.y) / ts)
	if start == target:
		return [target]
	var seen := {start: true}
	var q: Array = [[start, []]]
	while not q.is_empty():
		var cur = q.pop_front()
		var pos: Vector2i = cur[0]
		var path: Array = cur[1]
		for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var n: Vector2i = pos + d
			if seen.has(n):
				continue
			if n == target:
				return path + [n]
			if not sc.is_walkable(n.x, n.y):
				continue
			seen[n] = true
			q.append([n, path + [n]])
	return [target]


func _advance_fader(dt: float) -> void:
	var actor = _fader[0]
	var rate: float = _fader[1]
	actor.modulate.a = maxf(0.0, actor.modulate.a - rate * dt)
	if actor.modulate.a <= 0.0:
		_remove_actor(actor)
		_fader = null
		_begin_step()


func _remove_actor(actor) -> void:
	if _sm.current != null and actor in _sm.current.npcs:
		_sm.current.npcs.erase(actor)
	if actor in _party.followers:
		_party.followers.erase(actor)
	actor.queue_free()


func _on_dialogue_done() -> void:
	_await_dialogue = false
	_begin_step()


func _set_fade(target: float, seconds: float) -> void:
	_fade_to = target
	if seconds <= 0:
		_fade.color.a = target
		_fade_rate = 0.0
	else:
		_fade_rate = (target - _fade.color.a) / seconds


func _tile_center(t: Vector2i) -> Vector2:
	var ts := Config.TILE_SIZE
	return Vector2(t.x * ts + ts / 2, t.y * ts + ts / 2)


# ── per-frame update ──────────────────────────────────────────────────────────
func update(dt: float) -> void:
	if not active:
		return
	if _fade_rate != 0.0:
		_fade.color.a = clampf(_fade.color.a + _fade_rate * dt, 0.0, 1.0)
		if (_fade_rate > 0 and _fade.color.a >= _fade_to) or (_fade_rate < 0 and _fade.color.a <= _fade_to):
			_fade.color.a = _fade_to
			_fade_rate = 0.0
	if _await_dialogue:
		return
	if _wait > 0.0:
		_wait -= dt
		if _wait <= 0.0:
			_begin_step()
		return
	if _fader != null:
		_advance_fader(dt)
		return
	if not _movers.is_empty():
		_advance_movers(dt)


func _advance_movers(dt: float) -> void:
	var step := Config.TILE_MOVE_SPEED * dt
	var still: Array = []
	for m in _movers:
		var actor = m[0]
		var waypts: Array = m[1]
		var target: Vector2 = waypts[0]
		var d: Vector2 = target - actor.position
		var dist: float = d.length()
		if dist <= maxf(0.5, step):
			actor.position = target
			waypts.pop_front()
		else:
			_face_px(actor, target)
			actor.position += d / dist * step
			if "walking" in actor:
				actor.walking = true
			if "walk_phase" in actor:
				actor.walk_phase += step * 0.2
			actor.queue_redraw()
		if not waypts.is_empty():
			still.append([actor, waypts])
		else:
			if "walking" in actor:
				actor.walking = false
			actor.queue_redraw()
	_movers = still
	if _movers.is_empty():
		_begin_step()


func _face_px(actor, target: Vector2) -> void:
	var d: Vector2 = target - actor.position
	if absf(d.x) >= absf(d.y):
		actor.facing = "right" if d.x > 0 else "left"
	elif d.y != 0.0:
		actor.facing = "down" if d.y > 0 else "up"
