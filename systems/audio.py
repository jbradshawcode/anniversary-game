"""Background music — a thin, fail-safe wrapper over pygame.mixer.music.

Drives the whole game (one streamed track at a time); call play() with a new
path to swap themes, stop() to fade out. Every audio error is swallowed so a
missing file or a machine with no audio device never crashes the game.
"""
from typing import Optional
import os
import pygame

from config import MUSIC_VOLUME, MUSIC_FADE_MS, SFX_VOLUME

try:
    import numpy as np
    _HAVE_NUMPY = True
except ImportError:
    _HAVE_NUMPY = False


class MusicPlayer:
    def __init__(self, volume: float = MUSIC_VOLUME) -> None:
        self._volume = max(0.0, min(1.0, volume))
        self._current: Optional[str] = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._ok = True
        except pygame.error:
            self._ok = False

    def play(self, path: str, loop: bool = True, fade_ms: int = MUSIC_FADE_MS) -> None:
        # no-op if the same track is already playing, or the file isn't there yet
        if not self._ok or path == self._current:
            return
        if not os.path.isfile(path):
            self._current = None
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)
            self._current = path
        except pygame.error:
            self._current = None

    def restart(self, path: str, loop: bool = True, fade_ms: int = MUSIC_FADE_MS) -> None:
        """Play `path` from the beginning even if it's already the current track."""
        self._current = None        # clear the same-track guard so play() restarts it
        self.play(path, loop, fade_ms)

    def stop(self, fade_ms: int = MUSIC_FADE_MS) -> None:
        self._current = None
        if not self._ok:
            return
        try:
            pygame.mixer.music.fadeout(fade_ms) if fade_ms > 0 else pygame.mixer.music.stop()
        except pygame.error:
            pass

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        if self._ok:
            try:
                pygame.mixer.music.set_volume(self._volume)
            except pygame.error:
                pass


class SoundBank:
    """Procedural SFX, synthesised with numpy at startup — no asset files needed.
    Fail-safe: silently disables itself if numpy or the mixer is unavailable."""

    def __init__(self, volume: float = SFX_VOLUME) -> None:
        self._snd = {}
        self._ok = False
        if not _HAVE_NUMPY:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            init = pygame.mixer.get_init()
        except pygame.error:
            init = None
        if init is None:
            return
        self._ok = True
        self._freq, _, self._channels = init
        try:
            self._build(max(0.0, min(1.0, volume)))
        except Exception:
            self._ok = False

    def play(self, name: str) -> None:
        if not self._ok:
            return
        s = self._snd.get(name)
        if s is not None:
            s.play()

    # ── synthesis ────────────────────────────────────────────────────────────
    # Impacts are modelled, not tonal: a pitch-dropping "body" (_thump), a
    # band-limited noise transient (the slap/crack, _nband), and tanh saturation
    # for punch (_sat). Sines alone just beep.
    def _t(self, dur: float):
        return np.linspace(0.0, dur, int(self._freq * dur), False)

    def _amp(self, t, decay, attack=0.0015):
        # near-instant attack (no speaker click) then exponential decay
        return np.minimum(1.0, t / max(1e-6, attack)) * np.exp(-decay * t)

    def _thump(self, f0, f1, dur, decay, bend=45.0, attack=0.0015):
        # a damped sine whose pitch glides f0 -> f1: the "body" of an impact
        t = self._t(dur)
        inst = f1 + (f0 - f1) * np.exp(-bend * t)
        phase = 2.0 * np.pi * np.cumsum(inst) / self._freq
        return np.sin(phase) * self._amp(t, decay, attack)

    def _nband(self, dur, decay, lp=1, hp=False, attack=0.0008):
        # a noise burst, optionally low-passed (thud) or high-passed (crack)
        t = self._t(dur)
        n = np.random.uniform(-1.0, 1.0, t.shape[0])
        if lp > 1:
            n = np.convolve(n, np.ones(lp) / lp, mode='same')
        if hp:
            n = n - np.convolve(n, np.ones(10) / 10.0, mode='same')
        return n * self._amp(t, decay, attack)

    def _sat(self, wave, drive=1.0):
        return np.tanh(drive * wave)

    def _mix(self, *waves):
        n = max(w.shape[0] for w in waves)
        out = np.zeros(n)
        for w in waves:
            out[:w.shape[0]] += w
        return out

    def _sound(self, wave, volume):
        data = np.clip(wave, -1.0, 1.0)
        audio = (data * 32767.0).astype(np.int16)
        if self._channels == 2:
            audio = np.repeat(audio.reshape(-1, 1), 2, axis=1)
        snd = pygame.sndarray.make_sound(np.ascontiguousarray(audio))
        snd.set_volume(volume)
        return snd

    def _whistle(self):
        dur = 0.22
        t = self._t(dur)
        f = 3200.0 + 90.0 * np.sin(2.0 * np.pi * 22.0 * t)      # peaful trill
        phase = 2.0 * np.pi * np.cumsum(f) / self._freq
        tone = np.sin(phase) + 0.5 * np.sin(2.0 * phase) + 0.2 * np.sin(3.0 * phase)
        breath = 0.10 * np.random.uniform(-1.0, 1.0, t.shape[0])
        env = np.minimum(1.0, t / 0.012) * np.minimum(1.0, (dur - t) / 0.05)
        return 0.45 * (tone + breath) * env

    def _cheer(self):
        dur = 0.7
        t = self._t(dur)
        n = np.convolve(np.random.uniform(-1.0, 1.0, t.shape[0]),
                        np.ones(40) / 40.0, mode='same')        # heavy low-pass -> roar
        flutter = np.convolve(1.0 + 0.25 * np.random.uniform(-1.0, 1.0, t.shape[0]),
                              np.ones(200) / 200.0, mode='same')  # slow crowd swell
        return 0.6 * n * flutter * (np.sin(np.pi * t / dur) ** 1.3)

    def _build(self, v):
        spike = self._sat(self._mix(0.70 * self._nband(0.05, 58, hp=True),
                                    0.85 * self._thump(220, 90, 0.12, 26, 60)), 1.7)
        waves = {
            'dig':     self._sat(self._mix(0.70 * self._thump(255, 130, 0.12, 22, 55),
                                           0.25 * self._nband(0.04, 50, lp=6)), 1.1),
            'set':     self._mix(0.22 * self._nband(0.025, 85, lp=2),
                                 0.16 * self._thump(680, 470, 0.035, 70, 90)),
            'serve':   self._sat(self._mix(0.70 * self._thump(330, 150, 0.12, 20, 52),
                                           0.40 * self._nband(0.03, 70, lp=3)), 1.3),
            'spike':   spike,
            'perfect': self._sat(self._mix(0.80 * self._nband(0.05, 52, hp=True),
                                           0.95 * self._thump(240, 95, 0.13, 24, 60)), 2.0),
            'block':   self._sat(self._mix(0.80 * self._thump(165, 80, 0.16, 15, 42),
                                           0.30 * self._nband(0.05, 34, lp=10)), 1.15),
            'tip':     self._mix(0.18 * self._nband(0.02, 95, lp=2),
                                 0.12 * self._thump(600, 450, 0.03, 75, 85)),
            'blip':    0.35 * self._thump(420, 360, 0.025, 70, 25),   # dialogue typewriter
            'whistle': self._whistle(),
            'cheer':   self._cheer(),
        }
        quiet = {'cheer': 0.8, 'blip': 0.5}      # these play a lot / sit in the background
        self._snd = {k: self._sound(w, v * quiet.get(k, 1.0)) for k, w in waves.items()}
