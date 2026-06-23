"""Every object key in a scene config maps to a known entity class, so a typo'd
key fails here instead of silently spawning nothing."""
from scene_configs import SCENE_CONFIGS
from systems.factory import ObjectFactory, _ENTITY_MAP


def test_scene_object_keys_are_known():
    errors = []
    for scene_key, cfg in SCENE_CONFIGS.items():
        for key in cfg.get('objects', {}):
            if key not in _ENTITY_MAP:
                errors.append("{0}: unknown object type {1!r}".format(scene_key, key))
    assert not errors, "\n".join(errors)


def test_every_scene_builds():
    # Instantiates each scene's objects — also catches a wrong-arity placement.
    import pygame
    pygame.init()
    for scene_key in SCENE_CONFIGS:
        ObjectFactory.create_scene_objects(scene_key)
