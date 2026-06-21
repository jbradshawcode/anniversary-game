"""Diving minigame (Ch3) — James keeps a dig rally alive.

Short balls are fed to your side one after another; run under each (momentum
movement) and press Z to dig it back. Each feed lands further out as the streak
grows; balls you can't reach standing need a committed dive — a proper
launch-extend-land animation. Digs are graded PERFECT/NICE/SHANK (shanks still
count). Drop one and the rally pauses; press Z to reset the streak and feed on.
The drill ends at DIVE_TARGET digs. Self-contained real-time scene.
"""
import math
import random
from typing import Callable, Optional
import pygame

from config import (SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_NAME, UI_TITLE_FONT_NAME,
                    DIVE_PLAYER_SPEED, DIVE_PLAYER_ACCEL, DIVE_DIG_REACH,
                    DIVE_LUNGE_REACH, DIVE_FALL_TIME, DIVE_FALL_MIN, DIVE_DIG_WINDOW,
                    DIVE_FEED_GAP, DIVE_LUNGE_TIME, DIVE_LUNGE_HOP,
                    DIVE_TARGET, DIVE_MAX_FEEDS)
from systems.input_handler import Action
from systems import menu
from systems.fx import FX
from systems.audio import SoundBank
from entities import James, Player
from scenes.base import Scene

# gym skin (matches scenes/gym.py so it reads as the sports hall, side-on)
_WALL = (202, 182, 142)
_WALL_DK = (184, 163, 122)
_GFLOOR = (66, 130, 180)
_GFLOOR_SHEEN = (78, 143, 192)
_LINE = (248, 248, 248)
_BALL = (245, 238, 220)
_GOOD = (120, 230, 140)
_BAD = (240, 120, 120)
_LOB_PEAK = 120              # how high Sarah's feed arcs


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


