"""TileMap walkability — pure logic, no pygame, no display."""
import unittest

from systems.tilemap import TileMap


def _map(static_blocked=(), walls=frozenset()):
    # 6x6 grid; walkable rectangle is cols 1-4, rows 1-4.
    return TileMap((1, 4), (1, 4), 6, 6, static_blocked, walls)


class TileMapTest(unittest.TestCase):
    def test_inside_walkable_rect(self):
        tm = _map()
        self.assertTrue(tm.is_walkable(1, 1))
        self.assertTrue(tm.is_walkable(4, 4))

    def test_outside_rect_is_blocked(self):
        tm = _map()
        self.assertFalse(tm.is_walkable(0, 0))
        self.assertFalse(tm.is_walkable(5, 5))

    def test_out_of_bounds(self):
        tm = _map()
        self.assertFalse(tm.is_walkable(-1, 2))
        self.assertFalse(tm.is_walkable(2, 6))
        self.assertFalse(tm.is_walkable(6, 2))

    def test_static_blocked_tile(self):
        tm = _map(static_blocked=[(2, 2)])
        self.assertFalse(tm.is_walkable(2, 2))
        self.assertTrue(tm.is_walkable(3, 2))

    def test_dynamic_blocker(self):
        tm = _map()
        self.assertTrue(tm.is_walkable(3, 3))
        tm.set_blockers([(3, 3)])
        self.assertFalse(tm.is_walkable(3, 3))

    def test_rebuild_frees_vacated_tile(self):
        # The despawn invariant: clearing blockers re-opens the tile.
        tm = _map()
        tm.set_blockers([(3, 3)])
        self.assertFalse(tm.is_walkable(3, 3))
        tm.set_blockers([])
        self.assertTrue(tm.is_walkable(3, 3))

    def test_static_survives_a_rebuild(self):
        tm = _map(static_blocked=[(2, 2)])
        tm.set_blockers([(3, 3)])
        self.assertFalse(tm.is_walkable(2, 2))
        self.assertFalse(tm.is_walkable(3, 3))

    def test_has_wall_is_directional(self):
        tm = _map(walls=frozenset({((1, 1), (1, 2))}))
        self.assertTrue(tm.has_wall(1, 1, 1, 2))
        self.assertFalse(tm.has_wall(1, 2, 1, 1))   # reverse edge absent
        self.assertFalse(tm.has_wall(2, 2, 2, 3))


if __name__ == "__main__":
    unittest.main()
