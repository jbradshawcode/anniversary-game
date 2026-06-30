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
var _minigame_layer: CanvasLayer
var _minigame: VolleyCourt
var _dive: DiveGame
var _phone: Phone
var _phone_layer: CanvasLayer
var _phone_done := Callable()
var _card: Card
var _card_layer: CanvasLayer
var _baking := false        # true during the --bake run: the overworld game isn't wired up

# Music policy (mirror of app.py): per-scene looping track + the character theme
# that overrides it while that character speaks.
var _scene_music := {}
var _speaker_music := ""

# Shot/telemetry: which interlude path last fired + the chapter-start label.
var _last_stub := ""
var _chapter_card := ""


func _ready() -> void:
	Engine.max_fps = 60  # cap so dt stays sane (the 2D scenes otherwise run 1000s of fps)

	if "--bake" in OS.get_cmdline_user_args():
		# Asset-bake pipeline: render the procedural _draw() art to PNG textures, then
		# quit. The .gd remains the source of truth; PNGs are regenerable build artifacts.
		_baking = true                     # _process must no-op: the game state isn't built
		await _bake()
		get_tree().quit()
		return

	_scene_music = {                          # scene_id -> looping track (else silence)
		1: Config.GYM_MUSIC, 2: Config.KING_ST_MUSIC,
		3: Config.SALUTATION_MUSIC, 4: Config.GARDEN_MUSIC,
		5: Config.LATIMER_MUSIC, 6: Config.LATIMER_MUSIC, 7: Config.LATIMER_MUSIC,
		8: Config.LATIMER_MUSIC, 9: Config.LATIMER_MUSIC,   # school grounds, not the gym
		10: Config.WETHERSPOONS_MUSIC,
	}

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
	_story = StoryManager.new(Screenplay.weeks())
	_cutscene.bind(_dialogue, _sm, _player, _party, fade, _story)
	_story.bind(_dialogue, _sm, _player, _party, _cutscene)
	_cutscene.on_game_over = _on_game_over
	_wire_story_stubs()
	_sm.story = _story

	_save_mgr = SaveManager.new()
	_save_mgr.bind(_story, _sm, _player)

	_minigame_layer = CanvasLayer.new()
	_minigame_layer.layer = 3     # above everything (world / dialogue / menu) — covers the overworld
	add_child(_minigame_layer)

	var menu_layer := CanvasLayer.new()
	menu_layer.layer = 2          # above dialogue/fade (layer 1)
	add_child(menu_layer)
	_menu = Menu.new()
	menu_layer.add_child(_menu)

	if "--shot" in OS.get_cmdline_user_args():
		await _shot()
	else:
		_open_title()


# Story hooks. The minigames launch for real (volleyball + dive); the interludes are
# full-screen Cards (results / chapter / interlude title / "The End"), each gating the
# overworld behind it and, where the screenplay chains, handing off to the Phone widget.
func _wire_story_stubs() -> void:
	_story.on_launch_vb = func():
		_launch_vb()
	_story.on_launch_dive = func():
		_launch_dive()

	# A texts-only beat (interlude or the finale): a title card, then the thread.
	_story.on_phone = func(thread, with_who, adv, title, _date):
		_last_stub = "phone"
		# Split "Interlude — First Contact" / "Finale — The Date" into kicker + name.
		var parts := str(title).split("—")
		var kicker: String = parts[0].strip_edges()
		var nm := parts[1].strip_edges() if parts.size() > 1 else ""
		if kicker == "":
			kicker = "Interlude"
		if nm == "":
			nm = kicker
		var end_game: bool = _story.beat().get("end_game", false)
		Audio.play(Config.CHAPTER_END_MUSIC if kicker == "Finale" else Config.INTERLUDE_MUSIC)
		var card := Card.new()
		card.setup_interlude(kicker, nm, _date)
		_open_card(card, func():
			_close_card()
			_open_phone(thread, with_who, func():
				_close_phone()
				if end_game:
					_finish_finale(adv)
				else:
					Audio.reset()   # interludes sit between chapters -> resume marks start fresh
					update_scene_music(_sm.current_id())
					_story.set_flag(adv)))

	# An end-of-chapter beat: the star results card, then the post-week phone wrap-up.
	_story.on_week_end = func():
		_last_stub = "week_end"
		var b := _story.beat()
		var week := int(b.get("week", 1))
		var adv: String = b.get("advance_when", "")
		Audio.play(Config.CHAPTER_END_MUSIC)         # end-of-chapter screen theme
		var card := Card.new()
		card.setup_results(_story.stars(), maxi(1, _story.vb_attempts),
			"%s Complete" % str(_story.week_title()))
		_open_card(card, func():
			_close_card()
			_open_phone(Screenplay.phone_thread(week), "Dan", func():
				_close_phone()
				_finish_week(adv)))

	# A new chapter began (after its goto). The crew resets each chapter; Chapter 2+
	# shows a transition card first — the beat's opening cutscene is already queued
	# and resumes when the card closes (it stays frozen behind the card meanwhile).
	_story.on_chapter_start = func(week, title, first):
		_chapter_card = "Week %d — %s" % [week, title]
		_party.clear()
		if not first:
			var card := Card.new()
			card.setup_chapter(week - 1, week)
			_open_card(card, func(): _close_card())


