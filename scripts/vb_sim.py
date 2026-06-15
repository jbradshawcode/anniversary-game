"""Headless checks for the volleyball minigame (scene 11).

Run:  SDL_VIDEODRIVER=dummy python3 scripts/vb_sim.py
Asserts arc determinism, momentum/dive/serve-meter/aim-step mechanics, that a
full match completes cleanly, and that the same seed is byte-deterministic
(proving the fx RNG is isolated). Renders a few frames to gym_refs/ to eyeball.
"""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((640, 480))
os.makedirs("gym_refs", exist_ok=True)

from entities.volleyball import VolleyBall, Role         # noqa: E402
from scenes import VolleyCourt                            # noqa: E402
from scenes.court import Phase, _COURT, _CX, _SET, _DIG, VB_NET_Y  # noqa: E402
from config import (VB_TOP_SPEED, VB_AIMSTEP_SLOWMO,  # noqa: E402
                    VB_SERVE_NET_MAX, VB_SERVE_OUT_MIN, VB_NET_CONTACT, VB_TIP_DROP,
                    VB_DIG_CLEAN, VB_BLOCK_REACH,
                    VB_SPIKE_SWEET_LO, VB_SPIKE_SWEET_HI, VB_PLAYER_TAKE_RADIUS)

_SWEET = (VB_SPIKE_SWEET_LO + VB_SPIKE_SWEET_HI) / 2.0   # meter value for a PERFECT hit


def _grab(c):
    s = pygame.Surface((640, 480))
    c.draw(s)
    c.draw_overlay(s)
    return s


def check_arc():
    b = VolleyBall()
    b.launch((100, 400), (500, 120), 110, 1.0)
    assert abs(b.z) < 1e-6, "z(0) should be 0"
    b.t = 0.5
    b._recompute()
    assert abs(b.z - 110) < 1e-6, "z(0.5) should equal peak"
    b.t = 1.0
    b._recompute()
    assert abs(b.z) < 1e-6, "z(1) should be 0"
    assert b.landing_point() == (500.0, 120.0), "landing must equal end"
    print("arc determinism: OK")


def check_momentum():
    c = VolleyCourt()
    c.enter(None)
    v = 0.0
    for _ in range(20):
        v = c._approach(v, VB_TOP_SPEED, 1 / 60.0)
    assert 0 < v <= VB_TOP_SPEED, "should ramp toward top speed"
    assert abs(v - VB_TOP_SPEED) < 1.0, "should reach top speed"
    for _ in range(30):
        v = c._approach(v, 0.0, 1 / 60.0)
    assert abs(v) < 1e-6, "decel should fully stop"
    print("momentum ramp/clamp/decel: OK")


def check_serve_lateral():
    c = VolleyCourt()
    c.enter(None)
    c.serving = 0
    c._start_serve()
    assert c._serve_stage == 'power'
    for power, zone in ((0.05, "net"), (0.5, "in"), (0.95, "out")):     # depth still faults
        _, z, _ = c._serve_target(power, 0.5, 0)
        assert z == zone, "power %.2f -> %s, got %s" % (power, zone, z)
    assert VB_SERVE_NET_MAX < 0.5 < VB_SERVE_OUT_MIN
    (lx, _), _, _ = c._serve_target(0.5, 0.0, 0)
    (rx, _), _, _ = c._serve_target(0.5, 1.0, 0)
    assert lx < rx, "lateral 0 must be left of lateral 1"
    assert _COURT.left <= lx and rx <= _COURT.right, "lateral stays in bounds"
    # two-stage flow: first X locks power -> lateral; second X serves
    c._intro = False
    c.phase = Phase.SERVE
    assert c._server().is_player
    c._serve_meter = 0.5
    c._action = True
    c.update(1 / 60.0)
    assert c._serve_stage == 'lateral', "first X locks power, advances to lateral"
    c._serve_lat = 0.5
    c._action = True
    c.update(1 / 60.0)
    assert c.phase == Phase.RALLY and c._crossing and not c._serve_fault, "second X serves in"
    pygame.image.save(_grab(_serve_lateral_frame()), "gym_refs/_vb_serve_lateral.png")
    print("serve two-stage L/R: OK")


