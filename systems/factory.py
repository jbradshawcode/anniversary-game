"""Factory for creating game objects from config"""
from typing import List
from config import SCENE_CONFIGS
from entities import (GameObject, Tree, Rock, BallBasket, James, Dan, Bench,
                      Matt, Nat, Leonard, Barkeep)

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
    'barkeep': Barkeep,
}


class ObjectFactory:
    @staticmethod
    def create_scene_objects(scene_key: str) -> List[GameObject]:
        if scene_key not in SCENE_CONFIGS:
            raise ValueError(f"Unknown scene: {scene_key}")
        objects: List[GameObject] = []
        for key, cls in _ENTITY_MAP.items():
            for args in SCENE_CONFIGS[scene_key]['objects'].get(key, []):
                objects.append(cls(*args))
        return objects
