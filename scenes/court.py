"""Scene 11 — 3v3 volleyball minigame (real-time, free movement, own input).

Enlarged top-down court: your team near (bottom), opponents far (top), net across
the middle. You control one player with momentum movement (arrows); the other
five are AI. Z = dig/attack/serve/block, X = set, C = tip/dump. A
rally chains dig -> set -> spike per side; the ball pops to the setter on a dig.
The spike is a hero beat: timing the Z press enters a brief slow-mo "aim-step"
where arrows steer a reticle and the press timing sets the power.
First to 7, win by 2; the near team rotates clockwise on side-out so you cycle
setter -> hitter roles. Launched from the gym coach; on_finish() returns there.
"""
import random
import pygame
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

from .base import Scene
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_NAME, VB_NET_Y, VB_ACTOR_SPEED,
                    VB_CONTACT_RADIUS, VB_TIMING_WINDOW, VB_PERFECT_WINDOW,
                    VB_SCORE_TO_WIN,
                    VB_DIG_CLEAN, VB_DIG_SHANK, VB_DIG_MOVE_PEN, VB_DIG_OFFSET_PEN,
                    VB_DIG_DIFF_PEN, VB_OOS_POWER_CAP, VB_OOS_RANGE,
                    VB_DIG_EARLY_EDGE, VB_DIG_IDEAL, VB_DIG_GRACE, VB_DIG_TOL,
                    VB_DIG_TIME_FLOOR, VB_DIG_GOOD_TOL, VB_DIG_SWITCH_MARGIN,
                    VB_TOP_SPEED, VB_ACCEL, VB_DECEL, VB_BACKPEDAL_FACTOR,
                    VB_AIMSTEP_SLOWMO, VB_AIMSTEP_WINDOW, VB_RETICLE_SPEED,
                    VB_SPIKE_METER_SPEED, VB_SPIKE_SWEET_LO, VB_SPIKE_SWEET_HI,
                    VB_SPIKE_MIN_POWER, VB_AIM_OUT, VB_OUT_LAND,
                    VB_PLAYER_TAKE_RADIUS, VB_SETTER_TAKE_RADIUS, VB_SETTER_PLAYER_BIAS,
                    VB_SERVE_METER_SPEED, VB_SERVE_LAT_SPEED, VB_SERVE_NET_MAX,
                    VB_SERVE_OUT_MIN, VB_SERVE_GREEN, VB_SERVE_PEAK, VB_SERVE_DUR,
                    VB_TUT_RESOLVE, VB_TUT_SUCCESS, VB_TUT_FAIL,
                    VB_NET_CONTACT, VB_TIP_PEAK, VB_TIP_DUR, VB_TIP_DROP,
                    VB_BLOCK_DURATION, VB_TUT_BLOCK_DURATION, VB_BLOCK_COOLDOWN, VB_BLOCK_REACH,
                    VB_BLOCK_NET_DIST, VB_BLOCK_ELIGIBLE, VB_BLOCK_SQUARE, VB_BLOCK_Y_BAND,
                    VB_BLOCK_SQ_STUFF, VB_BLOCK_SQ_SOFT, VB_BLOCK_SQ_TOOL,
                    VB_BLOCK_GL_STUFF, VB_BLOCK_GL_TOOL, VB_BLOCK_GL_SOFT, VB_BLOCK_GL_ROOF,
                    VB_AI_TIP_BIAS,
                    VB_OOS_ERROR_MULT, VB_RALLY_MAX,
                    VB_DIFFICULTY)
from systems.input_handler import Action
from systems.fx import FX
from systems.audio import SoundBank
from entities.volleyball import VolleyBall, VBActor, Role, Pose
from entities import Player, James, Dan, Matt, Nat, Leonard, Bailey, Matus

# 3v3 rosters by chapter (near = your side, far = opponents). HITTER_R near is always
# the human. Leonard leaves after Ch1, so Week 2 reshuffles the sides.
_ROSTERS = {
    1: ({Role.HITTER_R: Player, Role.SETTER: Dan, Role.HITTER_L: Matt},
        {Role.SETTER: James, Role.HITTER_L: Nat, Role.HITTER_R: Leonard}),
    2: ({Role.HITTER_R: Player, Role.SETTER: James, Role.HITTER_L: Nat},
        {Role.SETTER: Dan, Role.HITTER_L: Matt, Role.HITTER_R: Bailey}),
    3: ({Role.HITTER_R: Player, Role.SETTER: James, Role.HITTER_L: Nat},
        {Role.SETTER: Dan, Role.HITTER_L: Matt, Role.HITTER_R: Bailey}),
}

# ── Palette ──────────────────────────────────────────────────────────────────
_CLAD     = (22, 26, 34)
_FLOOR    = (52, 112, 160)      # hall / run-off
_FLOOR_CT = (70, 140, 192)      # court surface (lighter)
_FLOOR_ATK = (61, 126, 178)     # attack zones (3m either side of the net)
_FLOOR_EDGE = (34, 78, 116)     # hall inner border
_LINE     = (244, 247, 250)
_NET_W    = (252, 252, 252)
_NET_BG   = (40, 84, 158)
_NET_MESH = (152, 180, 222)
_POST     = (172, 176, 186)
_MARK     = (250, 230, 120)
_BANNER   = (20, 24, 30)
_GREEN    = (90, 230, 120)
_RED      = (235, 80, 70)
_GUIDE    = (150, 172, 205)
_PANEL    = (16, 20, 30, 185)
_PANEL_BD = (92, 122, 168, 130)

# ── Geometry (pixels) — a volleyball court is 2:1 (18m long x 9m wide). With the
#    net horizontal the long axis runs top-to-bottom, so the court is TALL and
#    NARROW. Enlarged to fill the screen height; wide side margins hold the HUD. ─
_HALL  = pygame.Rect(150, 6, 340, 468)            # blue sprung floor
_COURT = pygame.Rect(206, 26, 228, 428)           # 9m x 18m, centred; run-off all sides
_ATTACK = 76                                       # 3m attack line offset
_RUN = 40                                          # run-off room beyond the lines
_CX = _COURT.centerx
_X_MIN, _X_MAX = _COURT.left - _RUN, _COURT.right + _RUN
_NEAR_MIN_Y, _NEAR_MAX_Y = VB_NET_Y + 12, _HALL.bottom - 12
_FAR_MIN_Y, _FAR_MAX_Y = _HALL.top + 12, VB_NET_Y - 12

# homes derive from the court: setter near the net, two hitters at the back.
_HX = 58
_HOME = {
    0: {Role.SETTER: (_CX, VB_NET_Y + 56),
        Role.HITTER_L: (_CX - _HX, _COURT.bottom - 56),
        Role.HITTER_R: (_CX + _HX, _COURT.bottom - 56)},
    1: {Role.SETTER: (_CX, VB_NET_Y - 56),
        Role.HITTER_L: (_CX + _HX, _COURT.top + 56),
        Role.HITTER_R: (_CX - _HX, _COURT.top + 56)},
}
_SERVE_POS = {0: (_CX, _COURT.bottom - 12), 1: (_CX, _COURT.top + 12)}
_CW = {Role.SETTER: Role.HITTER_R, Role.HITTER_R: Role.HITTER_L, Role.HITTER_L: Role.SETTER}

# arc tuning: (peak height px, duration s)
_DIG = (120, 1.00)
_SET = (115, 0.95)
_SPIKE_AI = (56, 0.68)        # flatter/faster -> digs sometimes fail, so kills actually land
_REBOUND = (40, 0.6)          # low, short scramble pop off a botched platform (hard to chase)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def _hang(peak: float) -> float:
    """Ballistic hang-time for a lobbed shot: higher arc -> longer in the air."""
    return 0.45 + 0.072 * (peak ** 0.5)


class Phase(Enum):
    SERVE = 0
    RALLY = 1
    POINT = 2
    OVER = 3


# Tutorial: one mechanic at a time, gated on doing it once.
_TUT_STEPS = [
    ('serve', "SERVE — tap Z for power, then Z again to aim. Land it in."),
    ('dig',   "DIG — run under the ball with the arrows, then Z to bump it up."),
    ('set',   "SET — the pass floats up to you at the net. X to set either way."),
    ('spike', "SPIKE — run up from the back, Z to leap, aim, then Z to swing."),
    ('block', "BLOCK — move to their hitter and TIME your jump. Z to stuff it."),
]