# After the post-week phone thread: reset the per-chapter star tally and set the
# chapter's "left" flag, which advances into the next chapter (firing its card).
func _finish_week(adv: String) -> void:
	Audio.reset()                        # new chapter -> songs start fresh, not resumed
	update_scene_music(_sm.current_id())
	_story.vb_attempts = 0
	_story.set_flag(adv)


# After the finale's phone thread: set its flag, then the closing "The End" card.
# Confirming it starts a fresh playthrough.
func _finish_finale(adv: String) -> void:
	Audio.play(Config.CHAPTER_END_MUSIC)
	_story.set_flag(adv)
	var card := Card.new()
	card.setup_the_end(false)
	_open_card(card, func():
		_close_card()
		Audio.reset()             # play again -> no stale resume marks
		_story.start_new())


# ── Volleyball orchestration (mirror of app.py _launch_match / _end_volleyball) ──
func _launch_vb() -> void:
	var week := int(_story.beat().get("week", 1))
	var level: String = {1: "easy", 2: "medium", 3: "hard", 4: "insane"}.get(week, "hard")
	if week == 1 and _story.has("w1_want_tut") and not _story.has("w1_tut_done"):
		_launch_court("tutorial", level, 1, _end_tutorial)
		return
	_launch_court("match", level, week, _end_volleyball)


func _launch_court(mode: String, level: String, week: int, finish: Callable) -> void:
	# The match gets the volleyball theme; the tutorial keeps the gym theme carried in.
	if mode == "match":
		Audio.play(Config.VB_MUSIC)
	var vc := VolleyCourt.new()
	vc.configure(mode, level, week)
	vc.on_finish = finish
	_minigame = vc
	_minigame_layer.add_child(vc)


func _close_minigame() -> void:
	if _minigame != null:
		_minigame.queue_free()
		_minigame = null


# ── Phone / text-thread interlude (mirror of app.py enter_phone / PhoneMode) ─────
func _open_phone(thread: Array, other: String, on_done: Callable) -> void:
	_phone_layer = CanvasLayer.new()
	_phone_layer.layer = 4            # above the overworld, dialogue, menu and minigames
	add_child(_phone_layer)
	_phone = Phone.new()
	_phone.setup(thread, other)
	_phone_layer.add_child(_phone)
	_phone_done = on_done


func _close_phone() -> void:
	if _phone_layer != null:
		_phone_layer.queue_free()
		_phone_layer = null
		_phone = null
	_phone_done = Callable()


# ── Full-screen story cards (results / chapter / interlude / the-end) ────────────
func _open_card(card: Card, on_confirm: Callable) -> void:
	_card_layer = CanvasLayer.new()
	_card_layer.layer = 5             # above the overworld, dialogue, menu, minigames and phone
	add_child(_card_layer)
	_card = card
	_card.on_confirm = on_confirm
	_card_layer.add_child(_card)


func _close_card() -> void:
	if _card_layer != null:
		_card_layer.queue_free()
		_card_layer = null
		_card = null


func _end_tutorial() -> void:
	_close_minigame()
	_story.set_flag("w1_tut_done")   # records the warm-up; not an advance flag
	_launch_vb()                      # straight into the real match


func _end_volleyball() -> void:
	_story.vb_attempts += 1            # counts toward this chapter's results-card stars
	var won := _minigame.player_won()
	_close_minigame()
	if won:
		_return_to_gym_and_advance()  # this chapter's win flag
	else:
		Audio.stop()                  # match pygame: lost -> theme dips, retry re-attacks it
		_launch_vb()                  # lost -> retry the match


# ── Diving drill orchestration (mirror of app.py _launch_dive / _end_dive) ──────
func _launch_dive() -> void:
	Audio.play(Config.DIVE_MUSIC)
	var dg := DiveGame.new()
	dg.on_finish = _end_dive
	_dive = dg
	_minigame_layer.add_child(dg)


func _end_dive() -> void:
	if _dive != null:
		_dive.queue_free()
		_dive = null
	_return_to_gym_and_advance()


func _return_to_gym_and_advance() -> void:
	if _sm.current_id() != 1:
		_sm.go_to(1, _player, Vector2i(_player.tile_x, _player.tile_y))
	update_scene_music(1)              # back in the gym -> gym theme (the scene instance is
	_story.set_flag(_story.beat().get("advance_when", ""))  # unchanged, so the seam won't fire)


func _on_game_over(lines: Array) -> void:
	# Plays once, then silence; the scene's track resumes when the message closes and
	# we replay the current beat's cutscene from the top.
	Audio.play(Config.GAME_OVER_MUSIC, false)
	_dialogue.start(lines, "", func():
		update_scene_music(_sm.current_id())
		_cutscene.start(_story.beat().get("cutscene", [])))


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
			Audio.reset()         # fresh game -> no stale song resume marks
			_sm.go_to(1, _player, Vector2i(5, 6))
			_story.start_new()
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
	if _baking:                 # --bake run: no overworld state to update
		return
	if _minigame != null:       # the minigame drives its own update + input
		return
	if _phone != null:          # the phone interlude freezes the overworld
		return
	if _card != null:           # a story card freezes the overworld (and any queued cutscene)
		return
	_update_camera_limits()
	update_speaker_music()             # a speaking character's theme overrides the scene track
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
	if _speaker_music == "":             # don't stomp a character theme that's mid-line
		update_scene_music(_sm.current_id())
	_party.on_scene_change(_player)  # snap the crew to the player's new entry point
	if _sm.story != null:
		_sm.story.notify_enter(_sm.current_id())  # beat on-enter lines + advancement


