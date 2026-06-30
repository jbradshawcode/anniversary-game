# Sarah — tile-based movement with smooth pixel interpolation.
# Movement ported from entities/characters/player.py (try_move + update);
# art ported from the procedural pixel-rect head/body draw calls.
class_name Player
extends Node2D

# Palette (player.py)
var _SKIN := Color8(205, 165, 125)
var _SKIN_SH := Color8(180, 140, 105)
var _HAIR := Color8(95, 55, 30)
var _HAIR_LT := Color8(140, 85, 48)
var _HAIR_DK := Color8(65, 35, 18)
var _TEE := Color8(238, 236, 230)
var _TEE_SH := Color8(210, 208, 200)
var _EYE := Color8(50, 35, 25)
var _LASH := Color8(25, 12, 3)
var _LIP := Color8(195, 120, 110)
var _CHEEK := Color8(210, 155, 130)
var _GLINT := Color8(240, 245, 235)
var _EYE_W := Color8(235, 235, 240)
# Body palette defaults (humanoid.py Palette)
var _SHORT := Color8(35, 35, 38)
var _SHORT_SH := Color8(25, 25, 28)
var _SHOE := Color8(65, 42, 28)
var _SOLE := Color8(45, 30, 18)

var tile_x: int
var tile_y: int
var _target := Vector2.ZERO
var moving := false
var facing := "down"
var sitting := false
var holding := ""               # "" or a Drinks.KINDS value
var _drink_off := Vector2(0, 32)
var scene  # the active scene (provides is_walkable / has_wall)
var bare := false               # volleyball: head+body only (no shadow/drink/bob/glow)

# Native render path: the overworld body comes from this AnimatedSprite2D (frames
# baked from _draw()), picked by facing/sitting. _draw() keeps the procedural body
# for `bare` (volleyball) and as the re-bake seed; the bake tool flips this off.
var use_baked_sprite := true
var _anim: AnimatedSprite2D
const _SHEET := "res://assets/baked/player_sheet.png"
const _CELL := Vector2i(48, 64)
const _FACES := ["down", "up", "left", "right"]


func _init(start_tx := 0, start_ty := 0) -> void:
	tile_x = start_tx
	tile_y = start_ty


func _ready() -> void:
	position = _tile_center(tile_x, tile_y)
	_target = position
	if bare:
		return                  # volleyball actors get a team ring instead of the glow

	z_as_relative = false       # absolute z so the player depth-sorts against Fixture nodes by Y

	# A warm personal glow that travels with Sarah — dynamic lighting the pygame
	# version can't do (it would mean re-compositing an alpha overlay every frame).
	var glow := PointLight2D.new()
	glow.texture = LightTex.radial()
	glow.color = Color8(255, 240, 214)
	glow.energy = 0.85
	glow.texture_scale = (2.0 * 70.0) / 256.0
	add_child(glow)

	if use_baked_sprite:
		_anim = AnimatedSprite2D.new()
		_anim.sprite_frames = _build_frames()
		# Body draws behind Player's own canvas so a held drink (the only self-draw on
		# the baked path) overlays the hand instead of hiding under the sprite.
		_anim.show_behind_parent = true
		# Sheet is baked at Config.BAKE_SS× cell size; render at 1/BAKE_SS with LINEAR
		# filtering (SSAA downscale), matching the backdrop bake in Scene.gd.
		_anim.scale = Vector2.ONE / float(Config.BAKE_SS)
		_anim.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		add_child(_anim)        # centred -> the baked cell centre lands on the tile centre
		_sync_sprite()


# Build the SpriteFrames from the baked sheet: one 1-frame animation per state,
# each an AtlasTexture region into the horizontal strip (idle_*, then sit_*).
func _build_frames() -> SpriteFrames:
	var tex := load(_SHEET)
	var cell := _CELL * Config.BAKE_SS    # baked cell size; _anim.scale renders it back to _CELL
	var sf := SpriteFrames.new()
	sf.remove_animation("default")
	var i := 0
	for prefix in ["idle_", "sit_"]:
		for face in _FACES:
			sf.add_animation(prefix + face)
			sf.set_animation_loop(prefix + face, false)
			var at := AtlasTexture.new()
			at.atlas = tex
			at.region = Rect2(i * cell.x, 0, cell.x, cell.y)
			sf.add_frame(prefix + face, at)
			i += 1
	return sf


