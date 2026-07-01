# Walkability grid for a scene — pure tile logic, no rendering.
# Direct port of systems/tilemap.py: a static walkable rectangle minus blocked
# scenery, plus walled edges between adjacent tiles, plus a dynamic blocker layer.
class_name TileGrid
extends RefCounted

var _map_cols: int
var _map_rows: int
var _walls := {}
var _base: Array = []
var _grid: Array = []


func _init(walkable_cols: Vector2i, walkable_rows: Vector2i,
		map_cols: int, map_rows: int,
		static_blocked: Array, walls: Array) -> void:
	_map_cols = map_cols
	_map_rows = map_rows
	for edge in walls:
		_walls[_edge_key(edge[0], edge[1])] = true

	_base = []
	for r in range(map_rows):
		var row: Array = []
		row.resize(map_cols)
		row.fill(0)
		_base.append(row)
	for r in range(walkable_rows.x, walkable_rows.y + 1):
		for c in range(walkable_cols.x, walkable_cols.y + 1):
			_base[r][c] = 1
	for t in static_blocked:
		if t.y >= 0 and t.y < map_rows and t.x >= 0 and t.x < map_cols:
			_base[t.y][t.x] = 0
	set_blockers([])


func _edge_key(a: Vector2i, b: Vector2i) -> String:
	return "%d,%d>%d,%d" % [a.x, a.y, b.x, b.y]


func set_blockers(tiles: Array) -> void:
	_grid = []
	for row in _base:
		_grid.append(row.duplicate())
	for t in tiles:
		if t.y >= 0 and t.y < _map_rows and t.x >= 0 and t.x < _map_cols:
			_grid[t.y][t.x] = 0


func is_walkable(tx: int, ty: int) -> bool:
	if tx < 0 or tx >= _map_cols or ty < 0 or ty >= _map_rows:
		return false
	return _grid[ty][tx] == 1


func has_wall(fx: int, fy: int, tx: int, ty: int) -> bool:
	return _walls.has(_edge_key(Vector2i(fx, fy), Vector2i(tx, ty)))
