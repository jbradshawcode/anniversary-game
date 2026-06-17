"""Maps keyboard input to named game actions"""
from enum import Enum, auto
from typing import Optional, Tuple
import pygame


class Action(Enum):
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    # Undertale-style scheme. In the volleyball minigame these double as:
    CONFIRM = auto()        # Z — confirm / advance / interact   (vb: dig/attack/serve/block)
    CANCEL = auto()         # X — cancel / speed up text          (vb: set)
    MENU = auto()           # C — open the menu                   (vb: tip / dump)
    QUIT = auto()
    DEBUG_GARDEN = auto()
    DEBUG_CHAPTER = auto()   # N — dev only: jump to the next chapter's start


_KEY_MAP = {
    pygame.K_LEFT:   Action.MOVE_LEFT,
    pygame.K_RIGHT:  Action.MOVE_RIGHT,
    pygame.K_UP:     Action.MOVE_UP,
    pygame.K_DOWN:   Action.MOVE_DOWN,
    pygame.K_z:      Action.CONFIRM,
    pygame.K_RETURN: Action.CONFIRM,
    pygame.K_x:      Action.CANCEL,
    pygame.K_c:      Action.MENU,
    pygame.K_ESCAPE: Action.QUIT,
    pygame.K_g:      Action.DEBUG_GARDEN,
    pygame.K_n:      Action.DEBUG_CHAPTER,
}


_DIRECTION_KEYS = [
    (pygame.K_UP,    ( 0, -1)),
    (pygame.K_DOWN,  ( 0,  1)),
    (pygame.K_LEFT,  (-1,  0)),
    (pygame.K_RIGHT, ( 1,  0)),
]


def get_held_direction() -> Optional[Tuple[int, int]]:
    keys = pygame.key.get_pressed()
    for key, direction in _DIRECTION_KEYS:
        if keys[key]:
            return direction
    return None


def get_held_vector() -> Tuple[float, float]:
    """Free 8-direction movement vector from the arrow keys (minigame use)."""
    keys = pygame.key.get_pressed()
    dx = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
    dy = (1 if keys[pygame.K_DOWN] else 0) - (1 if keys[pygame.K_UP] else 0)
    if dx and dy:
        return (dx * 0.7071, dy * 0.7071)
    return (float(dx), float(dy))


def event_to_action(event: pygame.event.Event) -> Optional[Action]:
    """Map a single KEYDOWN event to an action, or None if unmapped."""
    if event.type == pygame.KEYDOWN:
        return _KEY_MAP.get(event.key)
    return None