# Point the sprite at the animation for the current facing/seated state.
func _sync_sprite() -> void:
	if _anim != null:
		_anim.animation = ("sit_" if sitting else "idle_") + facing


func _tile_center(tx: int, ty: int) -> Vector2:
	var ts := Config.TILE_SIZE
	return Vector2(tx * ts + ts / 2, ty * ts + ts / 2)


func place(tx: int, ty: int) -> void:
	tile_x = tx
	tile_y = ty
	position = _tile_center(tx, ty)
	_target = position
	moving = false


func _process(delta: float) -> void:
	if not bare:                             # depth-sort against Fixture nodes by feet-Y
		z_index = int(round(position.y))
	if moving:
		var to_target := _target - position
		var dist := to_target.length()
		var step := Config.TILE_MOVE_SPEED * delta
		if step >= dist:
			position = _target
			moving = false
		else:
			position += to_target / dist * step
		queue_redraw()
	if _anim != null:                        # mirror facing/seat + the walk bob onto the sprite
		_sync_sprite()
		var bob := 0.0
		if moving and not sitting:
			var t := 1.0 - (_target - position).length() / float(Config.TILE_SIZE)
			bob = 3.0 * 4.0 * t * (1.0 - t)
		_anim.position.y = -bob


func try_move(dtx: int, dty: int, target_scene) -> bool:
	stand()                          # any move stands you up; a seated drink stays behind
	if moving:
		return false
	var ntx := tile_x + dtx
	var nty := tile_y + dty
	if not target_scene.is_walkable(ntx, nty):
		return false
	if target_scene.has_wall(tile_x, tile_y, ntx, nty):
		return false
	tile_x = ntx
	tile_y = nty
	_target = _tile_center(ntx, nty)
	moving = true
	if dtx > 0:
		facing = "right"
	elif dtx < 0:
		facing = "left"
	elif dty > 0:
		facing = "down"
	else:
		facing = "up"
	queue_redraw()
	return true


func _r(x: float, y: float, w: float, h: float, c: Color) -> void:
	draw_rect(Rect2(x, y, w, h), c)


func _shadow() -> void:
	draw_set_transform(Vector2(0, 14), 0, Vector2(1, 0.4))
	draw_circle(Vector2.ZERO, 9, Color(0, 0, 0, 0.27))
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


func _draw() -> void:
	if bare:                        # volleyball: VBActor owns the position/lean/jump
		match facing:
			"up":
				_head_up()
			"right":
				_head_right()
			"left":
				_head_left()
			_:
				_head_down()
		_body()
		if facing == "up":
			_back_hair()
		return
	if use_baked_sprite:        # overworld body comes from the AnimatedSprite2D; overlay the drink
		_blit_drink()
		return
	if sitting:
		_draw_seated()
		return
	_shadow()

	var bob := 0.0
	if moving:
		var remaining := (_target - position).length()
		var t := 1.0 - remaining / float(Config.TILE_SIZE)
		bob = 3.0 * 4.0 * t * (1.0 - t)
	draw_set_transform(Vector2(0, -bob), 0, Vector2.ONE)

	match facing:
		"up":
			_head_up()
		"right":
			_head_right()
		"left":
			_head_left()
		_:
			_head_down()
	_body()
	if facing == "up":
		_back_hair()
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)
	_blit_drink()


# ── seating / drink ───────────────────────────────────────────────────────────
func sit(face := "") -> void:
	sitting = true
	if face != "":
		facing = face
	if holding != "":
		place_drink()
	queue_redraw()


func stand() -> void:
	if sitting:
		holding = ""
	sitting = false
	queue_redraw()


func carry(kind: String) -> void:
	holding = kind
	if kind != "" and sitting:
		place_drink()
	queue_redraw()


func place_drink() -> void:
	var off := {"up": Vector2(0, -22), "down": Vector2(0, 32),
		"left": Vector2(-28, 4), "right": Vector2(28, 4)}
	var o: Vector2 = off.get(facing, Vector2(0, 32))
	_drink_off = o + Vector2(randf_range(-3.5, 3.5), randf_range(-2.0, 2.0))


func _blit_drink() -> void:
	if holding == "":
		return
	if sitting:
		Drinks.draw(self, _drink_off.x, _drink_off.y, holding)
	else:
		Drinks.draw(self, 8, 6, holding)


