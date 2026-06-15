"""Lightweight visual juice — particles + screen-shake.

Cosmetic only. Uses a private random.Random() so the gameplay RNG (seeded in
tests) stays byte-identical regardless of how much juice is on screen.
"""
import math
import random
from typing import List, Tuple

Color = Tuple[int, int, int]


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'size', 'color', 'gravity')

    def __init__(self, x: float, y: float, vx: float, vy: float, life: float,
                 size: float, color: Color, gravity: float) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.gravity = gravity

    def update(self, dt: float) -> None:
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt


class FX:
    def __init__(self) -> None:
        self._rng = random.Random(20260531)
        self.particles: List[Particle] = []
        self._shake_mag = 0.0
        self._shake_t = 0.0
        self._shake_dur = 0.0
        self._ox = 0.0
        self._oy = 0.0

    def emit_burst(self, x: float, y: float, color: Color, count: int = 12,
                   speed: float = 160.0) -> None:
        for _ in range(count):
            ang = self._rng.uniform(0, math.tau)
            spd = self._rng.uniform(0.35, 1.0) * speed
            self.particles.append(Particle(
                x, y, math.cos(ang) * spd, math.sin(ang) * spd,
                self._rng.uniform(0.25, 0.5), self._rng.uniform(2, 4), color, 320.0))

    def emit_dust(self, x: float, y: float, count: int = 8) -> None:
        for _ in range(count):
            ang = self._rng.uniform(-math.pi, 0)        # upward fan
            spd = self._rng.uniform(20, 70)
            self.particles.append(Particle(
                x, y, math.cos(ang) * spd, math.sin(ang) * spd,
                self._rng.uniform(0.3, 0.6), self._rng.uniform(2, 3),
                (210, 214, 220), 120.0))

    def shake(self, mag: float, dur: float) -> None:
        if mag > self._shake_mag:
            self._shake_mag = mag
        self._shake_dur = max(self._shake_dur, dur)
        self._shake_t = self._shake_dur

    def update(self, dt: float) -> None:
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        if self._shake_t > 0:
            self._shake_t -= dt
            k = max(0.0, self._shake_t / self._shake_dur) if self._shake_dur else 0.0
            amp = self._shake_mag * k
            self._ox = self._rng.uniform(-amp, amp)
            self._oy = self._rng.uniform(-amp, amp)
        else:
            self._shake_mag = 0.0
            self._ox = self._oy = 0.0

    def offset(self) -> Tuple[int, int]:
        return int(self._ox), int(self._oy)

    def draw(self, screen) -> None:
        import pygame
        for p in self.particles:
            a = max(0.0, min(1.0, p.life / p.max_life))
            s = max(1, int(p.size * (0.4 + 0.6 * a)))
            pygame.draw.circle(screen, p.color, (int(p.x), int(p.y)), s)
