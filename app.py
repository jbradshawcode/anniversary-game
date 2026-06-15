"""Main game — loop, event handling, and top-level wiring only"""
import math
import pygame
import sys
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, UI_FONT_NAME,
                    VB_MUSIC, KING_ST_MUSIC, PHONE_THREAD)
from entities import Player
from scenes import (Gym, KingSt, Salutation, Garden, Corridor, Reception,
                    Courtyard, Passage, Courts, WilliamMorris, VolleyCourt)
from systems.scene_manager import SceneManager
from systems.input_handler import (Action, event_to_action, get_held_direction,
                                    get_held_vector)
from systems.audio import MusicPlayer, SoundBank
from systems.dialogue import DialogueBox
from systems.story import StoryManager
from systems import menu, save, screens
from systems.party import Party
from systems.cutscene import Cutscene
from systems.lighting import Lighting


# Single source of truth for the four directions; the other maps derive from it.
_FACING_DELTA = {
    'left':  (-1,  0),
    'right': ( 1,  0),
    'up':    ( 0, -1),
    'down':  ( 0,  1),
}

_MOVE_MAP = {
    Action.MOVE_LEFT:  _FACING_DELTA['left'],
    Action.MOVE_RIGHT: _FACING_DELTA['right'],
    Action.MOVE_UP:    _FACING_DELTA['up'],
    Action.MOVE_DOWN:  _FACING_DELTA['down'],
}

_DIR_FACING = {delta: facing for facing, delta in _FACING_DELTA.items()}