def check_arc_physics():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    _set_to_player(c)
    c._vel = [0.0, 0.0]
    c._in_system = True
    c._action = True
    c._resolve(1 / 60.0)
    c._aimstep['block_x'] = None
    c._aimstep['meter'], c._aimstep['power_cap'] = _SWEET, 1.0
    c._aimstep['rx'] = float(_CX)
    c._aimstep['ry'] = (_COURT.top + VB_NET_Y) / 2.0
    c._action = True
    c._update_aimstep(1 / 60.0)
    spike_dur = c.ball.duration
    c2 = VolleyCourt()
    c2.enter(None)
    c2._intro = False
    _set_to_player(c2)
    c2._action = True
    c2._resolve(1 / 60.0)
    c2._tip_pressed = True
    c2._action = False
    c2._update_aimstep(1 / 60.0)
    tip_dur = c2.ball.duration
    assert tip_dur > spike_dur, "tip hangs longer than a spike (%.2f vs %.2f)" % (tip_dur, spike_dur)
    c3 = VolleyCourt()
    c3.enter(None)
    c3.serving = 0
    c3._start_serve()
    c3._execute_serve(0.30, 0.5)
    short_dur = c3.ball.duration
    c3._start_serve()
    c3._execute_serve(0.85, 0.5)
    deep_dur = c3.ball.duration
    assert short_dur > deep_dur, "short serve hangs longer than deep (%.2f vs %.2f)" % (
        short_dur, deep_dur)
    print("arc physics (tip > spike, short serve > deep): OK")


def _serve_frame():
    c = VolleyCourt()
    c.enter(None)
    c.serving = 0
    c._start_serve()
    c._serve_meter = 0.5
    return c


def _serve_lateral_frame():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    c.serving = 0
    c._start_serve()
    c._serve_stage = 'lateral'
    c._serve_power = 0.5
    c._serve_lat = 0.35
    return c


def _set_to_player(c):
    """Put the ball mid-flight as a set arriving at the player AT THE NET."""
    c.phase = Phase.RALLY
    p = c._player()
    setter = c._role(0, Role.SETTER)
    net = c._net_point(0, p.x)
    c.ball.launch((setter.x, setter.y), net, *_SET)
    c.ball.team = 0
    c._await = ('spike', p)
    while c.ball.remaining() > 0.10:
        c.ball.update(1 / 60.0)
    p.x, p.y = c.ball.end
    return p


def check_aimstep():
    c = VolleyCourt()
    c.enter(None)
    _set_to_player(c)
    c._action = True
    c._resolve(1 / 60.0)
    assert c._aimstep is not None, "spike press should enter aim-step"
    assert c._time_target == VB_AIMSTEP_SLOWMO, "slow-mo should engage"
    c._aimstep['block_x'] = None        # isolate from the AI block for these asserts

    c._move = (9.0, 0.0)            # hard right; must clamp
    c._action = False
    c._update_aimstep(1 / 60.0)
    assert c._aimstep['rx'] <= _COURT.right + 20, "reticle must clamp"

    # clean cross
    c._aimstep['rx'] = float(_CX)
    c._aimstep['ry'] = (_COURT.top + VB_NET_Y) / 2.0
    c._action = True
    c._update_aimstep(1 / 60.0)
    assert c._aimstep is None and c._crossing and not c._serve_fault, "in -> clean cross"
    assert c._time_target == 1.0, "slow-mo should release"

    # net fault
    c2 = VolleyCourt()
    c2.enter(None)
    _set_to_player(c2)
    c2._action = True
    c2._resolve(1 / 60.0)
    c2._aimstep['ry'] = VB_NET_Y - 2
    c2._action = True
    c2._update_aimstep(1 / 60.0)
    assert c2._serve_fault and c2._serve_outcome[2] == "Into the net!", "short -> net"

    # out fault
    c3 = VolleyCourt()
    c3.enter(None)
    _set_to_player(c3)
    c3._action = True
    c3._resolve(1 / 60.0)
    c3._aimstep['ry'] = _COURT.top - 10
    c3._action = True
    c3._update_aimstep(1 / 60.0)
    assert c3._serve_fault and c3._serve_outcome[2] == "Out!", "long -> out"

    # render a mid-aim-step frame
    c4 = VolleyCourt()
    c4.enter(None)
    c4._intro = False
    _set_to_player(c4)
    c4._action = True
    c4._resolve(1 / 60.0)
    c4._aimstep['rx'] = _CX - 70           # aim cross for the render
    c4._aimstep['ry'] = _COURT.top + 60
    c4._update_aimstep(1 / 60.0)
    pygame.image.save(_grab(c4), "gym_refs/_vb_aimstep.png")
    print("aim-step enter/clamp/fire/net/out: OK")