func _draw_seated() -> void:
	_shadow()
	draw_set_transform(Vector2(0, 4), 0, Vector2.ONE)
	if facing == "left" or facing == "right":
		if facing == "left":
			_head_left()
		else:
			_head_right()
		_seat_side(facing == "right")
	else:
		if facing == "up":
			_head_up()
		else:
			_head_down()
		_seat_front()
		if facing == "up":
			_back_hair()
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)
	_blit_drink()


func _seat_front() -> void:
	_r(-5, 1, 10, 5, _TEE)
	_r(-5, 1, 1, 5, _TEE_SH)
	_r(-2, 1, 4, 1, _TEE_SH)
	_r(-5, 6, 10, 3, _SHORT)
	_r(-5, 6, 10, 1, _SHORT_SH)
	_r(-4, 9, 3, 2, _SKIN)
	_r(1, 9, 3, 2, _SKIN)
	_r(-4, 11, 3, 2, _SHOE)
	_r(1, 11, 3, 2, _SHOE)
	_r(-4, 12, 3, 1, _SOLE)
	_r(1, 12, 3, 1, _SOLE)


func _seat_side(right: bool) -> void:
	var sr := func(x, y, w, h, c):
		var x0 = x if right else -x - w
		draw_rect(Rect2(x0, y, w, h), c)
	sr.call(-5, 1, 10, 5, _TEE)
	sr.call(-5, 1, 1, 5, _TEE_SH)
	sr.call(-2, 1, 4, 1, _TEE_SH)
	sr.call(-4, 6, 5, 3, _SHORT)
	sr.call(-4, 6, 5, 1, _SHORT_SH)
	sr.call(0, 6, 7, 3, _SHORT)
	sr.call(0, 6, 7, 1, _SHORT_SH)
	sr.call(6, 9, 3, 3, _SKIN)
	sr.call(6, 9, 1, 3, _SKIN_SH)
	sr.call(6, 12, 5, 2, _SHOE)
	sr.call(6, 13, 5, 1, _SOLE)


func _body() -> void:
	_r(-2, -1, 4, 2, _SKIN)
	_r(-7, 1, 3, 2, _TEE)
	_r(4, 1, 3, 2, _TEE)
	_r(-7, 3, 3, 2, _SKIN)
	_r(4, 3, 3, 2, _SKIN)
	_r(-5, 1, 10, 5, _TEE)
	_r(-5, 1, 1, 5, _TEE_SH)
	_r(-2, 1, 4, 1, _TEE_SH)
	_r(-4, 6, 8, 1, _SHORT_SH)
	_r(-4, 7, 3, 3, _SHORT)
	_r(1, 7, 3, 3, _SHORT)
	_r(-4, 7, 3, 1, _SHORT_SH)
	_r(1, 7, 3, 1, _SHORT_SH)
	_r(-4, 10, 3, 3, _SKIN)
	_r(1, 10, 3, 3, _SKIN)
	_r(-4, 10, 1, 3, _SKIN_SH)
	_r(1, 10, 1, 3, _SKIN_SH)
	_r(-5, 13, 5, 2, _SHOE)
	_r(1, 13, 5, 2, _SHOE)
	_r(-5, 14, 5, 1, _SOLE)
	_r(1, 14, 5, 1, _SOLE)


func _head_down() -> void:
	_r(-7, -15, 14, 5, _HAIR)
	_r(-8, -11, 3, 8, _HAIR)
	_r(5, -11, 3, 8, _HAIR)
	_r(-4, -15, 3, 2, _HAIR_LT)
	_r(-8, -11, 1, 6, _HAIR_DK)
	_r(7, -11, 1, 6, _HAIR_DK)
	draw_circle(Vector2(0, -6), 5, _SKIN)
	_r(-5, -11, 10, 2, _HAIR)
	_r(-3, -11, 4, 1, _HAIR_LT)
	_r(-4, -8, 3, 1, _LASH)
	_r(1, -8, 3, 1, _LASH)
	_r(-4, -7, 3, 2, _EYE)
	_r(-4, -7, 1, 1, _GLINT)
	_r(1, -7, 3, 2, _EYE)
	_r(1, -7, 1, 1, _GLINT)
	_r(-4, -5, 2, 1, _CHEEK)
	_r(2, -5, 2, 1, _CHEEK)
	_r(-1, -4, 2, 1, _LIP)