class VolleyCourt(Scene):
    wants_raw_input = True

    def __init__(self) -> None:
        super().__init__('court')
        self.on_finish: Optional[Callable[[], None]] = None
        self._font: Optional[pygame.font.Font] = None
        self._big: Optional[pygame.font.Font] = None
        self._small: Optional[pygame.font.Font] = None
        self._kf: Optional[pygame.font.Font] = None
        self._huge: Optional[pygame.font.Font] = None
        self._canvas_surf: Optional[pygame.Surface] = None
        self._dim_surf: Optional[pygame.Surface] = None
        self.near: List[VBActor] = []
        self.far: List[VBActor] = []
        self.ball = VolleyBall()
        self.fx = FX()
        self.sfx = SoundBank()
        self._ref = Matus(0, 0)                # Matúš, slumped on a stool by the sideline
        self._ref.x, self._ref.y = float(_HALL.left + 26), float(VB_NET_Y + 6)
        self._ref.facing = 'right'
        self._prev_y = self.ball.y
        self._mode = 'match'       # 'match' | 'tutorial'
        self._level = 'hard'       # difficulty; opponent strength
        self._week = 1             # which chapter's roster to field
        self._opp = dict(VB_DIFFICULTY['hard'])
        self._tut: Optional[Dict[str, object]] = None

    def configure(self, mode: str = 'match', level: str = 'hard', week: int = 1) -> None:
        """Set by game.py before entering: match vs tutorial, difficulty, and which
        chapter's roster to field."""
        self._mode = mode
        self._level = level if level in VB_DIFFICULTY else 'hard'
        self._week = week if week in _ROSTERS else 1

    # ── Setup ────────────────────────────────────────────────────────────────
    def enter(self, player) -> None:
        # real characters; identity persists through role rotation (only .role changes)
        near_cls, far_cls = _ROSTERS.get(self._week, _ROSTERS[1])
        near_sprites = {r: near_cls[r](0, 0) for r in Role}
        far_sprites = {r: far_cls[r](0, 0) for r in Role}
        self.near = [VBActor(*_HOME[0][r], 0, r, sprite=near_sprites[r]) for r in Role]
        self.far = [VBActor(*_HOME[1][r], 1, r, sprite=far_sprites[r]) for r in Role]
        for a in self.near:
            a.is_player = a.role == Role.HITTER_R
        self.fx = FX()
        self._opp = dict(VB_DIFFICULTY[self._level])   # opponent (team 1) strength
        self.score = [0, 0]
        self.serving = random.randint(0, 1)
        self._await: Optional[Tuple[str, Optional[VBActor]]] = None
        self._crossing = False
        self._move: Tuple[float, float] = (0.0, 0.0)
        self._face: Tuple[float, float] = (0.0, -1.0)
        self._vel: List[float] = [0.0, 0.0]
        self._action = False
        self._set_pressed = False
        self._tip_pressed = False
        self._aimstep: Optional[Dict[str, object]] = None
        self._setstep: Optional[Dict[str, object]] = None
        self._in_system = True
        self._block_jump = 0.0
        self._block_cd = 0.0
        self._ai_block_jump = 0.0
        self._block_target: Optional[Dict[str, object]] = None
        self._recv_cache: Optional[Tuple[tuple, VBActor]] = None
        self._react_t = 0.0          # defenders' reaction delay before breaking for the ball
        self._was_crossing = False
        self._last_contact: Optional[VBActor] = None   # no consecutive double-touch by one player
        self._touches = 0            # contacts on the current side — the 3rd MUST cross the net
        self._time_scale = 1.0
        self._time_target = 1.0
        self._serve_meter = 0.0
        self._serve_dir = 1
        self._serve_stage = 'power'
        self._serve_lat = 0.0
        self._serve_lat_dir = 1
        self._serve_power = 0.5
        self._serve_fault = False
        self._serve_outcome: Optional[Tuple[str, int, str]] = None
        self._rally_touches = 0
        self._dig_grace = 0.0
        self._hit_feedback: Optional[Tuple[str, float]] = None
        self._banner = ""
        self._timer = 0.0
        self._serve_timer = 0.0
        self._last_winner = 0
        self._intro = True
        self._tut: Optional[Dict[str, object]] = None
        self.phase = Phase.SERVE
        self._start_serve()
        if self._mode == 'tutorial':
            self._intro = False         # skip the wall-of-text card; steps guide instead
            self._tut_setup(0)

    # ── Input ────────────────────────────────────────────────────────────────
    def handle_action(self, action) -> bool:
        if action == Action.CONFIRM:
            self._action = True
            return True
        if action == Action.CANCEL:
            self._set_pressed = True
            return True
        if action == Action.MENU:
            self._tip_pressed = True
            return True
        return False

    def handle_held(self, vec: Tuple[float, float]) -> None:
        self._move = vec
        if vec != (0.0, 0.0):
            self._face = vec

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _team(self, t: int) -> List[VBActor]:
        return self.near if t == 0 else self.far

    def _role(self, t: int, role: Role) -> VBActor:
        return next(a for a in self._team(t) if a.role == role)

    def _player(self) -> VBActor:
        return next(a for a in self.near if a.is_player)

    def _opp_half(self, t: int) -> Tuple[int, int, int, int]:
        lo, hi = _COURT.left + 12, _COURT.right - 12
        if t == 0:                       # near attacks the far court
            return lo, hi, _COURT.top + 12, VB_NET_Y - 12
        return lo, hi, VB_NET_Y + 12, _COURT.bottom - 12

    def _nearest_defender(self, team: int, pt: Tuple[float, float]) -> VBActor:
        defenders = [a for a in self._team(team) if a.role != Role.SETTER]
        return min(defenders, key=lambda a: a.dist_to(*pt))

    def _receiver(self, team: int) -> VBActor:
        # who takes the first ball (agency: you take balls near you; the setter
        # avoids first balls unless one lands right at it or no back can reach).
        # The last player to touch it is ineligible — no consecutive double-touch.
        pt = self.ball.end
        elig = [a for a in self._team(team) if a is not self._last_contact] or self._team(team)
        setter = self._role(team, Role.SETTER)
        backs = [a for a in elig if a.role != Role.SETTER]
        human = next((a for a in elig if a.is_player), None)
        h_d = human.dist_to(*pt) if human is not None else 1e9
        setter_on = setter in elig and setter.dist_to(*pt) <= VB_SETTER_TAKE_RADIUS
        if setter_on and setter.dist_to(*pt) <= h_d:        # a ball on the setter is theirs
            return setter
        if (human is not None and human.role != Role.SETTER
                and h_d <= VB_PLAYER_TAKE_RADIUS):
            return human                                    # else you take balls near you
        if setter_on:
            return setter
        reach = VB_ACTOR_SPEED * max(0.05, self.ball.remaining()) + VB_CONTACT_RADIUS
        in_reach = [a for a in backs if a.dist_to(*pt) <= reach]
        if in_reach:
            return min(in_reach, key=lambda a: a.dist_to(*pt))
        if setter in elig and setter.dist_to(*pt) <= reach:  # short/quick -> setter covers
            return setter
        return min(backs, key=lambda a: a.dist_to(*pt)) if backs else elig[0]

    def _best_digger(self, team: int) -> Optional[VBActor]:
        # who should take the first ball RIGHT NOW: you if it's near you, else the
        # closest AI back that can reach, else the setter (out of system). Re-evaluated
        # each frame so the nearest player actually breaks for the ball.
        pt = self.ball.end
        elig = [a for a in self._team(team) if a is not self._last_contact] or self._team(team)
        setter = self._role(team, Role.SETTER)
        human = next((a for a in elig if a.is_player), None)
        h_d = human.dist_to(*pt) if human is not None else 1e9
        if (setter in elig and not setter.is_player          # a ball on the AI setter is theirs
                and setter.dist_to(*pt) <= VB_SETTER_TAKE_RADIUS and setter.dist_to(*pt) <= h_d):
            return setter
        if (human is not None and human.role != Role.SETTER and h_d <= VB_PLAYER_TAKE_RADIUS):
            return human
        reach = VB_ACTOR_SPEED * max(0.05, self.ball.remaining()) + VB_CONTACT_RADIUS
        backs = [a for a in elig if a.role != Role.SETTER and not a.is_player]
        reachable = [a for a in backs if a.dist_to(*pt) <= reach]
        if reachable:
            return min(reachable, key=lambda a: a.dist_to(*pt))
        if setter in elig and not setter.is_player and setter.dist_to(*pt) <= reach:
            return setter
        return min(backs, key=lambda a: a.dist_to(*pt)) if backs else elig[0]

    def _current_contactor(self) -> Optional[VBActor]:
        if not self._await:
            return None
        kind, c = self._await
        if kind == 'receive':
            return c if c is not None else self._nearest_defender(self.ball.team, self.ball.end)
        return c

    def _player_radius(self) -> float:
        return VB_CONTACT_RADIUS

    def _at_net(self, a: VBActor) -> bool:
        return abs(a.y - VB_NET_Y) < VB_BLOCK_NET_DIST

    def _block_lane(self, hitter: VBActor) -> float:
        # variable: take the line, the cross, or the seam — so each block reads differently
        r = random.random()
        if r < 0.4:
            lane = hitter.x                       # line (straight ahead of the hitter)
        elif r < 0.8:
            lane = 2 * _CX - hitter.x             # cross (the angle)
        else:
            lane = (hitter.x + _CX) / 2.0         # seam
        return _clamp(lane + random.uniform(-14, 14), _COURT.left + 20, _COURT.right - 20)

    def _commit_block(self, hitter: VBActor) -> None:
        # when a set goes up, the defending AI setter (almost always) commits to a lane
        # and moves there; a human defender blocks via the free jump instead.
        blocker = self._role(1 - hitter.team, Role.SETTER)
        bc = self._opp['block_chance']
        if blocker.is_player or random.random() >= bc:
            self._block_target = None
            return
        self._block_target = {'blocker': blocker, 'lane_x': self._block_lane(hitter)}

    def _net_point(self, team: int, x: float) -> Tuple[float, float]:
        # the attack contact point at the net, in the hitter's lane
        nx = _clamp(x, _COURT.left + 16, _COURT.right - 16)
        ny = VB_NET_Y + VB_NET_CONTACT if team == 0 else VB_NET_Y - VB_NET_CONTACT
        return nx, ny

    # ── Serve ────────────────────────────────────────────────────────────────
    def _start_serve(self) -> None:
        self.phase = Phase.SERVE
        self._await = None
        self._crossing = False
        self._last_contact = None
        self._touches = 0
        self._serve_fault = False
        self._serve_meter = 0.0
        self._serve_dir = 1
        self._serve_stage = 'power'
        self._serve_lat = 0.0
        self._serve_lat_dir = 1
        self._serve_power = 0.5
        self._rally_touches = 0
        self._in_system = True
        self._vel = [0.0, 0.0]
        self._setstep = None
        self._block_jump = 0.0
        self._ai_block_jump = 0.0
        self._block_target = None
        self._time_target = 1.0
        for a in self.near + self.far:
            a.x, a.y = a.home
            a.vx = a.vy = 0.0
            a.set_pose(Pose.READY)
            a.z = 0.0
        srv = self._server()
        srv.x, srv.y = _SERVE_POS[self.serving]
        self._serve_timer = 0.8
        self.ball.hold_at(*_SERVE_POS[self.serving])

    def _server(self) -> VBActor:
        return self._role(self.serving, Role.HITTER_R)

    def _do_serve(self) -> None:
        x0, x1, y0, y1 = self._opp_half(self.serving)
        aggr = self._opp['serve_aggr']     # AI always serves (you serve manually) -> opponent
        cx = (x0 + x1) / 2.0
        net_side, base = (y1, y0) if self.serving == 0 else (y0, y1)
        # aim at the back of the court (away from the net / setter), with some spread
        target = (_lerp(cx, random.uniform(x0 + 40, x1 - 40), aggr),
                  _lerp(net_side, base, random.uniform(0.45, 0.78)))   # less deep -> reachable
        peak = _lerp(VB_SERVE_PEAK[0], VB_SERVE_PEAK[1], 0.5)
        dur = _lerp(VB_SERVE_DUR[0], VB_SERVE_DUR[1], 0.5)
        self.ball.launch(_SERVE_POS[self.serving], target, peak, dur)
        self.ball.team = self.serving
        self._crossing = True
        self._rally_touches = 1
        self.sfx.play('serve')
        self.phase = Phase.RALLY

    def _serve_target(self, power: float, lateral: float,
                      server: int) -> Tuple[Tuple[float, float], str, float]:
        x0, x1, y0, y1 = self._opp_half(server)
        lat = _lerp(x0 + 10, x1 - 10, lateral)        # left .. right across the court
        net_side, base = (y1, y0) if server == 0 else (y0, y1)
        if power < VB_SERVE_NET_MAX:
            return (lat, float(VB_NET_Y)), 'net', 0.0
        if power > VB_SERVE_OUT_MIN:                  # land clearly past the baseline (out)
            out_y = _COURT.top - VB_OUT_LAND if server == 0 else _COURT.bottom + VB_OUT_LAND
            return (lat, float(out_y)), 'out', 1.0
        frac = (power - VB_SERVE_NET_MAX) / (VB_SERVE_OUT_MIN - VB_SERVE_NET_MAX)
        return (lat, net_side + (base - net_side) * frac), 'in', frac

    def _serve_quality(self, power: float) -> float:
        # 1.0 inside the green band (fast, flat serve), falling to 0 at the fault edges
        glo, ghi = VB_SERVE_GREEN
        if power <= glo:
            q = (power - VB_SERVE_NET_MAX) / (glo - VB_SERVE_NET_MAX)
        elif power >= ghi:
            q = (VB_SERVE_OUT_MIN - power) / (VB_SERVE_OUT_MIN - ghi)
        else:
            q = 1.0
        return max(0.0, min(1.0, q))

    def _execute_serve(self, power: float, lateral: float) -> None:
        server = self.serving
        target, zone, frac = self._serve_target(power, lateral, server)
        self.ball.team = server
        self._serve_outcome = None
        self._rally_touches = 1
        sp = _SERVE_POS[server]
        self.fx.emit_burst(sp[0], sp[1] - 16, (255, 240, 150), 8, 130)
        self.sfx.play('serve')
        if zone == 'in':
            q = self._serve_quality(power)            # green band -> flatter & faster
            peak = _lerp(VB_SERVE_PEAK[0], VB_SERVE_PEAK[1], q)
            dur = _lerp(VB_SERVE_DUR[0], VB_SERVE_DUR[1], q)
            self.ball.launch(sp, target, peak, dur)
            self._crossing = True
            self._serve_fault = False
        else:
            peak, dur = (70, 0.7) if zone == 'net' else (130, 1.05)
            self.ball.launch(sp, target, peak, dur)
            self._crossing = False
            self._serve_fault = True
            self._serve_outcome = ('fault', 1 - server,
                                   "In the net!" if zone == 'net' else "Serve out!")
        self.phase = Phase.RALLY
        if not self._serve_fault:
            self._tut_player_action('serve')

    # ── Contacts / net ───────────────────────────────────────────────────────
    def _on_cross_net(self) -> None:
        self.ball.team = 1 - self.ball.team
        self._crossing = False
        self._block_target = None
        self._last_contact = None              # new possession: the touch count resets
        self._touches = 0
        self._await = ('receive', self._receiver(self.ball.team))

    def _check_block(self) -> bool:
        # a front-row blocker on the DEFENDING side (1 - attacker), airborne at the net
        # and in the crossing ball's lane, stuffs the attack. Works both ways: the human
        # free-jumps, and either team's AI setter auto-blocks (its jump is armed in
        # _ai_setter_block). The human's OWN spike is resolved in the aim-step instead —
        # _enter_aimstep clears _ai_block_jump so it can't double-resolve here.
        attacker = self.ball.team
        defteam = 1 - attacker
        candidates = []
        human = self._player()
        if (human.team == defteam and self._block_jump > 0
                and abs(human.y - VB_NET_Y) < VB_BLOCK_NET_DIST + 8):
            candidates.append(human)
        setter = self._role(defteam, Role.SETTER)
        if (not setter.is_player and self._ai_block_jump > 0
                and abs(setter.y - VB_NET_Y) < VB_BLOCK_NET_DIST + 8):
            candidates.append(setter)
        in_lane = [b for b in candidates if abs(b.x - self.ball.x) <= VB_BLOCK_REACH]
        if not in_lane:
            return False
        p = min(in_lane, key=lambda b: abs(b.x - self.ball.x))
        if p.is_player:
            self._tut_player_action('block')            # a real, well-timed stuff passes the rep
        offset = abs(p.x - self.ball.x)
        p.set_pose(Pose.BLOCK)
        self.fx.emit_burst(p.x, p.y - 24, (255, 240, 150), 16, 220)
        start = (float(self.ball.x), float(VB_NET_Y))
        r = random.random()
        if offset <= VB_BLOCK_REACH * VB_BLOCK_SQUARE:     # square block: stuff / soft / tool / rebound
            if r < VB_BLOCK_SQ_STUFF:                       # clean stuff -> driven down, point
                ax = _clamp(self.ball.x, _COURT.left + 16, _COURT.right - 16)
                ay = float(VB_NET_Y - 38 if attacker == 1 else VB_NET_Y + 38)
                self.fx.shake(7, 0.26)
                self._block_send(1 - attacker, start, (ax, ay), 30, 0.42, "Block!")
            elif r < VB_BLOCK_SQ_STUFF + VB_BLOCK_SQ_SOFT:  # soft block -> slowed over to our side
                self.fx.shake(3, 0.16)
                self._block_outcome(1 - attacker, deep=False)
            elif r < VB_BLOCK_SQ_STUFF + VB_BLOCK_SQ_SOFT + VB_BLOCK_SQ_TOOL:  # tooled out -> their point
                self._tool_out(attacker, start, self.ball.end[1])
            else:                                           # rebounds back to the attacker's side
                self.fx.shake(4, 0.18)
                self._block_outcome(attacker, deep=True)
            return True
        # glancing / off-centre block: stuff is rare, tooling and soft touches dominate
        if r < VB_BLOCK_GL_STUFF:
            ax = _clamp(self.ball.x, _COURT.left + 16, _COURT.right - 16)
            ay = float(VB_NET_Y - 38 if attacker == 1 else VB_NET_Y + 38)
            self.fx.shake(6, 0.22)
            self._block_send(1 - attacker, start, (ax, ay), 30, 0.42, "Block!")
        elif r < VB_BLOCK_GL_STUFF + VB_BLOCK_GL_TOOL:
            self._tool_out(attacker, start, self.ball.end[1])
        elif r < VB_BLOCK_GL_STUFF + VB_BLOCK_GL_TOOL + VB_BLOCK_GL_SOFT:
            self.fx.shake(3, 0.16)
            self._block_outcome(1 - attacker, deep=False)   # soft over to our side
        elif r < VB_BLOCK_GL_STUFF + VB_BLOCK_GL_TOOL + VB_BLOCK_GL_SOFT + VB_BLOCK_GL_ROOF:
            self.fx.shake(4, 0.18)
            self._block_outcome(1 - attacker, deep=True)    # roofs deep onto our side
        else:
            self.fx.shake(4, 0.18)
            self._block_outcome(attacker, deep=True)        # rebounds to their side
        return True

    def _tool_out(self, attacker: int, start: Tuple[float, float], ry: float) -> None:
        # the hitter tools the ball off the block and out of bounds -> attacker's point
        side = float(_COURT.left - 36 if start[0] < _CX else _COURT.right + 36)
        self.fx.shake(4, 0.18)
        self._block_send(attacker, start, (side, float(ry)), 80, 0.7, "Off the block!")

    def _block_send(self, winner: int, start: Tuple[float, float], end: Tuple[float, float],
                    peak: float, dur: float, msg: str) -> None:
        # launch the ball off the block on a believable arc; the point is awarded when
        # it lands (deferred via the serve-fault resolve), so the touch is fully animated.
        self.ball.launch(start, end, peak, dur)
        self.ball.team = winner
        self._crossing = False
        self._serve_fault = True
        self._serve_outcome = ('block', winner, msg)

    def _block_outcome(self, recv_team: int, deep: bool) -> None:
        # pop the ball up for recv_team to chase; rally continues (no point)
        net_off = 90 if deep else 56
        ty = VB_NET_Y - net_off if recv_team == 1 else VB_NET_Y + net_off
        tx = _clamp(self.ball.x + random.uniform(-60, 60), _COURT.left + 16, _COURT.right - 16)
        peak = 150 if deep else 125               # more hang on the short pop -> the digger can reach it
        self.ball.launch((self.ball.x, float(VB_NET_Y)), (tx, ty), peak, _hang(peak))
        self.ball.team = recv_team
        self._crossing = False
        self._await = ('receive', self._receiver(recv_team))

    def _attackers(self, team: int, exclude: Optional[VBActor] = None) -> List[VBActor]:
        atk = [a for a in self._team(team) if a.role != Role.SETTER and a is not exclude]
        return atk if atk else [a for a in self._team(team) if a is not exclude]

    def _smart_hitter(self, team: int, exclude: Optional[VBActor] = None) -> VBActor:
        # the eligible attacker with the most open straight-ahead lane (excl. the setter)
        cands = self._attackers(team, exclude)
        if team == 0:                      # your team's setter favours setting YOU the swing
            human = next((h for h in cands if h.is_player), None)
            if human is not None and random.random() < VB_SETTER_PLAYER_BIAS:
                return human
        if random.random() < self._opp['avoid_block']:
            bx = self._player().x          # AI attacking you: bias away from your blocker
            return max(cands, key=lambda h: abs(h.x - bx))
        opp = self._team(1 - team)
        return max(cands, key=lambda h: min(abs(a.x - h.x) for a in opp))

    def _emergency_setter(self, team: int) -> VBActor:
        # when the setter digs, the hitter nearest the net/centre sets out of system
        hitters = [a for a in self._team(team) if a.role != Role.SETTER]
        return min(hitters, key=lambda a: abs(a.y - VB_NET_Y) + abs(a.x - _CX))

    def _spike_target_ai(self, team: int, perfect: bool) -> Tuple[float, float]:
        # aim at the most open spot — sample candidates, pick the one farthest from any
        # defender — so the AI hits gaps instead of straight at a defender.
        x0, x1, y0, y1 = self._opp_half(team)
        opp = self._team(1 - team)
        best, best_d = (float(_CX), (y0 + y1) / 2.0), -1.0
        for _ in range(10):
            tx = random.uniform(x0 + 24, x1 - 24)
            ty = random.uniform(y0 + 16, y1 - 16)
            d = min(a.dist_to(tx, ty) for a in opp)
            if d > best_d:
                best, best_d = (tx, ty), d
        sc = (8.0 if perfect else 18.0) * self._opp['attack_spread']
        return (_clamp(best[0] + random.uniform(-sc, sc), x0, x1),
                _clamp(best[1] + random.uniform(-sc, sc), y0, y1))

    def _ai_tip(self, team: int, c: VBActor) -> None:
        # a soft drop into the open front zone (punishes deep defenders)
        x0, x1, _, _ = self._opp_half(team)
        front_y = float(VB_NET_Y - 46 if team == 0 else VB_NET_Y + 46)
        opp = self._team(1 - team)
        best_x, best_d = float(_CX), -1.0
        for _ in range(6):
            tx = random.uniform(x0 + 24, x1 - 24)
            d = min(a.dist_to(tx, front_y) for a in opp)
            if d > best_d:
                best_x, best_d = tx, d
        self.ball.launch((c.x, c.y), (best_x, front_y), VB_TIP_PEAK, VB_TIP_DUR)

    # ── Receive quality (clean / shank / error) ──────────────────────────────
    def _difficulty(self) -> float:
        b = self.ball
        dist = ((b.end[0] - b.start[0]) ** 2 + (b.end[1] - b.start[1]) ** 2) ** 0.5
        speed = dist / max(0.05, b.duration)
        return _clamp((speed - 180.0) / (430.0 - 180.0), 0.0, 1.0)

    def _team_diff(self, team: int) -> Dict[str, float]:
        # the OPPONENT (far team) plays at the chosen level; your team-mates always
        # play at full strength — so picking Easy never makes your own side flub.
        return self._opp if team == 1 else VB_DIFFICULTY['hard']

    def _dig_timing_factor(self, rem: float) -> float:
        # full quality inside the sweet spot, easing to TIME_FLOOR only for notably
        # early/late presses — timing nudges the pass, body position still leads.
        off = abs(rem - VB_DIG_IDEAL)
        if off <= VB_DIG_GOOD_TOL:
            return 1.0
        return _clamp(1.0 - (off - VB_DIG_GOOD_TOL) / VB_DIG_TOL, VB_DIG_TIME_FLOOR, 1.0)

    def _dig_feedback(self, rem: float, outcome: str, late: bool) -> None:
        # hybrid label: a clear EARLY/LATE when timing is the problem; otherwise the
        # honest pass quality (so good timing + bad position still reads as a shank).
        if late:
            label = "LATE!"
        elif rem - VB_DIG_IDEAL > VB_DIG_GOOD_TOL:
            label = "EARLY"
        elif rem - VB_DIG_IDEAL < -VB_DIG_GOOD_TOL:
            label = "LATE"
        elif outcome == 'clean':
            label = "PERFECT"
        else:
            label = "SHANK"
        self._hit_feedback = (label, 0.7)

    def _player_dig_quality(self, c: VBActor) -> float:
        spd = (self._vel[0] ** 2 + self._vel[1] ** 2) ** 0.5 / VB_TOP_SPEED
        offset = c.dist_to(*self.ball.end) / max(1.0, self._player_radius())
        q = (1.0 - VB_DIG_MOVE_PEN * _clamp(spd, 0.0, 1.0)
             - VB_DIG_OFFSET_PEN * _clamp(offset, 0.0, 1.0)
             - VB_DIG_DIFF_PEN * self._difficulty())
        return _clamp(q, 0.0, 1.0)

    def _ai_receive(self, c: VBActor) -> None:
        diff = self._difficulty()
        params = self._team_diff(c.team)        # your side full strength; opponent at level
        p_good = _lerp(params['dig_base'], params['dig_hard'], diff)
        err = params['error_frac']
        r = random.random()
        if r < p_good:
            outcome = 'clean'
        elif r < p_good + (1.0 - p_good) * err:
            outcome = 'error'
        else:
            outcome = 'shank'
        self._do_receive(c, outcome)

    def _shank_target(self, c: VBActor, team: int) -> Tuple[float, float]:
        if team == 0:
            y = _clamp(c.y + random.uniform(-30, 30), VB_NET_Y + 40, _COURT.bottom - 30)
        else:
            y = _clamp(c.y + random.uniform(-30, 30), _COURT.top + 30, VB_NET_Y - 40)
        side = -1.0 if c.x > _CX else 1.0
        x = _clamp(c.x + side * random.uniform(50, 110), _COURT.left + 20, _COURT.right - 20)
        return (x, y)

    def _rebound_target(self, c: VBActor) -> Tuple[float, float]:
        # a botched platform pops the ball a short, low, semi-random distance, still
        # on the receiving side — close enough that only a quick team-mate rescues it.
        team = c.team
        side = -1.0 if random.random() < 0.5 else 1.0
        dist = random.uniform(40, 95)
        x = _clamp(c.x + side * dist, _COURT.left + 12, _COURT.right - 12)
        if team == 0:
            y = _clamp(c.y + random.uniform(-20, 50), VB_NET_Y + 28, _COURT.bottom - 18)
        else:
            y = _clamp(c.y + random.uniform(-50, 20), _COURT.top + 18, VB_NET_Y - 28)
        return x, y

    def _rebound(self, c: VBActor) -> None:
        """A shanked receive (or a ball let to hit the body) caroms low off the
        platform — playable, but only a team-mate close + quick enough saves it."""
        team = c.team
        self._last_contact = c                       # the botcher can't chase their own pop
        self._touches += 1
        self._rally_touches += 1
        if self._touches >= 3 or self._rally_touches >= VB_RALLY_MAX:
            self.fx.emit_dust(c.x, c.y)              # a botched 3rd touch can't pop up -> down
            self._point(1 - team)
            return
        self._in_system = False
        c.set_pose(Pose.DIG)
        self.sfx.play('dig')
        self.fx.emit_dust(c.x, c.y)
        tx, ty = self._rebound_target(c)
        self.ball.launch((c.x, c.y), (tx, ty), *_REBOUND)
        self.ball.team = team
        mates = [a for a in self._team(team) if a is not c] or [c]
        self._await = ('receive', min(mates, key=lambda a: a.dist_to(tx, ty)))

    def _do_receive(self, c: VBActor, outcome: str) -> None:
        team = c.team
        self._last_contact = c                       # lock out an immediate second touch
        if outcome == 'error':
            self._rebound(c)                         # no longer an instant point — chase it!
            return
        self._touches += 1
        self._rally_touches += 1
        if c.is_player:
            self._tut_player_action('dig')
        if self._touches >= 3:                        # third contact must cross -> free ball over
            self._dump_over(c)
            return
        c.set_pose(Pose.DIG)
        self.sfx.play('dig')
        self.fx.emit_burst(c.x, c.y - 8, (180, 220, 255), 6, 90)
        if c.role == Role.SETTER:
            # the setter took the first ball -> a hitter sets out of system
            self._in_system = False
            em = self._emergency_setter(team)
            self.ball.launch((c.x, c.y), (em.x, em.y), 150, _hang(150))
            self.ball.team = team
            self._await = ('set', em)
            return
        setter = self._role(team, Role.SETTER)
        if outcome == 'clean':
            # 3v3: whoever's closest (within reach) takes ball 2, not always the setter.
            self._in_system = True
            spot = (float(_CX), float(VB_NET_Y + 54 if team == 0 else VB_NET_Y - 54))
            handler = self._second_handler(team, c, spot)
            self.ball.launch((c.x, c.y), spot, *_DIG)
            self.ball.team = team
            self._await = ('set', handler)
            return
        # shank — pops up off to the side; setter must chase, out of system
        self._in_system = False
        sx, sy = self._shank_target(c, team)
        self.ball.launch((c.x, c.y), (sx, sy), 150, _hang(150))
        self.ball.team = team
        self._await = ('set', setter)

    def _second_handler(self, team: int, digger: VBActor,
                        spot: Tuple[float, float]) -> VBActor:
        """Closest non-digger teammate that can reach the set spot in time."""
        cands = [a for a in self._team(team) if a is not digger]
        reach = VB_ACTOR_SPEED * _DIG[1] + VB_CONTACT_RADIUS
        able = [a for a in cands if a.dist_to(*spot) <= reach]
        pool = able or cands
        return min(pool, key=lambda a: a.dist_to(*spot))

    def _ball_to_side(self, team: int) -> bool:
        ey = self.ball.end[1]
        return ey > VB_NET_Y if team == 0 else ey < VB_NET_Y

    def _read_block(self, c: VBActor) -> bool:
        # the hitter reads a block committed in its lane and (with the level's reaction
        # skill) adjusts the swing. A block parked squarely ahead is easy to read; a
        # disguised seam/cross block is hard. The set's flight is the reaction window.
        bt = self._block_target
        if bt is None:
            return False
        squareness = _clamp(1.0 - abs(float(bt['lane_x']) - c.x) / (VB_BLOCK_REACH * 4.0), 0.0, 1.0)
        return random.random() < self._opp.get('read', 0.0) * (0.5 + 0.5 * squareness)

    def _contact_success(self, kind: str, c: VBActor, perfect: bool) -> None:
        team = c.team
        self._last_contact = c                       # lock out an immediate second touch
        self._touches += 1
        self._rally_touches += 1
        if kind == 'set' and self._touches >= 3:     # no setting a 4th touch -> free ball over
            self._dump_over(c)
            return
        self.sfx.play('set' if kind == 'set' else 'spike')
        if kind == 'set':
            c.set_pose(Pose.READY)
            hitter = self._smart_hitter(team, exclude=c)
            self.ball.launch((c.x, c.y), self._net_point(team, hitter.x), *_SET)
            self.ball.team = team
            self._await = ('spike', hitter)
            self._commit_block(hitter)
        else:  # AI spike
            c.set_pose(Pose.JUMP)
            err = self._team_diff(team)['attack_err']
            if not self._in_system:
                err *= VB_OOS_ERROR_MULT          # a scrambled swing misses more
            if self._rally_touches >= VB_RALLY_MAX or random.random() < err:
                self._ai_attack_error(team, c)    # unforced error / cap -> point, rally ends
                return
            if self._read_block(c):               # read a committed block -> tip over or place around it
                if random.random() < VB_AI_TIP_BIAS:
                    self._ai_tip(team, c)
                else:                             # place into a gap, powered down (lost the crush)
                    tx, ty = self._spike_target_ai(team, False)
                    self.ball.launch((c.x, c.y), (tx, ty), 72, 0.80)
                    self.fx.shake(2, 0.12)
            elif self._in_system and random.random() < self._opp['tip_chance']:
                self._ai_tip(team, c)          # mix in a tip into the open front
            elif self._in_system:
                self.ball.launch((c.x, c.y), self._spike_target_ai(team, perfect), *_SPIKE_AI)
                self.fx.shake(3, 0.14)
            else:                              # out of system -> a driven down-ball (still a hit)
                tx, ty = self._spike_target_ai(team, False)
                self.ball.launch((c.x, c.y), (tx, ty), 76, 0.88)
                self.fx.shake(2, 0.12)
            self.ball.team = team
            self._await = None
            self._crossing = True
            self._ai_setter_block(team)

    def _ai_setter_block(self, attacker: int) -> None:
        # at the spike strike the defending AI setter jumps IN PLACE — only if it
        # actually slid into a block at the net (else it gives way and defends).
        rsetter = self._role(1 - attacker, Role.SETTER)
        if rsetter.is_player or not self._at_net(rsetter):
            return
        rsetter.set_pose(Pose.BLOCK)
        self._ai_block_jump = VB_BLOCK_DURATION

    def _ai_attack_error(self, team: int, c: VBActor) -> None:
        # an unforced attacking error -> point to the other side (same award path as a
        # player fault). Net errors are the rare kind; most misses sail long/out.
        if random.random() < 0.20:                          # into the net (uncommon)
            ny = float(VB_NET_Y - 8 if team == 0 else VB_NET_Y + 8)
            self.ball.launch((c.x, c.y), (c.x, ny), 44, 0.5)
            msg = "Into the net!"
        else:                                               # long over the baseline
            cx = _clamp(c.x + random.uniform(-50, 50), _COURT.left, _COURT.right)
            base = _COURT.top - VB_OUT_LAND if team == 0 else _COURT.bottom + VB_OUT_LAND
            ox, oy = self._out_landing(cx, float(base), team)
            self.ball.launch((c.x, c.y), (ox, oy), 72, 0.8)
            msg = "Out!"
        self.ball.team = team
        self._await = None
        self._crossing = False
        self._serve_fault = True
        self._serve_outcome = ('fault', 1 - team, msg)

    # ── Aim-step (player spike) ──────────────────────────────────────────────
    def _set_quality(self, hitter: VBActor) -> float:
        # how good the set was to attack: in-system + met cleanly (planted, centred)
        base = 1.0 if self._in_system else 0.5
        if hitter.is_player:
            spd = (self._vel[0] ** 2 + self._vel[1] ** 2) ** 0.5 / VB_TOP_SPEED
            offset = hitter.dist_to(*self.ball.end) / max(1.0, self._player_radius())
            base -= 0.30 * _clamp(spd, 0.0, 1.0) + 0.30 * _clamp(offset, 0.0, 1.0)
        return _clamp(base, 0.0, 1.0)

    def _enter_aimstep(self, c: VBActor) -> None:
        self._ai_block_jump = 0.0       # the human's block is the aim-step's job, not _check_block
        _, _, y0, y1 = self._opp_half(c.team)
        sq = self._set_quality(c)
        # in-court reach narrows out of system; the wide-out margin is constant so a
        # decent set can always drift the reticle just past the sideline (-> out/red)
        half = (_COURT.width / 2.0) * _lerp(VB_OOS_RANGE, 1.0, sq) + VB_AIM_OUT
        block_x = None
        blocker = self._role(1 - c.team, Role.SETTER)   # block is where the setter actually got to
        if not blocker.is_player and self._at_net(blocker):
            block_x = blocker.x                          # only a blocker already at the net can stuff
            blocker.set_pose(Pose.BLOCK)                 # (it slid there legally via _commit_block; no snap)
        self._aimstep = {
            'contactor': c, 'power_cap': _lerp(VB_OOS_POWER_CAP, 1.0, sq),
            'sq': sq, 'xmin': _CX - half, 'xmax': _CX + half, 'block_x': block_x,
            'timer': VB_AIMSTEP_WINDOW, 'rx': float(_CX), 'ry': (y0 + y1) / 2.0,
            'meter': 0.0,
        }
        self._time_target = VB_AIMSTEP_SLOWMO
        c.set_pose(Pose.JUMP)
        self.ball.hold_at(c.x, c.y)
        self.ball.z = 30.0
        self._rally_touches += 1
        self._action = False

    def _update_aimstep(self, raw_dt: float) -> None:
        a = self._aimstep
        c = a['contactor']
        mx, my = self._move
        a['rx'] = _clamp(a['rx'] + mx * VB_RETICLE_SPEED * raw_dt,
                         a['xmin'], a['xmax'])
        if c.team == 0:
            a['ry'] = _clamp(a['ry'] + my * VB_RETICLE_SPEED * raw_dt,
                             _COURT.top - 30, VB_NET_Y - 2)
        else:
            a['ry'] = _clamp(a['ry'] + my * VB_RETICLE_SPEED * raw_dt,
                             VB_NET_Y + 2, _COURT.bottom + 30)
        a['meter'] += VB_SPIKE_METER_SPEED * raw_dt   # sweeps continuously up, then wraps
        if a['meter'] >= 1.0:
            a['meter'] -= 1.0
        a['timer'] -= raw_dt
        if self._tip_pressed:
            self._fire_tip()
        elif self._action:
            self._fire_spike()
        elif a['timer'] <= 0:
            self._fire_spike(timed_out=True)   # dithered -> a weak hit, not a free perfect

    def _hit_quality(self, meter: float) -> Tuple[str, float]:
        # centred sweet spot: the closer to the middle, the better; edges = weak
        if VB_SPIKE_SWEET_LO <= meter <= VB_SPIKE_SWEET_HI:
            return 'PERFECT', 1.0
        if meter < VB_SPIKE_SWEET_LO:
            frac = (VB_SPIKE_SWEET_LO - meter) / max(1e-6, VB_SPIKE_SWEET_LO)
            return 'EARLY', _lerp(0.85, VB_SPIKE_MIN_POWER, frac)
        frac = (meter - VB_SPIKE_SWEET_HI) / max(1e-6, 1.0 - VB_SPIKE_SWEET_HI)
        return 'LATE', _lerp(0.85, VB_SPIKE_MIN_POWER, frac)

    def _spike_zone(self, target: Tuple[float, float], team: int) -> str:
        tx, ty = target
        if team == 0:
            if ty >= VB_NET_Y - 6:
                return 'net'
            if ty < _COURT.top:
                return 'out'
        else:
            if ty <= VB_NET_Y + 6:
                return 'net'
            if ty > _COURT.bottom:
                return 'out'
        if tx < _COURT.left or tx > _COURT.right:
            return 'out'
        return 'in'

    def _out_landing(self, rx: float, ry: float, team: int) -> Tuple[float, float]:
        # push an out ball clearly past whichever line it missed (lands in the run-off)
        ox, oy = rx, ry
        if rx < _COURT.left:
            ox = _COURT.left - VB_OUT_LAND
        elif rx > _COURT.right:
            ox = _COURT.right + VB_OUT_LAND
        if team == 0 and ry < _COURT.top:
            oy = _COURT.top - VB_OUT_LAND
        elif team == 1 and ry > _COURT.bottom:
            oy = _COURT.bottom + VB_OUT_LAND
        return (_clamp(ox, _HALL.left + 6, _HALL.right - 6),
                _clamp(oy, _HALL.top + 4, _HALL.bottom - 4))

    def _in_landing(self, tx: float, ty: float, team: int) -> Tuple[float, float]:
        # keep an in ball a touch inside the lines so scatter can't make it look out
        ix = _clamp(tx, _COURT.left + 6, _COURT.right - 6)
        if team == 0:
            iy = _clamp(ty, _COURT.top + 6, VB_NET_Y - 8)
        else:
            iy = _clamp(ty, VB_NET_Y + 8, _COURT.bottom - 6)
        return (ix, iy)

    def _fire_spike(self, timed_out: bool = False) -> None:
        a = self._aimstep
        self._aimstep = None
        self._time_target = 1.0
        c = a['contactor']
        if timed_out:                               # ran the clock down -> a weak swing
            label, power = 'LATE', VB_SPIKE_MIN_POWER
        else:
            label, power = self._hit_quality(float(a['meter']))
        power = min(power, float(a['power_cap']))
        self._hit_feedback = (label, 0.7)
        zone = self._spike_zone((a['rx'], a['ry']), c.team)
        scatter = 6.0 + 18.0 * (1.0 - power)
        tx = a['rx'] + random.uniform(-scatter, scatter)
        ty = a['ry'] + random.uniform(-scatter, scatter)
        self.ball.team = c.team
        c.set_pose(Pose.JUMP)
        self.fx.emit_burst(c.x, c.y - 24, (255, 240, 150), 14, 210)
        if label == 'PERFECT':
            self.fx.emit_burst(c.x, c.y - 24, (255, 255, 215), 12, 300)
        self.fx.shake(6.0 if label == 'PERFECT' else 3.0, 0.20)
        self.sfx.play('perfect' if label == 'PERFECT' else 'spike')
        over = False
        if zone == 'net':
            self.ball.launch((c.x, c.y), (tx, float(VB_NET_Y)), 60, 0.55)
            self._crossing = False
            self._serve_fault = True
            self._serve_outcome = ('fault', 1 - c.team, "Into the net!")
        elif zone == 'out':
            ox, oy = self._out_landing(a['rx'], a['ry'], c.team)   # land clearly past the line
            self.ball.launch((c.x, c.y), (ox, oy), 80, 0.7)
            self._crossing = False
            self._serve_fault = True
            self._serve_outcome = ('fault', 1 - c.team, "Out!")
        elif self._spike_blocked(a, c):
            pass                          # stuffed / tooled off the block
        else:
            peak = 82.0 - 46.0 * power
            dur = 0.84 - 0.46 * power     # a perfect hit is flat & fast (hard to dig)
            tx, ty = self._in_landing(tx, ty, c.team)         # keep an "in" ball inside the lines
            self.ball.launch((c.x, c.y), (tx, ty), peak, dur)
            self._await = None
            self._crossing = True
            over = True
        self._action = False
        if c.is_player:
            if self._tut_is('spike'):
                # tutorial: the hit always plays out; only a PERFECT one over passes,
                # otherwise watch it land then redo
                self._tut_player_action('spike', ok=(label == 'PERFECT' and over))
            else:
                self._tut_player_action('spike')

    def _spike_blocked(self, a: Dict[str, object], c: VBActor) -> bool:
        # a hard spike into the blocker's lane -> mostly stuffed, sometimes tooled out
        bx = a.get('block_x')
        if bx is None or abs(a['rx'] - float(bx)) > VB_BLOCK_REACH:
            return False
        self.fx.emit_burst(float(bx), float(VB_NET_Y), (255, 240, 150), 12, 220)
        start = (float(bx), float(VB_NET_Y))
        attacker = c.team
        offset = abs(a['rx'] - float(bx))
        if offset <= VB_BLOCK_REACH * VB_BLOCK_SQUARE:    # same stuff/tool/soft/rebound split as a defence
            stuff, tool, soft = VB_BLOCK_SQ_STUFF, VB_BLOCK_SQ_TOOL, VB_BLOCK_SQ_SOFT
        else:
            stuff, tool, soft = VB_BLOCK_GL_STUFF, VB_BLOCK_GL_TOOL, VB_BLOCK_GL_SOFT
        r = random.random()
        if r < stuff:                                     # stuffed straight down -> their point
            self.fx.shake(7, 0.26)
            px = _clamp(c.x, _COURT.left + 16, _COURT.right - 16)
            py = float(VB_NET_Y + 40 if c.team == 0 else VB_NET_Y - 40)
            self._block_send(1 - c.team, start, (px, py), 30, 0.42, "Stuffed!")
        elif r < stuff + tool:                            # tooled off the block, out -> your point
            self.fx.shake(5, 0.20)
            self._tool_out(attacker, start, a['ry'])
        elif r < stuff + tool + soft:                     # soft block -> drops on their side, playable
            self._block_outcome(1 - attacker, deep=False)
        else:                                             # rebounds back to you -> swing again
            self._block_outcome(attacker, deep=True)
        return True

    def _fire_tip(self) -> None:
        a = self._aimstep
        self._aimstep = None
        self._time_target = 1.0
        c = a['contactor']
        tx = _clamp(a['rx'], _COURT.left + 14, _COURT.right - 14)
        ty = (VB_NET_Y - VB_TIP_DROP) if c.team == 0 else (VB_NET_Y + VB_TIP_DROP)
        self.ball.team = c.team
        c.set_pose(Pose.JUMP)
        self.fx.emit_burst(c.x, c.y - 22, (200, 230, 255), 8, 120)
        self.sfx.play('tip')
        self.ball.launch((c.x, c.y), (tx, ty), VB_TIP_PEAK, VB_TIP_DUR)
        self._await = None
        self._crossing = True
        self._action = False
        self._set_pressed = False
        self._tip_pressed = False

    # ── Set-step (player setter: choose side / dump, in slow-mo) ──────────────
    def _enter_setstep(self, c: VBActor) -> None:
        self._time_target = VB_AIMSTEP_SLOWMO
        self.ball.hold_at(c.x, c.y)
        self.ball.z = 28.0
        # in the set rep both teammates are up as hitters, so you can pick either side
        attackers = ([a for a in self._team(c.team) if a is not c]
                     if self._tut_is('set') else self._attackers(c.team, c))
        self._setstep = {'contactor': c, 'attackers': attackers,
                         'choice': self._smart_hitter(c.team, c),
                         'timer': VB_AIMSTEP_WINDOW}
        c.set_pose(Pose.READY)
        self._rally_touches += 1
        self._action = False
        self._set_pressed = False

    def _update_setstep(self, raw_dt: float) -> None:
        s = self._setstep
        atk = sorted(s['attackers'], key=lambda a: a.x)
        mx = self._move[0]
        if len(atk) >= 2:
            if mx <= -0.3:
                s['choice'] = atk[0]
            elif mx >= 0.3:
                s['choice'] = atk[-1]
        s['timer'] -= raw_dt
        if self._tip_pressed:                       # C: dump over instead of setting
            self._setter_dump()
        elif self._set_pressed or s['timer'] <= 0:  # X / timeout: set to the chosen hitter
            self._confirm_set()

    def _confirm_set(self) -> None:
        s = self._setstep
        self._setstep = None
        self._time_target = 1.0
        setter, hitter = s['contactor'], s['choice']
        self.ball.launch((setter.x, setter.y), self._net_point(hitter.team, hitter.x), *_SET)
        self.ball.team = hitter.team
        self._await = ('spike', hitter)
        self._commit_block(hitter)
        self.sfx.play('set')
        self._action = False
        self._set_pressed = False
        if setter.is_player:
            self._tut_player_action('set')      # complete the rep here so the set plays out

    def _dump_over(self, c: VBActor) -> None:
        # a soft drop just over the net on the opponent's side (tip / setter dump)
        tx = _clamp(c.x, _COURT.left + 14, _COURT.right - 14)
        ty = (VB_NET_Y - VB_TIP_DROP) if c.team == 0 else (VB_NET_Y + VB_TIP_DROP)
        self.ball.team = c.team
        c.set_pose(Pose.JUMP)
        self.fx.emit_burst(c.x, c.y - 20, (200, 230, 255), 8, 120)
        self.sfx.play('tip')
        self.ball.launch((c.x, c.y), (tx, ty), VB_TIP_PEAK, VB_TIP_DUR)
        self._await = None
        self._crossing = True

    def _setter_dump(self) -> None:
        c = self._setstep['contactor']
        self._setstep = None
        self._time_target = 1.0
        self._dump_over(c)
        self._action = False
        self._set_pressed = False
        self._tip_pressed = False

    def _quick_dump(self, c: VBActor) -> None:
        # C on the 2nd ball: dump straight over without entering the set-step
        self._rally_touches += 1
        self._dump_over(c)
        self._action = False
        self._set_pressed = False
        self._tip_pressed = False

    # ── Block-step (player front-row setter: slow-mo slide + jump) ────────────
    def _start_block(self) -> None:
        p = self._player()
        p.set_pose(Pose.BLOCK)
        p.facing = 'up'                  # square up to the net (block from where you stand — no snap)
        dur = VB_TUT_BLOCK_DURATION if self._tut_is('block') else VB_BLOCK_DURATION
        self._block_jump = dur
        self._block_cd = dur + VB_BLOCK_COOLDOWN
        self.fx.emit_burst(p.x, p.y - 24, (255, 240, 150), 8, 150)
        self.sfx.play('block')
        # note: the tutorial only counts a block that actually stuffs the ball
        # (see _check_block) — jumping alone, e.g. too early, doesn't pass

    def _can_block(self) -> bool:
        # a free jump: near the net, ball on the opponent's side / incoming
        p = self._player()
        return (self._block_cd <= 0 and self._block_jump <= 0
                and abs(p.y - VB_NET_Y) < VB_BLOCK_ELIGIBLE   # must actually be at the net
                and self.ball.team == 1 and self.ball.in_flight)

    # ── Resolve ──────────────────────────────────────────────────────────────
    def _resolve(self, dt: float) -> None:
        b = self.ball
        if self._serve_fault:
            if not b.in_flight:
                _, winner, msg = self._serve_outcome
                self.fx.emit_dust(b.end[0], b.end[1])
                self._point(winner)
                self._banner = msg
                self._serve_fault = False
            return
        if self._crossing:
            # a raised blocker stuffs the ball anywhere in a band around the net (not just
            # the single crossing frame) — so timing is forgiving and reads accurately
            if (b.in_flight and abs(b.y - VB_NET_Y) <= VB_BLOCK_Y_BAND
                    and self._check_block()):
                return
            crossed = (self._prev_y - VB_NET_Y) * (b.y - VB_NET_Y) <= 0
            if b.in_flight and crossed and abs(b.y - VB_NET_Y) <= 80:
                self._on_cross_net()
            elif not b.in_flight:
                self._on_cross_net()
            return
        if not self._await:
            return
        kind = self._await[0]
        c = self._current_contactor()
        # If the tasked AI clearly can't reach the ball, commit the nearest mate who can
        # (stable: only fires when the tasked one is out of range, so it doesn't thrash).
        if (c is not None and not c.is_player and b.in_flight
                and kind in ('receive', 'set', 'spike')):
            creach = VB_ACTOR_SPEED * max(0.05, b.remaining()) + VB_CONTACT_RADIUS
            if c.dist_to(*b.end) > creach:
                cands = [a for a in self._team(c.team)
                         if not a.is_player and a is not self._last_contact]
                if cands:
                    cand = min(cands, key=lambda a: a.dist_to(*b.end))
                    if cand is not c and cand.dist_to(*b.end) + 1.0 < c.dist_to(*b.end):
                        self._await = (kind, cand)
                        c = cand
        radius = self._player_radius()                 # identical contact reach for you and the AI
        in_range = c.dist_to(*b.end) <= radius
        if c.is_player:
            if kind == 'spike':
                if self._action and b.in_flight and b.remaining() <= VB_TIMING_WINDOW and in_range:
                    self._enter_aimstep(c)
                elif not b.in_flight:
                    self.fx.emit_dust(b.end[0], b.end[1])
                    self._point(1 - c.team)
            elif kind == 'set':
                if b.in_flight and b.remaining() <= VB_TIMING_WINDOW and in_range:
                    third = self._touches >= 2              # this contact would be the 3rd
                    if self._action:                        # Z: attack on 2 (at net)...
                        if self._at_net(c):
                            self._enter_aimstep(c)
                        elif third:                         # ...can't set a 4th -> pass it over
                            self._quick_dump(c)
                        else:
                            self._enter_setstep(c)
                    elif self._set_pressed:                 # X: set to a hitter (or forced over)
                        self._quick_dump(c) if third else self._enter_setstep(c)
                    elif self._tip_pressed:                 # C: dump over
                        self._quick_dump(c)
                elif not b.in_flight:
                    self.fx.emit_dust(b.end[0], b.end[1])
                    self._point(1 - c.team)
            else:  # receive (dig) — timing AND body position both shape the pass
                if b.in_flight:
                    self._dig_grace = VB_DIG_GRACE          # arm the after-landing window
                    rem = b.remaining()
                    if self._action and in_range and rem <= VB_DIG_EARLY_EDGE:
                        q = self._player_dig_quality(c) * self._dig_timing_factor(rem)
                        outcome = ('clean' if q >= VB_DIG_CLEAN
                                   else 'shank' if q >= VB_DIG_SHANK else 'error')
                        self._dig_feedback(rem, outcome, late=False)
                        self._do_receive(c, outcome)
                elif self._dig_grace > 0:                   # ball down — brief late window
                    if self._action and in_range:
                        q = self._player_dig_quality(c) * VB_DIG_TIME_FLOOR
                        outcome = 'shank' if q >= VB_DIG_SHANK else 'error'
                        self._dig_feedback(0.0, outcome, late=True)
                        self._do_receive(c, outcome)
                        self._dig_grace = 0.0
                    else:
                        self._dig_grace -= dt
                else:                                       # ball reached the floor
                    if in_range:                            # you were under it -> it bounces low off you
                        self._rebound(c)
                    else:                                   # it dropped in open court
                        if self._action:                    # swung at it, just too late
                            self._hit_feedback = ("LATE!", 0.8)
                        self.fx.emit_dust(b.end[0], b.end[1])
                        self._point(1 - c.team)
        elif self._tut is not None:
            if (self._tut_is('set') and kind == 'spike' and b.in_flight
                    and b.remaining() <= 0.05 and in_range):
                self._contact_success(kind, c, True)   # the hitter you set finishes the swing
            elif not b.in_flight:               # otherwise the AI doesn't play; ball just drops
                self.fx.emit_dust(b.end[0], b.end[1])
                self._point(1 - c.team)
        else:
            if b.in_flight and b.remaining() <= 0.05:
                actor = c if in_range else None
                if actor is None:                    # tasked one isn't there — does a mate cover?
                    mates = [a for a in self._team(c.team)
                             if not a.is_player and a is not self._last_contact]
                    mate = min(mates, key=lambda a: a.dist_to(*b.end)) if mates else None
                    if mate is not None and mate.dist_to(*b.end) <= VB_CONTACT_RADIUS:
                        actor = mate
                if actor is not None:
                    if kind == 'receive':
                        self._ai_receive(actor)
                    else:
                        self._contact_success(kind, actor, True)
            elif not b.in_flight:
                self.fx.emit_dust(b.end[0], b.end[1])
                self._point(1 - c.team)

    # ── Scoring / rotation ───────────────────────────────────────────────────
    def _point(self, winner: int) -> None:
        if self._tut is not None:        # tutorial: a dropped ball just means "try again"
            self._tut_miss()
            return
        self.score[winner] += 1
        self._last_winner = winner
        self._await = None
        self._crossing = False
        self._aimstep = None
        self._setstep = None
        self._block_jump = 0.0
        self._ai_block_jump = 0.0
        self._block_target = None
        self._time_target = 1.0
        self.phase = Phase.POINT
        self._banner = "Your point!" if winner == 0 else "Their point"
        self._timer = 0.9
        self.fx.emit_burst(self.ball.end[0], self.ball.end[1], (250, 230, 120), 10, 140)
        self.sfx.play('whistle')                        # the unobtrusive synth whistle per point
        if winner == 0:
            self.sfx.play('cheer')
        for a in self._team(winner):
            a.set_pose(Pose.CELEBRATE)

    def _rotate(self, team_list: List[VBActor]) -> None:
        for a in team_list:
            a.role = _CW[a.role]
            a.home = _HOME[a.team][a.role]

    def _after_point(self) -> None:
        if max(self.score) >= VB_SCORE_TO_WIN and abs(self.score[0] - self.score[1]) >= 2:
            self.phase = Phase.OVER
            self._banner = "YOU WIN!" if self.score[0] > self.score[1] else "You lost"
            return
        if self._last_winner != self.serving:          # side-out -> rotate
            self.serving = self._last_winner
            self._rotate(self.near)
            self._rotate(self.far)
        self._start_serve()

    # ── Tutorial (instruct -> Z to start -> try -> pass/fail) ────────────────
    def _tut_setup(self, step: int) -> None:
        # land on the instruction screen; the exercise waits for Z (_tut_begin)
        self._tut = {'step': step, 'phase': 'intro', 't': 0.0}
        self._reset_for_tut()
        self._tut_stage(step)

    def _reset_for_tut(self) -> None:
        self._await = None
        self._crossing = False
        self._aimstep = None
        self._setstep = None
        self._serve_fault = False
        self._serve_outcome = None
        self._block_jump = self._block_cd = self._ai_block_jump = 0.0
        self._block_target = None
        self._in_system = True
        self._time_target = 1.0
        for a in self.near + self.far:
            a.x, a.y = a.home
            a.set_pose(Pose.READY)
            a.z = 0.0

    def _tut_stage(self, step: int) -> None:
        # position the player and hold the ball ready — nothing flies until Z
        p = self._player()
        mech = _TUT_STEPS[step][0]
        if mech == 'serve':
            self.serving = 0
            self.phase = Phase.SERVE
            self._serve_meter, self._serve_dir, self._serve_stage = 0.0, 1, 'power'
            self._serve_lat, self._serve_lat_dir, self._serve_power = 0.0, 1, 0.5
            srv = self._server()
            srv.x, srv.y = _SERVE_POS[0]
            self.ball.hold_at(*_SERVE_POS[0])
        elif mech == 'dig':
            # start a touch back: an opponent serve from across the net floats over to you
            self.phase = Phase.RALLY
            p.x, p.y = float(_CX), float(_COURT.bottom - 70)
            srv = self._role(1, Role.HITTER_R)
            srv.x, srv.y = _SERVE_POS[1]
            srv.set_pose(Pose.READY)
            self.ball.hold_at(*_SERVE_POS[1])
        elif mech == 'set':
            # you set at the net; your two hitters are up on the wings, ready to attack
            self.phase = Phase.RALLY
            p.x, p.y = float(_CX), float(VB_NET_Y + 58)        # setter position, at the net
            hl, st = self._role(0, Role.HITTER_L), self._role(0, Role.SETTER)
            hl.x, hl.y = float(_CX - 74), float(VB_NET_Y + 46)  # hitters up on the wings
            st.x, st.y = float(_CX + 74), float(VB_NET_Y + 46)
            self.ball.hold_at(float(_COURT.right - 46), float(_COURT.bottom - 44))
        elif mech == 'spike':
            # left-side hitter: start at your base, run the approach as the setter sets you
            self.phase = Phase.RALLY
            p.x, p.y = float(_CX - 70), float(_COURT.bottom - 64)   # your base (back-left)
            st = self._role(0, Role.SETTER)
            st.x, st.y = float(_CX + 16), float(VB_NET_Y + 48)   # setter at the net, ready to set
            st.set_pose(Pose.READY)
            hl = self._role(0, Role.HITTER_L)
            hl.x, hl.y = float(_CX + 70), float(_COURT.bottom - 60)   # other hitter at base
            self.ball.hold_at(st.x, float(st.y - 6))
        else:  # block — read the pass to the setter, then the set to the hitter
            self.phase = Phase.RALLY
            p.x, p.y = float(_CX), float(VB_NET_Y + 22)
            nst = self._role(0, Role.SETTER)                   # your mates drop into back-row D
            nst.x, nst.y = float(_CX + 72), float(VB_NET_Y + 128)
            nhl = self._role(0, Role.HITTER_L)
            nhl.x, nhl.y = float(_CX - 72), float(VB_NET_Y + 128)
            setter = self._role(1, Role.SETTER)
            setter.x, setter.y = float(_CX - 60), float(VB_NET_Y - 48)   # clear of the hit lane
            setter.set_pose(Pose.READY)
            atk = self._role(1, Role.HITTER_L)
            atk.x, atk.y = float(_CX), float(VB_NET_Y - 120)    # at their base; runs the approach
            atk.set_pose(Pose.READY)
            self.ball.hold_at(float(_CX + 50), float(VB_NET_Y - 150))
        self._separate()        # guarantee no staged formation overlaps the player

    def _tut_begin(self) -> None:
        # Z pressed on the instruction screen -> feed the ball, exercise is live
        t = self._tut
        t['phase'] = 'active'
        p = self._player()
        mech = _TUT_STEPS[t['step']][0]
        if mech == 'serve':
            return                                  # serve is player-initiated (the meter)
        if mech == 'dig':
            # a serve floats over the net from the far baseline so you can read it
            self.ball.launch(_SERVE_POS[1], (p.x, p.y), 178, 1.6)
            self.ball.team = 0
            self._await = ('receive', p)
        elif mech == 'set':
            # a dig floats up from the back court to you at the net
            self.ball.launch((float(_COURT.right - 46), float(_COURT.bottom - 44)),
                             (p.x, p.y), 178, 1.45)
            self.ball.team = 0
            self._await = ('set', p)
        elif mech == 'spike':
            st = self._role(0, Role.SETTER)
            st.set_pose(Pose.DIG)                       # a high outside set; run up and swing
            self.ball.launch((st.x, float(st.y - 6)), self._net_point(0, p.x), 150, 1.35)
            self.ball.team = 0
            self._await = ('spike', p)
        else:  # block — a pass floats to the setter; _tut_block_lead runs the chain
            t['bseq'] = 0
            setter = self._role(1, Role.SETTER)
            self.ball.launch((float(_CX + 50), float(VB_NET_Y - 150)),
                             (setter.x, setter.y - 6), 150, 1.35)
            self.ball.team = 1
            self._crossing = False

    def _tut_block_lead(self, dt: float) -> None:
        # scripted read for the block rep: pass -> set to the net -> hitter approaches,
        # jumps and drives the ball down at you
        t = self._tut
        atk = self._role(1, Role.HITTER_L)
        self.ball.update(dt)
        if t['bseq'] == 1 and self.ball.in_flight:
            # close to the net while the set hangs, so the swing reads as an approach
            tx, ty = t['atk_to']
            atk.x += (tx - atk.x) * min(1.0, 6.0 * dt)
            atk.y += (ty - atk.y) * min(1.0, 6.0 * dt)
            atk.set_pose(Pose.RUN)
            return
        if self.ball.in_flight:
            return
        if t['bseq'] == 0:
            setter = self._role(1, Role.SETTER)
            setter.set_pose(Pose.DIG)
            t['atk_to'] = (atk.x, float(VB_NET_Y - 40))             # approach point at the net
            self.ball.launch((setter.x, setter.y), (atk.x, float(VB_NET_Y - 46)), 118, 1.0)
            self.ball.team = 1
            t['bseq'] = 1
        else:  # hitter is at the net -> jump and drive it down across the net at you
            atk.x, atk.y = t['atk_to']
            atk.set_pose(Pose.JUMP)
            atk.z = 26.0
            start = (atk.x, float(VB_NET_Y - 58))      # high contact -> the ball has to travel
            self.ball.launch(start, (float(_CX), float(VB_NET_Y + 85)), 26, 1.2)
            self.ball.team = 1
            self._crossing = True
            t['bseq'] = 2

    def _tut_is(self, mech: str) -> bool:
        return self._tut is not None and _TUT_STEPS[self._tut['step']][0] == mech

    def _tut_player_action(self, mech: str, ok: bool = True) -> None:
        t = self._tut
        if t is None or t['phase'] != 'active' or _TUT_STEPS[t['step']][0] != mech:
            return
        # let the ball/players finish the action (so you see it land), then pass or redo
        t['phase'], t['t'], t['ok'] = 'resolve', VB_TUT_RESOLVE, ok

    def _tut_miss(self) -> None:
        t = self._tut
        if t is not None and t['phase'] == 'active':
            t['phase'], t['t'] = 'fail', VB_TUT_FAIL   # show a message, brief pause, then retry

    def _tut_meta(self, raw_dt: float) -> bool:
        """Drive the intro/success/fail phases. Returns True while the exercise is
        paused (freeze normal play); False during 'active' (let it run)."""
        t = self._tut
        ph = t['phase']
        if ph == 'intro':
            if self._action:
                self._tut_begin()
            return True
        if ph == 'resolve':
            # play runs so the ball arcs and players animate; end once it settles, then
            # pass ("Nice!") or redo ("going again") depending on how the rep went
            t['t'] -= raw_dt
            landed = not self.ball.in_flight
            if t['t'] <= 0 or (landed and t['t'] < VB_TUT_RESOLVE - 0.3):
                if t.get('ok', True):
                    t['phase'], t['t'] = 'success', VB_TUT_SUCCESS
                else:
                    t['phase'], t['t'] = 'fail', VB_TUT_FAIL
            return False
        if ph == 'success':
            t['t'] -= raw_dt
            if t['t'] <= 0:
                if t['step'] + 1 >= len(_TUT_STEPS):
                    self._banner = "Tutorial complete!"
                    self.phase = Phase.OVER
                    self._tut = None
                else:
                    self._tut_setup(t['step'] + 1)
            return True
        if ph == 'fail':
            t['t'] -= raw_dt
            if t['t'] <= 0:
                t['phase'] = 'intro'
                self._reset_for_tut()
                self._tut_stage(t['step'])
            return True
        # 'active': during the block read the lead drives the ball, but YOU may move and
        # jump freely — so an early jump can mistime and miss, which is how you learn it
        if _TUT_STEPS[t['step']][0] == 'block' and t.get('bseq', 2) < 2:
            self._update_timers(raw_dt)
            self._move_player(raw_dt)
            if self._action and self._can_block():
                self._start_block()
            self._tut_block_lead(raw_dt)
            return True
        return False                              # 'active' -> normal gameplay

    # ── Update ───────────────────────────────────────────────────────────────
    def _approach(self, v: float, target: float, dt: float) -> float:
        if target == 0.0 or (v != 0.0 and (target > 0) != (v > 0)) or abs(target) < abs(v):
            rate = VB_DECEL
        else:
            rate = VB_ACCEL
        if v < target:
            return min(target, v + rate * dt)
        return max(target, v - rate * dt)

    def _update_timers(self, dt: float) -> None:
        if self._block_jump > 0:
            self._block_jump -= dt
        if self._block_cd > 0:
            self._block_cd -= dt
        if self._ai_block_jump > 0:
            self._ai_block_jump -= dt

    def _move_player(self, dt: float) -> None:
        if self.phase not in (Phase.SERVE, Phase.RALLY):
            return
        p = self._player()
        if self.phase == Phase.SERVE and p is self._server():
            p.x, p.y = _SERVE_POS[self.serving]
            return
        ty_target = self._move[1] * VB_TOP_SPEED
        if ty_target > 0:                       # +y = away from the net (near team) -> backpedal is slow
            ty_target *= VB_BACKPEDAL_FACTOR
        self._vel[0] = self._approach(self._vel[0], self._move[0] * VB_TOP_SPEED, dt)
        self._vel[1] = self._approach(self._vel[1], ty_target, dt)
        if p.pose in (Pose.READY, Pose.RUN):
            spd = abs(self._vel[0]) + abs(self._vel[1])
            p.set_pose(Pose.RUN if spd > 24 else Pose.READY)
        fx, fy = self._face
        if abs(fx) >= abs(fy):
            p.facing = 'right' if fx > 0 else 'left'
        else:
            p.facing = 'down' if fy > 0 else 'up'
        p.x = _clamp(p.x + self._vel[0] * dt, _X_MIN, _X_MAX)
        p.y = _clamp(p.y + self._vel[1] * dt, _NEAR_MIN_Y, _NEAR_MAX_Y)

    def _defense_base(self, d_team: int, hitter: VBActor) -> List[Tuple[float, float]]:
        # base back-court defence: one in the line lane, one in the cross lane, at a
        # dig depth that's close enough to still run in for a short ball / tip.
        dig_y = float(VB_NET_Y + 138 if d_team == 0 else VB_NET_Y - 138)   # start deep (backpedal is slow)
        line_x = _clamp(hitter.x, _COURT.left + 34, _COURT.right - 34)
        cross_x = _clamp(2 * _CX - hitter.x, _COURT.left + 34, _COURT.right - 34)
        if abs(line_x - cross_x) < 80:           # centred attack: split the seam, don't stack
            line_x = _clamp(_CX - 62, _COURT.left + 34, _COURT.right - 34)
            cross_x = _clamp(_CX + 62, _COURT.left + 34, _COURT.right - 34)
        return [(line_x, dig_y), (cross_x, dig_y)]

    def _defend_zone(self, a: VBActor, recv: int) -> Tuple[float, float]:
        # off-ball defence: the setter releases to the net to set ball 2; the non-digging
        # back holds its OWN wide sideline lane (covering the gap the digger leaves),
        # rather than collapsing onto the ball with the digger.
        if a.role == Role.SETTER:
            side = -1.0 if self.ball.end[0] > _CX else 1.0
            return (_clamp(_CX + side * 46, _COURT.left + 18, _COURT.right - 18),
                    float(VB_NET_Y + 48 if recv == 0 else VB_NET_Y - 48))
        wing = 1.0 if a.home[0] >= _CX else -1.0
        return (_clamp(_CX + wing * 104, _COURT.left + 30, _COURT.right - 30),
                float(VB_NET_Y + 138 if recv == 0 else VB_NET_Y - 138))   # start deep (backpedal is slow)

    def _attack_wing(self, a: VBActor) -> Tuple[float, float]:
        # a hitter climbs onto its pin near the net, so the setter can swing the ball wide
        wing = 1.0 if a.home[0] >= _CX else -1.0
        return (_clamp(_CX + wing * 96, _COURT.left + 24, _COURT.right - 24),
                float(VB_NET_Y + 44 if a.team == 0 else VB_NET_Y - 44))

    def _crossing_receiver(self, recv_team: int) -> VBActor:
        # pick the digger once per flight (keyed on the ball's arc) so two players
        # don't keep swapping who chases the ball as it comes over
        key = (self.ball.start, self.ball.end)
        if self._recv_cache is None or self._recv_cache[0] != key:
            self._recv_cache = (key, self._receiver(recv_team))
        return self._recv_cache[1]

    def _ball_player(self) -> Optional[VBActor]:
        # the AI team-mate committed to the next contact (receive / set / spike).
        # _separate exempts it from the human's shove so crowding your digger can't
        # push it off the ball (which left nobody to play it).
        if self._await and self._await[0] in ('receive', 'set', 'spike'):
            c = self._await[1]
            if c is None and self._await[0] == 'receive':
                c = self._nearest_defender(self.ball.team, self.ball.end)
            return c if (c is not None and not c.is_player) else None
        if self._crossing and self.ball.in_flight:
            c = self._crossing_receiver(1 - self.ball.team)
            return c if not c.is_player else None
        return None

    def _separate(self, dt: Optional[float] = None) -> None:
        # keep teammates from stacking: the AI gives way, but only by a legal step per
        # frame (it drifts apart at movement speed — never an instant un-stacking teleport).
        # dt=None is a one-shot full separation, used only for initial staging (setup).
        min_d = 42.0
        cap = VB_ACTOR_SPEED * dt if dt is not None else min_d
        protected = self._ball_player()
        for team in (self.near, self.far):
            for i, a in enumerate(team):
                for b in team[i + 1:]:
                    # don't let the human shove the team-mate playing the ball off it
                    if protected is not None and (
                            (a.is_player and b is protected)
                            or (b.is_player and a is protected)):
                        continue
                    dx, dy = b.x - a.x, b.y - a.y
                    d2 = dx * dx + dy * dy
                    if d2 >= min_d * min_d or d2 < 1e-6:
                        continue
                    d = d2 ** 0.5
                    shove = min(min_d - d, cap)         # at most one legal step of give-way
                    ux, uy = dx / d, dy / d
                    if a.is_player:
                        b.x, b.y = b.x + ux * shove, b.y + uy * shove
                    elif b.is_player:
                        a.x, a.y = a.x - ux * shove, a.y - uy * shove
                    else:
                        a.x, a.y = a.x - ux * shove * 0.5, a.y - uy * shove * 0.5
                        b.x, b.y = b.x + ux * shove * 0.5, b.y + uy * shove * 0.5
            for a in team:
                if a.is_player:
                    continue
                a.x = _clamp(a.x, _X_MIN, _X_MAX)
                a.y = (_clamp(a.y, VB_NET_Y + 10, _NEAR_MAX_Y) if a.team == 0
                       else _clamp(a.y, _FAR_MIN_Y, VB_NET_Y - 10))

    def _ai_step(self, a: VBActor, tx: float, ty: float, dt: float) -> None:
        # Same movement model as the player: ramp to top speed via accel/decel, with
        # backpedalling (away from the net) slowed identically. The target velocity is
        # capped by braking distance so the actor decelerates onto its spot, no overshoot.
        dx, dy = tx - a.x, ty - a.y
        d = (dx * dx + dy * dy) ** 0.5
        if d <= 1.0:
            a.x, a.y, a.vx, a.vy = tx, ty, 0.0, 0.0
            return
        vmax = min(VB_TOP_SPEED, (2.0 * VB_DECEL * d) ** 0.5)
        tvx, tvy = dx / d * vmax, dy / d * vmax
        if (tvy > 0 if a.team == 0 else tvy < 0):       # backpedalling is slow, same as you
            tvy *= VB_BACKPEDAL_FACTOR
        a.vx = self._approach(a.vx, tvx, dt)
        a.vy = self._approach(a.vy, tvy, dt)
        a.x += a.vx * dt
        a.y += a.vy * dt

    def _move_ai(self, dt: float) -> None:
        # Human-like reaction: when a fresh ball comes over the net, defenders hold
        # their read (base/zone) for a beat before breaking for the exact landing —
        # so a hard or well-placed ball into open court drops before they cover it.
        self._react_t = max(0.0, self._react_t - dt)
        if self._crossing and not self._was_crossing:
            self._react_t = self._team_diff(1 - self.ball.team).get('reaction', 0.25)
        self._was_crossing = self._crossing
        # react during the crossing too (not only once a receive is queued), so the
        # digger and the clearing setter both start moving as the attack comes over.
        if self._await and self._await[0] == 'receive':
            recv, receiver = self.ball.team, self._await[1]
        elif self._crossing and self.ball.in_flight:
            recv = 1 - self.ball.team
            receiver = self._crossing_receiver(recv)     # commit one digger, don't thrash
        else:
            recv, receiver = None, None
        # re-commit the digger to the closest reachable team-mate as the ball develops,
        # switching only when a candidate is clearly closer (hysteresis -> no thrash), so
        # the nearest player actually breaks for the ball instead of holding its shape.
        if receiver is not None and recv is not None and self.ball.in_flight:
            best = self._best_digger(recv)
            if (best is not None and best is not receiver
                    and receiver.dist_to(*self.ball.end)
                        > best.dist_to(*self.ball.end) + VB_DIG_SWITCH_MARGIN):
                receiver = best
                if self._await and self._await[0] == 'receive':
                    self._await = ('receive', best)
                else:
                    self._recv_cache = ((self.ball.start, self.ball.end), best)
        stored = self._await[1] if (self._await and self._await[0] in ('set', 'spike')) else None
        aim_block = (self._aimstep is not None and self._aimstep.get('block_x') is not None)
        bt = self._block_target
        base = {}                                            # base defensive formation
        if self._await and self._await[0] == 'spike':
            hitter = self._await[1]
            slots = self._defense_base(1 - hitter.team, hitter)
            for d in [a for a in self._team(1 - hitter.team)
                      if a.role != Role.SETTER and not a.is_player]:
                if not slots:
                    break
                slot = min(slots, key=lambda s: (d.x - s[0]) ** 2 + (d.y - s[1]) ** 2)
                base[d] = slot
                slots.remove(slot)
        for a in self.near + self.far:
            if a.is_player:
                continue
            if a.role == Role.SETTER and a.team == 0 and self._ai_block_jump > 0:
                continue                                     # holding a block at the net
            if aim_block and a.role == Role.SETTER and a.team == 1:
                continue                                     # opp blocker holds during your aim-step
            if bt is not None and a is bt['blocker']:        # slide along the net to the block lane
                ny = float(VB_NET_Y - VB_NET_CONTACT if a.team == 1 else VB_NET_Y + VB_NET_CONTACT)
                a.move_toward(float(bt['lane_x']), ny, dt, VB_ACTOR_SPEED)
                continue
            if a in base:                                    # take your base dig position
                self._ai_step(a, base[a][0], base[a][1], dt)
                continue
            if a is stored or (a is receiver and self._react_t <= 0.0):
                target = self.ball.end                       # commit to the ball (after the read)
            elif recv is not None and a.team == recv:
                target = self._defend_zone(a, recv)          # hold a wide zone until you've reacted
            elif (stored is not None and self._await[0] == 'set'
                  and a.team == stored.team and a.role != Role.SETTER):
                target = self._attack_wing(a)                # hitters climb onto the pins for a wide set
            elif self._tut is not None:
                target = (a.x, a.y)                            # tutorial: mates hold shape
            elif (self.ball.in_flight and a.role != Role.SETTER
                  and self._ball_to_side(a.team)
                  and a.dist_to(*self.ball.end) < VB_CONTACT_RADIUS * 2.5):
                target = self.ball.end                        # a ball's dropping near you — go!
            else:
                target = a.home
            self._ai_step(a, target[0], target[1], dt)
        self._separate(dt)

    def update(self, dt: float) -> None:
        raw_dt = dt
        self._time_scale += (self._time_target - self._time_scale) * min(1.0, 10.0 * raw_dt)
        game_dt = raw_dt * self._time_scale
        self._prev_y = self.ball.y

        self.fx.update(raw_dt)
        for a in self.near + self.far:
            a.update_anim(raw_dt)
        if self._hit_feedback is not None:
            lbl, t = self._hit_feedback
            self._hit_feedback = (lbl, t - raw_dt) if t - raw_dt > 0 else None

        if self._intro:
            if self._action:
                self._intro = False
            self._action = False
            self._set_pressed = False
            self._tip_pressed = False
            return

        if self._tut is not None:
            if self._tut_meta(raw_dt):
                self._action = self._set_pressed = self._tip_pressed = False
                return

        if self.phase == Phase.OVER:
            if self._action and self.on_finish:
                self.on_finish()
            self._action = False
            self._set_pressed = False
            self._tip_pressed = False
            return
        if self.phase == Phase.POINT:
            self.ball.update(game_dt)
            if self._timer > 0:
                self._timer -= raw_dt          # brief hold so the point reads...
            elif self._action:
                self._after_point()            # ...then wait for Z to start the next point
            self._action = False
            self._set_pressed = False
            self._tip_pressed = False
            return

        if self._aimstep is not None:
            self._update_aimstep(raw_dt)
            self._move_ai(game_dt)
            self._action = False
            self._set_pressed = False
            self._tip_pressed = False
            return

        if self._setstep is not None:
            self._update_setstep(raw_dt)
            self._move_ai(game_dt)
            self._action = False
            self._set_pressed = False
            self._tip_pressed = False
            return

        self._update_timers(game_dt)
        self._move_player(game_dt)
        if self._action and self._can_block():
            self._start_block()
        self.ball.update(game_dt)
        self._move_ai(game_dt)

        if self.phase == Phase.SERVE:
            if self._server().is_player:
                if self._serve_stage == 'power':
                    self._serve_meter += VB_SERVE_METER_SPEED * game_dt * self._serve_dir
                    if self._serve_meter >= 1.0:
                        self._serve_meter, self._serve_dir = 1.0, -1
                    elif self._serve_meter <= 0.0:
                        self._serve_meter, self._serve_dir = 0.0, 1
                    if self._action:
                        self._serve_power = self._serve_meter
                        self._serve_stage = 'lateral'
                else:                              # lateral: sweep a left/right marker
                    self._serve_lat += VB_SERVE_LAT_SPEED * game_dt * self._serve_lat_dir
                    if self._serve_lat >= 1.0:
                        self._serve_lat, self._serve_lat_dir = 1.0, -1
                    elif self._serve_lat <= 0.0:
                        self._serve_lat, self._serve_lat_dir = 0.0, 1
                    if self._action:
                        self._execute_serve(self._serve_power, self._serve_lat)
            else:
                self._serve_timer -= game_dt
                if self._serve_timer <= 0:
                    self._do_serve()
        else:
            self._resolve(game_dt)
        self._action = False
        self._set_pressed = False
        self._tip_pressed = False

    # ── Render ───────────────────────────────────────────────────────────────
    def _ensure_fonts(self) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont(UI_FONT_NAME, 14)
            self._big = pygame.font.SysFont(UI_FONT_NAME, 28, bold=True)
            self._small = pygame.font.SysFont(UI_FONT_NAME, 12)
            self._kf = pygame.font.SysFont(UI_FONT_NAME, 11, bold=True)
            self._huge = pygame.font.SysFont(UI_FONT_NAME, 36, bold=True)

    @staticmethod
    def _wrap(font, text: str, max_w: int) -> List[str]:
        lines, cur = [], ""
        for word in text.split(' '):
            trial = word if not cur else cur + ' ' + word
            if font.size(trial)[0] <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def _canvas(self) -> pygame.Surface:
        if self._canvas_surf is None:
            self._canvas_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        return self._canvas_surf

    def _draw_court(self, screen: pygame.Surface) -> None:
        screen.fill(_CLAD)
        pygame.draw.rect(screen, _FLOOR_EDGE, _HALL)                 # darker hall border
        pygame.draw.rect(screen, _FLOOR, _HALL.inflate(-10, -10))    # hall floor
        pygame.draw.rect(screen, _FLOOR_CT, _COURT)                  # court surface
        for top in (VB_NET_Y - _ATTACK, VB_NET_Y):                  # 3m attack zones
            pygame.draw.rect(screen, _FLOOR_ATK, (_COURT.left, top, _COURT.width, _ATTACK))
        pygame.draw.rect(screen, _LINE, _COURT, 2)
        for dy in (-_ATTACK, _ATTACK):
            pygame.draw.line(screen, _LINE, (_COURT.left, VB_NET_Y + dy),
                             (_COURT.right, VB_NET_Y + dy), 1)
        band = pygame.Rect(_COURT.left - 6, VB_NET_Y - 6, _COURT.width + 12, 12)
        pygame.draw.rect(screen, _NET_BG, band)
        for mx in range(band.left, band.right, 7):                  # net mesh
            pygame.draw.line(screen, _NET_MESH, (mx, band.top + 2), (mx, band.bottom - 2), 1)
        pygame.draw.line(screen, _NET_W, (band.left, band.top), (band.right, band.top), 2)
        pygame.draw.line(screen, _NET_W, (band.left, band.bottom), (band.right, band.bottom), 2)
        for px in (_COURT.left - 6, _COURT.right + 6):              # posts
            pygame.draw.rect(screen, _POST, (px - 2, VB_NET_Y - 20, 4, 40))

    def _draw_target(self, screen: pygame.Surface, pt: Tuple[float, float],
                     col: Tuple[int, int, int], rem: float) -> None:
        # a landing target: an outer ring that shrinks onto the bounce + a crosshair
        mx, my = int(pt[0]), int(pt[1])
        r = int(7 + 20 * min(1.0, rem / 0.9))
        pygame.draw.ellipse(screen, col, (mx - r, my - r // 2, r * 2, r), 1)
        pygame.draw.ellipse(screen, col, (mx - 9, my - 5, 18, 10), 2)
        pygame.draw.line(screen, col, (mx - 12, my), (mx + 12, my), 1)
        pygame.draw.line(screen, col, (mx, my - 7), (mx, my + 7), 1)

    def _draw_aimstep(self, screen: pygame.Surface) -> None:
        self._dim(screen)
        a = self._aimstep
        c = a['contactor']
        c.draw(screen)
        self.ball.draw(screen)
        # LINE (straight ahead) + CROSS (diagonal) guides from the hitter's lane
        deep_y = _COURT.top + 30 if c.team == 0 else _COURT.bottom - 30
        line_x = _clamp(c.x, _COURT.left + 26, _COURT.right - 26)
        cross_x = _clamp(2 * _CX - c.x, _COURT.left + 26, _COURT.right - 26)
        for gx, label in ((line_x, "LINE"), (cross_x, "CROSS")):
            reachable = a['xmin'] <= gx <= a['xmax']        # narrowed when out of system
            col = _GUIDE if reachable else (78, 88, 104)
            gxi, gyi = int(gx), int(deep_y)
            pygame.draw.line(screen, col, (int(c.x), int(c.y)), (gxi, gyi), 1)
            pygame.draw.circle(screen, col, (gxi, gyi), 9, 1)
            lab = self._small.render(label, True, col)
            ly = gyi + 12 if c.team == 0 else gyi - 24
            screen.blit(lab, (gxi - lab.get_width() // 2, ly))
        # opponent block: a covered lane you should aim around
        bx = a.get('block_x')
        in_block = bx is not None and abs(a['rx'] - float(bx)) <= VB_BLOCK_REACH
        if bx is not None:
            bxi = int(bx)
            top = _COURT.top if c.team == 0 else VB_NET_Y
            band = pygame.Surface((VB_BLOCK_REACH * 2, abs(VB_NET_Y - top) + 4), pygame.SRCALPHA)
            band.fill((235, 80, 70, 70))
            screen.blit(band, (bxi - VB_BLOCK_REACH, min(VB_NET_Y, top)))
            blocker = self._role(1 - c.team, Role.SETTER)
            blocker.draw(screen)
            pygame.draw.line(screen, _RED, (bxi - VB_BLOCK_REACH, VB_NET_Y),
                             (bxi + VB_BLOCK_REACH, VB_NET_Y), 3)
        zone = self._spike_zone((a['rx'], a['ry']), c.team)
        col = _RED if (in_block or zone != 'in') else _GREEN
        rx, ry = int(a['rx']), int(a['ry'])
        pygame.draw.circle(screen, col, (rx, ry), 16, 2)
        pygame.draw.line(screen, col, (rx - 22, ry), (rx + 22, ry), 1)
        pygame.draw.line(screen, col, (rx, ry - 22), (rx, ry + 22), 1)
        _, pw = self._hit_quality(float(a['meter']))        # live power preview
        pygame.draw.rect(screen, (40, 40, 50), (rx - 18, ry + 22, 36, 5))
        pygame.draw.rect(screen, (250, 220, 90), (rx - 18, ry + 22, int(36 * pw), 5))

    def _dim(self, screen: pygame.Surface) -> None:
        if self._dim_surf is None:
            self._dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._dim_surf.fill((6, 8, 24, 120))
        screen.blit(self._dim_surf, (0, 0))

    def _draw_setstep(self, screen: pygame.Surface) -> None:
        self._dim(screen)
        s = self._setstep
        atk = sorted(s['attackers'], key=lambda a: a.x)
        labels = ("LEFT", "RIGHT") if len(atk) >= 2 else ("SET",)
        for h, label in zip(atk, labels):
            h.draw(screen)
            chosen = h is s['choice']
            col = _GREEN if chosen else _GUIDE
            pygame.draw.circle(screen, col, (int(h.x), int(h.y)), 20, 2 if chosen else 1)
            lab = self._small.render(label, True, col)
            screen.blit(lab, (int(h.x) - lab.get_width() // 2, int(h.y) + 18))
        s['contactor'].draw(screen)
        self.ball.draw(screen)

    def _draw_block(self, screen: pygame.Surface) -> None:
        # inline reach bar at the net while the player is airborne blocking
        p = self._player()
        pygame.draw.line(screen, _GREEN, (int(p.x - VB_BLOCK_REACH), VB_NET_Y),
                         (int(p.x + VB_BLOCK_REACH), VB_NET_Y), 3)

    def draw(self, screen: pygame.Surface) -> None:
        self._ensure_fonts()
        canvas = self._canvas()
        self._draw_court(canvas)
        rx, ry = int(self._ref.x), int(self._ref.y)        # the ref on his stool
        pygame.draw.rect(canvas, (60, 50, 40), (rx - 7, ry + 6, 14, 6))
        self._ref.draw(canvas)
        if self.phase == Phase.SERVE and self._server().is_player:
            if self._serve_stage == 'power':
                power, lat = self._serve_meter, 0.5
            else:
                power, lat = self._serve_power, self._serve_lat
            (tx, ty), zone, _ = self._serve_target(power, lat, self.serving)
            self._draw_target(canvas, (tx, ty), _GREEN if zone == 'in' else _RED, 0.0)
            if self._serve_stage == 'lateral':
                x0, x1, _, _ = self._opp_half(self.serving)
                lx = int(_lerp(x0 + 10, x1 - 10, self._serve_lat))
                base_y = _COURT.top + 16 if self.serving == 0 else _COURT.bottom - 16
                pygame.draw.line(canvas, (255, 240, 150), (lx, VB_NET_Y), (lx, base_y), 1)
                pygame.draw.circle(canvas, (255, 240, 150), (lx, base_y), 5)
        if self.ball.in_flight and (self._await or self._crossing or self._serve_fault):
            fault = (self._serve_fault and self._serve_outcome is not None
                     and self._serve_outcome[0] == 'fault')   # out / into the net
            self._draw_target(canvas, self.ball.end, _RED if fault else _MARK,
                              self.ball.remaining())
        for a in sorted(self.far + self.near, key=lambda a: a.y):
            a.draw(canvas)
        self.ball.draw(canvas)
        cc = self._current_contactor()
        if (self.phase == Phase.RALLY and cc and cc.is_player
                and self.ball.in_flight and self._aimstep is None):
            rem = self.ball.remaining()
            if rem <= VB_TIMING_WINDOW:
                r = int(10 + 26 * (rem / VB_TIMING_WINDOW))
                col = (250, 240, 140) if rem <= VB_PERFECT_WINDOW else (240, 250, 250)
                pygame.draw.circle(canvas, col, (int(cc.x), int(cc.y)), r, 2)
        if self._aimstep is not None:
            self._draw_aimstep(canvas)
        if self._setstep is not None:
            self._draw_setstep(canvas)
        if self._block_jump > 0:
            self._draw_block(canvas)
        self.fx.draw(canvas)
        ox, oy = self.fx.offset()
        screen.fill((0, 0, 0))
        screen.blit(canvas, (ox, oy))

    def draw_overlay(self, screen: pygame.Surface) -> None:
        self._ensure_fonts()
        if self._intro:
            self._draw_intro(screen)
            return
        # scoreboard — top centre (in the run-off above play)
        sb = self._big.render("%d  -  %d" % (self.score[0], self.score[1]), True, (245, 248, 255))
        self._panel(screen, SCREEN_WIDTH // 2 - sb.get_width() // 2 - 16, 6,
                    sb.get_width() + 32, 38)
        screen.blit(sb, (SCREEN_WIDTH // 2 - sb.get_width() // 2, 10))
        if self._tut is not None:
            self._draw_tut(screen)
        # HUD lives in the side rails so nothing overlaps the court
        self._draw_left_hud(screen)
        self._draw_now(screen)
        self._draw_legend(screen)
        self._draw_right_hud(screen)
        if self.phase == Phase.SERVE and self._server().is_player:
            self._draw_serve_meter(screen)
        if self._aimstep is not None:
            self._draw_spike_meter(screen)
        if self._hit_feedback is not None:
            self._draw_hit_feedback(screen)
        if self.phase in (Phase.POINT, Phase.OVER) and self._banner:
            txt = self._big.render(self._banner, True, (255, 255, 255))
            bx = SCREEN_WIDTH // 2 - txt.get_width() // 2
            by = SCREEN_HEIGHT // 2 - 20
            pygame.draw.rect(screen, _BANNER,
                             (bx - 16, by - 8, txt.get_width() + 32, txt.get_height() + 16))
            screen.blit(txt, (bx, by))
            if self.phase == Phase.OVER or (self.phase == Phase.POINT and self._timer <= 0):
                label = "press Z" if self.phase == Phase.OVER else "press Z for next point"
                sub = self._font.render(label, True, (220, 220, 220))
                screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, by + 40))

    def _draw_tut(self, screen: pygame.Surface) -> None:
        t = self._tut
        step, ph = t['step'], t['phase']
        head = "Tutorial  %d/%d" % (step + 1, len(_TUT_STEPS))
        instr = _TUT_STEPS[step][1]
        if ph == 'success':
            status, col = "Nice!", (170, 255, 185)
        elif ph == 'fail':
            msg = ("Needs a PERFECT hit over — going again..."
                   if _TUT_STEPS[step][0] == 'spike' else "Just missed — going again...")
            status, col = msg, (255, 190, 170)
        elif ph == 'intro':
            status, col = "Press Z to start", (255, 230, 140)
        else:
            status, col = "", (250, 245, 200)
        hs = self._small.render(head, True, (180, 200, 230))
        ins = self._font.render(instr, True, (245, 242, 212))
        ss = self._font.render(status, True, col) if status else None
        w = max(hs.get_width(), ins.get_width(), ss.get_width() if ss else 0) + 36
        h = 44 + (20 if ss else 0)
        x = SCREEN_WIDTH // 2 - w // 2
        cx = SCREEN_WIDTH // 2
        self._panel(screen, x, 42, w, h)
        screen.blit(hs, (cx - hs.get_width() // 2, 48))
        screen.blit(ins, (cx - ins.get_width() // 2, 64))
        if ss:
            screen.blit(ss, (cx - ss.get_width() // 2, 86))

    def _panel(self, screen: pygame.Surface, x: int, y: int, w: int, h: int) -> None:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, _PANEL, (0, 0, w, h), border_radius=8)
        pygame.draw.rect(s, _PANEL_BD, (0, 0, w, h), 1, border_radius=8)
        screen.blit(s, (x, y))

    def _draw_left_hud(self, screen: pygame.Surface) -> None:
        self._panel(screen, 6, 50, 140, 46)
        rn = self._player().role.name
        role = {'HITTER_R': 'Hitter R', 'HITTER_L': 'Hitter L', 'SETTER': 'Setter'}.get(rn, rn)
        screen.blit(self._kf.render("YOU · " + role, True, (150, 200, 255)), (16, 58))
        serve_txt = "Your serve" if self.serving == 0 else "Their serve"
        screen.blit(self._small.render(serve_txt, True, (205, 210, 220)), (16, 76))

    def _draw_now(self, screen: pygame.Surface) -> None:
        # the contextual action hint — moved off the court into the left rail
        prompt = self._prompt()
        if not prompt:
            return
        lines = self._wrap(self._small, prompt, 124)
        self._panel(screen, 6, 104, 140, 24 + len(lines) * 15)
        screen.blit(self._kf.render("NOW", True, (150, 200, 255)), (16, 110))
        for i, ln in enumerate(lines):
            screen.blit(self._small.render(ln, True, (245, 240, 200)), (16, 124 + i * 15))

    def _draw_right_hud(self, screen: pygame.Surface) -> None:
        if self.phase == Phase.RALLY:
            self._panel(screen, 494, 50, 140, 30)
            screen.blit(self._small.render("Rally · %d touches" % self._rally_touches,
                                           True, (220, 225, 235)), (504, 58))

    def _draw_legend(self, screen: pygame.Surface) -> None:
        ctrls = (('Arrows', 'Move'), ('Z', 'Hit'), ('X', 'Set'),
                 ('C', 'Tip / dump'), ('Esc', 'Pause'))
        row = 18
        h = 24 + len(ctrls) * row
        y0 = SCREEN_HEIGHT - 8 - h
        self._panel(screen, 6, y0, 140, h)
        screen.blit(self._kf.render("CONTROLS", True, (150, 180, 225)), (16, y0 + 8))
        for i, (key, act) in enumerate(ctrls):
            yy = y0 + 26 + i * row
            kb = self._kf.render(key, True, (20, 24, 32))
            kw = kb.get_width() + 10
            pygame.draw.rect(screen, (205, 214, 230), (16, yy, kw, 15), border_radius=4)
            screen.blit(kb, (21, yy + 1))
            screen.blit(self._small.render(act, True, (220, 225, 235)), (16 + kw + 8, yy))

    def _draw_intro(self, screen: pygame.Surface) -> None:
        w, h = 404, 322
        x = SCREEN_WIDTH // 2 - w // 2
        y = SCREEN_HEIGHT // 2 - h // 2
        pygame.draw.rect(screen, (16, 20, 28), (x, y, w, h))
        pygame.draw.rect(screen, (90, 150, 220), (x, y, w, h), 2)
        title = self._big.render("HOW TO PLAY", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, y + 12))
        lines = [
            "You control the highlighted player",
            "(bright ring + marker). 3 vs 3.",
            "",
            "Rally:  serve  ->  dig  ->  set  ->  spike",
            "",
            "Arrows : move (run under the ball)",
            "Z      : dig / attack / serve / block",
            "X      : set       C : tip / dump",
            "",
            "At the net: Z to leap into slow-mo, aim",
            "with arrows, then Z spike or C tip.",
            "",
            "At the net on ball 2: Z attack / X set",
            "/ C dump.  On D: Z to block their hit.",
            "Serve: Z power, then Z to aim L/R.",
            "",
            "First to 7, win by 2.",
        ]
        ly = y + 50
        for ln in lines:
            screen.blit(self._small.render(ln, True, (220, 224, 230)), (x + 20, ly))
            ly += 14
        go = self._font.render("press Z to start", True, (250, 240, 160))
        screen.blit(go, (SCREEN_WIDTH // 2 - go.get_width() // 2, y + h - 24))

    def _draw_serve_meter(self, screen: pygame.Surface) -> None:
        bx, by, bw, bh = 506, 130, 16, 220
        pygame.draw.rect(screen, (24, 26, 34), (bx - 2, by - 2, bw + 4, bh + 4))
        nm, om = VB_SERVE_NET_MAX, VB_SERVE_OUT_MIN
        glo, ghi = VB_SERVE_GREEN
        segs = ((0.0, nm, (150, 50, 46)), (nm, glo, (208, 132, 52)),
                (glo, ghi, (70, 200, 110)), (ghi, om, (208, 132, 52)),
                (om, 1.0, (150, 50, 46)))             # red->orange->green->orange->red
        for v0, v1, col in segs:
            y0 = int(by + bh * (1.0 - v1))
            pygame.draw.rect(screen, col, (bx, y0, bw, int(by + bh * (1.0 - v0)) - y0))
        val = self._serve_meter if self._serve_stage == 'power' else self._serve_power
        my = int(by + bh * (1.0 - val))
        locked = self._serve_stage != 'power'
        pygame.draw.rect(screen, (110, 200, 130) if locked else (255, 240, 150),
                         (bx - 4, my - 2, bw + 8, 4))
        screen.blit(self._small.render("PWR", True, (220, 220, 220)), (bx - 6, by - 20))

    def _draw_spike_meter(self, screen: pygame.Surface) -> None:
        bx, by, bw, bh = 506, 130, 16, 220
        pygame.draw.rect(screen, (24, 26, 34), (bx - 2, by - 2, bw + 4, bh + 4))
        lo, hi, ow = VB_SPIKE_SWEET_LO, VB_SPIKE_SWEET_HI, 0.17
        segs = ((0.0, lo - ow, (172, 56, 50)), (lo - ow, lo, (208, 132, 52)),
                (lo, hi, (70, 200, 110)), (hi, hi + ow, (208, 132, 52)),
                (hi + ow, 1.0, (172, 56, 50)))               # red->orange->green->orange->red
        for v0, v1, col in segs:
            y0 = int(by + bh * (1.0 - v1))
            pygame.draw.rect(screen, col, (bx, y0, bw, int(by + bh * (1.0 - v0)) - y0))
        my = int(by + bh * (1.0 - float(self._aimstep['meter'])))
        pygame.draw.rect(screen, (255, 255, 255), (bx - 4, my - 2, bw + 8, 4))
        screen.blit(self._small.render("HIT", True, (220, 220, 220)), (bx - 6, by - 20))

    def _draw_hit_feedback(self, screen: pygame.Surface) -> None:
        label, t = self._hit_feedback
        if label == 'PERFECT':
            col = (255, 224, 90)
        elif label in ('SHANK', 'LATE', 'LATE!', 'EARLY'):
            col = (240, 150, 150)            # off-timing / poor pass reads red
        else:
            col = (245, 180, 120)
        txt = self._huge.render(label + ("!" if label == 'PERFECT' else ""), True, col)
        a = max(0.0, min(1.0, t / 0.7))
        y = int(SCREEN_HEIGHT * 0.30) - int((1.0 - a) * 10)
        screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y))

    def _prompt(self) -> str:
        if self.phase == Phase.SERVE and self._server().is_player:
            if self._serve_stage == 'power':
                return "Z: set power (green = fast)"
            return "Z: aim left / right"
        if self._aimstep is not None:
            return "Aim · Z spike · C tip"
        if self._setstep is not None:
            return "Pick side · X set · C dump"
        if self._block_jump > 0:
            return "BLOCK!"
        if self._can_block():
            return "At the net — Z to block"
        cc = self._current_contactor()
        if self.phase == Phase.RALLY and cc and cc.is_player:
            kind = self._await[0]
            if kind == 'receive':
                return "Get under it — Z to dig"
            if kind == 'set':
                if self._at_net(cc):
                    return "Z hit · X set · C dump"
                return "X to set · C dump"
            if kind == 'spike':
                return "Run in — Z to leap & aim"
        return ""