def check_net_spike():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    setter = c._role(0, Role.SETTER)
    c.ball.team = 0
    c._contact_success('set', setter, True)
    ex, ey = c.ball.end
    assert abs(ey - VB_NET_Y) <= VB_NET_CONTACT + 1, "set must land at the net (y=%.0f)" % ey
    assert c._await[0] == 'spike', "should await a spike"
    print("net-spike set target: OK")


def check_tip():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    _set_to_player(c)
    c._action = True
    c._resolve(1 / 60.0)
    assert c._aimstep is not None, "should be in aim-step"
    c._aimstep['rx'] = float(_CX)
    c._tip_pressed = True
    c._action = False
    c._update_aimstep(1 / 60.0)
    assert c._aimstep is None, "X should fire the tip"
    assert c._crossing and not c._serve_fault, "tip is a clean soft cross"
    _, ey = c.ball.end
    assert ey < VB_NET_Y and (VB_NET_Y - ey) <= VB_TIP_DROP + 2, "tip drops just over the net"
    print("tip (X) soft drop: OK")


def _player_as_setter(c):
    c._intro = False
    c._rotate(c.near)
    c._rotate(c.near)            # player (HITTER_R) -> HITTER_L -> SETTER
    for a in c.near + c.far:     # rotation changes roles/homes; settle onto the new homes
        a.x, a.y = a.home
    return c._player()


def _open_setstep(c):
    p = c._player()
    c.phase = Phase.RALLY
    c.ball.launch((p.x, p.y + 40), (p.x, p.y), *_DIG)
    c.ball.team = 0
    c._await = ('set', p)
    while c.ball.remaining() > 0.10:
        c.ball.update(1 / 60.0)
    p.x, p.y = c.ball.end
    c._set_pressed = True               # X enters the set-step
    c._resolve(1 / 60.0)
    return p


def check_setstep():
    c = VolleyCourt()
    c.enter(None)
    p = _player_as_setter(c)
    assert p.role == Role.SETTER, "player should be setter after two rotations"
    _open_setstep(c)
    assert c._setstep is not None, "X should enter the set-step"
    c._move = (1.0, 0.0)
    c._set_pressed = False
    c._update_setstep(1 / 60.0)
    assert c._setstep['choice'].role == Role.HITTER_R, "right picks the right hitter"
    c._move = (-1.0, 0.0)
    c._update_setstep(1 / 60.0)
    assert c._setstep['choice'].role == Role.HITTER_L, "left picks the left hitter"
    c._move = (0.0, 0.0)
    c._set_pressed = True
    c._update_setstep(1 / 60.0)
    assert c._setstep is None and c._await[0] == 'spike', "X confirms the set"
    assert c._await[1].role == Role.HITTER_L, "set goes to the chosen hitter"
    _, ey = c.ball.end
    assert abs(ey - VB_NET_Y) <= VB_NET_CONTACT + 1, "set lands at the net"

    d = VolleyCourt()
    d.enter(None)
    _player_as_setter(d)
    _open_setstep(d)
    d._tip_pressed = True
    d._update_setstep(1 / 60.0)
    assert d._setstep is None and d._crossing and not d._serve_fault, "C dumps over the net"
    _, ey2 = d.ball.end
    assert ey2 < VB_NET_Y, "dump lands on the opponent side"

    g = VolleyCourt()
    g.enter(None)
    _player_as_setter(g)
    _open_setstep(g)
    pygame.image.save(_grab(g), "gym_refs/_vb_setstep.png")
    print("set-step side/dump: OK")


def _setup_block(c, p, offset):
    c.score = [0, 0]
    c._serve_fault = False
    c.phase = Phase.RALLY
    c._await = None
    c._crossing = True
    c.ball.team = 1
    c.ball.in_flight = True
    c.ball.x, c.ball.y = float(_CX), float(VB_NET_Y)
    c.ball.end = (float(_CX), float(_COURT.bottom - 40))
    p.x, p.y = float(_CX + offset), float(VB_NET_Y + 18)
    c._block_jump = 0.3


