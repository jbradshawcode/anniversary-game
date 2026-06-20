"""Save slots — small JSON files under saves/. Three slots, 1-indexed.

A save holds where the player is (scene + tile + facing) and the story state
(beat + flags), plus display labels (scene/beat name, timestamp) so the slot
menu can show them without loading the world.
"""
import json
import os
from datetime import datetime
from typing import Optional

_SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saves')

SLOTS = (1, 2, 3)
AUTOSAVE = 0           # written automatically at each chapter start; load-only in the menu


def _slot_path(slot: int) -> str:
    return os.path.join(_SAVE_DIR, "slot{0}.json".format(slot))


def has_save(slot: int) -> bool:
    return os.path.exists(_slot_path(slot))


def load_game(slot: int) -> Optional[dict]:
    path = _slot_path(slot)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def slot_info(slot: int) -> Optional[dict]:
    """Display summary for the slot menu, or None if the slot is empty."""
    data = load_game(slot)
    if data is None:
        return None
    return {
        'scene_name': data.get('scene_name', '?'),
        'beat_name': data.get('beat_name', '?'),
        'saved_at': data.get('saved_at', ''),
    }


_TRASH_DIR = os.path.join(_SAVE_DIR, 'deleted')


def delete_game(slot: int) -> None:
    """Delete a slot, but keep a timestamped backup under saves/deleted/."""
    path = _slot_path(slot)
    if not os.path.exists(path):
        return
    os.makedirs(_TRASH_DIR, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = os.path.join(_TRASH_DIR, "slot{0}-{1}.json".format(slot, stamp))
    os.replace(path, backup)


def save_game(slot: int, data: dict) -> None:
    os.makedirs(_SAVE_DIR, exist_ok=True)
    out = dict(data)
    out['saved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(_slot_path(slot), 'w') as f:
        json.dump(out, f, indent=2)
