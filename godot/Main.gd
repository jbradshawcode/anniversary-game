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
var _save_mgr: SaveManager
var _menu: Menu


func _ready() -> void:
	Engine.max_fps = 60  # cap so dt stays sane (the 2D scenes otherwise run 1000s of fps)

	var world := Node2D.new()
	add_child(world)

	var party_layer := Node2D.new()
	add_child(party_layer)  # followers draw above the scene, below the player

	_sm = SceneManager.new(world)
	_sm.register(1, Gym.new())
	_sm.register(2, KingSt.new())
	_sm.register(3, Pub.new())
	_sm.register(4, Garden.new())
	_sm.register(5, Corridor.new())
	_sm.register(6, Reception.new())
	_sm.register(7, Courtyard.new())
	_sm.register(8, Passage.new())
	_sm.register(9, Courts.new())
	_sm.register(10, Wetherspoons.new())
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

	_save_mgr = SaveManager.new()
	_save_mgr.bind(_story, _sm, _player)

	var menu_layer := CanvasLayer.new()
	menu_layer.layer = 2          # above dialogue/fade (layer 1)
	add_child(menu_layer)
	_menu = Menu.new()
	menu_layer.add_child(_menu)

	if "--shot" in OS.get_cmdline_user_args():
		await _shot()
	else:
		_open_title()


func _open_title() -> void:
	var opts := ["New Game"]
	if _save_mgr.has(1):
		opts.append("Continue")
	opts.append("Quit")
	_menu.open("ANNIVERSARY", opts, _on_title_select, "press Z to select")


func _on_title_select(i: int) -> void:
	var label: String = _menu.options[i]
	match label:
		"New Game":
			_menu.close()
			_sm.go_to(1, _player, Vector2i(5, 6))
			_story.restore(0, [])
			_story.begin()
		"Continue":
			_menu.close()
			_save_mgr.apply(_save_mgr.load_slot(1))
		"Quit":
			get_tree().quit()


func _open_pause() -> void:
	var opts := ["Resume", "Save", "Load"] if _save_mgr.has(1) else ["Resume", "Save"]
	opts.append("Quit to Title")
	_menu.open("Paused", opts, _on_pause_select)


func _on_pause_select(i: int) -> void:
	match _menu.options[i]:
		"Resume":
			_menu.close()
		"Save":
			_save_mgr.save(1)
			_menu.close()
		"Load":
			_save_mgr.apply(_save_mgr.load_slot(1))
			_menu.close()
		"Quit to Title":
			_menu.close()
			_open_title()


func _process(delta: float) -> void:
	_update_camera_limits()
	if not _cutscene.active:           # the cutscene drives the crew during scripted moves
		_party.update(delta, _player)
	_cutscene.update(delta)
	if _menu.is_open() or _dialogue.active or _player.moving or _cutscene.active:
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

	if _menu.is_open():                # the menu owns input while it's up
		match event.keycode:
			KEY_UP:
				_menu.move(-1)
			KEY_DOWN:
				_menu.move(1)
			KEY_Z, KEY_ENTER:
				_menu.select()
			KEY_ESCAPE:
				if _menu.title == "Paused":
					_menu.close()
		return

	if event.keycode == KEY_ESCAPE and not _dialogue.active and not _cutscene.active:
		_open_pause()
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
		KEY_S:
			if not _dialogue.active and not _cutscene.active:
				_save_mgr.save(1)
		KEY_L:
			if _save_mgr.has(1) and not _dialogue.active and not _cutscene.active:
				_save_mgr.apply(_save_mgr.load_slot(1))


