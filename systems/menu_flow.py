"""Menu navigation + save/load sub-state machine.

A self-contained state machine over Menu screens: it owns where you are in the
title/pause menu tree and the slot save/load flow, and fires terminal effects
back through a context. It knows nothing about pygame beyond the Menu it builds;
the surfaces that show it (TitleMode, the pause overlay) own the presentation.

Roots:
  'title' — New Game / Load Game / Quit
  'pause' — Resume / Save Game / Quit to Title / Quit to Desktop

The context must provide: start_new(), load_slot(slot), save_to_slot(slot),
resume(), open_title(), quit_game().
"""
from typing import List, Optional
from systems import menu, save
from systems.input_handler import Action

_TITLE_HINT = "Arrows = move   Z = select   X = back"
_PAUSE_HINT = "Z = select   X / Esc = back"


class MenuFlow:
    def __init__(self, root: str, ctx) -> None:
        self._root = root            # 'title' or 'pause'
        self._ctx = ctx
        self._state = 'root'         # 'root' | 'save' | 'load' | 'slot_action'
        self._slot_target: Optional[int] = None
        self._slot_source: Optional[str] = None
        self.menu = None
        self._open_root()

    # ---- queried by the surfaces (TitleMode / pause overlay) ----
    @property
    def at_root(self) -> bool:
        return self._state == 'root'

    @property
    def current_menu(self):
        return self.menu

    # ---- input ----
    def handle_action(self, action) -> None:
        if action == Action.MOVE_UP:
            self.menu.move(-1)
        elif action == Action.MOVE_DOWN:
            self.menu.move(1)
        elif action == Action.CONFIRM:
            self._select()
        elif action in (Action.CANCEL, Action.QUIT):
            self._back()

    # ---- navigation ----
    def _select(self) -> None:
        i = self.menu.index
        if self._state == 'root':
            self._select_root(i)
        elif self._state in ('save', 'load'):
            self._select_slot(i)
        else:                                # 'slot_action'
            self._select_slot_action(i)

    def _select_root(self, i: int) -> None:
        if self._root == 'title':
            (self._ctx.start_new,
             lambda: self._open_slots('load'),
             self._ctx.quit_game)[i]()
        else:                                # 'pause'
            (self._ctx.resume,
             lambda: self._open_slots('save'),
             self._ctx.open_title,
             self._ctx.quit_game)[i]()

    def _select_slot(self, i: int) -> None:
        if i >= len(save.SLOTS):             # the trailing "Back"
            self._back()
            return
        slot = save.SLOTS[i]
        if save.has_save(slot):
            self._open_slot_action(slot, self._state)
        elif self._state == 'save':          # empty slot: save straight in
            self._ctx.save_to_slot(slot)
            self._open_root()

    def _select_slot_action(self, i: int) -> None:
        slot = self._slot_target
        if i == 0:                           # Load / Overwrite
            if self._slot_source == 'load':
                self._ctx.load_slot(slot)
            else:
                self._ctx.save_to_slot(slot)
                self._open_root()
        elif i == 1:                         # Delete
            save.delete_game(slot)
            self._open_slots(self._slot_source)
        else:                                # Back
            self._open_slots(self._slot_source)

    def _back(self) -> None:
        if self._state in ('save', 'load'):
            self._open_root()
        elif self._state == 'slot_action':
            self._open_slots(self._slot_source)
        elif self._root == 'pause':          # at root
            self._ctx.resume()
        else:                                # title root
            self._ctx.quit_game()

    # ---- menu builders ----
    def _open_root(self) -> None:
        self._state = 'root'
        if self._root == 'title':
            self.menu = menu.Menu("PYGAME ADVENTURE",
                                  ["New Game", "Load Game", "Quit"], hint=_TITLE_HINT)
        else:
            self.menu = menu.Menu("Paused",
                                  ["Resume", "Save Game", "Quit to Title", "Quit to Desktop"],
                                  hint=_PAUSE_HINT)

    def _open_slots(self, state: str) -> None:
        self._state = state                  # 'save' or 'load'
        title = "Save Game" if state == 'save' else "Load Game"
        self.menu = menu.Menu(title, self._slot_labels() + ["Back"])

    def _open_slot_action(self, slot: int, source: str) -> None:
        self._slot_target = slot
        self._slot_source = source
        self._state = 'slot_action'
        verb = "Load" if source == 'load' else "Overwrite"
        self.menu = menu.Menu("Slot {0}".format(slot), [verb, "Delete", "Back"])

    @staticmethod
    def _slot_labels() -> List[str]:
        labels = []
        for slot in save.SLOTS:
            info = save.slot_info(slot)
            if info:
                labels.append("Slot {0}: {1}  {2}".format(
                    slot, info['scene_name'], info['saved_at']))
            else:
                labels.append("Slot {0}: Empty".format(slot))
        return labels
