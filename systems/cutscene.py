"""Scripted cutscenes — interleave dialogue, scripted actor movement and fades.

A cutscene is a flat list of steps run in order. Steps are tuples whose first
element is a verb; the runner blocks on the current step until it completes,
then advances. Story beats carry a 'cutscene' list (see config.STORY_WEEKS);
StoryManager hands it here on beat-enter. The main loop routes confirm/cancel to
the bound DialogueBox while a cutscene is active and locks overworld movement.

Steps:
  ('say', [lines])                  dialogue, no speaker tag
  ('say', [lines], 'Name')          dialogue with a speaker tag
  ('ask', text, {label: outcome})   a choice; ('ask', text, outcomes, 'Name')
  ('hub', text, {label: [steps]})   explore-all menu: pick a topic, run its
                                    steps, return to the menu with that topic
                                    removed; once all are explored, continue.
                                    ('hub', text, topics, 'Name') for a speaker.
  ('walk', who, (col, row))         tween one actor to a tile; wait until arrived
  ('move', {who: (col, row), ...})  tween several actors in parallel; wait for all
  ('face', who, 'down'|'up'|...)    set facing (player only draws facing)
  ('pose', who, 'left'|'right'|None) sprawled dive/prone pose (None clears it)
  ('wait', seconds)                 hold
  ('fade_out', seconds)             fade screen to black
  ('fade_in', seconds)              fade screen up from black
  ('flag', name)                    set a story flag (drives beat advancement)
  ('call', fn)                      run an arbitrary callable once

An `outcome` (for 'ask') is one of: ('flag', name) sets a story flag;
('game_over', [lines]) shows the game-over screen (the beat replays on retry);
or a list of further steps spliced in at the current point (an empty list just
continues). A 'hub' topic value is always a list of steps.

`who` is a case-insensitive name: 'sarah'/'player'/'you' -> the player, else a
party follower or current-scene object matched on its class/display name.
"""
import pygame
from typing import List, Optional, Tuple, TYPE_CHECKING
from config import TILE_SIZE, TILE_MOVE_SPEED

if TYPE_CHECKING:
    from systems.dialogue import DialogueBox
    from systems.scene_manager import SceneManager
    from systems.story import StoryManager
    from systems.party import Party
    from entities.characters.player import Player

_Pt = Tuple[float, float]
_PLAYER_NAMES = {'sarah', 'player', 'you'}


def _tile_center(col: int, row: int) -> _Pt:
    return (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)


