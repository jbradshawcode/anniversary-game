"""Diving drill (Ch3) — Sarah coaches James through digging, one stage at a time.

A fed ball is a three-stage dig, each with its own input and timing:

    STEP   move ←/→ onto the telegraphed landing ring while the ball is up.
    PUSH   a timing needle sweeps a bar — press Z in the band to load your legs.
    SLIDE  a second sweep — press Z to extend the platform and pass it back.

Nothing here is a reaction test: the feed lands close (low, capped variation) and
the two sweeps run at a constant tempo every ball, so the rally is a rhythm you
learn rather than a twitch you survive. The dive animation is just what the SLIDE
looks like when you're stretched — there is no "dive" button. Quality is a blend
of the three stages; you only drop a ball by skipping the slide or positioning so
badly even a dive can't reach. The drill ends at DIVE_TARGET digs. Self-contained.
"""
import math
import random
from typing import Callable, Optional
import pygame

from config import (SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_NAME, UI_TITLE_FONT_NAME,
                    DIVE_PLAYER_SPEED, DIVE_PLAYER_ACCEL, DIVE_STEP_TIME,
                    DIVE_PUSH_SWEEP, DIVE_SLIDE_SWEEP, DIVE_PUSH_CENTRE,
                    DIVE_SLIDE_CENTRE, DIVE_BAND_GOOD, DIVE_BAND_PERFECT,
                    DIVE_SET_GOOD, DIVE_SET_PERFECT, DIVE_REACH,
                    DIVE_SPREAD_MIN, DIVE_SPREAD_MAX, DIVE_SPREAD_GROW,
                    DIVE_PERFECT_AT, DIVE_NICE_AT, DIVE_DIVE_CAP,
                    DIVE_SWING_PREROLL, DIVE_SLIDE_CONNECT,
                    DIVE_LUNGE_TIME, DIVE_LUNGE_HOP, DIVE_FEED_GAP,
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
_GOLD = (250, 210, 90)
_BAD = (240, 120, 120)
_SHANK = (240, 170, 90)
_TRACK = (28, 32, 38)
_LOB_PEAK = 132              # how high Sarah's feed arcs


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
        self._streak = self._best = self._digs = self._feeds = 0
        self._px = SCREEN_WIDTH / 2.0
        self._pvx = self._move_x = 0.0

    def enter(self, player) -> None:
        self._james = James(0, 0)
        self._sarah = Player(0, 0)
        self._sarah.facing = 'right'
        self._fx = FX()
        self._sfx = SoundBank()
        self._reset_state()
        self._phase = 'intro'                # learn the controls; Z starts the first feed

    def _reset_state(self) -> None:
        self._px = SCREEN_WIDTH / 2.0
        self._pvx = self._move_x = 0.0
        self._streak = self._best = self._digs = self._feeds = 0
        self._dig_anim = self._sarah_toss = self._step_hint = 0.0
        self._pop = None
        self._verdict = None                 # floating PERFECT/NICE/SHANK label
        self._tx = self._px
        self._needle = 0.0
        self._swing_delay = 0.0              # the "ready" beat before a bar starts sweeping
        self._step_q = self._push_q = self._slide_q = 0.0
        self._slide_pressed = False
        self._james.diving = None

    def _restart(self) -> None:
        """Run the drill again from the top (the Retry option)."""
        self._reset_state()
        self._phase = 'intro'

    # ── feed / outcomes ──────────────────────────────────────────────────────
    def _feed_or_end(self) -> None:
        if self._feeds >= DIVE_MAX_FEEDS:
            self._phase = 'done'
        else:
            self._toss()

    def _toss(self) -> None:
        """Start a new ball: pick a close, capped landing spot and lob it there."""
        self._feeds += 1
        spread = min(DIVE_SPREAD_MAX, DIVE_SPREAD_MIN + DIVE_SPREAD_GROW * self._digs)
        offset = random.uniform(0.45, 1.0) * spread * random.choice((-1.0, 1.0))
        margin = 24
        self._tx = _clamp(self._px + offset, self._left + margin, self._right - margin)
        self._bx0 = float(self._sx)                        # the ball leaves Sarah's hands
        self._step_t = 0.0
        self._needle = 0.0
        self._swing_delay = 0.0
        self._step_q = self._push_q = self._slide_q = 0.0
        self._slide_pressed = False
        self._sarah_toss = 0.18                            # her little pass motion
        self._pop = None
        self._james.diving = None
        self._phase = 'step'
        if self._sfx is not None:
            self._sfx.play('set')

    # ── geometry of the fed ball ───────────────────────────────────────────--
    _READY_Y_OFF = 56          # ball hovers this far above the floor when you're set
    _DIG_Y_OFF = 16            # contact height above the floor

    def _ball_pos(self):
        """Ball position for the current sub-phase (arc in, then drop through PUSH/SLIDE)."""
        ready_y = self._floor_y - self._READY_Y_OFF
        dig_y = self._floor_y - self._DIG_Y_OFF
        if self._phase == 'step':
            t = self._step_t
            ease = 1.0 - (1.0 - t) ** 2
            x = self._bx0 + (self._tx - self._bx0) * ease
            hand_y = self._floor_y - 24
            y = hand_y + (ready_y - hand_y) * t - _LOB_PEAK * math.sin(math.pi * t)
            return x, y
        if self._phase == 'push':
            return self._tx, ready_y + (dig_y - ready_y) * (0.5 * self._needle)
        if self._phase == 'slide':
            return self._tx, ready_y + (dig_y - ready_y) * (0.5 + 0.5 * self._needle)
        return self._tx, dig_y

    # ── scoring helpers ────────────────────────────────────────────────────--
    @staticmethod
    def _band_score(pos: float, centre: float) -> float:
        """1.0 at the gold centre, 0.5 at the edge of the green band, →0 beyond."""
        d = abs(pos - centre)
        if d <= DIVE_BAND_PERFECT:
            return 1.0
        if d <= DIVE_BAND_GOOD:
            return 1.0 - 0.5 * (d - DIVE_BAND_PERFECT) / (DIVE_BAND_GOOD - DIVE_BAND_PERFECT)
        return max(0.0, 0.5 - 2.0 * (d - DIVE_BAND_GOOD))

    @staticmethod
    def _set_score(gap: float) -> float:
        """Footwork quality from how far your feet are off the landing spot."""
        if gap <= DIVE_SET_PERFECT:
            return 1.0
        if gap <= DIVE_SET_GOOD:
            return 1.0 - 0.4 * (gap - DIVE_SET_PERFECT) / (DIVE_SET_GOOD - DIVE_SET_PERFECT)
        if gap <= DIVE_REACH:
            return max(0.0, 0.6 * (1.0 - (gap - DIVE_SET_GOOD) / (DIVE_REACH - DIVE_SET_GOOD)))
        return 0.0

    _VERDICTS = {'perfect': ("PERFECT!", _GOLD),
                 'nice':    ("NICE!", _GOOD),
                 'shank':   ("SHANK!", _SHANK)}

    # ── input ────────────────────────────────────────────────────────────────
    def handle_action(self, action) -> bool:
        if self._phase == 'done':                          # drill over
            won = self._digs >= DIVE_TARGET                # won -> Z/X continue; short -> Z Retry, X give up
            if action == Action.CONFIRM and not won:
                self._restart()
            elif action in (Action.CONFIRM, Action.CANCEL):
                if self.on_finish is not None:
                    self.on_finish()
            return True
        if action != Action.CONFIRM:
            return False
        if self._phase == 'intro':
            self._toss()
        elif self._phase == 'step':                        # too early — the ball's still up
            self._step_hint = 0.6
            self._fx.shake(2, 0.12)
        elif self._phase == 'push':
            if self._swing_delay <= 0:                      # ignore presses during the ready beat
                self._push_q = self._band_score(self._needle, DIVE_PUSH_CENTRE)
                self._enter_slide()
        elif self._phase == 'slide':
            if self._swing_delay <= 0:
                self._slide_pressed = True
                self._slide_q = self._band_score(self._needle, DIVE_SLIDE_CENTRE)
                self._resolve()
        elif self._phase == 'over':                        # acknowledge the drop, feed on
            self._streak = 0
            self._feed_or_end()
        return True

    def handle_held(self, vec) -> None:
        self._move_x = -1.0 if vec[0] < -0.3 else (1.0 if vec[0] > 0.3 else 0.0)

    def _enter_slide(self) -> None:
        self._needle = 0.0
        self._swing_delay = DIVE_SWING_PREROLL
        self._phase = 'slide'
        if self._sfx is not None:
            self._sfx.play('serve')

    # ── resolve a dig ──────────────────────────────────────────────────────--
    def _resolve(self) -> None:
        gap = abs(self._px - self._tx)
        # How far you can extend is set by how well you loaded (PUSH) and reached
        # (SLIDE): a clean swing covers the full dive reach, a sloppy one barely
        # leaves your stance. Good footwork (small gap) reaches regardless, so the
        # timing only bites when you're stretched — which is where it should.
        power = 0.35 * self._push_q + 0.65 * self._slide_q
        eff_reach = DIVE_SET_GOOD + (DIVE_REACH - DIVE_SET_GOOD) * power
        if (not self._slide_pressed or self._slide_q < DIVE_SLIDE_CONNECT
                or gap > eff_reach):
            self._miss()                                   # whiffed the contact, or couldn't get there
            return
        diving = gap > DIVE_SET_GOOD
        combine = 0.34 * self._step_q + 0.33 * self._push_q + 0.33 * self._slide_q
        if diving:
            combine = min(combine, DIVE_DIVE_CAP)          # a scrappy dive never reads "perfect"
        quality = ('perfect' if combine >= DIVE_PERFECT_AT else
                   'nice' if combine >= DIVE_NICE_AT else 'shank')
        if diving:
            self._start_dive(quality)
        else:
            self._dig_anim = 0.22
            self._score(quality, self._tx)
            self._after_contact()

    def _score(self, quality: str, x: float) -> None:
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
                         'x': float(x), 'y': float(self._floor_y - 48)}

    def _after_contact(self) -> None:
        if self._digs >= DIVE_TARGET:
            self._phase = 'done'
        else:
            self._phase = 'feed'
            self._feed_t = DIVE_FEED_GAP

    def _start_dive(self, quality: str) -> None:
        self._phase = 'dive'
        self._dive_dir = 1 if self._tx >= self._px else -1
        self._dive_x0 = self._px
        self._dive_x1 = _clamp(self._tx, self._left, self._right)
        self._dive_t = 0.0
        self._dive_quality = quality
        self._dive_scored = False
        self._pvx = 0.0
        self._fx.emit_dust(self._px, self._floor_y, 7)

    def _miss(self) -> None:
        self._james.diving = None
        bx = self._ball_pos()[0]
        self._fx.emit_dust(bx, self._floor_y, 8)
        self._fx.shake(4, 0.2)
        self._verdict = None
        self._phase = 'over'                                # wait for Z, then reset streak and feed on

    # ── update ─────────────────────────────────────────────────────────────--
    def update(self, dt: float) -> None:
        self._fx.update(dt)
        if self._dig_anim > 0:
            self._dig_anim = max(0.0, self._dig_anim - dt)
        if self._sarah_toss > 0:
            self._sarah_toss = max(0.0, self._sarah_toss - dt)
        if self._step_hint > 0:
            self._step_hint = max(0.0, self._step_hint - dt)
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

        if self._phase == 'step':
            self._move_player(dt)
            self._step_t += dt / DIVE_STEP_TIME
            if self._step_t >= 1.0:
                self._step_t = 1.0
                self._step_q = self._set_score(abs(self._px - self._tx))
                self._needle = 0.0
                self._swing_delay = DIVE_SWING_PREROLL      # a ready beat before PUSH sweeps
                self._phase = 'push'
        elif self._phase == 'push':
            if self._swing_delay > 0:
                self._swing_delay = max(0.0, self._swing_delay - dt)
            else:
                self._needle += dt / DIVE_PUSH_SWEEP
                if self._needle >= 1.0:                     # let it sweep past — a no-press push scores 0
                    self._needle = 1.0
                    self._push_q = 0.0
                    self._enter_slide()
        elif self._phase == 'slide':
            if self._swing_delay > 0:
                self._swing_delay = max(0.0, self._swing_delay - dt)
            else:
                self._needle += dt / DIVE_SLIDE_SWEEP
                if self._needle >= 1.0:                     # never pressed slide -> dropped
                    self._needle = 1.0
                    self._resolve()
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
        if not self._dive_scored and self._dive_t >= 0.5:   # contact at full extension
            self._dive_scored = True
            self._score(self._dive_quality, self._dive_x1)
            self._fx.shake(6, 0.26)
        if self._dive_t >= 1.0:
            self._james.diving = None
            self._fx.emit_dust(self._dive_x1, self._floor_y, 10)   # landing slide
            self._px = self._dive_x1
            self._after_contact()

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

        if self._phase in ('step', 'push', 'slide'):
            self._draw_target(screen, ox, oy)
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
            if self._phase in ('push', 'slide'):
                self._draw_timing(screen)
            if self._phase == 'done':
                self._draw_done(screen)

    def _draw_target(self, screen, ox, oy) -> None:
        """The landing ring on the floor — telegraphed the instant the ball is fed."""
        tx = int(self._tx) + ox
        fy = self._floor_y + oy
        gap = abs(self._px - self._tx)
        set_now = gap <= DIVE_SET_GOOD
        col = _GOOD if set_now else (210, 196, 150)
        # the ring swells in the last beat of STEP so PUSH doesn't ambush you
        arriving = self._phase == 'step' and self._step_t > 0.78
        grow = int(6 * math.sin(self._step_t * math.pi * 6)) if arriving else 0
        pygame.draw.ellipse(screen, col, (tx - 26 - grow, fy - 7, 52 + 2 * grow, 14), 2)
        pygame.draw.ellipse(screen, col, (tx - 13, fy - 4, 26, 8), 1)
        if self._phase == 'step' and set_now:
            menu.text(screen, "SET", tx, fy - 30, menu.font(UI_FONT_NAME, 14), _GOOD)

    def _draw_sarah(self, screen, ox, oy) -> None:
        sa = self._sarah
        sa.facing = 'right'                                  # facing James, across the court
        sa.walking = False
        sa.x = self._sx + ox
        sa.y = self._floor_y - 14 - (4 if self._sarah_toss > 0 else 0) + oy   # little toss bob
        sa.draw(screen)

    def _draw_ball(self, screen, ox, oy) -> None:
        if self._pop is not None:
            px, py = int(self._pop['x']) + ox, int(self._pop['y']) + oy
            pygame.draw.circle(screen, _BALL, (px, py), 8)
            pygame.draw.circle(screen, (200, 190, 170), (px, py), 8, 1)
        live = self._phase in ('step', 'push', 'slide') or (self._phase == 'dive' and not self._dive_scored)
        if not live:
            return
        if self._phase == 'dive':
            bx, by = self._tx, self._floor_y - self._DIG_Y_OFF
            drop = 1.0
        else:
            bx, by = self._ball_pos()
            drop = (self._step_t if self._phase == 'step' else      # 0..1 of the full descent
                    0.5 * self._needle if self._phase == 'push' else
                    0.5 + 0.5 * self._needle)
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
            crouch = 6 if (self._dig_anim > 0 or self._phase in ('push', 'slide')) else 0
            j.x = self._px + ox
            j.y = self._floor_y - 14 + crouch + oy
            if self._phase == 'step' and abs(self._pvx) > 24:
                j.walking = True
                j.facing = 'right' if self._pvx > 0 else 'left'
            else:
                j.walking = False
                j.facing = 'up'
        j.draw(screen)

    # ── HUD / timing bar / cards ───────────────────────────────────────────--
    _STAGE_LABEL = {'step': "STEP — get under it", 'push': "PUSH — load your legs",
                    'slide': "SLIDE — pass it back!"}

    def _draw_hud(self, screen) -> None:
        menu.text(screen, "DIG RALLY", SCREEN_WIDTH // 2, 16,
                  menu.font(UI_TITLE_FONT_NAME, 28), (56, 48, 36))     # dark, on the tan wall
        col = (44, 110, 56) if self._streak >= 5 else (72, 64, 52)
        menu.text(screen, "Streak {0}   ·   Best {1}   ·   {2}/{3}".format(
            self._streak, self._best, self._digs, DIVE_TARGET),
            SCREEN_WIDTH // 2, 50, menu.font(UI_FONT_NAME, 16), col)
        if self._phase == 'step':
            menu.text(screen, self._STAGE_LABEL['step'], SCREEN_WIDTH // 2,
                      self._floor_y + 34, menu.font(UI_FONT_NAME, 16), (236, 240, 244))
            if self._step_hint > 0:                         # pressed Z too early
                menu.text(screen, "wait for it…", SCREEN_WIDTH // 2, self._floor_y + 58,
                          menu.font(UI_FONT_NAME, 15), _GOLD)
            else:
                menu.text(screen, "<-  ->  move", SCREEN_WIDTH // 2, self._floor_y + 58,
                          menu.font(UI_FONT_NAME, 15), (210, 216, 222))
        elif self._phase == 'over':
            menu.text(screen, "DROPPED!", SCREEN_WIDTH // 2, self._floor_y + 26,
                      menu.font(UI_TITLE_FONT_NAME, 32), _BAD, shadow=True)
            menu.text(screen, "Z to continue", SCREEN_WIDTH // 2, self._floor_y + 60,
                      menu.font(UI_FONT_NAME, 16), (236, 240, 244))

    def _draw_timing(self, screen) -> None:
        """The PUSH / SLIDE bar: green good band, gold perfect centre, sweeping needle."""
        centre = DIVE_PUSH_CENTRE if self._phase == 'push' else DIVE_SLIDE_CENTRE
        w, h = 340, 22
        x0 = SCREEN_WIDTH // 2 - w // 2
        y0 = self._floor_y + 40
        menu.text(screen, self._STAGE_LABEL[self._phase], SCREEN_WIDTH // 2, y0 - 26,
                  menu.font(UI_FONT_NAME, 16), (236, 240, 244))
        pygame.draw.rect(screen, _TRACK, (x0, y0, w, h), border_radius=4)
        good = pygame.Rect(int(x0 + (centre - DIVE_BAND_GOOD) * w), y0,
                           int(2 * DIVE_BAND_GOOD * w), h)
        pygame.draw.rect(screen, _GOOD, good, border_radius=4)
        perf = pygame.Rect(int(x0 + (centre - DIVE_BAND_PERFECT) * w), y0,
                           int(2 * DIVE_BAND_PERFECT * w), h)
        pygame.draw.rect(screen, _GOLD, perf)
        ready = self._swing_delay > 0                       # the pre-roll beat: needle parked, dimmed
        nx = int(x0 + _clamp(self._needle, 0.0, 1.0) * w)
        pygame.draw.rect(screen, (120, 124, 130) if ready else (250, 250, 252),
                         (nx - 2, y0 - 5, 4, h + 10))
        pygame.draw.rect(screen, (250, 250, 252), (x0, y0, w, h), 2, border_radius=4)
        menu.text(screen, "ready…" if ready else "Z", SCREEN_WIDTH // 2, y0 + h + 6,
                  menu.font(UI_FONT_NAME, 15), (210, 216, 222))

    def _draw_intro(self, screen) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        cx = SCREEN_WIDTH // 2
        menu.text(screen, "DIG RALLY", cx, SCREEN_HEIGHT // 2 - 118,
                  menu.font(UI_TITLE_FONT_NAME, 40), (245, 238, 220), shadow=True)
        lines = ["Sarah feeds you short balls. Keep the rally alive.",
                 "Three beats to every dig:",
                 "STEP   <-  ->   onto the ring on the floor.",
                 "PUSH   Z  in the band as the needle sweeps.",
                 "SLIDE  Z  again to pass it back — stretched balls dive.",
                 "Drop one and the streak resets. Get to {0} digs.".format(DIVE_TARGET)]
        for i, ln in enumerate(lines):
            big = ln.startswith(("STEP", "PUSH", "SLIDE"))
            menu.text(screen, ln, cx, SCREEN_HEIGHT // 2 - 64 + i * 28,
                      menu.font(UI_FONT_NAME, 18), (228, 232, 238) if big else (200, 204, 212))
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
