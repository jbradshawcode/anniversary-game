# Root + overworld coordinator. Owns the SceneManager, drives tile movement
# (held-key -> SceneManager.try_move, which handles exits), the talk interaction,
# and dialogue gating. Mirrors OverworldMode in systems/modes.py.
# Run with `-- --shot` to walk through the gym's top exit into the corridor and screenshot.
extends Node2D

const _FACING_DELTA := {
	"up": Vector2i(0, -1), "down": Vector2i(0, 1),
	"left": Vector2i(-1, 0), "right": Vector2i(1, 0),
}
const _OPPOSITE := {"up": "down", "down": "up", "left": "right", "right": "left"}

var _sm: SceneManager
var _player: Player
var _dialogue: DialogueBox
var _camera: Camera2D
var _last_scene: GameScene
var _party: Party
var _cutscene: Cutscene
var _story: StoryManager


func _ready() -> void:
	Engine.max_fps = 60  # cap so dt stays sane (the 2D scenes otherwise run 1000s of fps)

	var world := Node2D.new()
	add_child(world)

	var party_layer := Node2D.new()
	add_child(party_layer)  # followers draw above the scene, below the player

	_sm = SceneManager.new(world)
	_sm.register(1, Gym.new())
	_sm.register(5, Corridor.new())
	_sm.register(6, Promenade.new())
	_party = Party.new(party_layer, _sm)

	_player = Player.new(5, 6)
	_sm.start(1, _player)
	add_child(_player)  # sibling after `world` -> drawn on top of the scene

	# Camera follows the player; per-scene limits make narrow scenes static and
	# wide ones scroll. Godot clamps to the limits natively (no world_surface blit).
	_camera = Camera2D.new()
	_player.add_child(_camera)
	_camera.make_current()

	var ui := CanvasLayer.new()
	add_child(ui)
	var fade := ColorRect.new()      # cutscene screen fade, under the dialogue text
	fade.color = Color(0, 0, 0, 0)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(fade)
	fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_dialogue = DialogueBox.new()
	ui.add_child(_dialogue)

	_cutscene = Cutscene.new()
	_story = StoryManager.new(_screenplay())
	_cutscene.bind(_dialogue, _sm, _player, _party, fade, _story)
	_story.bind(_dialogue, _sm, _player, _party, _cutscene)
	_sm.story = _story

	if "--shot" in OS.get_cmdline_user_args():
		await _shot()
	else:
		_story.begin()


func _process(delta: float) -> void:
	_update_camera_limits()
	_party.update(delta, _player)
	_cutscene.update(delta)
	if _dialogue.active or _player.moving or _cutscene.active:
		return
	var dtx := 0
	var dty := 0
	if Input.is_action_pressed("ui_right"):
		dtx = 1
	elif Input.is_action_pressed("ui_left"):
		dtx = -1
	elif Input.is_action_pressed("ui_down"):
		dty = 1
	elif Input.is_action_pressed("ui_up"):
		dty = -1
	if dtx != 0 or dty != 0:
		# Turn to face the pressed direction even if the step is blocked, so you
		# can face an NPC/wall before talking.
		var nf := _facing_for(dtx, dty)
		if _player.facing != nf:
			_player.facing = nf
			_player.queue_redraw()
		_sm.try_move(dtx, dty, _player)


# Re-clamp the camera to the world bounds when the active scene changes.
func _update_camera_limits() -> void:
	if _sm.current == _last_scene:
		return
	_last_scene = _sm.current
	_camera.limit_left = 0
	_camera.limit_top = 0
	_camera.limit_right = _sm.current.world_width()
	_camera.limit_bottom = Config.SCREEN_HEIGHT
	_party.on_scene_change(_player)  # snap the crew to the player's new entry point
	if _sm.story != null:
		_sm.story.notify_enter(_sm.current_id())  # beat on-enter lines + advancement


func _facing_for(dtx: int, dty: int) -> String:
	if dtx > 0:
		return "right"
	if dtx < 0:
		return "left"
	if dty > 0:
		return "down"
	return "up"


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_Z, KEY_ENTER:
			if _dialogue.active:
				_dialogue.advance()
			elif not _cutscene.active:
				_interact_ahead()
		KEY_X:
			if _dialogue.active:
				_dialogue.skip()
		KEY_UP:
			if _dialogue.is_choosing():
				_dialogue.move_choice(-1)
		KEY_DOWN:
			if _dialogue.is_choosing():
				_dialogue.move_choice(1)
		KEY_P:
			if not _party.active() and not _cutscene.active:
				_party.form(_player, _crew_roster())
		KEY_C:
			if not _cutscene.active and not _dialogue.active:
				_cutscene.start(_demo_cutscene())


func _crew_roster() -> Array:
	return [
		{"tee": Color8(70, 90, 150), "name": "James"},
		{"tee": Color8(70, 140, 90), "name": "Dan"},
		{"tee": Color8(170, 70, 70), "name": "Matt"},
		{"tee": Color8(150, 90, 165), "name": "Nat"},
	]


func _demo_cutscene() -> Array:
	return [
		["say", ["Right, listen up — two courts, nets up.", "Try not to embarrass me out there."], "Matúš"],
		["walk", "sarah", Vector2i(7, 6)],
		["face", "matúš", "left"],
		["say", ["Ready when you are."], "Sarah"],
	]


func _demo_choice() -> Array:
	return [
		["ask", "Warm up first?", {
			"Yes, let's stretch.": [["flag", "warmed_up"]],
			"No — I'm ready now.": [["say", ["Cocky. I like it."], "Matúš"]],
		}, "Matúš"],
	]