# Swap to the active scene's looping track (or fade to silence if it has none).
func update_scene_music(scene_id: int) -> void:
	var track: String = _scene_music.get(scene_id, "")
	if track != "":
		Audio.play(track)
	else:
		Audio.stop()


# While a character with a theme is talking, play it (resuming where it last left
# off — Audio banks positions); restore the scene's track once they stop.
func update_speaker_music() -> void:
	var speaker := _dialogue.current_speaker()
	var theme: String = Config.CHARACTER_MUSIC.get(speaker, "") if speaker != "" else ""
	if theme != "":
		if speaker != _speaker_music:
			Audio.play(theme)
			_speaker_music = speaker
	elif _speaker_music != "":
		_speaker_music = ""
		update_scene_music(_sm.current_id())


func _facing_for(dtx: int, dty: int) -> String:
	if dtx > 0:
		return "right"
	if dtx < 0:
		return "left"
	if dty > 0:
		return "down"
	return "up"


func _unhandled_input(event: InputEvent) -> void:
	if _minigame != null:              # the minigame owns input while it's up
		return
	if not (event is InputEventKey and event.pressed and not event.echo):
		return

	if _card != null:                  # a story card owns input while it's up
		if event.keycode == KEY_Z or event.keycode == KEY_ENTER:
			_card.confirm()
		elif (event.keycode == KEY_X or event.keycode == KEY_ESCAPE) \
				and _card.kind == Card.Kind.THE_END and _card.loaded:
			_close_card()              # backing out of a completed-save prompt
			_open_title()
		return

	if _phone != null:                 # the phone interlude owns input while it's up
		if event.keycode == KEY_Z or event.keycode == KEY_ENTER:
			if not _phone.advance():
				var done := _phone_done
				done.call()            # the thread is exhausted -> finish (closes the phone)
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

	# ESC or C open the pause menu — mirror of pygame's QUIT / MENU bindings.
	if (event.keycode == KEY_ESCAPE or event.keycode == KEY_C) \
			and not _dialogue.active and not _cutscene.active:
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

	if not Config.DEV:
		return
	# Dev-only affordances (set ANNIV_DEV=1) — saving/loading also live in the pause menu.
	match event.keycode:
		KEY_P:
			if not _party.active() and not _cutscene.active:
				_party.form(_player, _crew_roster())
		KEY_G:
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


# Interact with the tile the player faces. The story gets first refusal (a
# checklist tick, an interact_ask choice cutscene, or a line to a seated follower);
# only if it declines do we fall back to the NPC's own idle lines. Both turn to
# face each other when there's someone there.
func _interact_ahead() -> void:
	var d: Vector2i = _FACING_DELTA[_player.facing]
	var tx := _player.tile_x + d.x
	var ty := _player.tile_y + d.y
	var who = null
	for npc in _sm.current.npcs:
		if npc.tile_x == tx and npc.tile_y == ty:
			who = npc
			break
	if who == null:
		for f in _party.followers:
			if f.tile_x == tx and f.tile_y == ty:
				who = f
				break
	var name: String = str(who.display_name) if who != null else ""

	if _sm.story != null and _sm.story.interact(tx, ty, name):
		if who != null:
			who.facing = _OPPOSITE[_player.facing]
			who.queue_redraw()
		return
	if _sm.story != null and _sm.story.talk(name):
		return
	if who != null:
		who.facing = _OPPOSITE[_player.facing]
		who.queue_redraw()
		who.on_interact()                # e.g. Matúš's deafening whistle
		_dialogue.start(who.interaction_lines(), who.display_name)


