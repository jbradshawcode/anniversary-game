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
            beats.append(beat)
    return beats


_BEATS = _flatten(STORY_WEEKS)

# Pub seats in WEEK1_CREW order — must match the final tiles the 'pub_queue'
# cutscene walks them to (config.STORY_WEEKS).
# James, Dan, Matt, Nat, Bailey, Mayu, Wallace
PUB_SEATS = [(13, 8), (11, 8), (9, 8), (7, 11),
             (11, 11), (13, 11), (10, 10)]
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
        elif isinstance(directive, dict) and 'settle' in directive:
            for sid, tiles in directive['settle'].items():
                self._party.settle(sid, tiles)

    def exit_blocked(self, scene_id: Optional[int], direction: str) -> bool:
        locked = self.beat.get('locked_exits', {}).get(scene_id)
        if locked is None:
            return False
        return locked == 'all' or direction in locked

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
        if item is None or self._dialogue is None:
            return False
        beat = self.beat
        flag = item['flag']
        spk = item.get('speaker')                     # per-item speaker (e.g. who you greeted)
        if flag in self.flags:                        # already ticked off
            self._dialogue.start(beat.get('checked_again', item['lines']), speaker=spk)
            return True
        last = all(it['flag'] in self.flags for t, it in checklist.items() if it is not item)
        suffix = beat.get('check_done', []) if last else beat.get('check_more', [])
        lines = list(item['lines']) + list(suffix)    # suffix optional (greets need none)
        advance = beat.get('advance_when')

        def _after() -> None:
            self.flags.add(flag)
            if all(it['flag'] in self.flags for it in checklist.values()):
                self.set_flag(advance)
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

    def debug_next_chapter(self) -> None:
        """Dev only: jump to the first beat of the next chapter (fresh flags, no
        leftover party). No-op once we're in the last chapter."""
        here = self.beat.get('week_title')
        for i in range(self._beat + 1, len(_BEATS)):
            if _BEATS[i].get('week_title') != here:
                self._beat = i
                self.flags = set()
                self._fired = set()
                self.vb_attempts = 0
                if self._party is not None:
                    self._party.clear()
                self._enter_beat()
                return

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

    def sync_party(self, player: 'Player') -> None:
        """Rebuild the follower crew to match the current beat (new game / load)."""
        if self._party is None:
            return
        self._party.clear()
        directive = None
        for b in _BEATS[:self._beat + 1]:
            if b.get('party'):
                directive = b.get('party')
        if directive == 'form':
            self._party.form(player, self._scenes)
        elif isinstance(directive, dict) and 'settle' in directive:
            self._party.form(player, self._scenes)
            for sid, tiles in directive['settle'].items():
                self._party.settle(sid, tiles)
        # Loading into the pub once everyone's sat down: park them at the seats
        # the queue cutscene leaves them in (in WEEK1_CREW order).
        if self._party.active and self.beat['name'] in _SEATED_BEATS:
            self._party.settle(3, PUB_SEATS)
