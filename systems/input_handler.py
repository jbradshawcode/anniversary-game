"""Maps keyboard + gamepad input to named game actions.

A PS5 DualSense (or any SDL-recognised pad) works alongside the keyboard: face
buttons map to the Z/X/C scheme, and the left stick or D-pad drive movement.
Button indices follow SDL's game-controller layout, so Cross/Circle/Square/
Triangle land on 0/1/2/3 for a DualSense on macOS.
"""
from enum import Enum, auto
from typing import Dict, Optional, Tuple
import pygame


class Action(Enum):
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    # Undertale-style scheme. In the volleyball minigame these double as:
    CONFIRM = auto()        # Z / Cross — confirm / advance / interact   (vb: dig/attack/serve/block)
    CANCEL = auto()         # X / Circle — cancel / speed up text          (vb: set)
    MENU = auto()           # C / Square — open the menu                   (vb: tip / dump)
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

# ── gamepad ───────────────────────────────────────────────────────────────--
# D-pad as buttons (SDL controller layout) -> screen-space deltas. Many pads,
# DualSense included, report the D-pad this way rather than as a hat.
_DPAD_BUTTONS = {
    11: ( 0, -1),   # up
    12: ( 0,  1),   # down
    13: (-1,  0),   # left
    14: ( 1,  0),   # right
}
# DualSense face buttons under SDL's game-controller mapping.
_BUTTON_MAP = {
    0: Action.CONFIRM,   # Cross  (✕)
    1: Action.CANCEL,    # Circle (○)
    2: Action.MENU,      # Square (□)
    3: Action.MENU,      # Triangle (△) — handy second menu button
    6: Action.QUIT,      # Options — opens the pause menu
    11: Action.MOVE_UP,
    12: Action.MOVE_DOWN,
    13: Action.MOVE_LEFT,
    14: Action.MOVE_RIGHT,
}
# D-pad hat -> discrete move (SDL hat y is +1 up, so screen y is negated below).
_HAT_MAP = {
    (-1,  0): Action.MOVE_LEFT,
    ( 1,  0): Action.MOVE_RIGHT,
    ( 0,  1): Action.MOVE_UP,
    ( 0, -1): Action.MOVE_DOWN,
}
_STICK_DEADZONE = 0.5        # stick push that counts as a held direction
_ANALOG_DEADZONE = 0.25      # below this the analog vector reads as centred

_joysticks: Dict[int, "pygame.joystick.Joystick"] = {}
_axis_state: Dict[Tuple[int, int], int] = {}   # (instance_id, axis) -> -1/0/1, for edge detection
_last_device = 'keyboard'                       # 'keyboard' or 'gamepad' — drives on-screen prompts


def last_input_device() -> str:
    """Which input method was used most recently (so the UI can label controls)."""
    return _last_device


def init_joysticks() -> None:
    if not pygame.joystick.get_init():
        pygame.joystick.init()
    for i in range(pygame.joystick.get_count()):
        add_joystick(i)


def add_joystick(device_index: int) -> None:
    js = pygame.joystick.Joystick(device_index)
    js.init()
    _joysticks[js.get_instance_id()] = js


def remove_joystick(instance_id: int) -> None:
    _joysticks.pop(instance_id, None)
    for key in [k for k in _axis_state if k[0] == instance_id]:
        del _axis_state[key]


def _axis_to_action(event: pygame.event.Event) -> Optional[Action]:
    """Discrete move when the left stick crosses the deadzone (for menus/dialogue)."""
    if event.axis not in (0, 1):
        return None
    key = (event.instance_id, event.axis)
    prev = _axis_state.get(key, 0)
    cur = -1 if event.value < -_STICK_DEADZONE else (1 if event.value > _STICK_DEADZONE else 0)
    _axis_state[key] = cur
    if cur == 0 or cur == prev:           # only fire on a fresh push past the deadzone
        return None
    if event.axis == 0:
        return Action.MOVE_LEFT if cur < 0 else Action.MOVE_RIGHT
    return Action.MOVE_UP if cur < 0 else Action.MOVE_DOWN


def _pad_vector() -> Tuple[float, float]:
    """Movement vector from the first pad with input: D-pad takes priority, else
    the left stick (with deadzone). Screen coords (down = +y)."""
    for js in _joysticks.values():
        hx, hy = js.get_hat(0) if js.get_numhats() > 0 else (0, 0)
        if hx or hy:
            return (float(hx), float(-hy))
        nb = js.get_numbuttons()
        bx = by = 0
        for btn, (dx, dy) in _DPAD_BUTTONS.items():
            if btn < nb and js.get_button(btn):
                bx += dx
                by += dy
        if bx or by:
            return (float(bx), float(by))
        ax = js.get_axis(0) if js.get_numaxes() > 0 else 0.0
        ay = js.get_axis(1) if js.get_numaxes() > 1 else 0.0
        if abs(ax) > _ANALOG_DEADZONE or abs(ay) > _ANALOG_DEADZONE:
            return (ax if abs(ax) > _ANALOG_DEADZONE else 0.0,
                    ay if abs(ay) > _ANALOG_DEADZONE else 0.0)
    return (0.0, 0.0)


def get_held_direction() -> Optional[Tuple[int, int]]:
    keys = pygame.key.get_pressed()
    for key, direction in _DIRECTION_KEYS:
        if keys[key]:
            return direction
    jx, jy = _pad_vector()
    if abs(jx) > _STICK_DEADZONE and abs(jx) >= abs(jy):
        return (1, 0) if jx > 0 else (-1, 0)
    if abs(jy) > _STICK_DEADZONE:
        return (0, 1) if jy > 0 else (0, -1)
    return None


def get_held_vector() -> Tuple[float, float]:
    """Free 8-direction movement vector from the arrow keys or left stick (minigame use)."""
    keys = pygame.key.get_pressed()
    dx = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
    dy = (1 if keys[pygame.K_DOWN] else 0) - (1 if keys[pygame.K_UP] else 0)
    if dx or dy:
        if dx and dy:
            return (dx * 0.7071, dy * 0.7071)
        return (float(dx), float(dy))
    jx, jy = _pad_vector()
    mag = (jx * jx + jy * jy) ** 0.5
    if mag > 1.0:                          # clamp so analog never exceeds full speed
        jx, jy = jx / mag, jy / mag
    return (jx, jy)


def event_to_action(event: pygame.event.Event) -> Optional[Action]:
    """Map a single input event to an action, or None if unmapped. Also notes which
    device was last used (ignoring sub-deadzone stick drift) for control prompts."""
    global _last_device
    if event.type == pygame.KEYDOWN:
        _last_device = 'keyboard'
        return _KEY_MAP.get(event.key)
    if event.type == pygame.JOYBUTTONDOWN:
        _last_device = 'gamepad'
        return _BUTTON_MAP.get(event.button)
    if event.type == pygame.JOYHATMOTION:
        if event.value != (0, 0):
            _last_device = 'gamepad'
        return _HAT_MAP.get(event.value)
    if event.type == pygame.JOYAXISMOTION:
        if abs(event.value) > _STICK_DEADZONE:
            _last_device = 'gamepad'
        return _axis_to_action(event)
    return None
