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
  ('walkto', who, (col, row))       like walk, but pathfind around solid tiles
  ('move', {who: (col, row), ...})  tween several actors in parallel; wait for all
  ('moveto', {who: (col, row), ...}) like move, but each actor pathfinds round solids
  ('face', who, 'down'|'up'|...)    set facing (player only draws facing)
  ('pose', who, 'left'|'right'|None) sprawled dive/prone pose (None clears it)
  ('vanish', who[, seconds])        fade the actor's sprite out, then remove it from
                                    the scene (gone for good — no re-interaction)
  ('hold', who, kind)               give the actor a drink to carry (entities DRINKS);
                                    rendered in-hand, or on the table once they sit
  ('if_flag', name, [steps])        splice the steps in only if the story flag is set
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
from collections import deque
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


def face_toward(a, b) -> None:
    """Turn actor a to face actor b's tile (4-way). No-op if either lacks a tile or
    facing, or if they share a tile. Shared so any system can apply the project rule:
    people look at whoever they're talking to."""
    if (a is None or b is None or a is b or not hasattr(a, 'facing')
            or not hasattr(a, 'tile_x') or not hasattr(b, 'tile_x')):
        return
    dx, dy = b.tile_x - a.tile_x, b.tile_y - a.tile_y
    if dx == 0 and dy == 0:
        return
    if abs(dx) >= abs(dy):
        a.facing = 'right' if dx > 0 else 'left'
    else:
        a.facing = 'down' if dy > 0 else 'up'


# Verb -> (min, max) number of args after the verb. Single source of truth for
# what _begin_step accepts; keep in sync when adding a verb there. Used by
# iter_step_errors() so an authored script is checked before it can silently
# no-op in play (an unknown verb just advances the step pointer otherwise).
_STEP_ARITY = {
    'say': (1, 2), 'ask': (2, 3), 'hub': (2, 3),
    'walk': (2, 2), 'walkto': (2, 2), 'move': (1, 1), 'moveto': (1, 1),
    'face': (2, 2), 'pose': (2, 2), 'vanish': (1, 2), 'hold': (2, 2),
    'if_flag': (2, 2), 'wait': (1, 1), 'fade_out': (1, 1), 'fade_in': (1, 1),
    'flag': (1, 1), 'call': (1, 1), 'sit': (1, 2), 'sit_all': (0, 0),
    'settle': (0, 0),
}


# Verbs whose first arg names a single actor; move/moveto instead key a dict by
# actor name. Used only for the optional actor-reference check below.
_WHO_AT_1 = frozenset({'walk', 'walkto', 'face', 'pose', 'vanish', 'hold', 'sit'})


