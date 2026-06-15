"""Volleyball with a deterministic parabolic arc (top-down + height z).

An arc is fully determined at launch (start/end/peak/duration), so the landing
point is known exactly — the landing-shadow marker needs no prediction. A short
visual trail + a spinning seam are cosmetic (driven by t, no extra RNG).
"""
import math
import pygame
from collections import deque
from typing import Deque, Tuple

_BALL    = (240, 228, 120)
_BALL_SH = (206, 188, 86)
_BALL_HI = (253, 250, 214)
_BALL_LN = (70, 60, 30)
_TRAIL   = (252, 246, 196)


class VolleyBall:
    def __init__(self) -> None:
        self.x = 320.0
        self.y = 380.0
        self.z = 0.0
        self.start: Tuple[float, float] = (self.x, self.y)
        self.end: Tuple[float, float] = (self.x, self.y)
        self.peak = 0.0
        self.t = 1.0
        self.duration = 1.0
        self.team = 0
        self.in_flight = False
        self.spin = 0.0
        self.trail: Deque[Tuple[float, float]] = deque(maxlen=8)

    def launch(self, start: Tuple[float, float], end: Tuple[float, float],
               peak: float, duration: float) -> None:
        self.start = (float(start[0]), float(start[1]))
        self.end = (float(end[0]), float(end[1]))
        self.peak = float(peak)
        self.duration = max(0.05, float(duration))
        self.t = 0.0
        self.in_flight = True
        self.trail.clear()
        self._recompute()

    def hold_at(self, x: float, y: float) -> None:
        self.x, self.y, self.z = float(x), float(y), 0.0
        self.in_flight = False
        self.trail.clear()

    def _recompute(self) -> None:
        sx, sy = self.start
        ex, ey = self.end
        t = self.t
        self.x = sx + (ex - sx) * t
        self.y = sy + (ey - sy) * t
        self.z = 4.0 * self.peak * t * (1.0 - t)

    def update(self, dt: float) -> None:
        if not self.in_flight:
            return
        self.trail.appendleft((self.x, self.y - self.z))
        self.spin += dt * 14.0
        self.t += dt / self.duration
        if self.t >= 1.0:
            self.t = 1.0
            self.in_flight = False
        self._recompute()

    def landing_point(self) -> Tuple[float, float]:
        return self.end

    def remaining(self) -> float:
        """Seconds until the ball reaches its landing point."""
        return max(0.0, (1.0 - self.t) * self.duration)

    def draw(self, screen: pygame.Surface) -> None:
        # soft shadow on the floor — wider + fainter the higher the ball is
        sr = 7 + int(self.z / 10)
        sh = pygame.Surface((sr * 2 + 2, sr + 2), pygame.SRCALPHA)
        alpha = max(40, 120 - int(self.z / 2))
        pygame.draw.ellipse(sh, (18, 40, 58, alpha), (1, 1, sr * 2, sr))
        screen.blit(sh, (int(self.x) - sr - 1, int(self.y) - sr // 2 - 1))
        if self.in_flight:
            n = max(1, len(self.trail))
            for i, (tx, ty) in enumerate(self.trail):
                r = max(1, 5 - i)
                a = int(130 * (1.0 - i / n))
                ts = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(ts, (_TRAIL[0], _TRAIL[1], _TRAIL[2], a), (r, r), r)
                screen.blit(ts, (int(tx) - r, int(ty) - r))
        bx, by = int(self.x), int(self.y - self.z)
        pygame.draw.circle(screen, _BALL_SH, (bx, by), 7)
        pygame.draw.circle(screen, _BALL, (bx, by), 6)
        pygame.draw.circle(screen, _BALL_HI, (bx - 2, by - 2), 3)
        ca, sa = math.cos(self.spin), math.sin(self.spin)
        pygame.draw.line(screen, _BALL_LN, (bx - int(5 * ca), by - int(5 * sa)),
                         (bx + int(5 * ca), by + int(5 * sa)), 1)
        pygame.draw.circle(screen, _BALL_LN, (bx, by), 7, 1)