class DiveGame(Scene):
    wants_raw_input = True

    def __init__(self) -> None:
        super().__init__('dive')
        self.on_finish: Optional[Callable[[], None]] = None
        self._james = None
        self._sarah = None
        self._fx = FX()
        self._sfx: Optional[SoundBank] = None
        self._floor_y = int(SCREEN_HEIGHT * 0.70)      # wall/floor boundary; players stand here
        self._sx = 70                                  # Sarah (the feeder) on the left
        self._left, self._right = 152, SCREEN_WIDTH - 44   # James's run range, right of Sarah
        self._phase = 'done'                 # safe default if drawn before enter()
        self._streak = self._best = 0
        self._px = SCREEN_WIDTH / 2.0
        self._pvx = self._move_x = 0.0

    def enter(self, player) -> None:
        self._james = James(0, 0)
        self._sarah = Player(0, 0)
        self._sarah.facing = 'right'
        self._fx = FX()
        self._sfx = SoundBank()
        self._px = SCREEN_WIDTH / 2.0
        self._pvx = self._move_x = 0.0
        self._streak = self._best = self._digs = self._feeds = 0
        self._dig_anim = 0.0
        self._sarah_toss = 0.0
        self._pop = None
        self._verdict = None                 # floating PERFECT/NICE/SHANK label
        self._james.diving = None
        self._phase = 'intro'                # learn the controls; Z starts the first feed

    # ── feed / outcomes ──────────────────────────────────────────────────────
    def _feed_or_end(self) -> None:
        if self._feeds >= DIVE_MAX_FEEDS:
            self._phase = 'done'
        else:
            self._toss()

    def _toss(self) -> None:
        self._feeds += 1
        self._bt = 0.0
        self._fall = max(DIVE_FALL_MIN, DIVE_FALL_TIME - 0.045 * self._streak)
        dist = min(DIVE_LUNGE_REACH + 150.0,               # each pass lands further out
                   DIVE_DIG_REACH * 0.7 + 30.0 * self._streak)
        sides = []                                         # ...on a side that stays in range
        if self._px + dist <= self._right:
            sides.append(1.0)
        if self._px - dist >= self._left:
            sides.append(-1.0)
        if not sides:
            sides = [-1.0 if self._px > (self._left + self._right) / 2.0 else 1.0]
        self._tx = _clamp(self._px + random.choice(sides) * dist, self._left, self._right)
        self._bx0 = float(self._sx)                        # the ball leaves Sarah's hands
        self._sarah_toss = 0.18                            # her little pass motion
        self._pop = None
        self._phase = 'rally'
        if self._sfx is not None:
            self._sfx.play('set')

    def _ball_pos(self):
        t = self._bt
        hand_y = self._floor_y - 24                         # Sarah's hands
        x = self._bx0 + (self._tx - self._bx0) * t
        y = hand_y + (self._floor_y - hand_y) * t - _LOB_PEAK * math.sin(math.pi * t)
        return x, y

    _VERDICTS = {'perfect': ("PERFECT!", (250, 210, 90)),
                 'nice':    ("NICE!", (120, 230, 140)),
                 'shank':   ("SHANK!", (240, 170, 90))}

    def _success(self, x, quality) -> bool:
        """Score a dig (a shank still counts); return True if that completes the drill."""
        self._digs += 1
        self._streak += 1
        self._best = max(self._best, self._streak)
        if self._sfx is not None:
            self._sfx.play('dig')
        self._fx.emit_burst(x, self._floor_y - 16, (180, 220, 255), 9, 130)
        self._pop = {'x': float(x), 'y': float(self._floor_y - 16),
                     'vx': (self._sx - x) * 0.9, 'vy': -320.0}   # dug back up towards Sarah
        text, col = self._VERDICTS[quality]
        self._verdict = {'text': text, 'col': col, 't': 0.7,
                         'x': float(x), 'y': float(self._floor_y - 40)}
        return self._digs >= DIVE_TARGET

    def _miss(self) -> None:
        self._james.diving = None
        bx = self._ball_pos()[0]
        self._fx.emit_dust(bx, self._floor_y, 8)
        self._fx.shake(4, 0.2)
        self._verdict = None
        self._phase = 'over'                                # wait for Z, then reset streak and feed on

    def _attempt(self) -> None:
        rem = (1.0 - self._bt) * self._fall
        if rem > DIVE_DIG_WINDOW:                          # too early — let it drop in
            return
        bx = self._ball_pos()[0]
        ad = abs(bx - self._px)
        if ad <= DIVE_DIG_REACH:                           # under it — standing bump
            self._dig_anim = 0.22
            quality = 'perfect' if ad <= DIVE_DIG_REACH * 0.4 else 'nice'
            if self._success(bx, quality):
                self._phase = 'done'
            else:
                self._phase = 'feed'
                self._feed_t = DIVE_FEED_GAP
        else:                                              # commit to a dive
            self._start_dive(bx, connect=ad <= DIVE_LUNGE_REACH)

    def _start_dive(self, bx, connect) -> None:
        self._phase = 'dive'
        self._dive_dir = 1 if bx >= self._px else -1
        self._dive_x0 = self._px
        reach = min(DIVE_LUNGE_REACH, abs(bx - self._px) + 8)
        self._dive_x1 = _clamp(self._px + self._dive_dir * reach, self._left, self._right)
        self._dive_t = 0.0
        self._dive_connect = connect
        self._dive_dug = False
        self._dive_won = False
        self._dive_ball = self._ball_pos()
        self._pvx = 0.0
        if self._sfx is not None:
            self._sfx.play('serve')
        self._fx.emit_dust(self._px, self._floor_y, 7)

    # ── input ────────────────────────────────────────────────────────────────
    def handle_action(self, action) -> bool:
        if self._phase == 'done':                          # drill over: pass -> continue;
            won = self._digs >= DIVE_TARGET                # fall short -> Retry (Z) or Give up (X)
            if not won and action == Action.CONFIRM:
                self._restart()
            elif action == Action.CONFIRM or (not won and action == Action.CANCEL):
                if self.on_finish is not None:
                    self.on_finish()
            return True
        if action != Action.CONFIRM:
            return False
        if self._phase == 'intro':
            self._toss()
            return True
        if self._phase == 'rally':
            self._attempt()
            return True
        if self._phase == 'over':                          # acknowledge the drop, feed on
            self._streak = 0
            self._feed_or_end()
            return True
        return False

    def _restart(self) -> None:
        """Run the drill again from the top (the Retry option)."""
        self._px = SCREEN_WIDTH / 2.0
        self._pvx = self._move_x = 0.0
        self._streak = self._best = self._digs = self._feeds = 0
        self._dig_anim = self._sarah_toss = 0.0
        self._pop = self._verdict = None
        self._james.diving = None
        self._phase = 'intro'

    def handle_held(self, vec) -> None:
        self._move_x = -1.0 if vec[0] < -0.3 else (1.0 if vec[0] > 0.3 else 0.0)

    # ── update ─────────────────────────────────────────────────────────────--
    def update(self, dt: float) -> None:
        self._fx.update(dt)
        if self._dig_anim > 0:
            self._dig_anim = max(0.0, self._dig_anim - dt)
        if self._sarah_toss > 0:
            self._sarah_toss = max(0.0, self._sarah_toss - dt)
        if self._pop is not None:                          # the dug ball flying away
            self._pop['vy'] += 900.0 * dt
            self._pop['x'] += self._pop['vx'] * dt
            self._pop['y'] += self._pop['vy'] * dt
            if self._pop['y'] > SCREEN_HEIGHT:
                self._pop = None
        if self._verdict is not None:                      # PERFECT/NICE/SHANK drifts up and fades
            self._verdict['t'] -= dt
            self._verdict['y'] -= 34.0 * dt
            if self._verdict['t'] <= 0:
                self._verdict = None

        if self._phase == 'rally':
            self._move_player(dt)
            self._bt += dt / self._fall
            if self._bt >= 1.0:
                self._miss()
        elif self._phase == 'dive':
            self._update_dive(dt)
        elif self._phase == 'feed':
            self._feed_t -= dt
            if self._feed_t <= 0:
                self._feed_or_end()

    def _move_player(self, dt: float) -> None:
        target = self._move_x * DIVE_PLAYER_SPEED
        if self._pvx < target:
            self._pvx = min(target, self._pvx + DIVE_PLAYER_ACCEL * dt)
        else:
            self._pvx = max(target, self._pvx - DIVE_PLAYER_ACCEL * dt)
        self._px = _clamp(self._px + self._pvx * dt, self._left, self._right)
        if (self._px <= self._left and self._pvx < 0) or (self._px >= self._right and self._pvx > 0):
            self._pvx = 0.0
        self._james.walk_phase += abs(self._pvx) * dt * 0.02

    def _update_dive(self, dt: float) -> None:
        self._dive_t += dt / DIVE_LUNGE_TIME
        if self._dive_connect and not self._dive_dug and self._dive_t >= 0.42:
            self._dive_dug = True                          # contact at full extension
            self._dive_won = self._success(self._dive_x1, 'shank')
            self._fx.shake(6, 0.26)
        if self._dive_t >= 1.0:
            self._james.diving = None
            self._fx.emit_dust(self._dive_x1, self._floor_y, 10)   # landing slide
            self._px = self._dive_x1
            if not self._dive_dug:
                self._miss()
            elif self._dive_won:
                self._phase = 'done'
            else:
                self._phase = 'feed'
                self._feed_t = DIVE_FEED_GAP

    # ── draw ───────────────────────────────────────────────────────────────--
    def draw(self, screen: pygame.Surface) -> None:
        ox, oy = self._fx.offset()
        fy = self._floor_y + oy
        screen.fill(_WALL)                                  # pale-timber clad wall
        for x in range(0, SCREEN_WIDTH, 9):
            pygame.draw.line(screen, _WALL_DK, (x, 0), (x, fy), 1)
        pygame.draw.rect(screen, _GFLOOR, (0, fy, SCREEN_WIDTH, SCREEN_HEIGHT - fy))   # sprung floor
        for i in range(0, SCREEN_HEIGHT - self._floor_y, 14):
            if (i // 14) % 3 == 0:
                pygame.draw.rect(screen, _GFLOOR_SHEEN, (0, fy + i, SCREEN_WIDTH, 5))
        pygame.draw.line(screen, _LINE, (0, fy), (SCREEN_WIDTH, fy), 3)                 # court line

        self._draw_sarah(screen, ox, oy)
        self._draw_ball(screen, ox, oy)
        self._draw_james(screen, ox, oy)
        self._fx.draw(screen)
        if self._verdict is not None:
            v = self._verdict
            menu.text(screen, v['text'], int(v['x']) + ox, int(v['y']) + oy,
                      menu.font(UI_TITLE_FONT_NAME, 24), v['col'], shadow=True)
        if self._phase == 'intro':
            self._draw_intro(screen)
        else:
            self._draw_hud(screen)
            if self._phase == 'done':
                self._draw_done(screen)

    def _draw_sarah(self, screen, ox, oy) -> None:
        sa = self._sarah
        sa.facing = 'right'                                  # facing James, across the court
        sa.walking = False
        sa.x = self._sx + ox
        sa.y = self._floor_y - 14 - (4 if self._sarah_toss > 0 else 0) + oy   # little toss bob
        sa.draw(screen)

    def _draw_ball(self, screen, ox, oy) -> None:
        if self._pop is not None:
            pygame.draw.circle(screen, _BALL, (int(self._pop['x']) + ox, int(self._pop['y']) + oy), 8)
            pygame.draw.circle(screen, (200, 190, 170), (int(self._pop['x']) + ox, int(self._pop['y']) + oy), 8, 1)
        live = self._phase == 'rally' or (self._phase == 'dive' and not self._dive_dug)
        if not live:
            return
        if self._phase == 'rally':
            bx, by = self._ball_pos()
            drop = self._bt
        else:
            bx, by = self._dive_ball
            drop = 0.9
        bx, by = int(bx) + ox, int(by) + oy
        sw = int(10 + 16 * drop)
        pygame.draw.ellipse(screen, (12, 16, 18), (bx - sw // 2, self._floor_y + oy + 2, sw, 6))
        pygame.draw.circle(screen, _BALL, (bx, by), 9)
        pygame.draw.circle(screen, (200, 190, 170), (bx, by), 9, 1)

    def _draw_james(self, screen, ox, oy) -> None:
        j = self._james
        if self._phase == 'dive':
            t = min(1.0, self._dive_t)
            j.diving = 'right' if self._dive_dir > 0 else 'left'
            ease = 1.0 - (1.0 - t) ** 2
            j.x = self._dive_x0 + (self._dive_x1 - self._dive_x0) * ease + ox
            j.y = self._floor_y - 4 - DIVE_LUNGE_HOP * math.sin(math.pi * t) + oy
        else:
            j.diving = None
            j.x = self._px + ox
            j.y = self._floor_y - 14 + (6 if self._dig_anim > 0 else 0) + oy
            if abs(self._pvx) > 24:
                j.walking = True
                j.facing = 'right' if self._pvx > 0 else 'left'
            else:
                j.walking = False
                j.facing = 'up'
        j.draw(screen)

    def _draw_hud(self, screen) -> None:
        menu.text(screen, "DIG RALLY", SCREEN_WIDTH // 2, 16,
                  menu.font(UI_TITLE_FONT_NAME, 28), (56, 48, 36))     # dark, on the tan wall
        col = (44, 110, 56) if self._streak >= 5 else (72, 64, 52)
        menu.text(screen, "Streak {0}   ·   Best {1}".format(self._streak, self._best),
                  SCREEN_WIDTH // 2, 50, menu.font(UI_FONT_NAME, 16), col)
        if self._phase in ('rally', 'feed', 'dive'):
            menu.text(screen, "<-  ->  run     Z  dig", SCREEN_WIDTH // 2,
                      self._floor_y + 36, menu.font(UI_FONT_NAME, 16), (236, 240, 244))
        elif self._phase == 'over':
            menu.text(screen, "DROPPED!", SCREEN_WIDTH // 2, self._floor_y + 26,
                      menu.font(UI_TITLE_FONT_NAME, 32), (240, 120, 120), shadow=True)
            menu.text(screen, "Z to continue", SCREEN_WIDTH // 2, self._floor_y + 60,
                      menu.font(UI_FONT_NAME, 16), (236, 240, 244))

    def _draw_intro(self, screen) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        cx = SCREEN_WIDTH // 2
        menu.text(screen, "DIG RALLY", cx, SCREEN_HEIGHT // 2 - 96,
                  menu.font(UI_TITLE_FONT_NAME, 40), (245, 238, 220), shadow=True)
        lines = ["Sarah feeds you short balls, one after another.",
                 "Run under each   <-  ->   and press Z to dig it back.",
                 "Out of reach? Z anyway to dive — scrappy shanks still count.",
                 "Drop one and the streak resets. Get to {0} digs.".format(DIVE_TARGET)]
        for i, ln in enumerate(lines):
            menu.text(screen, ln, cx, SCREEN_HEIGHT // 2 - 36 + i * 28,
                      menu.font(UI_FONT_NAME, 18), (214, 218, 224))
        menu.text(screen, "Z to start", cx, SCREEN_HEIGHT - 44,
                  menu.font(UI_FONT_NAME, 18), (245, 238, 220))

    def _draw_done(self, screen) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        cx = SCREEN_WIDTH // 2
        menu.text(screen, "Best rally: {0}".format(self._best), cx, SCREEN_HEIGHT // 2 - 40,
                  menu.font(UI_TITLE_FONT_NAME, 40), (240, 240, 245), shadow=True)
        quip = ("A literal wall." if self._best >= 12 else
                "Proper hands on you!" if self._best >= 6 else
                "Getting there." if self._best >= 2 else
                "Welp. We'll work on it.")
        menu.text(screen, quip, cx, SCREEN_HEIGHT // 2 + 14,
                  menu.font(UI_FONT_NAME, 18), (200, 204, 210))
        if self._digs >= DIVE_TARGET:
            prompt = "Z to continue"
        else:
            menu.text(screen, "{0} / {1} digs".format(self._digs, DIVE_TARGET),
                      cx, SCREEN_HEIGHT // 2 + 42, menu.font(UI_FONT_NAME, 15), (180, 184, 190))
            prompt = "Z - Retry     X - Give up"
        menu.text(screen, prompt, cx, SCREEN_HEIGHT - 40,
                  menu.font(UI_FONT_NAME, 16), (170, 174, 180))