func _shot() -> void:
	# Title screen.
	_open_title()
	await get_tree().create_timer(0.2).timeout
	assert(_menu.is_open(), "title menu not open")
	await _save("res://verify_title.png")
	_menu.close()

	# Audio: every procedural SFX bank built at startup, plus the loud whistle asset.
	for n in ["dig", "set", "serve", "spike", "perfect", "block", "tip", "blip",
			"whistle", "cheer", "whistle_loud"]:
		assert(Audio._banks.has(n), "sfx bank missing: %s" % n)
	Audio.sfx("blip")                            # smoke: a bankable sound plays without error

	# Gym (start scene) — verify the lit hall + the full Ch1 crew, before the story
	# tests below mutate it (despawn joiners, strip absent crew).
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
	await get_tree().create_timer(0.3).timeout
	await _save("res://verify_gym.png")
	# The scene-change seam started the gym's looping theme (Matúš's "lonely people music").
	assert(Audio._current == Config.GYM_MUSIC, "gym theme not playing in the gym")

	# Fixture depth-sort (Y->z): the ball cart at (2,7) is a Fixture node anchored at its
	# base, z = (7+1)*32 = 256. Standing above it the player must sort behind (cart occludes
	# the feet); one tile below, in front. Assert the relation both ways and shoot the above case.
	var cart_z := (7 + 1) * 32
	_player.place(2, 6)
	_player.facing = "down"
	_player.z_index = int(round(_player.position.y))   # _process sets this live; force it for the shot
	assert(_player.z_index < cart_z, "player above the cart must sort behind it")
	await get_tree().create_timer(0.2).timeout
	await _save("res://verify_gym_occlude.png")
	_player.place(2, 8)
	_player.z_index = int(round(_player.position.y))
	assert(_player.z_index > cart_z, "player below the cart must sort in front")
	_player.place(5, 6)
	_player.facing = "down"

	# ── The real screenplay ─────────────────────────────────────────────────────
	# New game: begin -> Week 1's opening (chapter card fires, then the check_baskets
	# cutscene runs; Nat walks to the bench and sits).
	_sm.go_to(1, _player, Vector2i(5, 6))
	_story.start_new()
	await get_tree().create_timer(0.4).timeout
	assert(_cutscene.active, "opening cutscene not running")
	assert(_story.beat()["name"] == "check_baskets", "wrong starting beat")
	assert(_chapter_card == "Week 1 — Week 1", "chapter-start callback did not fire")
	await _save("res://verify_cutscene.png")
	await _drive(900)                              # let the opening cutscene finish

	# Checklist beat: check both baskets in either order; the beat advances once
	# both are ticked (order-aware "more"/"done" lines).
	assert(_story.interact(2, 7), "near basket not interactable")
	await _drive(300)                              # near basket closes; beat does not advance yet
	assert(_story.has("w1_basket_near"), "first basket flag not set")
	assert(_story.beat()["name"] == "check_baskets", "advanced before both baskets checked")
	assert(_story.interact(17, 7), "far basket not interactable")
	assert(await _play_until("leonard_offer", 300), "checklist did not advance the beat")

	# Drive the choice/flag beats through to the volleyball launch: the leonard_offer
	# cutscene's flag advances, vb_setup's `ask` (choice 0) flags w1_vb_set, and
	# gym_match hands off to the launch_volleyball stub.
	assert(await _play_until("gym_match", 2000), "did not reach gym_match")
	assert(_minigame != null and _minigame is VolleyCourt, "volleyball minigame did not launch")
	# Ch1 opens with the controls tutorial (w1_want_tut); finishing it launches the match.
	if _minigame._mode == "tutorial":
		_minigame.phase = VolleyCourt.PHASE_OVER
		_minigame.on_finish.call()
		await get_tree().process_frame
	assert(_minigame != null and _minigame._mode == "match", "match did not start after tutorial")
	assert(Audio._current == Config.VB_MUSIC, "volleyball theme not playing in the match")
	# Dismiss the how-to card and drive a live AI-served rally for the shot.
	_minigame._intro = false
	_minigame.serving = 1
	_minigame._start_serve()
	await get_tree().create_timer(1.3).timeout
	assert(_minigame.near.size() == 3 and _minigame.far.size() == 3, "court not fielded 3v3")
	await _save("res://verify_volleyball.png")
	# Let the AI rally run on (dig -> set -> spike -> block, scoring, rotation) — a
	# faithful sim must survive several points without dying. The human stands still,
	# so balls hit at them score for the far side; that still drives _point/_after_point.
	await get_tree().create_timer(3.0).timeout
	assert(_minigame != null and is_instance_valid(_minigame), "sim crashed during rally")
	assert(_minigame.phase >= VolleyCourt.PHASE_SERVE and _minigame.phase <= VolleyCourt.PHASE_OVER,
		"sim phase invalid")

	# Player serve: the meter + aim-target HUD. Drive the power->lateral stage too.
	_minigame.serving = 0
	_minigame._start_serve()
	await get_tree().process_frame
	assert(_minigame._server().is_player and _minigame._serve_stage == "power", "player serve not armed")
	await _save("res://verify_volleyball_serve.png")
	_minigame._action = true
	await get_tree().process_frame
	assert(_minigame._serve_stage == "lateral", "serve power -> lateral stage failed")

	# Aim-step: leap into slow-mo, reticle + guides + spike meter + dim, contactor bumped.
	var pl: VBActor = _minigame._player()
	_minigame.phase = VolleyCourt.PHASE_RALLY
	_minigame.ball.hold_at(pl.x, pl.y)
	_minigame._enter_aimstep(pl)
	await get_tree().process_frame
	assert(_minigame._aimstep != null, "aim-step did not arm")
	await _save("res://verify_volleyball_aim.png")

	# Win path: a finished match advances the beat (pub_invite) via on_finish.
	_minigame.score = [7, 0]
	_minigame.phase = VolleyCourt.PHASE_OVER
	_minigame.on_finish.call()
	assert(Audio._current == Config.GYM_MUSIC, "gym theme not restored after the match")
	await get_tree().process_frame
	assert(_minigame == null, "minigame not closed after win")
	assert(_story.beat()["name"] == "pub_invite", "win did not advance to pub_invite")
	_cutscene.stop()
	_dialogue.active = false
	_dialogue.visible = false

	# Absent crew: entering a Week-2 beat strips Leonard from the gym.
	_story.restore(_story.index_of("w2_greet"), [])
	_story.begin()
	assert(not _sm.current.npcs.any(func(n): return n is Leonard), "absent crew not removed")

	# Party `form`: summon the Week-1 crew; the seven joiners despawn from the gym.
	_party.clear()
	var gym_before: int = _sm.current.npcs.size()
	_story.restore(_story.index_of("walk_to_pub"), [])
	_story.begin()
	assert(_party.followers.size() == 7, "party did not form the full crew")
	assert(_sm.current.npcs.size() == gym_before - 7, "joining crew not despawned from the gym")

	# `goto` relocates the player to the beat's scene + tile.
	_cutscene.stop()
	_party.clear()
	_story.restore(_story.index_of("w2_arrive"), [])
	_story.begin()
	assert(_sm.current_id() == 1 and _player.tile_x == 9 and _player.tile_y == 1, "goto did not relocate")
	_cutscene.stop()

	# Party form-with-exclude (w3_garden leaves Bailey behind).
	_party.clear()
	_story.restore(_story.index_of("w3_garden"), [])
	_story.begin()
	assert(not _party.followers.any(func(f): return f is Bailey), "excluded crew joined the party")
	assert(_party.followers.size() == 6, "form-with-exclude wrong crew size")
	_cutscene.stop()

	# Diving drill (scene 12): the w3_dive beat launches the real minigame. Drive
	# each path — intro, a live STEP feed, the PUSH/SLIDE timing bars, the dive pose,
	# a scored verdict, the done card — then finish and confirm it advances the beat.
	_party.clear()
	_dialogue.active = false
	_story.restore(_story.index_of("w3_dive"), [])
	_story.begin()
	assert(_dive != null and _dive is DiveGame, "diving drill did not launch")
	assert(Audio._current == Config.DIVE_MUSIC, "diving theme not playing")
	assert(_dive._phase == "intro", "dive did not open on the intro card")
	await get_tree().create_timer(0.2).timeout
	await _save("res://verify_dive_intro.png")

	# Dismiss the intro and feed a ball: STEP positions James under the landing ring.
	_dive._toss()
	assert(_dive._phase == "step", "toss did not start a STEP")
	await get_tree().create_timer(0.3).timeout
	await _save("res://verify_dive.png")

	# PUSH timing bar: park the needle in the band and screenshot the sweep UI.
	_dive._phase = "push"
	_dive._swing_delay = 0.0
	_dive._needle = Config.DIVE_PUSH_CENTRE
	await get_tree().process_frame
	await _save("res://verify_dive_push.png")

	# Dive pose: a stretched SLIDE sprawls James flat (Npc.diving). Drive the lunge.
	_dive._px = _dive._left + 40
	_dive._tx = _dive._px + Config.DIVE_SET_GOOD + 30   # gap > SET_GOOD -> a dive
	_dive._start_dive("perfect")
	assert(_dive._phase == "dive", "wide ball did not trigger a dive")
	await get_tree().create_timer(0.3).timeout   # past contact (t>=0.5), before the landing (t>=1.0)
	assert(_dive._james.diving != "", "James not in the diving pose mid-lunge")
	assert(_dive._digs >= 1, "dive did not score at full extension")
	await _save("res://verify_dive_pose.png")

	# Done card (a short rally): set the win state and screenshot the closing card.
	_dive._digs = Config.DIVE_TARGET
	_dive._best = 8
	_dive._phase = "done"
	await get_tree().process_frame
	await _save("res://verify_dive_done.png")

	# Finish (Z on a won drill) -> on_finish closes the minigame and advances the beat.
	_dive._handle_action(true)
	await get_tree().process_frame
	assert(_dive == null, "diving drill not closed after finish")
	assert(_story.beat()["name"] != "w3_dive", "dive finish did not advance the beat")
	_cutscene.stop()
	_dialogue.active = false
	_dialogue.visible = false

	# Interlude title card + phone (scrims): the on_phone hook shows the title card
	# first; Z hands off to the real Phone widget. Exhausting the thread sets the
	# advance flag, which crosses into Week 3 and fires a chapter card.
	_story.restore(_story.index_of("scrims_texts"), [])
	_story.begin()
	assert(_card != null and _card.kind == Card.Kind.INTERLUDE, "interlude title card did not open")
	assert(Audio._current == Config.INTERLUDE_MUSIC, "interlude theme not playing")
	await get_tree().create_timer(0.2).timeout
	await _save("res://verify_interlude_card.png")
	_card.confirm()                          # title card -> the texts
	assert(_card == null and _last_stub == "phone" and _phone != null,
		"interlude card did not hand off to the phone")
	_phone.advance()                        # reveal the date pill + the preformatted signup
	_phone.advance()                        # bubbles (centred multi-line text with inline emoji)
	await get_tree().create_timer(0.2).timeout
	await _save("res://verify_phone_interlude.png")
	while _phone.advance():                  # exhaust the thread, then the next Z finishes
		pass
	assert(_phone.done(), "phone thread not exhausted")
	_phone_done.call()                       # mirrors the final Z (nothing left to reveal)
	assert(_phone == null, "phone not closed after the thread ended")
	assert(_story.has("scrims_done"), "interlude did not advance the beat")
	# Crossing scrims -> Week 3 fired a chapter card; dismiss it (the chapter card is
	# screenshotted from the results path below, which crosses into Week 4).
	assert(_card != null and _card.kind == Card.Kind.CHAPTER, "chapter card did not open on the new week")
	_card.confirm()
	assert(_card == null, "chapter card did not close")
	_cutscene.stop()
	_dialogue.active = false
	_dialogue.visible = false

	# A standalone James<->Dan thread (the post-week wrap-up data) drives the bubble
	# kinds the interludes don't: a screenshot-of-a-chat bubble and a bank notification,
	# alongside reactions and inline colour emoji. (The results card chains into this
	# same thread; here we drive the widget directly to cover every render path.)
	var dl := CanvasLayer.new()
	dl.layer = 4
	add_child(dl)
	var dphone := Phone.new()
	dphone.setup(Screenplay.phone_thread(1), "Dan")
	dl.add_child(dphone)
	await get_tree().create_timer(0.2).timeout
	await _save("res://verify_phone_shot.png")   # bubble #0 is the screenshot-of-a-chat
	while dphone.advance():
		pass
	assert(dphone.done(), "standalone thread not fully revealed")
	await get_tree().create_timer(0.2).timeout
	await _save("res://verify_phone_thread.png")  # notif card + reactions + inline emoji
	dl.queue_free()
	await get_tree().process_frame

	# End-of-week results card -> phone wrap-up. The end_chapter beat shows the star
	# card (stars from vb_attempts); Z chains into the post-week thread; the final Z
	# resets the tally and sets the chapter's "left" flag — crossing into Week 4, whose
	# chapter card we screenshot here.
	_story.restore(_story.index_of("w3_end"), [])
	_story.vb_attempts = 4                    # 4 tries -> 4 of 5 stars (stars_for_attempts)
	_story.begin()
	assert(_last_stub == "week_end" and _card != null and _card.kind == Card.Kind.RESULTS,
		"results card did not open")
	assert(Audio._current == Config.CHAPTER_END_MUSIC, "chapter-end theme not playing on the results card")
	await get_tree().create_timer(0.2).timeout
	await _save("res://verify_results.png")
	_card.confirm()                           # results -> the phone wrap-up
	assert(_card == null and _phone != null, "results card did not hand off to the phone")
	while _phone.advance():
		pass
	_phone_done.call()
	assert(_phone == null, "phone not closed after the wrap-up")
	assert(_story.vb_attempts == 0, "week end did not reset the attempt tally")
	assert(_story.has("w3_left"), "week end did not set the chapter flag")
	assert(_card != null and _card.kind == Card.Kind.CHAPTER, "next chapter card did not open")
	await get_tree().create_timer(0.2).timeout
	await _save("res://verify_chapter_card.png")
	_card.confirm()
	assert(_card == null, "chapter card did not close")
	_cutscene.stop()
	_dialogue.active = false
	_dialogue.visible = false

	# Finale: an interlude card (kicker "Finale"), the phone thread, then the closing
	# "The End" card. Confirming it starts a fresh playthrough from the first beat.
	_story.restore(_story.index_of("the_date"), [])
	_story.begin()
	assert(_card != null and _card.kind == Card.Kind.INTERLUDE, "finale title card did not open")
	_card.confirm()                           # title card -> the texts
	assert(_phone != null, "finale phone did not open")
	while _phone.advance():
		pass
	_phone_done.call()
	assert(_phone == null and _card != null and _card.kind == Card.Kind.THE_END,
		"finale closing card did not show")
	assert(_story.has("the_date_done"), "finale did not set its flag")
	await get_tree().create_timer(0.2).timeout
	await _save("res://verify_the_end.png")
	_card.confirm()                           # "The End" -> a fresh playthrough
	assert(_card == null, "closing card did not close")
	assert(_story.beat()["name"] == "check_baskets", "play again did not restart the story")
	_cutscene.stop()
	_dialogue.active = false
	_dialogue.visible = false

	# gate_exit verdicts: a barred door blocks, the chapter-end edge ends the week.
	_story.restore(_story.index_of("wind_down"), [])
	assert(_story.gate_exit(3, "down", 4) == "block", "door_block not enforced")
	assert(_story.gate_exit(3, "left", 2) == "end_week", "end_week edge not detected")

	# interact_ask: talking to the named NPC fires its choice cutscene.
	_cutscene.stop()
	_dialogue.active = false
	_story.restore(_story.index_of("w2_ready"), [])
	assert(_story.interact(0, 0, "James"), "interact_ask did not fire")
	assert(_cutscene.active, "interact_ask cutscene not running")
	_cutscene.stop()

	# talk: a seated-crew goodbye line.
	_dialogue.active = false
	_story.restore(_story.index_of("wind_down"), [])
	assert(_story.talk("James"), "talk line not shown")
	assert(_dialogue.active, "talk did not open dialogue")

	# Disable the story for the remaining (save/load, lighting, party, choice) shots.
	_sm.story = null
	_cutscene.stop()
	_dialogue.active = false
	_dialogue.visible = false

	# Save/load round-trip: write a known state, scramble it, load it back.
	_story.restore(_story.index_of("w2_ready"), ["w2_arrived", "w2_greeted"])
	_sm.go_to(5, _player, Vector2i(3, 5))
	_player.facing = "left"
	_save_mgr.save(2)
	assert(_save_mgr.has(2), "save file not written")
	_story.restore(0, [])                       # scramble
	_sm.go_to(1, _player, Vector2i(9, 9))
	_player.facing = "down"
	_save_mgr.apply(_save_mgr.load_slot(2))     # load it back
	assert(_story.beat()["name"] == "w2_ready", "beat not restored")
	assert(_story.has("w2_greeted"), "flag not restored")
	assert(_sm.current_id() == 5, "scene not restored")
	assert(_player.tile_x == 3 and _player.tile_y == 5, "tile not restored")
	assert(_player.facing == "left", "facing not restored")
	_sm.go_to(1, _player, Vector2i(5, 6))       # back to the gym for the visual shots
	await get_tree().process_frame              # let the scene-change seam restart the gym theme

	# Speaker theme: Matt's music overrides the scene track while he speaks, then the
	# scene's track resumes when he stops (update_speaker_music, polled each play frame).
	_dialogue.start(["Test line."], "Matt")
	update_speaker_music()
	assert(Audio._current == Config.MATT_MUSIC and _speaker_music == "Matt",
		"Matt's theme did not override the scene music")
	_dialogue.active = false
	_dialogue.visible = false
	update_speaker_music()
	assert(_speaker_music == "" and Audio._current == Config.GYM_MUSIC,
		"scene theme did not resume after the speaker stopped")

	# Game-over track: plays once (no loop); the scene theme resumes when the message closes.
	_on_game_over(["Game over, man."])
	assert(Audio._current == Config.GAME_OVER_MUSIC, "game-over theme not playing")
	_dialogue.active = false
	_dialogue.visible = false
	Audio.play(Config.GYM_MUSIC)                 # park the music back on the gym for the shots

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
	assert(Audio._current == Config.SALUTATION_MUSIC, "Salutation theme not playing in the pub")
	assert(_sm.current.npcs.any(func(n): return n is Milla), "Milla not spawned in pub")
	await _save("res://verify_pub.png")

	# Feature-node fixtures: the player north of the mid-room column (16,6) must sort behind
	# it, one row south in front; and Milla (serving over the Z_BACK bar) must sort in front of it.
	var pub_col_z := 7 * 32
	_player.place(16, 5)
	_player.z_index = int(round(_player.position.y))
	assert(_player.z_index < pub_col_z, "player north of the column must sort behind it")
	_player.place(16, 8)
	_player.z_index = int(round(_player.position.y))
	assert(_player.z_index > pub_col_z, "player south of the column must sort in front")
	var pub_milla_z := -9999
	for o in _sm.current.npcs:
		if o is Milla:
			pub_milla_z = o.z_index
	assert(pub_milla_z > Fixture.Z_BACK, "Milla must sort in front of the bar")
	_player.place(12, 8)

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
	# "warmed_up" was set by the choice demo above, so if_flag should splice its steps.
	_cutscene.start([["if_flag", "warmed_up", [["flag", "if_ran"]]]])
	await get_tree().process_frame
	assert(_story.has("if_ran"), "if_flag did not splice its steps")

	# King Street (scrolling 180-tile street) — jump in by the Salutation and capture.
	_sm.go_to(2, _player, Vector2i(97, 5))
	_player.facing = "down"
	_player.queue_redraw()
	await get_tree().create_timer(0.3).timeout
	assert(_sm.current is KingSt, "King St not loaded")
	assert(Audio._current == Config.KING_ST_MUSIC, "King Street theme not playing")
	# Streetlamp depth-sort (Y->z): the north lamps are a Fixture anchored at the curb
	# row, z = 6*32 = 192. On the north pavement (row 5) the player must sort behind a
	# lamp (it occludes); stepping south onto a crossing tile (row 7) puts them in front.
	var lamp_z := 6 * 32
	_player.place(90, 5)                                # north pavement, at a lamp column
	_player.z_index = int(round(_player.position.y))   # _process sets this live; force it for the shot
	assert(_player.z_index < lamp_z, "player on the north pavement must sort behind a streetlamp")
	_player.place(96, 7)                                # crossing tile, south of the curb base
	_player.z_index = int(round(_player.position.y))
	assert(_player.z_index > lamp_z, "player on the crossing must sort in front of a north streetlamp")
	_player.place(97, 5)
	_player.facing = "down"
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


