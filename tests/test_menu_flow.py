"""MenuFlow navigation — the title/pause menu + save/load state machine.

Pure logic: a fake context records terminal effects, and the `save` module is
stubbed so no files are touched.
"""
import unittest

from systems import save
from systems.input_handler import Action
from systems.menu_flow import MenuFlow


class FakeCtx:
    def __init__(self):
        self.calls = []

    def start_new(self):
        self.calls.append('start_new')

    def load_slot(self, slot):
        self.calls.append(('load_slot', slot))

    def save_to_slot(self, slot):
        self.calls.append(('save_to_slot', slot))

    def resume(self):
        self.calls.append('resume')

    def open_title(self):
        self.calls.append('open_title')

    def quit_game(self):
        self.calls.append('quit_game')


def _press(flow, *actions):
    for a in actions:
        flow.handle_action(a)


CONFIRM = Action.CONFIRM
CANCEL = Action.CANCEL
DOWN = Action.MOVE_DOWN


class MenuFlowTest(unittest.TestCase):
    def setUp(self):
        # Stub the save module so navigation is deterministic and file-free.
        self._orig = (save.has_save, save.slot_info, save.delete_game)
        self._saved = set()           # slots that "have a save"
        self._deleted = []
        save.has_save = lambda slot: slot in self._saved
        save.slot_info = lambda slot: ({'scene_name': 'Gym', 'saved_at': 'now'}
                                       if slot in self._saved else None)
        save.delete_game = lambda slot: self._deleted.append(slot)

    def tearDown(self):
        save.has_save, save.slot_info, save.delete_game = self._orig

    # ---- title root ----
    def test_title_new_game(self):
        ctx = FakeCtx()
        _press(MenuFlow('title', ctx), CONFIRM)        # New Game
        self.assertEqual(ctx.calls, ['start_new'])

    def test_title_quit(self):
        ctx = FakeCtx()
        _press(MenuFlow('title', ctx), DOWN, DOWN, CONFIRM)   # -> Quit
        self.assertEqual(ctx.calls, ['quit_game'])

    def test_title_back_quits(self):
        ctx = FakeCtx()
        _press(MenuFlow('title', ctx), CANCEL)
        self.assertEqual(ctx.calls, ['quit_game'])

    # ---- pause root ----
    def test_pause_resume(self):
        ctx = FakeCtx()
        _press(MenuFlow('pause', ctx), CONFIRM)        # Resume
        self.assertEqual(ctx.calls, ['resume'])

    def test_pause_quit_to_title(self):
        ctx = FakeCtx()
        _press(MenuFlow('pause', ctx), DOWN, DOWN, CONFIRM)   # Quit to Title
        self.assertEqual(ctx.calls, ['open_title'])

    def test_pause_back_resumes(self):
        ctx = FakeCtx()
        _press(MenuFlow('pause', ctx), CANCEL)
        self.assertEqual(ctx.calls, ['resume'])

    # ---- save / load slot flow ----
    def test_save_into_empty_slot_then_returns_to_root(self):
        ctx = FakeCtx()
        flow = MenuFlow('pause', ctx)
        _press(flow, DOWN, CONFIRM)                    # Save Game -> slot list
        self.assertFalse(flow.at_root)
        _press(flow, CONFIRM)                          # slot 1 (empty) -> save straight in
        self.assertEqual(ctx.calls, [('save_to_slot', 1)])
        self.assertTrue(flow.at_root)                  # back at the pause root

    def test_load_occupied_slot_via_slot_action(self):
        self._saved.add(1)
        ctx = FakeCtx()
        flow = MenuFlow('title', ctx)
        _press(flow, DOWN, CONFIRM)                    # Load Game -> slot list
        _press(flow, CONFIRM)                          # slot 1 (occupied) -> slot action
        _press(flow, CONFIRM)                          # "Load"
        self.assertEqual(ctx.calls, [('load_slot', 1)])

    def test_delete_occupied_slot_returns_to_slots(self):
        self._saved.add(2)
        ctx = FakeCtx()
        flow = MenuFlow('pause', ctx)
        _press(flow, DOWN, CONFIRM)                    # Save Game -> slot list
        _press(flow, DOWN, CONFIRM)                    # slot 2 (occupied) -> slot action
        _press(flow, DOWN, CONFIRM)                    # "Delete"
        self.assertEqual(self._deleted, [2])
        self.assertEqual(ctx.calls, [])                # delete fires no ctx effect
        self.assertFalse(flow.at_root)                 # back on the slot list

    def test_back_from_slot_list_returns_to_root(self):
        ctx = FakeCtx()
        flow = MenuFlow('pause', ctx)
        _press(flow, DOWN, CONFIRM)                    # Save Game -> slot list
        _press(flow, CANCEL)                           # back
        self.assertTrue(flow.at_root)
        self.assertEqual(ctx.calls, [])


if __name__ == "__main__":
    unittest.main()