class Cutscene:
    def __init__(self) -> None:
        self._dialogue: Optional['DialogueBox'] = None
        self._scenes: Optional['SceneManager'] = None
        self._player: Optional['Player'] = None
        self._party: Optional['Party'] = None
        self._story: Optional['StoryManager'] = None
        self.active = False
        self.on_game_over = None               # set by game: fn(lines)
        self._steps: List[tuple] = []
        self._i = 0
        self._gen = 0                          # bumped on (re)start; guards reentrancy
        self._wait = 0.0
        self._movers: List[tuple] = []        # (actor, target_x, target_y)
        self._fade = 0.0                       # current black overlay alpha 0..255
        self._fade_to = 0.0
        self._fade_rate = 0.0
        self._await_dialogue = False
        self._ask_outcomes: dict = {}
        self._ask_choice = None
        self._hub_explored: set = set()    # labels seen in the current hub
        self._hub_key = None               # identity of the active hub's topic dict
        self._hub_outcomes: dict = {}
        self._hub_choice = None

    def bind(self, dialogue, scenes, player, party, story) -> None:
        self._dialogue = dialogue
        self._scenes = scenes
        self._player = player
        self._party = party
        self._story = story

    # ── lifecycle ────────────────────────────────────────────────────────────
    def start(self, steps) -> None:
        self.active = True
        self._gen += 1
        self._steps = list(steps)
        self._i = 0
        self._wait = 0.0
        self._movers = []
        self._await_dialogue = False
        self._hub_explored = set()
        self._hub_key = None
        self._begin_step()

    def _finish(self) -> None:
        self.active = False
        self._steps = []
        self._movers = []

    # ── actor lookup ───────────────────────────────────────────────────────--
    def _resolve(self, who: str):
        key = who.lower()
        if key in _PLAYER_NAMES:
            return self._player
        if self._party is not None:
            for f in self._party.followers:
                if type(f).__name__.lower() == key or (f.name or '').lower() == key:
                    return f
        if self._scenes is not None and self._scenes.current is not None:
            for o in self._scenes.current.objects:
                if (o.name or '').lower() == key:
                    return o
        return None

    # ── step dispatch ──────────────────────────────────────────────────────--
    def _begin_step(self) -> None:
        gen = self._gen
        while True:
            if self._i >= len(self._steps):
                self._finish()
                return
            step = self._steps[self._i]
            verb = step[0]
            if verb == 'say':
                lines = step[1]
                speaker = step[2] if len(step) > 2 else None
                self._i += 1
                self._await_dialogue = True
                if self._dialogue is not None:
                    self._dialogue.start(lines, speaker=speaker,
                                         on_done=self._on_dialogue_done)
                return
            if verb == 'ask':
                self._begin_ask(step)
                return
            if verb == 'hub':
                self._begin_hub(step)
                return
            if verb in ('walk', 'move'):
                self._setup_move(step)
                if self._movers:
                    return
            elif verb == 'face':
                actor = self._resolve(step[1])
                if actor is not None and hasattr(actor, 'facing'):
                    actor.facing = step[2]
            elif verb == 'pose':                  # ('pose', who, 'left'|'right'|None) — dive/prone
                actor = self._resolve(step[1])
                if actor is not None:
                    actor.diving = step[2]
            elif verb == 'sit':                   # ('sit', who[, facing]) — seated in place
                actor = self._resolve(step[1])
                if actor is not None:
                    self._seat(actor, step[2] if len(step) > 2 else None)
            elif verb == 'sit_all':               # seat the whole crew + player where they stand
                for f in (self._party.followers if self._party else []):
                    self._seat(f, None)
                if self._player is not None:
                    self._seat(self._player, None)
            elif verb == 'settle':
                if self._party is not None:
                    self._party.stop_following()
                    if self._scenes is not None and self._scenes.current is not None:
                        self._scenes.current.add_blockers(    # seated crew aren't walkable
                            (f.tile_x, f.tile_y) for f in self._party.followers)
            elif verb == 'wait':
                self._wait = float(step[1])
                if self._wait > 0:
                    self._i += 1
                    return
            elif verb == 'fade_out':
                self._set_fade(255.0, step[1])    # non-blocking: next step runs now
            elif verb == 'fade_in':
                self._fade = 255.0                # start from black, then ramp up
                self._set_fade(0.0, step[1])
            elif verb == 'flag':
                self._i += 1
                if self._story is not None:
                    self._story.set_flag(step[1])
                if self._gen != gen:       # set_flag may have restarted us
                    return
                continue
            elif verb == 'call':
                self._i += 1
                step[1]()
                if self._gen != gen:
                    return
                continue
            self._i += 1

    # ── choices ───────────────────────────────────────────────────────────--
    def _begin_ask(self, step) -> None:
        text, outcomes = step[1], step[2]
        speaker = step[3] if len(step) > 3 else None
        self._ask_outcomes = outcomes
        self._ask_choice = None
        self._i += 1
        page = {'text': text, 'choices': {label: [] for label in outcomes}}
        self._await_dialogue = True
        if self._dialogue is not None:
            self._dialogue.start([page], speaker=speaker,
                                 on_choice=self._on_ask_choice,
                                 on_done=self._on_ask_done)

    def _on_ask_choice(self, label: str) -> None:
        self._ask_choice = label

    def _on_ask_done(self) -> None:
        self._await_dialogue = False
        gen = self._gen
        outcome = self._ask_outcomes.get(self._ask_choice)
        if not outcome:                    # unknown label or empty branch: continue
            self._begin_step()
            return
        kind = outcome[0]
        if kind == 'flag':
            if self._story is not None:
                self._story.set_flag(outcome[1])
            if self._gen != gen:
                return
            self._begin_step()
        elif kind == 'game_over':
            if self.on_game_over is not None:
                self.on_game_over(outcome[1])
        else:                                  # a list of spliced steps
            self._steps[self._i:self._i] = list(outcome)
            self._begin_step()

    # ── hub (explore-all menu) ───────────────────────────────────────────────
    def _begin_hub(self, step) -> None:
        text, outcomes = step[1], step[2]
        speaker = step[3] if len(step) > 3 else None
        if id(outcomes) != self._hub_key:        # a fresh hub -> reset exploration
            self._hub_key = id(outcomes)
            self._hub_explored = set()
        remaining = [label for label in outcomes if label not in self._hub_explored]
        if not remaining:                        # every topic seen -> move on
            self._i += 1
            self._begin_step()
            return
        self._hub_outcomes = outcomes
        self._hub_choice = None
        page = {'text': text, 'choices': {label: [] for label in remaining}}
        self._await_dialogue = True
        if self._dialogue is not None:
            self._dialogue.start([page], speaker=speaker,
                                 on_choice=self._on_hub_choice,
                                 on_done=self._on_hub_done)

    def _on_hub_choice(self, label: str) -> None:
        self._hub_choice = label

    def _on_hub_done(self) -> None:
        self._await_dialogue = False
        self._hub_explored.add(self._hub_choice)
        branch = self._hub_outcomes.get(self._hub_choice) or []
        # Run the chosen topic, then fall back into the hub (still ahead at _i).
        self._steps[self._i:self._i] = list(branch)
        self._begin_step()

    def _setup_move(self, step) -> None:
        targets = {step[1]: step[2]} if step[0] == 'walk' else step[1]
        self._movers = []
        for who, (col, row) in targets.items():
            actor = self._resolve(who)
            if actor is None:
                continue
            tx, ty = _tile_center(col, row)
            actor.tile_x, actor.tile_y = col, row
            self._face_toward(actor, tx, ty)
            self._movers.append((actor, tx, ty))
        self._i += 1

    @staticmethod
    def _seat(actor, facing) -> None:
        actor.sitting = True
        if facing is not None and hasattr(actor, 'facing'):
            actor.facing = facing
        if hasattr(actor, '_sit_x'):
            actor._sit_x = actor.x        # the player sits in place, not bench-shifted

    @staticmethod
    def _face_toward(actor, tx, ty) -> None:
        if not hasattr(actor, 'facing'):
            return
        dx, dy = tx - actor.x, ty - actor.y
        if abs(dx) >= abs(dy):
            actor.facing = 'right' if dx > 0 else 'left'
        elif dy != 0:
            actor.facing = 'down' if dy > 0 else 'up'

    def _on_dialogue_done(self) -> None:
        self._await_dialogue = False
        self._begin_step()

    def _set_fade(self, target: float, seconds: float) -> None:
        self._fade_to = target
        if seconds <= 0:
            self._fade = target
            self._fade_rate = 0.0
        else:
            self._fade_rate = (target - self._fade) / seconds

    # ── per-frame update ───────────────────────────────────────────────────--
    def update(self, dt: float) -> None:
        if not self.active:
            return
        if self._fade_rate:
            self._fade += self._fade_rate * dt
            if (self._fade_rate > 0 and self._fade >= self._fade_to) or \
               (self._fade_rate < 0 and self._fade <= self._fade_to):
                self._fade = self._fade_to
                self._fade_rate = 0.0
        if self._await_dialogue:
            return
        if self._wait > 0:
            self._wait -= dt
            if self._wait <= 0:
                self._begin_step()
            return
        if self._movers:
            self._advance_movers(dt)
            return

    def _advance_movers(self, dt: float) -> None:
        step = TILE_MOVE_SPEED * dt
        still = []
        for actor, tx, ty in self._movers:
            dx, dy = tx - actor.x, ty - actor.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= max(0.5, step):
                actor.x, actor.y = tx, ty
                actor.walking = False
            else:
                actor.x += dx / dist * step
                actor.y += dy / dist * step
                actor.walking = True
                actor.walk_phase = getattr(actor, 'walk_phase', 0.0) + step * 0.2
                still.append((actor, tx, ty))
        self._movers = still
        if not self._movers:
            self._begin_step()

    # ── drawing ────────────────────────────────────────────────────────────--
    @property
    def fade_alpha(self) -> int:
        return int(max(0.0, min(255.0, self._fade)))

    def draw_fade(self, screen: pygame.Surface) -> None:
        a = self.fade_alpha
        if a <= 0:
            return
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, a))
        screen.blit(overlay, (0, 0))
