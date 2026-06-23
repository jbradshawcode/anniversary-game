"""Scene geometry — tile-coordinate definitions for every scene.

walkable_cols / walkable_rows are inclusive ranges. Add 'exits' to wire up
transitions without touching code. Pure data, imported by scenes/base.py
(scene build) and systems/factory.py (object spawns)."""

SCENE_CONFIGS = {
    'gym': {
        'id': 1,
        'walkable_cols': (1, 18),
        'walkable_rows': (1, 13),
        # up: through the double doors at the top (cols 8-11)
        'exits': {'up': {'scene': 5, 'cols': (8, 11)}},
        'entry_points': {'down': (9, 1)},
        'objects': {
            'trees': [], 'rocks': [],
            'ball_baskets': [(2, 7), (17, 7)],
            'james': [(5, 7)], 'dan': [(14, 7)],
            'matt': [(3, 4)],
            'leonard': [(16, 7)],        # Leonard's lot — only in Ch1 (absent weeks 2-4)
            'nat': [(8, 1)],             # starts beside Sarah, just inside the doors
            'bailey': [(6, 4)],
            'mayu': [(15, 10)],
            'wallace': [(8, 10)],
            'matus': [(18, 3)],          # the ref, sitting on the right-hand bench
            'benches': [(1, 2, 5), (1, 8, 5), (18, 2, 5), (18, 8, 5)],
        },
    },
    'king_st': {
        'id': 2,
        'map_cols': 180,
        'walkable_cols': (0, 179),
        'walkable_rows': (4, 10),
        'exits': {
            'down': {'scene': 7, 'cols': (3, 5)},
            # two doors on the north side: the Salutation (col 97) and the
            # Wetherspoons / William Morris (the far east frontage, cols 176-177)
            'up': [
                {'scene': 3, 'target': (2, 9), 'cols': (97, 97)},   # -> Salutation (inside front door)
                {'scene': 10, 'target': (9, 13), 'cols': (176, 177)},
            ],
        },
        'entry_points': {'down': (4, 10)},
        # No trees: King St is a paved high street. Street furniture (bollards lining
        # the kerb, bins, a post box) is drawn into the scene background instead.
        'objects': {},
    },
    'salutation': {
        'id': 3,
        # Wide, horizontally-scrolling pub (see scenes/salutation.py + specs): an
        # L-peninsula bar across the top-centre, tartan banquettes along the bottom
        # wall, a glazed conservatory lean-to on the right. Front door off-centre on
        # the WEST edge (off King St); bi-fold garden doors on the EAST edge.
        'map_cols': 34,
        'walkable_cols': (1, 32),
        'walkable_rows': (1, 11),
        'exits': {
            'left': {'scene': 2, 'target': (97, 5), 'rows': (8, 10)},   # front door -> King St (north pavement)
            'right': {'scene': 4, 'target': (2, 7), 'rows': (3, 5)},    # garden doors -> garden
        },
        'entry_points': {'left': (2, 9), 'right': (32, 5)},
        # Milla stands at the right end of the bar (a counter tile, drawn a row back):
        # order from (18, 4) facing up. The entry cutscene walks her to the left end
        # to serve the team, then back here for later "regular" ordering.
        'objects': {'milla': [(18, 3)]},
    },
    'garden': {
        'id': 4,
        # Compact single-screen walled garden: pub conservatory + loose-chair
        # foreground (left), a contiguous pillared booth run lining both walls
        # with the communal table central, deep planting close at the right.
        'walkable_cols': (1, 16),
        'walkable_rows': (1, 13),
        # left: back into the pub through the conservatory doors (rows 6-8)
        'exits': {'left': {'scene': 3, 'target': (32, 5), 'rows': (6, 8)}},
        'entry_points': {'up': (2, 7)},
        'objects': {},
    },
    'corridor': {
        'id': 5,
        'walkable_cols': (1, 18),
        'walkable_rows': (4, 13),
        'exits': {
            # right: out the east end of the hallway (rows 4-6)
            'right': {'scene': 6, 'rows': (4, 6)},
            # down: down the stem to the gym doors (cols 8-11)
            'down': {'scene': 1, 'cols': (8, 11)},
        },
        'entry_points': {
            'up': (10, 13),
            'left': (18, 5),
        },
        'objects': {},
    },
    'reception': {
        'id': 6,
        'walkable_cols': (1, 14),
        'walkable_rows': (5, 10),
        'exits': {
            # left/right doors sit at rows 6-7
            'left': {'scene': 5, 'rows': (6, 7)},
            'right': {'scene': 8, 'rows': (6, 7)},
        },
        'entry_points': {
            'right': (2, 7),
            'left': (14, 7),
        },
        'objects': {},
    },
    'courtyard': {
        'id': 7,
        'walkable_cols': (3, 16),
        'walkable_rows': (2, 12),
        'exits': {
            # up: through the gap between the buildings where the path runs (cols 9-10)
            'up': {'scene': 2, 'target': (4, 10), 'cols': (9, 10)},
            # Door back to courts sits at the foot of the central path (col 10),
            # one column off the col-9 arrival from courts so a held Down key
            # can't re-trigger it.
            'down': {'scene': 9, 'target': (5, 13), 'cols': (10, 10)},
        },
        'entry_points': {
            'up': (10, 11),
            'down': (10, 3),
        },
        'objects': {},
    },
    'passage': {
        'id': 8,
        'walkable_cols': (1, 18),
        'walkable_rows': (5, 12),
        'exits': {
            # left: out the reception door at the bottom-left (row 11)
            'left': {'scene': 6, 'rows': (11, 11)},
            'right': {'scene': 9, 'target': (3, 3), 'rows': (5, 7)},
        },
        'entry_points': {
            'right': (1, 11),
            'left': (17, 6),
        },
        'objects': {},
    },
    'courts': {
        'id': 9,
        'walkable_cols': (2, 16),
        'walkable_rows': (2, 14),
        'exits': {
            'left': {'scene': 8, 'target': (17, 6), 'rows': (2, 3)},
            # Exit at the bottom-left gate (cols 3,4) drops you at the foot of
            # the courtyard's central path (col 9), one column off the
            # courtyard's return-door so a held Down key won't bounce you back.
            'down': {'scene': 7, 'target': (9, 12), 'cols': (3, 4)},
        },
        'entry_points': {
            'right': (3, 3),
            'down': (10, 13),
        },
        'objects': {},
    },
    'wetherspoons': {
        'id': 10,
        'walkable_cols': (1, 18),
        'walkable_rows': (3, 13),
        'exits': {
            # out the front doors back onto King St, by the frontage
            'down': {'scene': 2, 'target': (177, 4), 'cols': (8, 11)},
        },
        'entry_points': {'up': (9, 13)},
        'objects': {},
    },
    # Volleyball minigame — self-contained real-time scene (free movement, own
    # input). The tile grid is unused; actors move on free pixel coordinates.
    'court': {
        'id': 11,
        'walkable_cols': (1, 18),
        'walkable_rows': (1, 13),
        'exits': {},
        'entry_points': {},
        'objects': {},
    },
    # Diving minigame (Ch3) — another self-contained real-time scene.
    'dive': {
        'id': 12,
        'walkable_cols': (1, 18),
        'walkable_rows': (1, 13),
        'exits': {},
        'entry_points': {},
        'objects': {},
    },
}
