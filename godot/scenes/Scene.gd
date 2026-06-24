# Base for all scenes — the Godot mirror of scenes/base.py. Owns the walkability
# grid, the walkable bounds, the NPC list, and the exits/entry-points data that
# SceneManager reads. Subclasses set those in _init and supply art via _draw.
class_name GameScene
extends Node2D

var grid: TileGrid
var npcs: Array = []
var walkable_cols: Vector2i
var walkable_rows: Vector2i
var exits: Dictionary = {}          # dir -> {scene:int, cols:Vector2i?, rows:Vector2i?, target:Vector2i?}
var entry_points: Dictionary = {}   # dir -> Vector2i (where the player lands arriving this way)
var world_cols := Config.MAP_COLS   # > MAP_COLS for scenes wider than one screen (scroll)

# Lighting, declared as data by subclasses in _init (the Godot mirror of the pygame
# per-scene `lighting` attribute). ambient (1,1,1) = no darkening; each light is a
# Dictionary {pos:Vector2, radius:float, color:Color, energy:float}.
var ambient_color := Color(1, 1, 1)
var lights: Array = []


func world_width() -> int:
	return world_cols * Config.TILE_SIZE


func _ready() -> void:
	if ambient_color != Color(1, 1, 1):
		var cm := CanvasModulate.new()
		cm.color = ambient_color
		add_child(cm)
	if not lights.is_empty():
		var tex := LightTex.radial()
		for l in lights:
			var pl := PointLight2D.new()
			pl.texture = tex
			pl.position = l["pos"]
			pl.color = l.get("color", Color(1, 1, 1))
			pl.energy = l.get("energy", 1.0)
			pl.texture_scale = (2.0 * float(l.get("radius", 100.0))) / 256.0
			add_child(pl)
	_on_ready()


# Subclass hook for non-lighting setup (NPCs, blockers). Base _ready owns lighting.
func _on_ready() -> void:
	pass


# Remove NPCs by display name (crew who join the party, or are absent this chapter)
# and rebuild the dynamic blocker layer so the tiles they vacated turn walkable.
func remove_named(names: Array) -> void:
	if names.is_empty():
		return
	var keep: Array = []
	for o in npcs:
		if str(o.display_name) in names:
			o.queue_free()
		else:
			keep.append(o)
	npcs = keep
	if grid != null:
		var blockers: Array = []
		for o in npcs:
			blockers.append(Vector2i(o.tile_x, o.tile_y))
		grid.set_blockers(blockers)


func is_walkable(tx: int, ty: int) -> bool:
	return grid.is_walkable(tx, ty)


func has_wall(fx: int, fy: int, tx: int, ty: int) -> bool:
	return grid.has_wall(fx, fy, tx, ty)