def iter_step_errors(steps, where: str = 'cutscene', known_actors=None):
    """Yield human-readable problems with a step list — unknown verbs, wrong
    arity, malformed choices — recursing into ask/hub/if_flag branches. The
    interface (the opcode vocabulary) becomes a test surface: a test runs this
    over every authored script so typos fail loudly instead of no-op'ing.

    Pass `known_actors` (a set of lowercased names) to also flag any `'who'`
    reference that wouldn't resolve at runtime — another silent no-op otherwise."""
    if not isinstance(steps, (list, tuple)):
        yield "{0}: not a step list".format(where)
        return
    for i, step in enumerate(steps):
        loc = "{0}[{1}]".format(where, i)
        if not isinstance(step, tuple) or not step:
            yield "{0}: not a (verb, ...) tuple".format(loc)
            continue
        verb = step[0]
        arity = _STEP_ARITY.get(verb)
        if arity is None:
            yield "{0}: unknown verb {1!r}".format(loc, verb)
            continue
        lo, hi = arity
        extra = len(step) - 1
        if not (lo <= extra <= hi):
            yield "{0}: verb {1!r} takes {2}-{3} args, got {4}".format(loc, verb, lo, hi, extra)
            continue
        if known_actors is not None:
            who = ([step[1]] if verb in _WHO_AT_1 else
                   list(step[1].keys()) if verb in ('move', 'moveto')
                   and isinstance(step[1], dict) else [])
            for nm in who:
                if isinstance(nm, str) and nm.lower() not in known_actors:
                    yield "{0}: unknown actor {1!r}".format(loc, nm)
        if verb in ('ask', 'hub'):
            outcomes = step[2]
            if not isinstance(outcomes, dict):
                yield "{0}: {1!r} choices must be a dict".format(loc, verb)
                continue
            for label, branch in outcomes.items():
                tag = "{0}/{1!r}".format(loc, label)
                if verb == 'ask' and isinstance(branch, tuple):
                    if not branch or branch[0] not in ('flag', 'game_over'):
                        yield "{0}: outcome tuple must start 'flag' or 'game_over'".format(tag)
                    continue
                for e in iter_step_errors(branch, tag, known_actors):
                    yield e
        elif verb == 'if_flag':
            for e in iter_step_errors(step[2], "{0}(if_flag)".format(loc), known_actors):
                yield e


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
        self._last_speaker: Optional[str] = None   # for turn-toward-each-other
        self._fader: Optional[list] = None         # [actor, rate] for a blocking 'vanish'

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
        self._last_speaker = None
        self._fader = None
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

    def _bfs_path(self, actor, target: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Tile path (adjacent steps, excluding the start) from the actor's tile to
        `target`, routing around solid tiles via the scene's walkability. Falls back to
        a straight step if there's no route or no scene. The target itself is allowed
        even if technically blocked, so a seat tucked against furniture is reachable."""
        sc = self._scenes.current if self._scenes is not None else None
        if sc is None:
            return [target]
        start = (int(actor.x // TILE_SIZE), int(actor.y // TILE_SIZE))
        if start == target:
            return [target]
        seen = {start}
        q = deque([(start, [])])
        while q:
            (x, y), path = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n in seen:
                    continue
                if n == target:
                    return path + [n]
                if not sc.is_walkable(*n):
                    continue
                seen.add(n)
                q.append((n, path + [n]))
        return [target]

    def _present_actors(self):
        out = []
        if self._player is not None:
            out.append(self._player)
        if self._party is not None:
            out += list(self._party.followers)
        if self._scenes is not None and self._scenes.current is not None:
            out += [o for o in self._scenes.current.objects if getattr(o, 'name', None)]
        return out

    def _nearest_actor(self, a):
        best, bd = None, None
        for o in self._present_actors():
            if o is a or not hasattr(o, 'tile_x'):
                continue
            d = (o.tile_x - a.tile_x) ** 2 + (o.tile_y - a.tile_y) ** 2
            if bd is None or d < bd:
                bd, best = d, o
        return best

    def _converse(self, speaker: Optional[str]) -> None:
        """Project rule: people turn to face whoever they're addressing. A reply faces
        the previous speaker; otherwise the line is taken to be aimed at Sarah (the
        game is her POV); failing that, at the nearest person. Both turn, so a
        conversation reads as two people facing each other. Narrator lines pass."""
        if speaker is None:
            return
        a = self._resolve(speaker)
        if a is None:
            self._last_speaker = speaker
            return
        b = None
        if self._last_speaker and self._last_speaker.lower() != speaker.lower():
            b = self._resolve(self._last_speaker)        # a reply -> face whoever just spoke
        if b is None and self._player is not None and a is not self._player:
            b = self._player                             # most lines are addressed to Sarah
        if b is None:
            b = self._nearest_actor(a)                   # otherwise face the nearest listener
        face_toward(a, b)
        face_toward(b, a)
        self._last_speaker = speaker

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
                self._converse(speaker)
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
            if verb in ('walk', 'move', 'moveto'):
                self._setup_move(step)
                if self._movers:
                    return
            elif verb == 'walkto':                # ('walkto', who, (col,row)) — pathfind round solids
                actor = self._resolve(step[1])
                self._i += 1
                if actor is not None:             # splice tile-by-tile straight walks along the path
                    path = self._bfs_path(actor, tuple(step[2]))
                    self._steps[self._i:self._i] = [('walk', step[1], t) for t in path]
                continue
            elif verb == 'face':
                actor = self._resolve(step[1])
                if actor is not None and hasattr(actor, 'facing'):
                    actor.facing = step[2]
            elif verb == 'pose':                  # ('pose', who, 'left'|'right'|None) — dive/prone
                actor = self._resolve(step[1])
                if actor is not None:
                    actor.diving = step[2]
            elif verb == 'hold':                  # ('hold', who, kind) — carry a drink (DRINKS)
                actor = self._resolve(step[1])
                if actor is not None and hasattr(actor, 'carry'):
                    actor.carry(step[2])
            elif verb == 'if_flag':               # ('if_flag', name, [steps]) — splice if flag set
                self._i += 1
                if self._story is not None and step[1] in self._story.flags:
                    self._steps[self._i:self._i] = list(step[2])
                continue
            elif verb == 'vanish':                # ('vanish', who[, secs]) — fade out, then remove
                actor = self._resolve(step[1])
                if actor is not None and hasattr(actor, 'fade'):
                    secs = float(step[2]) if len(step) > 2 else 0.8
                    self._fader = [actor, 255.0 / secs if secs > 0 else 1e9]
                    self._i += 1
                    return                        # block until the fade completes
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
        self._converse(speaker)
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
            self._finish()                     # drop this cutscene; retry replays the beat fresh
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
        verb = step[0]
        targets = {step[1]: step[2]} if verb == 'walk' else step[1]
        pathfind = verb == 'moveto'               # route round solids instead of a straight line
        self._movers = []
        for who, (col, row) in targets.items():
            actor = self._resolve(who)
            if actor is None:
                continue
            if hasattr(actor, 'stand'):
                actor.stand()                     # standing up to move; a seated drink stays on the table
            tiles = self._bfs_path(actor, (col, row)) if pathfind else [(col, row)]
            waypts = [_tile_center(c, r) for c, r in tiles]
            actor.tile_x, actor.tile_y = col, row     # logical tile = the destination
            self._movers.append([actor, waypts])
        self._i += 1

    @staticmethod
    def _seat(actor, facing) -> None:
        if hasattr(actor, 'sit'):         # sits in place, resting any held drink on the table
            actor.sit(facing)

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
        if self._fader is not None:
            self._advance_fader(dt)
            return
        if self._movers:
            self._advance_movers(dt)
            return

    def _advance_fader(self, dt: float) -> None:
        actor, rate = self._fader
        actor.fade = max(0.0, actor.fade - rate * dt)
        if actor.fade <= 0:
            actor.fade = 0.0
            if (self._scenes is not None and self._scenes.current is not None
                    and getattr(actor, 'name', None)):
                self._scenes.current.remove_named([actor.name])   # gone for good
            self._fader = None
            self._begin_step()

    def _advance_movers(self, dt: float) -> None:
        step = TILE_MOVE_SPEED * dt
        still = []
        for actor, waypts in self._movers:
            tx, ty = waypts[0]
            dx, dy = tx - actor.x, ty - actor.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= max(0.5, step):
                actor.x, actor.y = tx, ty
                waypts.pop(0)                      # reached this waypoint -> on to the next
            else:
                self._face_toward(actor, tx, ty)
                actor.x += dx / dist * step
                actor.y += dy / dist * step
                actor.walking = True
                actor.walk_phase = getattr(actor, 'walk_phase', 0.0) + step * 0.2
            if waypts:
                still.append([actor, waypts])
            else:
                actor.walking = False
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