def check_block_outcomes():
    c = VolleyCourt()
    c.enter(None)
    p = _player_as_setter(c)
    assert p.role == Role.SETTER
    _setup_block(c, p, 200)
    assert c._check_block() is False, "out of reach -> no touch"
    _setup_block(c, p, 0)
    c._block_jump = 0.0
    assert c._check_block() is False, "grounded (not jumped) -> no touch"

    random.seed(3)                          # squared: mostly stuffs, sometimes saved
    pts = alive = 0
    for _ in range(120):
        _setup_block(c, p, 0)
        assert c._check_block() is True, "squared airborne block connects"
        if c._serve_fault and c._serve_outcome[1] == 0:   # stuff -> deferred point to you
            pts += 1
            assert c.ball.in_flight and c.ball.end[1] < VB_NET_Y, "stuff drives down on their side"
        else:
            alive += 1                                    # saved -> rally continues
    assert pts > 60 and alive > 0, "squared mostly stuff, some saved (%d pt / %d alive)" % (pts, alive)

    random.seed(5)                          # glancing: deflect, never an INSTANT point
    for _ in range(20):
        _setup_block(c, p, VB_BLOCK_REACH * 0.8)
        assert c._check_block() is True, "glancing block connects"
        assert c.score[0] == 0 and c.score[1] == 0, "a glancing block is not an instant point"

    _setup_block(c, p, 0)
    c._check_block()
    pygame.image.save(_grab(c), "gym_refs/_vb_block.png")
    print("block outcomes (stuff/save/deflect/miss): OK")


def check_receive_quality():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    p = c._player()                          # a back defender on team 0
    c._vel = [0.0, 0.0]
    c.ball.launch((float(_CX), float(VB_NET_Y - 30)), (p.x, p.y), 150, 1.2)  # slow, planted, centred
    assert c._player_dig_quality(p) >= VB_DIG_CLEAN, "planted/centred/easy -> clean"
    c._vel = [VB_TOP_SPEED, 0.0]             # moving + off-centre + fast
    c.ball.launch((p.x, float(VB_NET_Y - 26)),
                  (p.x + c._player_radius() * 0.95, p.y), 60, 0.5)
    assert c._player_dig_quality(p) < VB_DIG_CLEAN, "moving/off-centre/hard -> reduced"

    setter = c._role(0, Role.SETTER)
    c.ball.launch((float(_CX), float(VB_NET_Y - 30)), (p.x, p.y), 150, 1.2)
    c.ball.team = 0
    c._do_receive(p, 'clean')
    # ball 2 pops to the central set spot; the closest teammate takes it (the setter,
    # here, since it stands at centre-net) — but it's no longer hardcoded to the setter.
    assert c._in_system and c._await == ('set', setter), "clean dig -> closest (setter here)"
    assert abs(c.ball.end[0] - _CX) < 1 and abs(c.ball.end[1] - (VB_NET_Y + 54)) < 1

    c.ball.launch((float(_CX), float(VB_NET_Y - 30)), (p.x, p.y), 150, 1.2)
    c.ball.team = 0
    c._do_receive(p, 'shank')
    assert (not c._in_system) and c._await[0] == 'set', "shank stays alive, out of system"

    before = c.score[1]
    c.ball.team = 0
    c.ball.end = (p.x, p.y)
    c._do_receive(p, 'error')
    assert c.score[1] == before + 1, "error gives the opponent the point"
    print("receive quality (clean/shank/error): OK")


def check_second_ball():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    setter = c._role(0, Role.SETTER)
    hl = c._role(0, Role.HITTER_L)
    hr = c._role(0, Role.HITTER_R)
    setter.x, setter.y = float(_COURT.left + 20), float(_COURT.bottom - 20)  # setter pulled far
    hr.x, hr.y = float(_CX), float(VB_NET_Y + 58)                            # hitter at the set spot
    c.ball.launch((hl.x, hl.y), (hl.x, hl.y), 150, 1.2)
    c.ball.team = 0
    c._do_receive(hl, 'clean')
    assert c._await[0] == 'set' and c._await[1] is hr, "ball 2 -> closest teammate, not the setter"
    print("second ball goes to the closest teammate: OK")


def check_difficulty():
    import random as _r

    def opp_clean_rate(level, n=500):
        c = VolleyCourt()
        c.configure('match', level)
        c.enter(None)
        c._intro = False
        back = c._role(1, Role.HITTER_L)          # an opponent back-row digger
        clean = 0
        for i in range(n):
            _r.seed(2000 + i)                     # same draws across levels -> p_good is the only diff
            c.score = [0, 0]
            c._in_system = True
            c.ball.launch((back.x, float(VB_NET_Y - 20)), (back.x, back.y), 100, 0.7)
            c.ball.team = 1
            c._ai_receive(back)
            if c.score[0] == 0 and c._in_system:  # clean pass kept it alive, in system
                clean += 1
        return clean / n

    hard, easy = opp_clean_rate('hard'), opp_clean_rate('easy')
    assert easy < hard - 0.10, "easy opponent must pass worse than hard (%.2f vs %.2f)" % (easy, hard)
    print("difficulty: opponent clean-pass easy %.2f < hard %.2f: OK" % (easy, hard))


