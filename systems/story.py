"""Story state — single source of truth for beats, flags and movement gating.

Story content is data (config.STORY_WEEKS, flattened to an ordered beat list);
this manager is consulted at a few hook points (exit/movement gating in
SceneManager, interaction/debug/reach in game.py) and is bound once to the
DialogueBox / SceneManager / Player / Party so it can drive dialogue, scene
jumps and the follower crew itself.
"""
from typing import Callable, List, Optional, Set, Tuple, TYPE_CHECKING
from config import STORY_WEEKS

if TYPE_CHECKING:
    from systems.dialogue import DialogueBox
    from systems.scene_manager import SceneManager
    from systems.party import Party
    from systems.cutscene import Cutscene
    from entities.characters.player import Player
    from entities.base import GameObject

Region = Tuple[Tuple[int, int], Tuple[int, int]]


def _flatten(weeks) -> List[dict]:
    beats: List[dict] = []
    for w in weeks:
        for b in w['beats']:
            beat = dict(b)
            beat['week'] = w['week']
            beat['week_title'] = w['title']
            beat['absent'] = w.get('absent', ())    # crew not present this chapter at all
            beats.append(beat)
    return beats


_BEATS = _flatten(STORY_WEEKS)

# Pub seats: two rows of four facing each other across the left booth.
#   chairs    (row 9):  Bailey, James, Sarah, Nat   (cols 10-13)
#   banquette (row 11): Wallace, Mayu, Dan, Matt     (cols 10-13)
# PUB_SEATS is in WEEK1_CREW order [James, Dan, Matt, Nat, Bailey, Mayu, Wallace].
PUB_SEATS = [(11, 9), (12, 11), (13, 11), (13, 9),
             (10, 9), (11, 11), (10, 11)]
SARAH_PUB_SEAT = (12, 9)        # Sarah's chair (between James and Nat)
_SEATED_BEATS = {'pub_queue', 'gifts', 'where_from', 'wind_down'}