# Shot driver: advance any active dialogue (picking choice 0 — verified safe, no
# game_over sits at index 0) and let movers/waits/fades run, until both the cutscene
# and dialogue go idle.
func _drive(cap: int) -> void:
	var g := 0
	while (_cutscene.active or _dialogue.active) and g < cap:
		g += 1
		if _dialogue.active:
			if _dialogue._typing:
				_dialogue.skip()
			else:
				_dialogue.advance()
		await get_tree().process_frame


# Like _drive, but stops as soon as the named beat becomes current (returns whether
# it was reached). Used to play forward through several beats to a checkpoint.
func _play_until(beat_name: String, cap: int) -> bool:
	var g := 0
	while _story.beat()["name"] != beat_name and g < cap:
		g += 1
		if _dialogue.active:
			if _dialogue._typing:
				_dialogue.skip()
			else:
				_dialogue.advance()
		await get_tree().process_frame
	return _story.beat()["name"] == beat_name


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


# ── Asset-bake pipeline (run via tools/bake.sh / `-- --bake`) ───────────────────
# Renders the procedural _draw() art into PNG textures so scenes can move to native
# Sprite2D/AnimatedSprite2D. Bake at SUPERSAMPLE>1 for crisper art under zoom; 1 is
# pixel-exact to the current game. The .gd stays the source of truth — re-run to
# regenerate. Each item renders in an isolated SubViewport (no scene lighting leaks).
const _BAKE_DIR := "res://assets/baked/"
const _BAKE_SS := 1                     # supersample factor (bump to 2-4 for zoom-crisp art)
const _PLAYER_CELL := Vector2i(48, 64)  # per-frame box; player art ≈ x[-12,12] y[-15,18] centred
const _PLAYER_FRAMES := [               # animation name -> (facing, sitting); one frame each
	["idle_down", "down", false], ["idle_up", "up", false],
	["idle_left", "left", false], ["idle_right", "right", false],
	["sit_down", "down", true], ["sit_up", "up", true],
	["sit_left", "left", true], ["sit_right", "right", true],
]