def check_oos_aim():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    c._in_system = True
    p = _set_to_player(c)
    c._vel = [0.0, 0.0]
    c._enter_aimstep(p)
    cap_in = c._aimstep['power_cap']
    range_in = c._aimstep['xmax'] - c._aimstep['xmin']
    assert cap_in > 0.9 and range_in > _COURT.width * 0.9, "in-system -> full power + wide aim"

    d = VolleyCourt()
    d.enter(None)
    d._intro = False
    d._in_system = False
    pd = _set_to_player(d)
    d._vel = [0.0, 0.0]
    d._enter_aimstep(pd)
    assert d._aimstep['power_cap'] < cap_in, "out-of-system caps power"
    assert (d._aimstep['xmax'] - d._aimstep['xmin']) < range_in, "out-of-system narrows aim"
    pygame.image.save(_grab(d), "gym_refs/_vb_oos_aim.png")
    print("out-of-system set limits options: OK")


def check_ai_reliability():
    random.seed(11)
    c = VolleyCourt()
    c.enter(None)
    cc = c._role(1, Role.HITTER_L)           # an AI defender on team 1
    for label, peak, dur, lo, hi in (("easy", 150, 1.2, 0.90, 1.0),
                                      ("hard", 64, 0.5, 0.55, 0.75)):
        clean = 0
        trials = 600
        for _ in range(trials):
            c.score = [0, 0]
            c._in_system = True
            c.ball.launch((float(_CX), float(VB_NET_Y + 30)), (cc.x, cc.y), peak, dur)
            c.ball.team = 1
            c._await = ('receive', cc)
            c._ai_receive(cc)
            if c.score[0] == 0 and c._in_system and c._await and c._await[0] == 'set':
                clean += 1
        rate = clean / trials
        assert lo <= rate <= hi, "%s clean rate %.2f outside [%.2f, %.2f]" % (label, rate, lo, hi)
    print("AI reliability (easy ~95%+, hard ~60-70%): OK")


def check_receiver():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    setter = c._role(0, Role.SETTER)
    # a short serve that crosses the net late: backs (at home) are out of time -> setter
    c.ball.launch((float(_CX), float(_COURT.top + 12)), (float(_CX), float(VB_NET_Y + 30)), 200, 1.5)
    c.ball.team = 0
    while c.ball.remaining() > 0.12:
        c.ball.update(1 / 60.0)
    assert c._receiver(0) is setter, "short serve nearly down -> the setter covers"
    # a deep ball with plenty of flight time -> a back defender reaches it
    c.ball.launch((float(_CX), float(_COURT.top + 12)), (float(_CX), float(_COURT.bottom - 40)), 120, 1.0)
    c.ball.team = 0
    assert c._receiver(0).role != Role.SETTER, "deep ball with time -> a back defender"
    # you take balls that land near you (agency)
    p = c._player()
    assert p.role != Role.SETTER
    c.ball.launch((float(_CX), float(VB_NET_Y - 30)), (p.x, p.y), 120, 1.0)
    c.ball.team = 0
    assert c._receiver(0) is p, "a ball within your take-radius -> you take it (dist < %d)" % VB_PLAYER_TAKE_RADIUS
    # a ball at the setter's feet -> the setter just plays it (no dodge), even though
    # the human is elsewhere
    p.x, p.y = float(_COURT.left + 8), float(_COURT.bottom - 8)
    c.ball.launch((float(_CX), float(VB_NET_Y - 30)), (setter.x, setter.y), 120, 1.0)
    c.ball.team = 0
    assert c._receiver(0) is setter, "ball within the setter's take-radius -> setter plays it"
    print("receiver (you near / setter at feet / short serve / deep): OK")


