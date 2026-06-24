# Drink glasses carried/rested by a humanoid. Ported from humanoid.draw_drink:
# pints (beer/cider) are tall tumblers; wines are stemmed. Drawn relative to a
# bottom-centre (gx, gy) on the given canvas.
class_name Drinks
extends RefCounted

const KINDS := ["beer", "cider", "white_wine", "red_wine"]


static func draw(canvas: CanvasItem, gx: float, gy: float, kind: String) -> void:
	var fills := {
		"beer": [Color8(240, 178, 36), Color8(208, 150, 22)],
		"cider": [Color8(228, 196, 104), Color8(198, 166, 80)],
		"white_wine": [Color8(236, 228, 156), Color8(206, 196, 120)],
		"red_wine": [Color8(146, 30, 46), Color8(110, 20, 34)],
	}
	if not fills.has(kind):
		return
	var glass := Color8(214, 228, 238)
	var glass_sh := Color8(150, 170, 186)
	var foam := Color8(250, 248, 240)
	var fill: Color = fills[kind][0]
	var fill_sh: Color = fills[kind][1]
	var dr := func(x, y, w, h, c): canvas.draw_rect(Rect2(gx + x, gy + y, w, h), c)

	if kind == "beer" or kind == "cider":          # tall pint tumbler
		dr.call(-3, -10, 6, 10, glass_sh)
		dr.call(-2, -9, 4, 9, fill)
		dr.call(-2, -9, 1, 9, fill_sh)
		dr.call(2, -9, 1, 9, glass)
		if kind == "beer":
			dr.call(-2, -10, 4, 2, foam)
	else:                                          # stemmed wine glass
		dr.call(-3, -9, 6, 3, glass_sh)
		dr.call(-2, -8, 4, 2, fill)
		dr.call(-2, -8, 1, 2, fill_sh)
		dr.call(2, -9, 1, 3, glass)
		dr.call(-1, -6, 2, 4, glass_sh)
		dr.call(-2, -2, 4, 1, glass_sh)
