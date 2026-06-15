"""Per-scene atmosphere: a soft vignette plus additive light pools.

Overlays are built once per scene key (numpy) and cached, then blitted each
frame — cheap. A scene opts in with a class attribute:

    lighting = {'vignette': 0.0..1.0,
                'pools': [(x, y, radius, (r, g, b), intensity), ...]}

`pools` are screen-space; intensity scales the additive colour (0..~0.5).
If numpy is unavailable the overlays degrade to no-ops.
"""
import pygame

try:
    import numpy as _np
except ImportError:  # pragma: no cover - numpy ships with pygame's surfarray
    _np = None


class Lighting:
    def __init__(self) -> None:
        self._cache: dict = {}        # key -> (vignette_surf|None, light_surf|None)

    def draw(self, screen: pygame.Surface, key, cfg) -> None:
        if not cfg or _np is None:
            return
        if key not in self._cache:
            w, h = screen.get_size()
            self._cache[key] = (
                self._vignette(w, h, cfg.get('vignette', 0.0)),
                self._light(w, h, cfg.get('pools')),
            )
        vig, light = self._cache[key]
        if light is not None:
            screen.blit(light, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        if vig is not None:
            screen.blit(vig, (0, 0))

    @staticmethod
    def _vignette(w: int, h: int, strength: float):
        if strength <= 0:
            return None
        yy, xx = _np.mgrid[0:h, 0:w]
        d = _np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        a = (_np.clip((d - 0.55) / 0.6, 0, 1) ** 1.6) * (strength * 255)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        rgb = pygame.surfarray.pixels3d(surf)
        rgb[:] = 0
        del rgb
        al = pygame.surfarray.pixels_alpha(surf)
        al[:] = a.T.astype('uint8')
        del al
        return surf

    @staticmethod
    def _light(w: int, h: int, pools):
        if not pools:
            return None
        acc = _np.zeros((h, w, 3), float)
        yy, xx = _np.mgrid[0:h, 0:w]
        for px, py, r, color, inten in pools:
            d = _np.sqrt((xx - px) ** 2 + (yy - py) ** 2) / max(1.0, r)
            f = (_np.clip(1 - d, 0, 1) ** 2) * inten
            for i, ch in enumerate(color):
                acc[..., i] += f * ch
        acc = _np.clip(acc, 0, 255).astype('uint8')
        surf = pygame.Surface((w, h))
        pygame.surfarray.blit_array(surf, acc.transpose(1, 0, 2))
        return surf