def check_spike_power():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    _set_to_player(c)
    c._vel = [0.0, 0.0]
    c._in_system = True
    c._action = True
    c._resolve(1 / 60.0)
    c._aimstep['block_x'] = None
    c._aimstep['meter'] = _SWEET
    c._aimstep['rx'] = float(_CX)
    c._aimstep['ry'] = (_COURT.top + VB_NET_Y) / 2.0
    c._action = True
    c._update_aimstep(1 / 60.0)
    assert c._hit_feedback[0] == 'PERFECT', "sweet-band meter -> PERFECT"
    perfect_dur = c.ball.duration

    d = VolleyCourt()
    d.enter(None)
    d._intro = False
    _set_to_player(d)
    d._vel = [0.0, 0.0]
    d._in_system = True
    d._action = True
    d._resolve(1 / 60.0)
    d._aimstep['block_x'] = None
    d._aimstep['meter'] = 0.0
    d._aimstep['rx'] = float(_CX)
    d._aimstep['ry'] = (_COURT.top + VB_NET_Y) / 2.0
    d._action = True
    d._update_aimstep(1 / 60.0)
    assert d._hit_feedback[0] == 'EARLY', "meter at 0 -> EARLY"
    early_dur = d.ball.duration
    assert perfect_dur < early_dur, "a perfect hit is faster/harder than a mistimed one (%.2f vs %.2f)" % (
        perfect_dur, early_dur)
    print("spike power (PERFECT faster than EARLY): OK")


def _pop_to_setter(c, at_net=True):
    p = _player_as_setter(c)
    c.phase = Phase.RALLY
    if at_net:
        p.x, p.y = float(_CX), float(VB_NET_Y + 30)
    c.ball.launch((p.x, p.y + 40), (p.x, p.y), *_DIG)
    c.ball.team = 0
    c._await = ('set', p)
    while c.ball.remaining() > 0.10:
        c.ball.update(1 / 60.0)
    p.x, p.y = c.ball.end
    return p


def check_attack_on_two():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    p = _pop_to_setter(c)
    assert c._at_net(p), "setter should be at the net for the attack test"
    c._action = True
    c._resolve(1 / 60.0)
    assert c._aimstep is not None, "Z at the net attacks the 2nd ball"

    d = VolleyCourt()
    d.enter(None)
    d._intro = False
    _pop_to_setter(d)
    d._set_pressed = True
    d._resolve(1 / 60.0)
    assert d._setstep is not None, "X enters the set-step on the 2nd ball"

    e = VolleyCourt()
    e.enter(None)
    e._intro = False
    _pop_to_setter(e)
    e._tip_pressed = True
    e._resolve(1 / 60.0)
    assert e._crossing and not e._serve_fault and e._setstep is None, "C dumps the 2nd ball over"
    assert e.ball.end[1] < VB_NET_Y, "dump lands on the opponent side"
    print("attack on 2 (Z attack / X set / C dump): OK")


def check_ai_block():
    random.seed(2)
    stuffs = 0
    trials = 60
    for _ in range(trials):
        c = VolleyCourt()
        c.enter(None)
        c._intro = False
        _set_to_player(c)
        c._action = True
        c._resolve(1 / 60.0)
        a = c._aimstep
        a['block_x'], a['xmin'], a['xmax'] = float(_CX), float(_COURT.left), float(_COURT.right)
        a['meter'], a['rx'], a['ry'] = _SWEET, float(_CX), (_COURT.top + VB_NET_Y) / 2.0
        c._action = True
        c._update_aimstep(1 / 60.0)          # spike INTO the block lane
        # the outcome is deferred + animated: the ball is launched and the point goes
        # to the winner when it lands. A stuff -> the blocking team (1).
        assert c.ball.in_flight and c._serve_fault, "a block touch launches the ball (animated)"
        if c._serve_outcome[1] == 1:         # stuffed -> blocking team's point
            stuffs += 1
    assert stuffs > trials * 0.5, "hitting into the block is mostly stuffed (%d/%d)" % (stuffs, trials)

    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    _set_to_player(c)
    c._action = True
    c._resolve(1 / 60.0)
    a = c._aimstep
    a['block_x'], a['xmin'], a['xmax'] = float(_CX), float(_COURT.left), float(_COURT.right)
    a['meter'], a['rx'], a['ry'] = _SWEET, float(_COURT.right - 20), (_COURT.top + VB_NET_Y) / 2.0
    blk = c._role(1, Role.SETTER)            # place the blocker under its lane for the render
    blk.x, blk.y = float(_CX), float(VB_NET_Y - VB_NET_CONTACT)
    pygame.image.save(_grab(c), "gym_refs/_vb_aim_block.png")
    c._action = True
    c._update_aimstep(1 / 60.0)              # aim away from the block
    assert c._crossing and not c._serve_fault, "aiming away from the block -> clean cross"

    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    _set_to_player(c)
    c._action = True
    c._resolve(1 / 60.0)
    c._aimstep['block_x'] = float(_CX)
    c._tip_pressed = True
    c._action = False
    c._update_aimstep(1 / 60.0)              # a tip beats the block
    assert c._crossing and not c._serve_fault and c._aimstep is None, "tip beats the block"
    print("AI block (into -> stuffed, around -> clean, tip beats it): OK")


