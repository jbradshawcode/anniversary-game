"""Character bust portraits for the dialogue box, rendered from the in-game sprite.

A speaker name maps to its character class; we draw that sprite facing down onto
a scratch surface, crop the head+torso, and scale it up into a crisp pixel bust.
Busts are cached per (name, size). Unknown speakers (narrator) return None.
"""
import pygame

_REG = None
_cache: dict = {}


def _registry() -> dict:
    global _REG
    if _REG is None:
        from entities import (James, Dan, Matt, Nat, Leonard, Player,
                              Milla, Bailey, Mayu, Wallace, Matus)
        _REG = {'james': James, 'dan': Dan, 'matt': Matt, 'nat': Nat,
                'leonard': Leonard, 'sarah': Player, 'you': Player, 'player': Player,
                'milla': Milla, 'bailey': Bailey, 'mayu': Mayu, 'wallace': Wallace,
                'matúš': Matus, 'matus': Matus}
    return _REG


def bust(name, size: int = 88):
    if not name:
        return None
    key = (name.lower(), size)
    if key not in _cache:
        cls = _registry().get(name.lower())
        surf = None
        if cls is not None:
            tmp = pygame.Surface((32, 44), pygame.SRCALPHA)
            ch = cls(0, 0)
            ch.x, ch.y = 16, 24
            ch.draw(tmp)                       # faces down; shadow sits below the crop
            crop = tmp.subsurface((5, 5, 22, 26)).copy()
            surf = pygame.transform.scale(crop, (int(22 * size / 26), size))
        _cache[key] = surf
    return _cache[key]
