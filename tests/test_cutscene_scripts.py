"""Every authored cutscene script in the story is validated against the opcode
grammar AND its actor references, so a typo'd verb, wrong-arity step, or unknown
'who' fails here instead of silently no-op'ing in play."""
from story_script import STORY_WEEKS
from systems.cutscene import iter_step_errors, _PLAYER_NAMES
from systems.factory import _ENTITY_MAP


def _known_actors():
    """Lowercased names a cutscene 'who' can resolve to: the player aliases plus
    every spawnable character by class name and display name (how _resolve matches)."""
    names = set(_PLAYER_NAMES)
    for cls in _ENTITY_MAP.values():
        names.add(cls.__name__.lower())
        display = getattr(cls, 'name', None)
        if display:
            names.add(display.lower())
    return names


def _scripts():
    """Yield (label, steps) for every step list reachable from the story config:
    beat cutscenes, talk-to-NPC choice cutscenes, and checklist greet steps."""
    for week in STORY_WEEKS:
        for beat in week['beats']:
            name = beat.get('name', '?')
            if beat.get('cutscene'):
                yield "{0}/cutscene".format(name), beat['cutscene']
            ask = beat.get('interact_ask')
            if ask and ask.get('steps'):
                yield "{0}/interact_ask".format(name), ask['steps']
            for item in (beat.get('checklist') or {}).values():
                if item.get('steps'):
                    yield "{0}/checklist".format(name), item['steps']


def test_all_story_scripts_valid():
    known = _known_actors()
    errors = []
    for label, steps in _scripts():
        errors.extend(iter_step_errors(steps, label, known_actors=known))
    assert not errors, "\n".join(errors)
