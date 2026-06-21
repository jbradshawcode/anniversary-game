"""App modes — the loop's active state.

A Mode owns input, update and draw for the current screen. The main loop holds
exactly one active Mode and dispatches to it uniformly. PlayMode is the
overworld; TitleMode and the interludes (GameOver/Results/Phone) replace it.
The pause menu is a Game-level overlay drawn on top of the active mode, not a
mode itself; dialogue and cutscenes are overlays PlayMode drives.
"""
import math
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_NAME, WHITE, DEV
from systems.input_handler import Action, get_held_direction, get_held_vector
from systems import menu, screens
from systems.menu_flow import MenuFlow


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


class Mode:
    def handle_action(self, action) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen) -> None:
        pass


class TitleMode(Mode):
    """The title screen; hosts a title-rooted MenuFlow (New Game / Load / Quit)."""
    def __init__(self, game) -> None:
        self._game = game
        self._flow = MenuFlow('title', game)

    def handle_action(self, action) -> None:
        self._flow.handle_action(action)

    def draw(self, screen) -> None:
        menu.title_backdrop(screen)
        current = self._flow.current_menu
        if self._flow.at_root:
            menu.hero(screen, "The Story of Us")
            menu.options(screen, current.options, current.index, 248)
            menu.text(screen, current.hint, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 34,
                      menu.font(UI_FONT_NAME, 14), menu.MUTED)
        else:
            current.draw(screen)