def check_block_movement():
    random.seed(1)
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    c.phase = Phase.RALLY
    setter0 = c._role(0, Role.SETTER)
    c.ball.team = 0
    bt = None
    tries = 0
    while bt is None and tries < 30:         # _commit_block has a chance; retry until it commits
        c._contact_success('set', setter0, True)
        bt = c._block_target
        tries += 1
    assert bt is not None and c._await[0] == 'spike', "an AI set commits a block"
    blocker = bt['blocker']
    assert blocker.team == 1 and blocker.role == Role.SETTER
    assert not c._at_net(blocker), "the blocker starts off the net (at home)"
    no_teleport = True
    for _ in range(int(0.95 * 60)):          # over the set's airtime it slides into place
        bx0 = blocker.x
        c._move_ai(1 / 60.0)
        if abs(blocker.x - bx0) > 30:
            no_teleport = False
    assert no_teleport, "the blocker moves gradually (never snaps)"
    assert c._at_net(blocker), "the blocker arrives at the net"
    assert abs(blocker.x - float(bt['lane_x'])) < 10, "the blocker reaches the committed lane"
    print("block movement (slides to the lane, no teleport): OK")


def check_block_out_animated():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    c.phase = Phase.RALLY
    c.ball.hold_at(float(_CX), float(VB_NET_Y + 30))
    before = list(c.score)
    c._block_send(0, (float(_CX), float(VB_NET_Y)),
                  (float(_COURT.right + 36), 200.0), 70, 0.6, "Off the block!")
    assert c.ball.in_flight and c._serve_fault, "a block touch launches the ball (animated)"
    assert c.score == before, "no instant point — it is deferred"
    frames = 0
    while c._serve_fault and frames < 120:
        c.ball.update(1 / 60.0)
        c._resolve(1 / 60.0)
        frames += 1
    assert c.score[0] == before[0] + 1, "the point is awarded only once the ball lands"
    print("block-out fully animated (deferred point on landing): OK")


def check_ai_avoid_block():
    random.seed(7)
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    c.serving = 0                            # keep team 1's hitters at their home lanes
    p = c._player()
    p.x = float(_COURT.right - 20)           # park the human blocker on the RIGHT
    c._role(1, Role.HITTER_R).x = float(_CX - 70)   # an attacker on the left
    c._role(1, Role.HITTER_L).x = float(_CX + 70)   # an attacker on the right
    for a in c._team(0):                     # defenders left -> the open lane is the RIGHT
        if a is not p:
            a.x = float(_COURT.left + 30)
    setter1 = c._role(1, Role.SETTER)
    trials = 240
    away = sum(1 for _ in range(trials) if c._smart_hitter(1, exclude=setter1).x < _CX)
    rate = away / trials
    # open lane is the RIGHT (toward the blocker); only the avoid bias sends it left, so
    # "away" should be frequent (~the 0.6 bias) but not always (openness sometimes wins).
    assert 0.4 < rate < 0.95, "AI biases away from the blocker, but not always (%.2f)" % rate
    print("AI avoids the blocker (biased, not always): OK")


def check_setter_dig_oos():
    c = VolleyCourt()
    c.enter(None)
    c._intro = False
    setter = c._role(0, Role.SETTER)
    c.ball.launch((float(_CX), float(VB_NET_Y - 26)), (setter.x, setter.y), 60, 0.6)
    c.ball.team = 0
    c._do_receive(setter, 'clean')
    assert c._in_system is False, "a setter dig is out of system"
    assert c._await[0] == 'set' and c._await[1].role != Role.SETTER, "a hitter sets out of system"
    em = c._await[1]
    c._contact_success('set', em, True)
    assert c._await[0] == 'spike', "the emergency set goes up to attack"
    assert c._await[1] is not em and c._await[1].role != Role.SETTER, \
        "the out-of-system spike comes from the other hitter"
    print("setter-dig out-of-system: OK")


