# A solid scene feature (bar, bench, net, ball cart, column…) as its own node, so it can
# move, be interacted with, own its collision, and depth-sort — none of which a flat baked
# backdrop allows. The scene supplies a `drawer` Callable that paints the feature (in absolute
# scene coords) onto this node's canvas. z is absolute (z_as_relative off): pass round(base_y)
# for a feature that should sort against movers by depth, or Z_BACK for one nothing ever walks
# behind (it renders just above the bg, behind all characters). The baked bg sits at z -10.
class_name Fixture
extends Node2D

const Z_BACK := -5     # nothing stands behind it: above the bg (-10), below every mover (z >= 0)

var _drawer: Callable


func setup(z: int, drawer: Callable) -> void:
	z_as_relative = false
	z_index = z
	_drawer = drawer


func _draw() -> void:
	if _drawer.is_valid():
		_drawer.call(self)


# The paint method backing this fixture (e.g. "_paint_bar") — for the review legend.
func get_drawer_name() -> String:
	return str(_drawer.get_method())