func _head_up() -> void:
	_r(-7, -15, 14, 4, _HAIR)
	_r(-8, -11, 16, 10, _HAIR)
	_r(-4, -15, 3, 2, _HAIR_LT)
	_r(-2, -11, 4, 8, _HAIR_LT)
	_r(-8, -11, 2, 8, _HAIR_DK)
	_r(6, -11, 2, 8, _HAIR_DK)


func _head_right() -> void:
	_r(-7, -15, 14, 3, _HAIR)
	_r(-5, -15, 4, 2, _HAIR_LT)
	_r(-7, -12, 5, 10, _HAIR)
	_r(-5, -12, 2, 7, _HAIR_LT)
	_r(-10, -9, 4, 3, _HAIR)
	_r(-12, -7, 5, 3, _HAIR)
	_r(-12, -4, 4, 3, _HAIR)
	_r(-11, -1, 3, 3, _HAIR)
	_r(-10, 2, 2, 2, _HAIR)
	_r(-10, -8, 2, 4, _HAIR_LT)
	_r(-12, -5, 2, 3, _HAIR_DK)
	_r(-11, -2, 2, 2, _HAIR_DK)
	_r(5, -12, 2, 5, _HAIR)
	_r(5, -12, 1, 3, _HAIR_LT)
	draw_circle(Vector2(2, -7), 4.5, _SKIN)
	_r(-2, -10, 2, 6, _SKIN_SH)
	_r(-2, -12, 8, 2, _HAIR)
	_r(0, -12, 3, 1, _HAIR_LT)
	_r(1, -9, 3, 1, _LASH)
	_r(1, -8, 1, 2, _EYE_W)
	_r(2, -8, 2, 2, _EYE)
	_r(2, -8, 1, 1, _GLINT)
	_r(1, -6, 3, 1, _LASH)
	_r(5, -7, 1, 2, _SKIN)
	_r(6, -6, 1, 1, _SKIN_SH)
	_r(3, -5, 2, 1, _CHEEK)
	_r(2, -4, 3, 1, _LIP)
	_r(2, -3, 2, 1, _SKIN_SH)


func _head_left() -> void:
	_r(-7, -15, 14, 3, _HAIR)
	_r(1, -15, 4, 2, _HAIR_LT)
	_r(2, -12, 5, 10, _HAIR)
	_r(3, -12, 2, 7, _HAIR_LT)
	_r(6, -9, 4, 3, _HAIR)
	_r(7, -7, 5, 3, _HAIR)
	_r(8, -4, 4, 3, _HAIR)
	_r(8, -1, 3, 3, _HAIR)
	_r(8, 2, 2, 2, _HAIR)
	_r(8, -8, 2, 4, _HAIR_LT)
	_r(10, -5, 2, 3, _HAIR_DK)
	_r(9, -2, 2, 2, _HAIR_DK)
	_r(-7, -12, 2, 5, _HAIR)
	_r(-6, -12, 1, 3, _HAIR_LT)
	draw_circle(Vector2(-2, -7), 4.5, _SKIN)
	_r(0, -10, 2, 6, _SKIN_SH)
	_r(-6, -12, 8, 2, _HAIR)
	_r(-3, -12, 3, 1, _HAIR_LT)
	_r(-4, -9, 3, 1, _LASH)
	_r(-2, -8, 1, 2, _EYE_W)
	_r(-4, -8, 2, 2, _EYE)
	_r(-3, -8, 1, 1, _GLINT)
	_r(-4, -6, 3, 1, _LASH)
	_r(-6, -7, 1, 2, _SKIN)
	_r(-7, -6, 1, 1, _SKIN_SH)
	_r(-5, -5, 2, 1, _CHEEK)
	_r(-5, -4, 3, 1, _LIP)
	_r(-4, -3, 2, 1, _SKIN_SH)


func _back_hair() -> void:
	_r(-3, -2, 6, 3, _HAIR)
	_r(-2, 1, 4, 4, _HAIR)
	_r(-1, 5, 2, 3, _HAIR)
	_r(-1, -1, 2, 2, _HAIR_LT)
	_r(0, 2, 1, 3, _HAIR_LT)
	_r(-2, 1, 1, 3, _HAIR_DK)