def check_intro():
    c = VolleyCourt()
    c.enter(None)
    assert c._intro is True, "intro shown at start"
    c.update(1 / 60.0)
    assert c._intro is True, "stays until X"
    c._action = True
    c.update(1 / 60.0)
    assert c._intro is False, "X dismisses the card"
    pygame.image.save(_grab(_serve_frame()), "gym_refs/_vb_intro.png")
    c2 = VolleyCourt()
    c2.enter(None)
    s = pygame.Surface((640, 480))
    c2.draw(s)
    c2.draw_overlay(s)
    pygame.image.save(s, "gym_refs/_vb_intro_card.png")
    print("intro card dismiss: OK")


def run_match(seed):
    random.seed(seed)
    c = VolleyCourt()
    c.enter(None)
    shots = {}
    frames = 0
    while c.phase != Phase.OVER and frames < 60 * 2000:   # perfect bot -> long rallies
        if c._intro:
            c._action = True
            c.update(1 / 60.0)
            frames += 1
            continue
        if c._aimstep is not None:
            team = c._aimstep['contactor'].team
            x0, x1, y0, y1 = c._opp_half(team)
            opp = c._team(1 - team)
            bx = c._aimstep.get('block_x')
            # aim at the corner farthest from defenders, and away from the block lane
            best, best_d = (x0 + 20, y0 + 20), -1.0
            for tx in (max(x0 + 20, c._aimstep['xmin']), min(x1 - 20, c._aimstep['xmax'])):
                if bx is not None and abs(tx - bx) <= VB_BLOCK_REACH:
                    continue                 # skip the blocked lane
                for ty in (y0 + 20, y1 - 20):
                    d = min(a.dist_to(tx, ty) for a in opp)
                    if d > best_d:
                        best, best_d = (tx, ty), d
            c._aimstep['rx'], c._aimstep['ry'] = best
            c._aimstep['meter'] = _SWEET     # bot times a PERFECT hit so the AI is pressured
            c._action = True
        elif c._setstep is not None:
            c._set_pressed = True       # X confirms with the default smart pick
        elif c.phase == Phase.SERVE and c._server().is_player:
            if c._serve_stage == 'power':
                c._serve_meter = 0.5
            else:
                c._serve_lat = 0.5
            c._action = True
        else:
            cc = c._current_contactor()
            if c.phase == Phase.RALLY and cc is not None and cc.is_player:
                p = c._player()
                p.x, p.y = c.ball.end
                c._vel = [0.0, 0.0]      # planted + centred -> clean digs/sets
                if c.ball.in_flight and c.ball.remaining() <= 0.12:
                    if c._await[0] == 'set':
                        c._set_pressed = True    # X: set to a hitter (avoid attacking on 2)
                    else:
                        c._action = True         # Z: dig / spike
        if (c.phase == Phase.RALLY and c.ball.in_flight and c._await
                and 0.25 < c.ball.remaining() < 0.5):
            shots.setdefault("rally", _grab(c))
        c.update(1 / 60.0)
        if c.phase == Phase.POINT:
            shots.setdefault("point", _grab(c))
        frames += 1
    return c, shots, frames


def check_determinism():
    ca, _, fa = run_match(42)
    cb, _, fb = run_match(42)
    assert ca.score == cb.score and fa == fb, "same seed must be identical (fx RNG leak?)"
    print("determinism (fx RNG isolated): OK")


if __name__ == "__main__":
    check_arc()
    check_arc_physics()
    check_momentum()
    check_serve_lateral()
    check_aimstep()
    check_net_spike()
    check_tip()
    check_setstep()
    check_oos_aim()
    check_receive_quality()
    check_second_ball()
    check_difficulty()
    check_ai_reliability()
    check_block_outcomes()
    check_spike_power()
    check_attack_on_two()
    check_ai_block()
    check_block_movement()
    check_block_out_animated()
    check_receiver()
    check_ai_avoid_block()
    check_setter_dig_oos()
    check_intro()
    for s in (1, 7, 42):
        c, shots, frames = run_match(s)
        assert c.phase == Phase.OVER, "match seed %d did not finish (%s)" % (s, c.score)
        assert max(c.score) >= 7 and abs(c.score[0] - c.score[1]) >= 2, "bad win condition"
        for name, surf in shots.items():
            pygame.image.save(surf, "gym_refs/_vb_%s.png" % name)
        pygame.image.save(_grab(c), "gym_refs/_vb_over.png")
        print("match seed %d: finished %s in %.1fs" % (s, c.score, frames / 60.0))
    check_determinism()
    print("all volleyball checks passed")
