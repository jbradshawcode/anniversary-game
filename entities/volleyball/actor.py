"""Volleyball player — free pixel movement, drawn with the game's real characters.

Each actor holds a `sprite` (a real character instance: Player / James / Dan /
Matt / Nat / Leonard) and draws it at a free pixel position. Teams are
told apart by a coloured ground ring; the controlled actor gets a bright ring +
a chevron marker. Pose / z / lean are purely cosmetic (driven by update_anim)
and never feed the contact maths, so gameplay stays deterministic.
"""
import math
import pygame
from enum import Enum
from typing import Optional, Tuple


class Role(Enum):
    SETTER = 0
    HITTER_L = 1
    HITTER_R = 2


class Pose(Enum):
    READY = 0
    RUN = 1
    DIG = 2
    JUMP = 3
    BLOCK = 4
    CELEBRATE = 5
    PRONE = 6


_SHADOW   = (40, 70, 96)
_RING_YOU = (250, 228, 120)
_RING_NEAR = (70, 140, 240)
_RING_FAR = (232, 96, 82)
_MARK_YOU = (255, 240, 120)


class VBActor:
    def __init__(self, x: float, y: float, team: int, role: Role,
                 sprite: Optional[object] = None, is_player: bool = False) -> None:
        self.x = float(x)
        self.y = float(y)
        self.team = team
        self.role = role
        self.sprite = sprite
        self.is_player = is_player
        self.facing = 'down'
        self.home: Tuple[float, float] = (float(x), float(y))
        self.pose = Pose.READY
        self.anim_t = 0.0
        self.z = 0.0          # cosmetic jump height
        self.lean = 0.0       # cosmetic lateral lean (px)

    def move_toward(self, tx: float, ty: float, dt: float, speed: float) -> None:
        dx, dy = tx - self.x, ty - self.y
        d = (dx * dx + dy * dy) ** 0.5
        if d <= 1.0:
            self.x, self.y = tx, ty
            return
        step = min(d, speed * dt)
        self.x += dx / d * step
        self.y += dy / d * step

    def dist_to(self, x: float, y: float) -> float:
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5

    def set_pose(self, pose: Pose) -> None:
        if pose != self.pose:
            self.pose = pose
            self.anim_t = 0.0

    def update_anim(self, dt: float) -> None:
        self.anim_t += dt
        t = self.anim_t
        if self.pose == Pose.JUMP:
            self.z = max(0.0, 26.0 * (1.0 - (2.4 * t - 1.0) ** 2))
            self.lean = 0.0
            if t > 0.85:
                self.set_pose(Pose.READY)
        elif self.pose == Pose.BLOCK:
            self.z = min(18.0, 90.0 * t)
            if t > 0.6:
                self.set_pose(Pose.READY)
        elif self.pose == Pose.DIG:
            self.z = 0.0
            if t > 0.4:
                self.set_pose(Pose.READY)
        elif self.pose == Pose.CELEBRATE:
            self.z = max(0.0, 10.0 * abs(math.sin(t * 9.0)))
            self.lean = 0.0
        elif self.pose == Pose.PRONE:
            self.z = 0.0
            if t > 0.5:
                self.set_pose(Pose.READY)
        else:
            self.z *= max(0.0, 1.0 - 12.0 * dt)
            self.lean *= max(0.0, 1.0 - 12.0 * dt)

    def _draw_sprite(self, screen: pygame.Surface, bx: int, by: int) -> None:
        sp = self.sprite
        if sp is None:
            return
        # the Player sprite is the only one with facing-aware heads
        if hasattr(sp, '_draw_head_up'):
            f = self.facing
            if f == 'up':
                sp._draw_head_up(screen, bx, by)
            elif f == 'right':
                sp._draw_head_right(screen, bx, by)
            elif f == 'left':
                sp._draw_head_left(screen, bx, by)
            else:
                sp._draw_head_down(screen, bx, by)
            sp._draw_body(screen, bx, by)
            if f == 'up':
                sp._draw_back_hair(screen, bx, by)
        else:
            sp._draw_head_down(screen, bx, by)
            sp._draw_body(screen, bx, by)

    def draw(self, screen: pygame.Surface) -> None:
        px, py = int(self.x), int(self.y)
        prone = self.pose == Pose.PRONE
        sw = 22 if prone else 16
        pygame.draw.ellipse(screen, _SHADOW, (px - sw // 2, py + 12, sw, 6))
        ring = _RING_NEAR if self.team == 0 else _RING_FAR
        pygame.draw.ellipse(screen, ring, (px - sw // 2 - 2, py + 11, sw + 4, 8), 2)
        if self.is_player:
            pygame.draw.ellipse(screen, _RING_YOU, (px - sw // 2 - 4, py + 10, sw + 8, 10), 2)
            mx, my = px, py - 26 - int(self.z)
            pygame.draw.polygon(screen, _MARK_YOU,
                                [(mx - 5, my - 5), (mx + 5, my - 5), (mx, my)])
        self._draw_sprite(screen, px + int(self.lean), py - int(self.z))