func _crew_roster() -> Array:
	# Four distinct crew with bespoke art; the full WEEK1_CREW is wired by the screenplay.
	return [James, Dan, Matt, Nat]


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
			"name": "to_reception",
			"on_enter_scene": {6: ["The reception lobby — quiet but for the hum behind the desk."]},
			"advance_on_enter": 6,
			"advance_when": "reached_reception",
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
	# Title screen.
	_open_title()
	await get_tree().create_timer(0.2).timeout
	assert(_menu.is_open(), "title menu not open")
	await _save("res://verify_title.png")
	_menu.close()

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
	assert(_story.beat()["name"] == "to_reception", "scene-enter did not advance the beat")
	assert(_dialogue.active, "corridor on-enter line did not show")

	# Disable the story for the remaining (lighting/party/choice) shots.
	_sm.story = null
	_cutscene.stop()
	_dialogue.active = false
	_dialogue.visible = false

	# Save/load round-trip: write a known state, scramble it, load it back.
	_story.restore(1, ["intro_done"])
	_sm.go_to(5, _player, Vector2i(3, 5))
	_player.facing = "left"
	_save_mgr.save(2)
	assert(_save_mgr.has(2), "save file not written")
	_story.restore(0, [])                       # scramble
	_sm.go_to(1, _player, Vector2i(9, 9))
	_player.facing = "down"
	_save_mgr.apply(_save_mgr.load_slot(2))     # load it back
	assert(_story.beat()["name"] == "to_corridor", "beat not restored")
	assert(_story.has("intro_done"), "flag not restored")
	assert(_sm.current_id() == 5, "scene not restored")
	assert(_player.tile_x == 3 and _player.tile_y == 5, "tile not restored")
	assert(_player.facing == "left", "facing not restored")
	_sm.go_to(1, _player, Vector2i(5, 6))       # back to the gym for the visual shots

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
	# Fan the standing crew across all four facings so the shot exercises every
	# head-art path (front / mirrored profile / back); leave Matúš in his seated pose.
	var dirs := ["down", "left", "right", "up"]
	var di := 0
	for o in _sm.current.npcs:
		if not o.sitting:
			o.facing = dirs[di % dirs.size()]
			di += 1
		o.queue_redraw()
	assert(_sm.current.npcs.size() == 9, "gym crew not fully spawned")
	await get_tree().process_frame

	# Gym (start scene) — verify the lit hall + the full Ch1 crew.
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

	# Corridor -> reception, entering through the west glass door.
	_player.place(18, 5)
	_player.facing = "right"
	await get_tree().process_frame
	_sm.try_move(1, 0, _player)
	assert(_sm.current is Reception, "corridor->reception transition failed")
	assert(_player.tile_x == 2 and _player.tile_y == 7, "reception entry point wrong")
	_player.facing = "right"
	_player.queue_redraw()
	await get_tree().create_timer(0.3).timeout
	await _save("res://verify_reception.png")

	# Party demo — summon the crew and walk across the lobby so they trail behind.
	_party.form(_player, _crew_roster())
	assert(_party.followers.size() == 4, "party did not form")
	await _walk_steps(6, 1, 0)
	assert(_player.tile_x == 8, "player did not walk 6 tiles")
	await get_tree().create_timer(0.4).timeout  # let the tail catch up
	await _save("res://verify_party.png")

	# The Salutation pub (scrolling) — jump in and capture mid-room.
	_sm.go_to(3, _player, Vector2i(12, 8))
	_player.facing = "up"
	_player.queue_redraw()
	await get_tree().create_timer(0.3).timeout
	assert(_sm.current is Pub, "pub not loaded")
	assert(_sm.current.npcs.any(func(n): return n is Milla), "Milla not spawned in pub")
	await _save("res://verify_pub.png")

	# Seating beat: walk the crew to the table and sit them with their drinks.
	_cutscene.start(_demo_seating())
	var guard := 0
	while _cutscene.active and guard < 600:
		guard += 1
		await get_tree().process_frame
	assert(not _cutscene.active, "seating cutscene did not finish")
	assert(_player.sitting and _player.holding == "red_wine", "Sarah not seated with a drink")
	await get_tree().create_timer(0.2).timeout
	await _save("res://verify_seated.png")

	# Remaining cutscene verbs: walkto (pathfind), vanish (fade+remove), if_flag.
	var crew0 = _party.followers[0]
	_cutscene.start([["walkto", crew0.display_name, Vector2i(8, 8)]])
	await _drain_cutscene(800)
	assert(crew0.tile_x == 8 and crew0.tile_y == 8, "walkto did not arrive")
	_cutscene.start([["vanish", crew0.display_name, 0.1]])
	await _drain_cutscene(200)
	assert(not (crew0 in _party.followers), "vanish did not remove the follower")
	_cutscene.start([["if_flag", "intro_done", [["flag", "if_ran"]]]])
	await get_tree().process_frame
	assert(_story.has("if_ran"), "if_flag did not splice its steps")

	# King Street (scrolling 180-tile street) — jump in by the Salutation and capture.
	_sm.go_to(2, _player, Vector2i(97, 5))
	_player.facing = "down"
	_player.queue_redraw()
	await get_tree().create_timer(0.3).timeout
	assert(_sm.current is KingSt, "King St not loaded")
	await _save("res://verify_kingst.png")

	# The beer garden (scene 4).
	_sm.go_to(4, _player, Vector2i(6, 7))
	_player.facing = "right"
	_player.queue_redraw()
	await get_tree().create_timer(0.3).timeout
	assert(_sm.current is Garden, "garden not loaded")
	await _save("res://verify_garden.png")

	# The underground passage (scene 8), entered for real through reception's east
	# door so the exit-transition path is exercised, not just a go_to jump.
	_sm.go_to(6, _player, Vector2i(14, 7))
	_player.facing = "right"
	await get_tree().process_frame
	_sm.try_move(1, 0, _player)
	assert(_sm.current is Passage, "reception->passage transition failed")
	assert(_player.tile_x == 1 and _player.tile_y == 11, "passage entry point wrong")
	_player.facing = "up"
	_player.queue_redraw()
	await get_tree().create_timer(0.3).timeout
	await _save("res://verify_passage.png")

	# The school courtyard (scene 7). No ported scene transitions into it yet, so
	# jump in, then drive both code paths: a normal in-scene step AND the up-exit
	# transition to King Street, asserting each post-condition.
	_sm.go_to(7, _player, Vector2i(10, 8))
	_player.facing = "down"
	_player.queue_redraw()
	await get_tree().create_timer(0.3).timeout
	assert(_sm.current is Courtyard, "courtyard not loaded")
	await _save("res://verify_courtyard.png")

	# Normal step along the central path (player.try_move path).
	_player.place(9, 5)
	_sm.try_move(1, 0, _player)
	await get_tree().create_timer(0.2).timeout
	assert(not _player.moving and _player.tile_x == 10, "courtyard normal move failed")

	# Up-exit transition: out the gate gap (cols 9-10) onto King Street.
	_player.place(9, 2)
	_player.facing = "up"
	await get_tree().process_frame
	_sm.try_move(0, -1, _player)
	assert(_sm.current is KingSt, "courtyard->King St transition failed")
	assert(_player.tile_x == 4 and _player.tile_y == 10, "King St entry point wrong")

	# The netball courts (scene 9), entered for real through the passage's east
	# exit so the exit-transition path is exercised, not just a go_to jump.
	_sm.go_to(8, _player, Vector2i(18, 6))
	_player.facing = "right"
	await get_tree().process_frame
	_sm.try_move(1, 0, _player)
	assert(_sm.current is Courts, "passage->courts transition failed")
	assert(_player.tile_x == 3 and _player.tile_y == 3, "courts entry point wrong")
	_player.facing = "down"
	_player.queue_redraw()
	await get_tree().create_timer(0.3).timeout
	await _save("res://verify_courts.png")

	# Normal in-scene step across the court (player.try_move path).
	_player.place(8, 8)
	_sm.try_move(1, 0, _player)
	await get_tree().create_timer(0.2).timeout
	assert(not _player.moving and _player.tile_x == 9, "courts normal move failed")

	# Down-exit transition: out the bottom-left gate gap (cols 3,4) to the courtyard.
	_player.place(3, 14)
	_player.facing = "down"
	await get_tree().process_frame
	_sm.try_move(0, 1, _player)
	assert(_sm.current is Courtyard, "courts->courtyard transition failed")
	assert(_player.tile_x == 9 and _player.tile_y == 12, "courtyard entry point wrong")

	# The William Morris / Wetherspoons (scene 10). No ported scene transitions
	# into it yet, so jump in, then drive both code paths: a normal in-scene step
	# AND the down-exit transition to King Street, asserting each post-condition.
	_sm.go_to(10, _player, Vector2i(9, 13))
	_player.facing = "up"
	_player.queue_redraw()
	await get_tree().create_timer(0.3).timeout
	assert(_sm.current is Wetherspoons, "wetherspoons not loaded")
	await _save("res://verify_wetherspoons.png")

	# Normal in-scene step across the front room (player.try_move path).
	_player.place(6, 13)
	_sm.try_move(1, 0, _player)
	await get_tree().create_timer(0.2).timeout
	assert(not _player.moving and _player.tile_x == 7, "wetherspoons normal move failed")

	# Down-exit transition: out the street doors (cols 8-11) onto King Street.
	_player.place(9, 13)
	_player.facing = "down"
	await get_tree().process_frame
	_sm.try_move(0, 1, _player)
	assert(_sm.current is KingSt, "wetherspoons->King St transition failed")
	assert(_player.tile_x == 177 and _player.tile_y == 4, "King St entry point wrong")

	get_tree().quit()


func _drain_cutscene(max_frames: int) -> void:
	var g := 0
	while _cutscene.active and g < max_frames:
		g += 1
		await get_tree().process_frame


func _demo_seating() -> Array:
	return [
		["move", {
			"James": Vector2i(10, 9), "Dan": Vector2i(11, 9), "sarah": Vector2i(12, 9),
			"Nat": Vector2i(13, 9), "Matt": Vector2i(16, 9),
		}],
		["sit", "James", "down"], ["hold", "James", "beer"],
		["sit", "Dan", "down"], ["hold", "Dan", "beer"],
		["sit", "sarah", "down"], ["hold", "sarah", "red_wine"],
		["sit", "Nat", "down"], ["hold", "Nat", "cider"],
		["sit", "Matt", "down"], ["hold", "Matt", "white_wine"],
		["settle"],
	]


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