class StoryManager:
    def __init__(self) -> None:
        self.flags: Set[str] = set()
        self._beat = 0
        self._fired: Set[Tuple[int, int]] = set()
        self.vb_attempts = 0
        self._dialogue: Optional['DialogueBox'] = None
        self._scenes: Optional['SceneManager'] = None
        self._player: Optional['Player'] = None
        self._party: Optional['Party'] = None
        self._cutscene: Optional['Cutscene'] = None
        self.on_launch_vb: Optional[Callable[[], None]] = None
        self.on_launch_dive: Optional[Callable[[], None]] = None
        self.on_week_end: Optional[Callable[[], None]] = None
        self.on_phone: Optional[Callable] = None
        self.on_chapter_start: Optional[Callable] = None   # (week, title, first)
        self._cur_week = None              # last week we entered, to spot chapter changes

    def bind(self, dialogue: 'DialogueBox', scene_manager: 'SceneManager',
             player: 'Player', party: 'Party',
             cutscene: Optional['Cutscene'] = None) -> None:
        self._dialogue = dialogue
        self._scenes = scene_manager
        self._player = player
        self._party = party
        self._cutscene = cutscene

    @property
    def beat(self) -> dict:
        return _BEATS[self._beat]

    @property
    def week_title(self) -> Optional[str]:
        return self.beat.get('week_title')

    def objective(self) -> Optional[str]:
        text = self.beat.get('objective')
        checklist = self.beat.get('checklist')
        if text and checklist:
            done = sum(1 for it in checklist.values() if it['flag'] in self.flags)
            return "{0} ({1}/{2})".format(text, done, len(checklist))
        return text

    def has(self, flag: str) -> bool:
        return flag in self.flags

    def interactable_at(self, tx: int, ty: int) -> bool:
        """Whether the object on this tile has a story line this beat (for the prompt)."""
        beat = self.beat
        if (tx, ty) in beat.get('dialogue', {}):
            return True
        cl = beat.get('checklist')
        return bool(cl and (tx, ty) in cl)

    def can_talk(self) -> bool:
        beat = self.beat
        return bool(beat.get('talk') or beat.get('talk_default'))

    def set_flag(self, name: Optional[str]) -> None:
        if not name:
            return
        self.flags.add(name)
        self._check_advance()

    def _check_advance(self) -> None:
        while self._beat < len(_BEATS) - 1:
            need = self.beat.get('advance_when')
            if need and need in self.flags:
                self._beat += 1
                self._enter_beat()
            else:
                break

    def begin(self) -> None:
        """Kick off the current beat (new game): apply its setup and cutscene."""
        self._enter_beat()

    def _enter_beat(self) -> None:
        beat = self.beat
        goto = beat.get('goto')                       # relocate the player (e.g. a chapter jump)
        if goto and self._scenes is not None and self._player is not None:
            self._scenes.jump_to(goto['scene'], self._player)
            if 'tile' in goto:
                self._player.teleport(*goto['tile'])
        self._apply_party(beat.get('party'))
        if beat.get('settle_party') and self._party is not None:
            self._party.stop_following()             # crew stays put (e.g. you head home alone)
        week = beat.get('week')
        if week is not None and week != self._cur_week:    # crossed into a new chapter
            first = self._cur_week is None
            self._cur_week = week
            if self.on_chapter_start is not None:
                self.on_chapter_start(week, beat.get('title', ''), first)
        if beat.get('launch_volleyball') and self.on_launch_vb is not None:
            self.on_launch_vb()
            return
        if beat.get('launch_dive') and self.on_launch_dive is not None:
            self.on_launch_dive()
            return
        if beat.get('end_chapter') and self.on_week_end is not None:
            self.on_week_end()                       # straight to results + texts
            return
        if beat.get('phone') and self.on_phone is not None:
            self.on_phone(beat['phone'], beat.get('phone_with', 'Sarah'),
                          beat.get('advance_when'),    # a texts-only interlude
                          beat.get('week_title', 'Interlude'), beat.get('card_date', ''))
            return
        cutscene = beat.get('cutscene')
        if cutscene and self._cutscene is not None:
            self._cutscene.start(cutscene)
            return
        if self._scenes is not None:
            self.notify_enter(self._scenes.current_id)

    def replay_beat(self) -> None:
        """Re-run the current beat's cutscene (e.g. after a game-over retry)."""
        cutscene = self.beat.get('cutscene')
        if cutscene and self._cutscene is not None:
            self._cutscene.start(cutscene)

    def _apply_party(self, directive) -> None:
        if self._party is None or not directive:
            return
        if directive == 'form':
            self._party.form(self._player, self._scenes)
        elif isinstance(directive, dict) and 'form' in directive:
            self._party.form(self._player, self._scenes, exclude=directive['form'])
        elif isinstance(directive, dict) and 'settle' in directive:
            for sid, tiles in directive['settle'].items():
                self._party.settle(sid, tiles)

    def exit_blocked(self, scene_id: Optional[int], direction: str) -> bool:
        locked = self.beat.get('locked_exits', {}).get(scene_id)
        if locked is None:
            return False
        return locked == 'all' or direction in locked

    def try_door_block(self, dest_scene_id: Optional[int]) -> bool:
        """A specific door (by destination scene) is barred this beat: show its
        message and refuse entry. Lets us block one of several same-edge doors
        (e.g. the wrong pub) without locking the whole side."""
        lines = self.beat.get('door_block', {}).get(dest_scene_id)
        if not lines:
            return False
        if self._dialogue is not None and not self._dialogue.active:
            self._dialogue.start(lines)
        return True

    def confine(self, scene_id: Optional[int]) -> Optional[Region]:
        confine = self.beat.get('confine')
        return confine.get(scene_id) if confine else None

    def notify_enter(self, scene_id: Optional[int]) -> None:
        beat = self.beat
        lines = beat.get('on_enter_scene', {}).get(scene_id)
        if lines:
            key = (self._beat, scene_id)
            if key not in self._fired:
                self._fired.add(key)
                if self._dialogue is not None:
                    self._dialogue.start(lines)
        if beat.get('advance_on_enter') == scene_id:
            self.set_flag(beat.get('advance_when'))

    def notify_reach(self, scene_id: Optional[int], tile: Tuple[int, int]) -> None:
        targets = self.beat.get('on_reach', {}).get(scene_id)
        if targets and tile in targets:
            self.set_flag(self.beat.get('advance_when'))

    def show_locked(self, scene_id: Optional[int]) -> None:
        lines = self.beat.get('locked_msg')
        if lines and self._dialogue is not None and not self._dialogue.active:
            self._dialogue.start(lines)

    def interact(self, obj: 'GameObject') -> bool:
        checklist = self.beat.get('checklist')
        if checklist is not None:
            return self._interact_checklist(obj, checklist)
        ask = self.beat.get('interact_ask')          # talk to a named NPC to fire a choice cutscene
        if (ask is not None and self._cutscene is not None
                and (getattr(obj, 'name', None) or '').lower() == ask['who'].lower()):
            self._cutscene.start(ask['steps'])
            return True
        lines = self.beat.get('dialogue', {}).get((obj.tile_x, obj.tile_y))
        if not lines or self._dialogue is None:
            return False
        flag = self.beat.get('advance_when')
        self._dialogue.start(lines, on_done=lambda: self.set_flag(flag))
        return True

    def _interact_checklist(self, obj: 'GameObject', checklist: dict) -> bool:
        """A 'check N things in any order' beat: each item sets its own flag; the
        beat advances once all are checked. Lines are order-aware (more left vs done)."""
        item = checklist.get((obj.tile_x, obj.tile_y))
        if item is None:
            return False
        beat = self.beat
        flag = item['flag']
        spk = item.get('speaker')                     # per-item speaker (e.g. who you greeted)
        advance = beat.get('advance_when')

        def _after() -> None:
            self.flags.add(flag)
            if all(it['flag'] in self.flags for it in checklist.values()):
                self.set_flag(advance)

        if flag in self.flags:                        # already ticked off
            again = beat.get('checked_again', item.get('lines', ['...']))
            if self._dialogue is not None:
                self._dialogue.start(again, speaker=spk)
            return True
        steps = item.get('steps')                     # a cutscene greet — can hold a choice
        if steps is not None and self._cutscene is not None:
            self._cutscene.start(list(steps) + [('call', _after)])
            return True
        if self._dialogue is None:
            return False
        last = all(it['flag'] in self.flags for t, it in checklist.items() if it is not item)
        suffix = beat.get('check_done', []) if last else beat.get('check_more', [])
        lines = list(item['lines']) + list(suffix)    # suffix optional (greets need none)
        self._dialogue.start(lines, speaker=spk, on_done=_after)
        return True

    def talk(self, name: Optional[str]) -> bool:
        """Speak to a seated follower; returns True if a line was shown."""
        if self._dialogue is None or not name:
            return False
        beat = self.beat
        lines = beat.get('talk', {}).get(name.lower()) or beat.get('talk_default')
        if not lines:
            return False
        self._dialogue.start(lines, speaker=name)
        return True

    def exit_ends_week(self, scene_id: Optional[int], direction: str) -> bool:
        return self.beat.get('end_week') == direction

    def trigger_week_end(self) -> None:
        if self.on_week_end is not None:
            self.on_week_end()

    def stars(self) -> int:
        from config import stars_for_attempts
        return stars_for_attempts(max(1, self.vb_attempts))

    def debug_advance(self) -> None:
        """Skip the current beat: satisfy its gate, applying the next beat's setup."""
        self.set_flag(self.beat.get('advance_when'))

    def debug_cycle(self) -> None:
        """Dev only: step to the next beat (sub-chapter), wrapping at the end, so you
        can walk through every bit of every chapter with the N key."""
        self.debug_jump_to((self._beat + 1) % len(_BEATS))

    def debug_jump_to(self, i: int) -> None:
        """Dev only: jump to beat index i in a playable state — fresh flags, gym
        repopulated, crew rebuilt, and the player placed in that beat's scene (its
        own goto, else the last goto / advance-on-enter scene up to here)."""
        self._beat = i
        beat = _BEATS[i]
        self.flags = set()
        self._fired = set()
        self.vb_attempts = 0
        self._cur_week = beat.get('week')          # no chapter card on a dev jump
        # work out which scene this beat happens in (preceding gotos / scene-entries)
        scene, tile = 1, None
        for b in _BEATS[:i]:
            if b.get('goto'):
                scene, tile = b['goto']['scene'], b['goto'].get('tile')
            elif b.get('advance_on_enter'):
                scene, tile = b['advance_on_enter'], None
        if beat.get('goto'):                        # the beat's own goto wins
            scene, tile = beat['goto']['scene'], beat['goto'].get('tile')
        if self._scenes is not None and self._scenes.scene(1) is not None:
            self._scenes.scene(1).repopulate()
            self._scenes.scene(1).remove_named(beat.get('absent', ()))
        if self._scenes is not None and self._player is not None:
            self._scenes.jump_to(scene, self._player)
            if tile is not None:
                self._player.teleport(*tile)
            self.sync_party(self._player)
        print("[dev] beat {0}/{1}: {2} ({3})".format(
            i + 1, len(_BEATS), beat.get('name'), beat.get('week_title') or beat.get('week')))
        self._enter_beat()

    def snapshot(self) -> dict:
        return {'beat': self._beat, 'flags': sorted(self.flags),
                'vb_attempts': self.vb_attempts}

    def restore(self, beat: int, flags, scene_id: Optional[int] = None,
                vb_attempts: int = 0) -> None:
        """Reset to a saved (or fresh) state. Pass scene_id to suppress that
        scene's one-shot on-enter line for the load that follows."""
        self._beat = beat
        self.flags = set(flags)
        self.vb_attempts = vb_attempts
        self._fired = {(beat, scene_id)} if scene_id is not None else set()
        self._cur_week = _BEATS[beat].get('week')   # sync so a load won't fire a chapter card

    def sync_party(self, player: 'Player') -> None:
        """Rebuild the follower crew to match the current beat (new game / load)."""
        if self._party is None:
            return
        self._party.clear()
        cur_week = _BEATS[self._beat].get('week')   # crew reset each chapter: only this week counts
        directive = None
        for b in _BEATS[:self._beat + 1]:
            if b.get('week') == cur_week and b.get('party'):
                directive = b.get('party')
        if directive == 'form':
            self._party.form(player, self._scenes)
        elif isinstance(directive, dict) and 'form' in directive:
            self._party.form(player, self._scenes, exclude=directive['form'])
        elif isinstance(directive, dict) and 'settle' in directive:
            self._party.form(player, self._scenes)
            for sid, tiles in directive['settle'].items():
                self._party.settle(sid, tiles)
        # Loading/jumping into the pub once everyone's sat down: park the crew at the
        # seats the queue cutscene leaves them in (WEEK1_CREW order), and seat Sarah
        # in her chair too (the 8th seat) so she isn't stranded at the door.
        if self._party.active and self.beat['name'] in _SEATED_BEATS:
            self._party.settle(3, PUB_SEATS)
            if player is not None:
                player.teleport(*SARAH_PUB_SEAT)
                player.sitting = True
                player.facing = 'up' if SARAH_PUB_SEAT[1] >= 10 else 'down'
                if hasattr(player, '_sit_x'):
                    player._sit_x = player.x