# A tiny three-beat screenplay over the existing scenes, to exercise the story
# machine: an intro cutscene, then progress gated by reaching the next scene.
func _screenplay() -> Array:
	return [
		{
			"name": "intro",
			"cutscene": [
				["say", ["Right, listen up — nets are up.", "Win this and the pub's on me."], "Matúš"],
				["say", ["Then let's not keep them waiting."], "Sarah"],
				["flag", "intro_done"],
			],
			"advance_when": "intro_done",
		},
		{
			"name": "to_corridor",
			"on_enter_scene": {5: ["You step into the corridor — the pool hums behind the glass."]},
			"advance_on_enter": 5,
			"advance_when": "reached_corridor",
		},
		{
			"name": "to_street",
			"on_enter_scene": {6: ["Out into the dusk. The others are already ahead."]},
			"advance_on_enter": 6,
			"advance_when": "reached_street",
		},
	]


# Talk to whatever NPC the player is facing; both turn to face each other.
func _interact_ahead() -> void:
	var d: Vector2i = _FACING_DELTA[_player.facing]
	var tx := _player.tile_x + d.x
	var ty := _player.tile_y + d.y
	for npc in _sm.current.npcs:
		if npc.tile_x == tx and npc.tile_y == ty:
			npc.facing = _OPPOSITE[_player.facing]
			npc.queue_redraw()
			_dialogue.start(npc.interaction_lines(), npc.display_name)
			return


func _shot() -> void:
	# Story: begin -> the intro cutscene (Matúš addresses Sarah; both turn to face).
	_story.begin()
	await get_tree().create_timer(0.4).timeout
	assert(_cutscene.active, "intro cutscene not running")
	assert(_story.beat()["name"] == "intro", "wrong starting beat")
	assert(_player.facing == "right", "Sarah did not turn to face Matúš")
	await _save("res://verify_cutscene.png")

	# A cutscene ['flag'] delegates to story.set_flag, which advances the beat.
	_cutscene.stop()
	_cutscene.start([["flag", "intro_done"]])
	await get_tree().process_frame
	assert(_story.beat()["name"] == "to_corridor", "intro flag did not advance the beat")
	# Entering the corridor fires its on-enter line and advances again.
	_story.notify_enter(5)
	assert(_story.beat()["name"] == "to_street", "scene-enter did not advance the beat")
	assert(_dialogue.active, "corridor on-enter line did not show")

	# Disable the story for the remaining (lighting/party/choice) shots.
	_sm.story = null
	_cutscene.stop()
	_dialogue.active = false
	_dialogue.visible = false

	# Choice demo: an `ask` with two branches; drive a selection and check the flag.
	_cutscene.start(_demo_choice())
	await get_tree().create_timer(0.5).timeout
	assert(_dialogue.is_choosing(), "choices did not appear")
	await _save("res://verify_choice.png")
	_dialogue.advance()   # pick the first option -> runs ["flag", "warmed_up"]
	await get_tree().process_frame
	await get_tree().process_frame
	assert(_story.has("warmed_up"), "ask branch did not run")  # cutscene flag -> story
	_cutscene.stop()
	_dialogue.active = false
	_dialogue.visible = false

	_player.place(5, 6)
	_player.facing = "down"
	for o in _sm.current.npcs:
		o.facing = "down"
		o.queue_redraw()
	await get_tree().process_frame

	# Gym (start scene) — verify the lit hall.
	await get_tree().create_timer(0.3).timeout
	await _save("res://verify_gym.png")

	# Exercise a normal in-scene step (player.try_move path) before any exit, so a
	# regression there can't hide behind the transition-only path.
	_player.place(5, 6)
	_sm.try_move(1, 0, _player)
	await get_tree().create_timer(0.2).timeout
	assert(not _player.moving and _player.tile_x == 6, "normal move failed")

	# Gym -> corridor.
	_player.place(9, 1)
	_player.facing = "up"
	await get_tree().process_frame
	_sm.try_move(0, -1, _player)
	assert(_sm.current is Corridor, "gym->corridor transition failed")
	await get_tree().create_timer(0.3).timeout
	await _save("res://verify_corridor.png")

	# Corridor -> wide promenade; stand deep in it so the camera has scrolled.
	_player.place(18, 5)
	_player.facing = "right"
	await get_tree().process_frame
	_sm.try_move(1, 0, _player)
	assert(_sm.current is Promenade, "corridor->promenade transition failed")
	_player.place(20, 7)
	_player.facing = "right"
	_player.queue_redraw()
	await get_tree().create_timer(0.4).timeout
	assert(_camera.limit_right == _sm.current.world_width(), "camera limit not updated")
	await _save("res://verify_promenade.png")

	# Party demo — summon the crew and walk so they trail in a staggered line.
	_party.form(_player, _crew_roster())
	assert(_party.followers.size() == 4, "party did not form")
	await _walk_steps(8, 1, 0)
	assert(_player.tile_x == 28, "player did not walk 8 tiles")
	await get_tree().create_timer(0.4).timeout  # let the tail catch up
	await _save("res://verify_party.png")

	get_tree().quit()


func _walk_steps(n: int, dtx: int, dty: int) -> void:
	for i in range(n):
		while _player.moving:
			await get_tree().process_frame
		_sm.try_move(dtx, dty, _player)
	while _player.moving:
		await get_tree().process_frame


func _save(path: String) -> void:
	# Force a fresh draw before read-back — the OS may stop rendering an
	# unfocused window, leaving get_image() with a stale frame otherwise.
	await get_tree().process_frame
	RenderingServer.force_draw()
	var img := get_viewport().get_texture().get_image()
	img.save_png(path)
