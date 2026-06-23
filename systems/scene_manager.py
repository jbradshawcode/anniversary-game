"""Manages the active scene and handles transitions between scenes.

To add a new scene:
  1. Add its config to SCENE_CONFIGS with an 'exits' dict (e.g. {'right': 3})
  2. Create the scene class in scenes/
  3. Register it: scene_manager.register(3, Salutation())
"""
from typing import Dict, Optional, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from scenes.base import Scene
    from entities.characters.player import Player


class SceneManager:
    def __init__(self):
        self._scenes: Dict[int, 'Scene'] = {}
        self._current_id: Optional[int] = None
        self.current: Optional['Scene'] = None
        self.story = None
        self.party = None

    def set_party(self, party) -> None:
        self.party = party              # so the player can't walk through the crew

    def register(self, scene_id: int, scene: 'Scene'):
        self._scenes[scene_id] = scene

    def _crew_at(self, tx: int, ty: int) -> bool:
        """A crew member occupies this tile — a person is solid whatever their state."""
        if self.party is None:
            return False
        return any(f.tile_x == tx and f.tile_y == ty for f in self.party.followers)

    def scene(self, scene_id: int) -> Optional['Scene']:
        return self._scenes.get(scene_id)

    def start(self, scene_id: int, player: 'Player'):
        self._current_id = scene_id
        self.current = self._scenes[scene_id]
        self.current.enter(player)

    def try_move(self, dtx: int, dty: int, player: 'Player'):
        """Process one tile-step request. Handles both normal moves and exits."""
        if player.moving:
            return

        exit_dir = None
        if dtx == 1 and player.tile_x >= self.current.walkable_cols[1]:
            exit_dir = 'right'
        elif dtx == -1 and player.tile_x <= self.current.walkable_cols[0]:
            exit_dir = 'left'
        elif dty == 1 and player.tile_y >= self.current.walkable_rows[1]:
            exit_dir = 'down'
        elif dty == -1 and player.tile_y <= self.current.walkable_rows[0]:
            exit_dir = 'up'

        if exit_dir:
            scene_id, entry_pos = self._resolve_exit(
                self.current.exits.get(exit_dir), player)
            if scene_id is not None:
                if self.story and self.story.try_door_block(scene_id):
                    return                        # this specific door is barred (e.g. wrong pub)
                if self.story and self.story.exit_blocked(self._current_id, exit_dir):
                    self.story.show_locked(self._current_id)
                    return
                if self.story and self.story.exit_ends_week(self._current_id, exit_dir):
                    self.story.trigger_week_end()    # head out -> results, not a scene swap
                    return
                self._transition_to(scene_id, player, exit_dir, entry_pos)
                return

        if self.story:
            region = self.story.confine(self._current_id)
            if region and not self._in_region(player.tile_x + dtx,
                                              player.tile_y + dty, region):
                return

        if self._crew_at(player.tile_x + dtx, player.tile_y + dty):
            return                            # a crew member is there — you can't walk through them

        player.try_move(dtx, dty, self.current)

    @staticmethod
    def _in_region(tx: int, ty: int, region) -> bool:
        (c0, r0), (c1, r1) = region
        return c0 <= tx <= c1 and r0 <= ty <= r1

    def _resolve_exit(
        self, exit_val: Optional[Union[int, dict]], player: 'Player',
    ) -> Tuple[Optional[int], Optional[tuple]]:
        if exit_val is None:
            return None, None
        # A direction may hold several gated exits (e.g. two doors on one edge);
        # return the first whose col/row gate matches the player.
        if isinstance(exit_val, list):
            for ev in exit_val:
                scene_id, entry_pos = self._resolve_exit(ev, player)
                if scene_id is not None:
                    return scene_id, entry_pos
            return None, None
        if isinstance(exit_val, dict):
            cols = exit_val.get('cols')
            if cols and not (cols[0] <= player.tile_x <= cols[1]):
                return None, None
            rows = exit_val.get('rows')
            if rows and not (rows[0] <= player.tile_y <= rows[1]):
                return None, None
            return exit_val['scene'], exit_val.get('target')
        return exit_val, None

    def _transition_to(self, new_id: int, player: 'Player', exit_dir: str,
                       entry_pos: Optional[tuple] = None):
        self.current.exit()
        self._current_id = new_id
        self.current     = self._scenes[new_id]
        self.current.clear_extra_blockers()    # stale seated-follower blockers, etc.

        if entry_pos:
            player.teleport(entry_pos[0], entry_pos[1])
        else:
            entry = self.current.entry_points.get(exit_dir)
            if entry:
                player.teleport(entry[0], entry[1])
            else:
                col0, col1 = self.current.walkable_cols
                row0, row1 = self.current.walkable_rows
                mid_col = (col0 + col1) // 2
                mid_row = (row0 + row1) // 2

                if exit_dir == 'right':
                    player.teleport(col0, mid_row)
                elif exit_dir == 'left':
                    player.teleport(col1, mid_row)
                elif exit_dir == 'down':
                    player.teleport(mid_col, row0)
                elif exit_dir == 'up':
                    player.teleport(mid_col, row1)
        self.current.enter(player)
        if self.story:
            self.story.notify_enter(self._current_id)

    def jump_to(self, scene_id: int, player: 'Player'):
        if self.current:
            self.current.exit()
        self._current_id = scene_id
        self.current = self._scenes[scene_id]
        self.current.clear_extra_blockers()
        entry = self.current.entry_points
        pos = next(iter(entry.values())) if entry else None
        if pos:
            player.teleport(pos[0], pos[1])
        self.current.enter(player)
        if self.story:
            self.story.notify_enter(self._current_id)

    @property
    def current_id(self) -> Optional[int]:
        return self._current_id
