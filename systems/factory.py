"""Factory for creating game objects from config"""
from typing import List
from scene_configs import SCENE_CONFIGS
from entities import (GameObject, Tree, Rock, BallBasket, James, Dan, Bench,
                      Matt, Nat, Leonard, Milla, Bailey, Mayu, Wallace, Matus)

_ENTITY_MAP = {
    'trees': Tree,
    'rocks': Rock,
    'ball_baskets': BallBasket,
    'james': James,
    'dan': Dan,
    'benches': Bench,
    'matt': Matt,
    'nat': Nat,
    'leonard': Leonard,
    'milla': Milla,
    'bailey': Bailey,
    'mayu': Mayu,
    'wallace': Wallace,
    'matus': Matus,
}


class ObjectFactory:
    @staticmethod
    def create_scene_objects(scene_key: str) -> List[GameObject]:
        if scene_key not in SCENE_CONFIGS:
            raise ValueError(f"Unknown scene: {scene_key}")
        placements = SCENE_CONFIGS[scene_key].get('objects', {})
        unknown = set(placements) - set(_ENTITY_MAP)
        if unknown:                      # a typo'd object key would otherwise spawn nothing, silently
            raise ValueError("Scene {0!r}: unknown object type(s) {1}".format(
                scene_key, sorted(unknown)))
        # Build in _ENTITY_MAP order, not config order, so draw/z-order is stable.
        objects: List[GameObject] = []
        for key, cls in _ENTITY_MAP.items():
            for args in placements.get(key, []):
                objects.append(cls(*args))
        return objects
