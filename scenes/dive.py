"""Diving minigame (Ch3) — James practises flinging himself at the floor.

A self-contained real-time scene (own input, ignores the tile grid). Volleyballs
are tossed to the left or right; press the matching arrow to dive and save one.
It is deliberately silly and forgiving — a correct-direction dive always saves;
the point is the flailing, not the skill.
"""
import random
from typing import Callable, Optional
import pygame

from config import (SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_NAME, UI_TITLE_FONT_NAME,
                    DIVE_ROUNDS, DIVE_BALL_TIME, DIVE_RESULT_TIME, DIVE_LUNGE)
from systems.input_handler import Action
from systems import menu
from systems.fx import FX
from systems.audio import SoundBank
from entities import James
from scenes.base import Scene

_FLOOR = (54, 92, 60)
_FLOOR_DK = (40, 70, 46)
_BALL = (245, 238, 220)
_SAVE = (120, 230, 140)
_FLOP = (240, 120, 120)
_SAVE_QUIPS = ["SAVE!", "DIG!", "GOT IT!", "OOH NICE!"]


class DiveGame(Scene):
    wants_raw_input = True

    def __init__(self) -> None:
        super().__init__('dive')
        self.on_finish: Optional[Callable[[], None]] = None
        self._james: Optional[James] = None
        self._fx = FX()
        self._sfx: Optional[SoundBank] = None
        self._floor_y = int(SCREEN_HEIGHT * 0.72)
        self._round = 0
        self._saves = 0
        self._phase = 'done'                      # safe default if drawn before enter()
        self._side = 1
        self._t = 0.0
        self._dived: Optional[int] = None
        self._result: Optional[str] = None
        self._timer = 0.0
        self._lunge = 0.0
        self._quip = _SAVE_QUIPS[0]
        self._bx = self._by = 0.0
        self._bvx = self._bvy = 0.0

    def enter(self, player) -> None:
        self._james = James(0, 0)
        self._fx = FX()
        self._sfx = SoundBank()
        self._round = 0
        self._saves = 0
        self._next_toss()

    def _next_toss(self) -> None:
        self._side = random.choice((-1, 1))      # -1 left, +1 right
        self._t = 0.0
        self._dived = None
        self._result = None
        self._lunge = 0.0
        self._phase = 'live'
        if self._sfx is not None:
            self._sfx.play('set')                # soft toss "pock"

    # ── input ────────────────────────────────────────────────────────────────
    def handle_action(self, action) -> bool:
        if self._phase == 'done':
            if action == Action.CONFIRM and self.on_finish is not None:
                self.on_finish()
            return True
        if self._phase == 'live' and self._dived is None:
            if action == Action.MOVE_LEFT:
                self._dive(-1)
                return True
            if action == Action.MOVE_RIGHT:
                self._dive(1)
                return True
        return False

    def handle_held(self, vec) -> None:
        pass

    def _dive(self, d: int) -> None:
        self._dived = d
        self._lunge = d * DIVE_LUNGE
        self._bx, self._by = self._ball_pos()
        if d == self._side:                      # correct way -> always a save (forgiving)
            self._result = 'save'
            self._saves += 1
            self._quip = random.choice(_SAVE_QUIPS)
            self._bvx, self._bvy = d * 220.0, -360.0     # bump the ball up and away
            self._fx.emit_burst(self._bx, self._by, _SAVE, 12, 200)
            self._fx.shake(5, 0.25)
            if self._sfx is not None:
                self._sfx.play('dig')
        else:                                    # dove the wrong way
            self._result = 'flop'
            self._bvx, self._bvy = 0.0, 120.0
            self._fx.shake(7, 0.3)
            if self._sfx is not None:
                self._sfx.play('block')
        self._fx.emit_dust(SCREEN_WIDTH // 2 + d * 30, self._floor_y, 10)
        self._phase = 'result'
        self._timer = DIVE_RESULT_TIME

    # ── update ─────────────────────────────────────────────────────────────--
    def update(self, dt: float) -> None:
        self._fx.update(dt)
        if self._phase == 'live':
            self._t += dt / DIVE_BALL_TIME
            if self._t >= 1.0 and self._dived is None:    # never committed -> whiff
                self._result = 'miss'
                self._bx, self._by = self._ball_pos()
                self._bvx, self._bvy = 0.0, 60.0
                self._fx.emit_dust(self._bx, self._floor_y, 6)
                self._phase = 'result'
                self._timer = DIVE_RESULT_TIME
        elif self._phase == 'result':
            self._lunge *= max(0.0, 1.0 - dt * 6)         # ease the flop back upright
            self._bvy += 900.0 * dt                       # gravity on the loose ball
            self._bx += self._bvx * dt
            self._by += self._bvy * dt
            self._timer -= dt
            if self._timer <= 0:
                self._round += 1
                if self._round >= DIVE_ROUNDS:
                    self._phase = 'done'
                else:
                    self._next_toss()

    # ── draw ───────────────────────────────────────────────────────────────--
    def _ball_pos(self):
        cx = SCREEN_WIDTH // 2
        tx = cx + self._side * int(SCREEN_WIDTH * 0.22)
        top = int(SCREEN_HEIGHT * 0.12)
        x = cx + (tx - cx) * self._t
        y = top + (self._floor_y - top) * self._t
        return float(x), float(y)

    def _draw_ball(self, screen, ox, oy):
        if self._phase == 'live':
            bx, by = self._ball_pos()
        elif self._phase == 'result':
            bx, by = self._bx, self._by
        else:
            return
        bx, by = int(bx) + ox, int(by) + oy
        drop = max(0.3, 1.0 - (self._floor_y - by) / float(self._floor_y))
        sw = int(8 + 12 * drop)                  # shadow grows as it nears the floor
        pygame.draw.ellipse(screen, (12, 16, 18), (bx - sw // 2, self._floor_y + oy + 2, sw, 6))
        pygame.draw.circle(screen, _BALL, (bx, by), 9)
        pygame.draw.circle(screen, (200, 190, 170), (bx, by), 9, 1)

    def draw(self, screen: pygame.Surface) -> None:
        ox, oy = self._fx.offset()
        screen.fill((18, 22, 26))
        pygame.draw.rect(screen, _FLOOR,
                         (0, self._floor_y + oy, SCREEN_WIDTH, SCREEN_HEIGHT - self._floor_y))
        pygame.draw.rect(screen, _FLOOR_DK, (0, self._floor_y + oy, SCREEN_WIDTH, 6))

        j = self._james
        cx = SCREEN_WIDTH // 2 + ox
        if self._phase == 'result' and self._result in ('save', 'flop'):
            j.diving = 'right' if self._dived > 0 else 'left'
            j.x, j.y = cx + self._lunge, self._floor_y + oy - 2
        else:
            j.diving = None
            j.facing = 'up'
            j.walking = False
            j.x, j.y = cx, self._floor_y + oy - 14
        j.draw(screen)
        self._draw_ball(screen, ox, oy)
        self._fx.draw(screen)

        menu.text(screen, "DIVING PRACTICE", SCREEN_WIDTH // 2, 22,
                  menu.font(UI_TITLE_FONT_NAME, 30), (235, 235, 240), shadow=True)
        menu.text(screen, "Saves {0}   ·   Toss {1}/{2}".format(
            self._saves, min(self._round + 1, DIVE_ROUNDS), DIVE_ROUNDS),
            SCREEN_WIDTH // 2, 58, menu.font(UI_FONT_NAME, 16), (180, 184, 190))

        if self._phase == 'live':
            menu.text(screen, "<-  or  ->  to DIVE!", SCREEN_WIDTH // 2,
                      self._floor_y + 42, menu.font(UI_FONT_NAME, 18), (220, 220, 90))
        elif self._phase == 'result':
            msg, col = {'save': (self._quip, _SAVE), 'flop': ("FLOP!", _FLOP),
                        'miss': ("...whiff.", _FLOP)}[self._result]
            menu.text(screen, msg, SCREEN_WIDTH // 2, self._floor_y + 36,
                      menu.font(UI_TITLE_FONT_NAME, 34), col, shadow=True)
        else:
            self._draw_done(screen)

    def _draw_done(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        cx = SCREEN_WIDTH // 2
        menu.text(screen, "Saves: {0} / {1}".format(self._saves, DIVE_ROUNDS),
                  cx, SCREEN_HEIGHT // 2 - 40, menu.font(UI_TITLE_FONT_NAME, 40),
                  (240, 240, 245), shadow=True)
        quip = ("Olympic. Genuinely." if self._saves >= 5 else
                "Some real flailing out there." if self._saves >= 2 else
                "You dove valiantly. At nothing.")
        menu.text(screen, quip, cx, SCREEN_HEIGHT // 2 + 14,
                  menu.font(UI_FONT_NAME, 18), (200, 204, 210))
        menu.text(screen, "Z to continue", cx, SCREEN_HEIGHT - 40,
                  menu.font(UI_FONT_NAME, 16), (170, 174, 180))