func _bake() -> void:
	DirAccess.make_dir_recursive_absolute(_BAKE_DIR)
	var backdrops := [                        # every non-minigame scene; minigames stay procedural
		["gym", Gym], ["kingst", KingSt], ["pub", Pub], ["garden", Garden],
		["corridor", Corridor], ["reception", Reception], ["courtyard", Courtyard],
		["passage", Passage], ["courts", Courts], ["wetherspoons", Wetherspoons],
	]
	# Optional filter: `-- --bake <name>` re-bakes only that scene (and skips the player
	# sheet) so a single-scene change doesn't rewrite every committed PNG.
	var args := OS.get_cmdline_user_args()
	var only := ""
	var bi := args.find("--bake")
	if bi != -1 and bi + 1 < args.size() and not args[bi + 1].begins_with("--"):
		only = args[bi + 1]
	var n := 0
	for b in backdrops:
		if only == "" or b[0] == only:
			await _bake_background(b[1], b[0])
			n += 1
	if only == "":
		await _bake_player_sheet()
	print("baked ", n, " backdrop(s)", (" + player sheet" if only == "" else ""), " into ", _BAKE_DIR)


# A scene backdrop -> one opaque PNG. We strip the scene's lighting + crew children
# so the texture is the raw, unlit art; runtime CanvasModulate/PointLight2D relight it.
# Viewport is sized to world_width() so wide scrolling scenes (King St, Pub, garden) bake whole.
func _bake_background(scene_class, fname: String) -> void:
	var scene: GameScene = scene_class.new()
	scene.use_baked_bg = false                # render the procedural art, not the (absent) bake
	scene.scale = Vector2(_BAKE_SS, _BAKE_SS)
	var vp := SubViewport.new()
	vp.size = Vector2i(scene.world_width(), Config.SCREEN_HEIGHT) * _BAKE_SS
	vp.transparent_bg = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	vp.add_child(scene)
	await get_tree().process_frame            # let Scene._ready add lights/modulate/crew
	for c in scene.get_children():            # drop them — bake structures only
		scene.remove_child(c)
		c.queue_free()
	var img := await _grab(vp)
	img.save_png(_BAKE_DIR + fname + "_bg.png")
	vp.queue_free()