class PlayMode(Mode):
    """The overworld: tile movement, interaction, party and scene transitions,
    plus the HUD. Dialogue and cutscenes are overlays it drives; the pause menu
    is a Game-level overlay drawn on top of it. Persistent for the game's life;
    re-entered after interludes."""
    def __init__(self, game) -> None:
        self._game = game
        self._turn_cooldown = 0.0
        self._scene_fade = 0.0           # quick fade-in on overworld scene change
        self._fade_black = None
        self._last_scene_id = game.scene_manager.current_id
        self._hint_surf = pygame.font.SysFont(UI_FONT_NAME, 14).render(
            "Arrows = move  |  Z = confirm  |  X = cancel  |  C = menu", True, WHITE)

    def mark_scene_synced(self) -> None:
        """Pin _last_scene_id to the current scene so a deliberate jump (new game,
        load, returning from the match) doesn't fire spurious scene-change work."""
        self._last_scene_id = self._game.scene_manager.current_id

    # ---- input ----
    def handle_action(self, action) -> None:
        g = self._game
        scene = g.scene_manager.current
        if action == Action.DEBUG_CYCLE and DEV:  # dev only: cycle through activities
            g.debug_cycle()
            return
        if action == Action.QUIT and not g.cutscene.active:
            g.open_pause()
            return
        if g.cutscene.active:                # cutscenes own input: only drive dialogue
            if g.dialogue.active:
                if action == Action.CONFIRM:
                    g.dialogue.advance()
                elif action == Action.CANCEL:
                    g.dialogue.skip()
                elif action in _MOVE_MAP:
                    g.dialogue.move_choice(_MOVE_MAP[action][0])
            return
        if getattr(scene, 'wants_raw_input', False) and not g.dialogue.active:
            if action is not None:
                scene.handle_action(action)
            return
        if action == Action.CONFIRM:
            if g.dialogue.active:
                g.dialogue.advance()
            elif not g.player.moving:
                self._interact_ahead()
        elif action == Action.CANCEL:
            if g.dialogue.active:
                g.dialogue.skip()            # X speeds the text to the full line
        elif action == Action.MENU:
            if not g.dialogue.active:
                g.open_pause()               # C opens the menu
        elif action == Action.DEBUG_GARDEN and DEV:
            g.story.debug_advance()
        elif action in _MOVE_MAP:
            dtx, dty = _MOVE_MAP[action]
            if g.dialogue.active:
                g.dialogue.move_choice(dtx)
            else:
                new_facing = _DIR_FACING[(dtx, dty)]
                if g.player.facing != new_facing and not g.player.moving:
                    g.player.facing = new_facing
                    self._turn_cooldown = 0.12
                else:
                    g.scene_manager.try_move(dtx, dty, g.player)

    def _interact_ahead(self) -> None:
        """Talk to whatever sprite the player is facing — scene object or a
        seated follower (the crew become party followers, not scene objects)."""
        g = self._game
        dx, dy = _FACING_DELTA[g.player.facing]
        tx = g.player.tile_x + dx
        ty = g.player.tile_y + dy
        here = [o for o in g.scene_manager.current.objects if o.occupies(tx, ty)]
        here.sort(key=lambda o: o.name is None)      # talking to a character beats a bench
        if here:
            obj = here[0]
            if not g.story.interact(obj):
                if hasattr(obj, 'on_interact'):
                    obj.on_interact(g)               # e.g. sitting on a bench
                lines = obj.interaction_lines(g.story)
                if lines:
                    g.dialogue.start(lines, speaker=obj.name)
            return
        for f in g.party.followers:
            if f.tile_x == tx and f.tile_y == ty:
                g.story.talk(f.name)
                return

    # ---- update ----
    def update(self, dt: float) -> None:
        g = self._game
        if g.poll_vb_retry():                # lost the 3v3 — relaunch this frame
            return
        if self._scene_fade > 0:
            self._scene_fade = max(0.0, self._scene_fade - dt / 0.22)
        g.dialogue.update(dt)
        g.update_speaker_music()             # swap to a speaker's theme while they talk
        scene = g.scene_manager.current
        if getattr(scene, 'wants_raw_input', False):
            scene.handle_held(get_held_vector())
            scene.update(dt)
            return

        # Scene-change bookkeeping runs even mid-cutscene (a transition can hand
        # straight off to a cutscene that repositions the crew).
        if g.scene_manager.current_id != self._last_scene_id:
            if not g.cutscene.active:        # cutscenes do their own fades
                self._scene_fade = 1.0
            self._last_scene_id = g.scene_manager.current_id
            g.party.on_scene_change(g.player)
            g.update_scene_music(g.scene_manager.current_id)

        scene.sync_blockers()                # NPCs block at their live tile, not their spawn

        if g.cutscene.active:
            g.cutscene.update(dt)
            scene.update(dt)
            return

        g.player.update(dt)
        scene.update(dt)
        g.party.update(dt, g.player)
        if not g.player.moving:
            g.story.notify_reach(g.scene_manager.current_id,
                                 (g.player.tile_x, g.player.tile_y))

        if self._turn_cooldown > 0:
            self._turn_cooldown -= dt
        elif not g.player.moving and not g.dialogue.active:
            direction = get_held_direction()
            if direction:
                g.scene_manager.try_move(direction[0], direction[1], g.player)

    # ---- draw ----
    def draw(self, screen) -> None:
        g = self._game
        scene = g.scene_manager.current
        hide_player = g.story.beat.get('hide_player')   # POV scenes where Sarah's left
        if scene.scrolling:
            world = scene.get_world_surface()
            scene.draw(world)
            g.party.draw(world)
            if not hide_player:
                g.player.draw(world)
            scene.draw_overlay(world)
            cam_x = scene.get_camera_x(g.player.x)
            screen.blit(world, (0, 0), (cam_x, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            scene.draw(screen)
            if not getattr(scene, 'wants_raw_input', False):
                g.party.draw(screen)
                if not hide_player:
                    g.player.draw(screen)
            scene.draw_overlay(screen)

        if not getattr(scene, 'wants_raw_input', False):
            g.lighting.draw(screen, g.scene_manager.current_id,
                            getattr(scene, 'lighting', None))

        raw = getattr(scene, 'wants_raw_input', False)
        if not g.dialogue.active and not raw and not g.cutscene.active:
            self._draw_objective(screen)
            screen.blit(self._hint_surf, (10, SCREEN_HEIGHT - 30))
            if g.pause is None and not scene.scrolling:
                self._draw_affordance(screen, scene)

        g.cutscene.draw_fade(screen)
        g.dialogue.set_anchor(g.player.tile_y)     # box flips to the top when the action is low
        g.dialogue.draw(screen)
        if self._scene_fade > 0:
            if self._fade_black is None:
                self._fade_black = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                self._fade_black.fill((0, 0, 0))
            self._fade_black.set_alpha(int(255 * self._scene_fade))
            screen.blit(self._fade_black, (0, 0))

    def _draw_objective(self, screen) -> None:
        text = self._game.story.objective()
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
        screen.blit(chip, pill.topleft)
        screen.blit(surf, (pill.centerx - surf.get_width() // 2,
                           pill.centery - surf.get_height() // 2))

    def _draw_affordance(self, screen, scene) -> None:
        """A small bobbing chevron over the interactable the player is facing."""
        g = self._game
        if g.player.moving:
            return
        dx, dy = _FACING_DELTA[g.player.facing]
        tx, ty = g.player.tile_x + dx, g.player.tile_y + dy
        target = None
        for obj in scene.objects:
            if obj.occupies(tx, ty) and (obj.interaction_text
                                         or g.story.interactable_at(tx, ty)):
                target = (obj.x, obj.y)
                break
        if target is None:
            for f in g.party.followers:
                if f.tile_x == tx and f.tile_y == ty and g.story.can_talk():
                    target = (f.x, f.y)
                    break
        if target is None:
            return
        bob = int(3 * abs(math.sin(pygame.time.get_ticks() / 220.0)))
        cx, cy = int(target[0]), int(target[1]) - 26 - bob
        pygame.draw.polygon(screen, (20, 20, 28),
                            [(cx - 7, cy - 1), (cx + 7, cy - 1), (cx, cy + 9)])
        pygame.draw.polygon(screen, (255, 240, 150),
                            [(cx - 6, cy), (cx + 6, cy), (cx, cy + 7)])


class GameOverMode(Mode):
    """Shown when a cutscene fails the player; CONFIRM replays the beat."""
    def __init__(self, game, lines) -> None:
        self._game = game
        self._lines = lines

    def handle_action(self, action) -> None:
        if action == Action.CONFIRM:
            self._game.retry_beat()

    def draw(self, screen) -> None:
        screens.draw_game_over(screen, self._lines)


class ResultsMode(Mode):
    """End-of-week star results; CONFIRM rolls on to the phone wrap-up."""
    def __init__(self, game, results) -> None:
        self._game = game
        self._results = results

    def handle_action(self, action) -> None:
        if action == Action.DEBUG_CYCLE:
            self._game.debug_cycle()
        elif action == Action.CONFIRM:
            self._game.enter_phone()

    def draw(self, screen) -> None:
        self._results.draw(screen)


class InterludeMode(Mode):
    """A between-chapters title card; CONFIRM rolls on to the interlude's texts."""
    def __init__(self, game, kicker, name, date, on_done) -> None:
        self._game = game
        self._kicker = kicker
        self._name = name
        self._date = date
        self._on_done = on_done

    def handle_action(self, action) -> None:
        if action == Action.DEBUG_CYCLE:
            self._game.debug_cycle()
        elif action == Action.CONFIRM:
            self._on_done()

    def draw(self, screen) -> None:
        screens.draw_interlude_card(screen, self._kicker, self._name, self._date)


class ChapterCardMode(Mode):
    """Between-chapters card ('Chapter N Complete' / 'Chapter N+1'); CONFIRM rolls
    on into the next chapter's opening (which is already queued behind it)."""
    def __init__(self, game, completed, starting, on_done) -> None:
        self._game = game
        self._completed = completed
        self._starting = starting
        self._on_done = on_done

    def handle_action(self, action) -> None:
        if action == Action.CONFIRM:
            self._on_done()

    def draw(self, screen) -> None:
        screens.draw_chapter_card(screen, self._completed, self._starting)


class GameEndMode(Mode):
    """The closing card after the finale, and the prompt shown when a completed save is
    loaded: CONFIRM starts a fresh playthrough; from a loaded save, CANCEL backs out."""
    def __init__(self, game, loaded: bool = False) -> None:
        self._game = game
        self._loaded = loaded

    def handle_action(self, action) -> None:
        if action == Action.CONFIRM:
            self._game.start_new()
        elif action in (Action.CANCEL, Action.QUIT) and self._loaded:
            self._game.open_title()

    def draw(self, screen) -> None:
        screens.draw_the_end(screen, self._loaded)


class PhoneMode(Mode):
    """A text thread; CONFIRM advances, and the last bubble runs on_done (which
    defaults to ending the week, but an interlude supplies its own continuation)."""
    def __init__(self, game, phone, on_done=None) -> None:
        self._game = game
        self._phone = phone
        self._on_done = on_done or game.finish_week

    def handle_action(self, action) -> None:
        if action == Action.DEBUG_CYCLE:
            self._game.debug_cycle()
        elif action == Action.CONFIRM and not self._phone.advance():
            self._on_done()

    def draw(self, screen) -> None:
        self._phone.draw(screen)