_SCENE_NAMES = {1: "Gym", 2: "King Street", 3: "The Salutation", 4: "Beer Garden",
                5: "Corridor", 6: "Reception", 7: "Courtyard",
                8: "Passage", 9: "Netball Courts", 10: "Wetherspoons",
                11: "Volleyball"}


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("Modular Game Framework")
        self.clock = pygame.time.Clock()
        self.running = True
        self.music = MusicPlayer()
        self.sfx = SoundBank()                   # shared UI/overworld SFX (dialogue blip, etc.)
        self._scene_music = {2: KING_ST_MUSIC}   # scene_id -> looping track (else silence)

        self._font_large = pygame.font.SysFont(UI_FONT_NAME, 28)
        self._font_small = pygame.font.SysFont(UI_FONT_NAME, 14)
        self._hint_surf = self._font_small.render(
            "Arrows = move  |  Z = confirm  |  X = cancel  |  C = menu", True, WHITE)
        self._title_surf = None
        self._title_scene_id = None
        self.dialogue = DialogueBox(self.sfx)
        self.lighting = Lighting()
        self._turn_cooldown = 0.0

        gym = Gym()
        king_st = KingSt()
        salutation = Salutation()
        garden = Garden()
        corridor = Corridor()
        reception = Reception()
        courtyard = Courtyard()
        passage = Passage()
        courts = Courts()
        wetherspoons = WilliamMorris()
        self.court = VolleyCourt()

        self._start_col = (gym.walkable_cols[0] + gym.walkable_cols[1]) // 2
        self._start_row = (gym.walkable_rows[0] + gym.walkable_rows[1]) // 2
        self.player = Player(self._start_col, self._start_row)

        self.scene_manager = SceneManager()
        self.scene_manager.register(1, gym)
        self.scene_manager.register(2, king_st)
        self.scene_manager.register(3, salutation)
        self.scene_manager.register(4, garden)
        self.scene_manager.register(5, corridor)
        self.scene_manager.register(6, reception)
        self.scene_manager.register(7, courtyard)
        self.scene_manager.register(8, passage)
        self.scene_manager.register(9, courts)
        self.scene_manager.register(10, wetherspoons)
        self.scene_manager.register(11, self.court)
        self.scene_manager.start(1, self.player)

        self.party = Party()
        self.story = StoryManager()
        self.cutscene = Cutscene()
        self.story.bind(self.dialogue, self.scene_manager, self.player,
                        self.party, self.cutscene)
        self.cutscene.bind(self.dialogue, self.scene_manager, self.player,
                           self.party, self.story)
        self.cutscene.on_game_over = self._game_over
        self.story.on_launch_vb = self._launch_match
        self.story.on_week_end = self._week_end
        self.scene_manager.story = self.story
        self._last_scene_id = self.scene_manager.current_id
        self._scene_fade = 0.0           # quick fade-in on overworld scene change
        self._fade_black = None
        self._vb_retry = False
        self._gameover_lines = []
        self._results = None
        self._phone = None

        # app_state in {'title', 'playing', 'paused'}; menu_mode selects the
        # active menu's options/dispatch (and 'title'/'paused' the backdrop).
        self.app_state = 'title'
        self.menu_mode = 'title'
        self.menu = None
        self._slot_target = None
        self._slot_source = None
        self._open_title()

    # ---- top-level state machine -------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            action = event_to_action(event)
            if self.app_state == 'playing':
                if action == Action.QUIT and not self.cutscene.active:
                    self._open_pause()           # pause -> Resume / Save / Quit to Title / Desktop
                else:
                    self._play_event(action)
            elif self.app_state in ('gameover', 'results', 'phone'):
                self._interlude_event(action)
            else:
                self._menu_event(action)

    def _interlude_event(self, action):
        if action != Action.CONFIRM:
            return
        if self.app_state == 'gameover':
            self._retry()
        elif self.app_state == 'results':
            self._phone = screens.Phone(PHONE_THREAD)
            self.app_state = 'phone'
        elif self.app_state == 'phone':
            if not self._phone.advance():      # all bubbles shown -> wrap the week
                self._finish_week()

    def _play_event(self, action):
        scene = self.scene_manager.current
        if self.cutscene.active:             # cutscenes own input: only drive dialogue
            if self.dialogue.active:
                if action == Action.CONFIRM:
                    self.dialogue.advance()
                elif action == Action.CANCEL:
                    self.dialogue.skip()
                elif action in _MOVE_MAP:
                    self.dialogue.move_choice(_MOVE_MAP[action][0])
            return
        if getattr(scene, 'wants_raw_input', False) and not self.dialogue.active:
            if action is not None:
                scene.handle_action(action)
            return
        if action == Action.CONFIRM:
            if self.dialogue.active:
                self.dialogue.advance()
            elif not self.player.moving:
                self._interact_ahead()
        elif action == Action.CANCEL:
            if self.dialogue.active:
                self.dialogue.skip()         # X speeds the text to the full line
        elif action == Action.MENU:
            if not self.dialogue.active:
                self._open_pause()           # C opens the menu
        elif action == Action.DEBUG_GARDEN:
            self.story.debug_advance()
        elif action in _MOVE_MAP:
            dtx, dty = _MOVE_MAP[action]
            if self.dialogue.active:
                self.dialogue.move_choice(dtx)
            else:
                new_facing = _DIR_FACING[(dtx, dty)]
                if self.player.facing != new_facing and not self.player.moving:
                    self.player.facing = new_facing
                    self._turn_cooldown = 0.12
                else:
                    self.scene_manager.try_move(dtx, dty, self.player)

    def _interact_ahead(self):
        """Talk to whatever sprite the player is facing — scene object or a
        seated follower (the crew become party followers, not scene objects)."""
        dx, dy = _FACING_DELTA[self.player.facing]
        tx = self.player.tile_x + dx
        ty = self.player.tile_y + dy
        for obj in self.scene_manager.current.objects:
            if obj.occupies(tx, ty):
                if not self.story.interact(obj) and obj.interaction_text:
                    self.dialogue.start(obj.interaction_text, speaker=obj.name)
                return
        for f in self.party.followers:
            if f.tile_x == tx and f.tile_y == ty:
                self.story.talk(f.name)
                return

    # ---- menus & save flow -------------------------------------------------
    def _open_title(self):
        self.app_state = 'title'
        self.menu_mode = 'title'
        self.menu = menu.Menu("PYGAME ADVENTURE", ["New Game", "Load Game", "Quit"],
                              hint="Arrows = move   Z = select   X = back")

    def _open_pause(self):
        self.app_state = 'paused'
        self.menu_mode = 'pause'
        self.menu = menu.Menu("Paused",
                              ["Resume", "Save Game", "Quit to Title", "Quit to Desktop"],
                              hint="Z = select   X / Esc = back")

    def _open_slots(self, mode):
        self.menu_mode = mode  # 'save' or 'load'; app_state (title/paused) is the backdrop
        title = "Save Game" if mode == 'save' else "Load Game"
        self.menu = menu.Menu(title, self._slot_labels() + ["Back"])

    def _open_slot_action(self, slot, source):
        self._slot_target = slot
        self._slot_source = source
        self.menu_mode = 'slot_action'
        verb = "Load" if source == 'load' else "Overwrite"
        self.menu = menu.Menu("Slot {0}".format(slot), [verb, "Delete", "Back"])

    def _slot_labels(self):
        labels = []
        for slot in save.SLOTS:
            info = save.slot_info(slot)
            if info:
                labels.append("Slot {0}: {1}  {2}".format(
                    slot, info['scene_name'], info['saved_at']))
            else:
                labels.append("Slot {0}: Empty".format(slot))
        return labels

    def _resume(self):
        self.app_state = 'playing'
        self.menu_mode = None
        self.menu = None

    def _menu_event(self, action):
        if action == Action.MOVE_UP:
            self.menu.move(-1)
        elif action == Action.MOVE_DOWN:
            self.menu.move(1)
        elif action == Action.CONFIRM:
            self._menu_select()
        elif action in (Action.CANCEL, Action.QUIT):
            self._menu_back()

    def _menu_select(self):
        i = self.menu.index
        mode = self.menu_mode
        if mode == 'title':
            (self._start_new, lambda: self._open_slots('load'),
             self._quit)[i]()
        elif mode == 'pause':
            (self._resume, lambda: self._open_slots('save'),
             self._open_title, self._quit)[i]()
        elif mode in ('save', 'load'):
            if i >= len(save.SLOTS):          # the trailing "Back"
                self._menu_back()
                return
            slot = save.SLOTS[i]
            if save.has_save(slot):
                self._open_slot_action(slot, mode)
            elif mode == 'save':              # empty slot: save straight in
                self._save_to_slot(slot)
                self._open_pause()
        elif mode == 'slot_action':
            slot = self._slot_target
            if i == 0:                        # Load / Overwrite
                if self._slot_source == 'load':
                    self._load_slot(slot)
                else:
                    self._save_to_slot(slot)
                    self._open_pause()
            elif i == 1:                      # Delete
                save.delete_game(slot)
                self._open_slots(self._slot_source)
            else:                             # Back
                self._open_slots(self._slot_source)

    def _menu_back(self):
        if self.menu_mode in ('save', 'load'):
            self._open_title() if self.app_state == 'title' else self._open_pause()
        elif self.menu_mode == 'slot_action':
            self._open_slots(self._slot_source)
        elif self.menu_mode == 'pause':
            self._resume()
        else:
            self._quit()

    def _quit(self):
        self.running = False

    def _start_new(self):
        self.cutscene.active = False
        self._vb_retry = False
        self.story.restore(0, [], scene_id=None)
        self.scene_manager.jump_to(1, self.player)
        self.player.teleport(self._start_col, self._start_row)
        self.player.facing = 'down'
        self._last_scene_id = self.scene_manager.current_id
        self._update_scene_music(self.scene_manager.current_id)
        self.story.sync_party(self.player)
        self._resume()
        self.story.begin()             # fire the opening cutscene (fade-in + intro)

    def _load_slot(self, slot):
        data = save.load_game(slot)
        if not data:
            return
        self.cutscene.active = False
        self._vb_retry = False
        self.story.restore(data['beat'], data['flags'], scene_id=data['scene_id'],
                           vb_attempts=data.get('vb_attempts', 0))
        self.scene_manager.jump_to(data['scene_id'], self.player)
        self.player.teleport(data['tile_x'], data['tile_y'])
        self.player.facing = data['facing']
        self._last_scene_id = self.scene_manager.current_id
        self._update_scene_music(self.scene_manager.current_id)
        self.story.sync_party(self.player)
        self._resume()

    def _save_to_slot(self, slot):
        data = {
            'scene_id': self.scene_manager.current_id,
            'scene_name': _SCENE_NAMES.get(self.scene_manager.current_id, '?'),
            'tile_x': self.player.tile_x,
            'tile_y': self.player.tile_y,
            'facing': self.player.facing,
            'beat_name': self.story.beat['name'],
        }
        data.update(self.story.snapshot())
        save.save_game(slot, data)

    def _draw_title(self):
        menu.title_backdrop(self.screen)
        if self.menu_mode == 'title':
            menu.hero(self.screen, "PYGAME ADVENTURE")
            menu.options(self.screen, self.menu.options, self.menu.index, 248)
            menu.text(self.screen, self.menu.hint, SCREEN_WIDTH // 2,
                      SCREEN_HEIGHT - 34, menu.font(UI_FONT_NAME, 14), menu.MUTED)
        else:
            # load / slot-action sub-menus share the backdrop
            self.menu.draw(self.screen)

    def _draw_objective(self):
        text = self.story.objective()
        if not text:
            return
        fnt = menu.font(UI_FONT_NAME, 15)
        surf = fnt.render(text, True, menu.INK)
        pill = pygame.Rect(0, 0, surf.get_width() + 28, surf.get_height() + 10)
        pill.topright = (SCREEN_WIDTH - 10, 10)   # tuck the objective into the top-right
        chip = pygame.Surface(pill.size, pygame.SRCALPHA)
        radius = pill.height // 2
        pygame.draw.rect(chip, (18, 18, 28, 205), chip.get_rect(), border_radius=radius)
        pygame.draw.rect(chip, menu.ACCENT, chip.get_rect(), 2, border_radius=radius)
        self.screen.blit(chip, pill.topleft)
        self.screen.blit(surf, (pill.centerx - surf.get_width() // 2,
                                pill.centery - surf.get_height() // 2))

    def update(self, dt: float):
        if self.app_state != 'playing':
            return
        if self._vb_retry:                       # lost the 3v3 — go again
            self._vb_retry = False
            self._launch_match()
            return
        if self._scene_fade > 0:
            self._scene_fade = max(0.0, self._scene_fade - dt / 0.22)
        self.dialogue.update(dt)
        scene = self.scene_manager.current
        if getattr(scene, 'wants_raw_input', False):
            scene.handle_held(get_held_vector())
            scene.update(dt)
            return

        # Scene-change bookkeeping runs even mid-cutscene (a transition can hand
        # straight off to a cutscene that repositions the crew).
        if self.scene_manager.current_id != self._last_scene_id:
            if not self.cutscene.active:         # cutscenes do their own fades
                self._scene_fade = 1.0
            self._last_scene_id = self.scene_manager.current_id
            self.party.on_scene_change(self.player)
            self._update_scene_music(self.scene_manager.current_id)

        if self.cutscene.active:
            self.cutscene.update(dt)
            scene.update(dt)
            return

        self.player.update(dt)
        scene.update(dt)
        self.party.update(dt, self.player)
        if not self.player.moving:
            self.story.notify_reach(self.scene_manager.current_id,
                                    (self.player.tile_x, self.player.tile_y))

        if self._turn_cooldown > 0:
            self._turn_cooldown -= dt
        elif not self.player.moving and not self.dialogue.active:
            direction = get_held_direction()
            if direction:
                self.scene_manager.try_move(direction[0], direction[1], self.player)

    def _update_scene_music(self, scene_id):
        track = self._scene_music.get(scene_id)
        if track:
            self.music.play(track)
        else:
            self.music.stop()

    def _launch_match(self):
        """Story hook: drop into the 3v3 (Leonard's lot) at the difficulty Dan
        picked in the vb_setup beat, running the controls warm-up first if asked."""
        level = ('easy' if self.story.has('w1_diff_easy')
                 else 'medium' if self.story.has('w1_diff_medium')
                 else 'hard')
        if self.story.has('w1_want_tut') and not self.story.has('w1_tut_done'):
            self._launch_tutorial(level)
            return
        self.court.configure('match', level)
        self.court.on_finish = self._end_volleyball
        self.music.play(VB_MUSIC)
        self.scene_manager.jump_to(11, self.player)

    def _launch_tutorial(self, level):
        """The warm-up: the 5-step controls tutorial, then straight into the match."""
        self.court.configure('tutorial', level)
        self.court.on_finish = self._end_tutorial
        self.music.play(VB_MUSIC)
        self.scene_manager.jump_to(11, self.player)

    def _end_tutorial(self):
        self.story.set_flag('w1_tut_done')   # records the warm-up; not an advance flag
        self._launch_match()

    def _end_volleyball(self):
        won = self.court.score[0] > self.court.score[1]
        self.story.vb_attempts += 1
        self.music.stop()
        if won:
            self.scene_manager.jump_to(1, self.player)
            self._last_scene_id = self.scene_manager.current_id
            self.story.set_flag('w1_won_vb')        # -> Dan asks about the pub
        else:
            self._vb_retry = True                   # relaunch next frame

    # ---- story interludes --------------------------------------------------
    def _game_over(self, lines):
        self._gameover_lines = lines
        self.app_state = 'gameover'

    def _retry(self):
        self.app_state = 'playing'
        self.story.replay_beat()

    def _week_end(self):
        self._results = screens.Results(self.story.stars(),
                                        max(1, self.story.vb_attempts))
        self.app_state = 'results'

    def _finish_week(self):
        self.app_state = 'playing'
        self.story.set_flag('w1_left')

    def draw(self):
        if self.app_state == 'title':
            self._draw_title()
            pygame.display.flip()
            return
        if self.app_state == 'gameover':
            screens.draw_game_over(self.screen, self._gameover_lines)
            pygame.display.flip()
            return
        if self.app_state == 'results':
            self._results.draw(self.screen)
            pygame.display.flip()
            return
        if self.app_state == 'phone':
            self._phone.draw(self.screen)
            pygame.display.flip()
            return

        scene = self.scene_manager.current
        if scene.scrolling:
            world = scene.get_world_surface()
            scene.draw(world)
            self.party.draw(world)
            self.player.draw(world)
            scene.draw_overlay(world)
            cam_x = scene.get_camera_x(self.player.x)
            self.screen.blit(world, (0, 0), (cam_x, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            scene.draw(self.screen)
            if not getattr(scene, 'wants_raw_input', False):
                self.party.draw(self.screen)
                self.player.draw(self.screen)
            scene.draw_overlay(self.screen)

        if not getattr(scene, 'wants_raw_input', False):
            self.lighting.draw(self.screen, self.scene_manager.current_id,
                               getattr(scene, 'lighting', None))

        if self._title_scene_id != self.scene_manager.current_id:
            self._title_scene_id = self.scene_manager.current_id
            name = _SCENE_NAMES.get(self._title_scene_id,
                                    f"Scene {self._title_scene_id}")
            self._title_surf = self._font_large.render(name, True, WHITE)

        self.screen.blit(self._title_surf,
                         (SCREEN_WIDTH // 2 - self._title_surf.get_width() // 2, 20))
        raw = getattr(scene, 'wants_raw_input', False)
        if not self.dialogue.active and not raw and not self.cutscene.active:
            self._draw_objective()
            self.screen.blit(self._hint_surf, (10, SCREEN_HEIGHT - 30))
            if self.app_state == 'playing' and not scene.scrolling:
                self._draw_affordance(scene)

        self.cutscene.draw_fade(self.screen)
        self.dialogue.draw(self.screen)
        if self.app_state == 'paused':
            self.menu.draw(self.screen, dim=True)
        if self._scene_fade > 0:
            if self._fade_black is None:
                self._fade_black = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                self._fade_black.fill((0, 0, 0))
            self._fade_black.set_alpha(int(255 * self._scene_fade))
            self.screen.blit(self._fade_black, (0, 0))
        pygame.display.flip()

    def _draw_affordance(self, scene):
        """A small bobbing chevron over the interactable the player is facing."""
        if self.player.moving:
            return
        dx, dy = _FACING_DELTA[self.player.facing]
        tx, ty = self.player.tile_x + dx, self.player.tile_y + dy
        target = None
        for obj in scene.objects:
            if obj.occupies(tx, ty) and (obj.interaction_text
                                         or self.story.interactable_at(tx, ty)):
                target = (obj.x, obj.y)
                break
        if target is None:
            for f in self.party.followers:
                if f.tile_x == tx and f.tile_y == ty and self.story.can_talk():
                    target = (f.x, f.y)
                    break
        if target is None:
            return
        bob = int(3 * abs(math.sin(pygame.time.get_ticks() / 220.0)))
        cx, cy = int(target[0]), int(target[1]) - 26 - bob
        pygame.draw.polygon(self.screen, (20, 20, 28),
                            [(cx - 7, cy - 1), (cx + 7, cy - 1), (cx, cy + 9)])
        pygame.draw.polygon(self.screen, (255, 240, 150),
                            [(cx - 6, cy), (cx + 6, cy), (cx, cy + 7)])

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