# The player's 8 overworld states -> a horizontal sprite sheet (one cell per frame).
func _bake_player_sheet() -> void:
	var cell := _PLAYER_CELL * _BAKE_SS
	var sheet := Image.create(cell.x * _PLAYER_FRAMES.size(), cell.y, false, Image.FORMAT_RGBA8)
	for i in _PLAYER_FRAMES.size():
		var st: Array = _PLAYER_FRAMES[i]
		var frame := await _render_player_frame(cell, st[1], st[2])
		sheet.blit_rect(frame, Rect2i(Vector2i.ZERO, cell), Vector2i(cell.x * i, 0))
	sheet.save_png(_BAKE_DIR + "player_sheet.png")


func _render_player_frame(cell: Vector2i, facing: String, sitting: bool) -> Image:
	var vp := SubViewport.new()
	vp.size = cell
	vp.transparent_bg = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var p := Player.new()
	p.use_baked_sprite = false                # draw the procedural body, not the AnimatedSprite2D
	p.scale = Vector2(_BAKE_SS, _BAKE_SS)
	vp.add_child(p)
	await get_tree().process_frame
	for c in p.get_children():
		if c is PointLight2D:
			c.queue_free()                    # the travelling glow is runtime light, not sprite art
	p.position = Vector2(cell) / 2.0          # origin (tile centre) -> cell centre
	p.facing = facing
	p.sitting = sitting
	p.queue_redraw()
	var img := await _grab(vp)
	vp.queue_free()
	return img


# Settle the SubViewport, force a draw, and read its texture back to an Image.
func _grab(vp: SubViewport) -> Image:
	await get_tree().process_frame
	await get_tree().process_frame
	RenderingServer.force_draw()
	return vp.get_texture().get_image()
