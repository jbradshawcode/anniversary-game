# Music + SFX layer — the Godot port of systems/audio.py (MusicPlayer + SoundBank),
# run as an autoload so it survives scene churn. Music streams one looping track at a
# time (play() to swap, stop() to fade out), banking each track's position so swapping
# back resumes where it left off. SFX are synthesised procedurally at startup (no asset
# files) into AudioStreamWAVs, played through a small voice pool so they can overlap.
# Every audio operation is fail-safe: a missing file or unbuilt bank is a silent no-op.
extends Node

const _FREQ := 44100.0
const _SFX_VOICES := 10

var _music: AudioStreamPlayer
var _sfx_pool: Array = []
var _sfx_next := 0
var _banks: Dictionary = {}          # name -> AudioStream (synth WAV or the loud whistle ogg)
var _streams: Dictionary = {}        # res:// path -> AudioStream (cached music)
var _positions: Dictionary = {}      # path -> seconds in; resume there instead of restarting
var _current := ""                   # the playing music path ("" = silence)
var _music_target_db := 0.0
var _fade: Tween


func _ready() -> void:
	_music = AudioStreamPlayer.new()
	add_child(_music)
	_music_target_db = linear_to_db(maxf(0.0001, Config.MUSIC_VOLUME))
	for i in _SFX_VOICES:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_sfx_pool.append(p)
	_build_sfx()


# ── Music (mirror of MusicPlayer) ────────────────────────────────────────────────
func play(path: String, loop := true, fade_ms := -1) -> void:
	if path == _current:
		return
	if fade_ms < 0:
		fade_ms = Config.MUSIC_FADE_MS
	var stream = _music_stream(path)
	if stream == null:
		_current = ""
		return
	_bank_position()                         # remember the outgoing track's place before we swap
	if stream is AudioStreamOggVorbis:
		stream.loop = loop
	_current = path
	var start: float = _positions.get(path, 0.0)
	_music.stream = stream
	_music.volume_db = -40.0
	_music.play(start)
	_fade_to(_music_target_db, fade_ms)


func stop(fade_ms := -1) -> void:
	if fade_ms < 0:
		fade_ms = Config.MUSIC_FADE_MS
	_bank_position()                         # so returning to this track resumes where it left off
	_current = ""
	if not _music.playing:
		return
	if fade_ms <= 0:
		_music.stop()
		return
	_fade_to(-40.0, fade_ms, true)


# Forget all resume marks (call between chapters so tracks start fresh).
func reset() -> void:
	_positions.clear()


func set_music_volume(v: float) -> void:
	_music_target_db = linear_to_db(maxf(0.0001, clampf(v, 0.0, 1.0)))
	if _music.playing and (_fade == null or not _fade.is_running()):
		_music.volume_db = _music_target_db


func _bank_position() -> void:
	if _current == "" or not _music.playing:
		return
	_positions[_current] = _music.get_playback_position()


func _fade_to(target_db: float, fade_ms: int, stop_after := false) -> void:
	if _fade != null and _fade.is_running():
		_fade.kill()
	if fade_ms <= 0:
		_music.volume_db = target_db
		if stop_after:
			_music.stop()
		return
	_fade = create_tween()
	_fade.tween_property(_music, "volume_db", target_db, fade_ms / 1000.0)
	if stop_after:
		_fade.tween_callback(_music.stop)


func _music_stream(path: String):
	if _streams.has(path):
		return _streams[path]
	var stream = AudioStreamOggVorbis.load_from_file(ProjectSettings.globalize_path(path))
	_streams[path] = stream                  # cache even null so a missing file isn't retried
	return stream


# ── SFX (mirror of SoundBank) ────────────────────────────────────────────────────
func sfx(name: String) -> void:
	var stream = _banks.get(name)
	if stream == null:
		return
	var p: AudioStreamPlayer = _sfx_pool[_sfx_next]
	_sfx_next = (_sfx_next + 1) % _SFX_VOICES
	p.stream = stream
	p.play()


# ── synthesis ────────────────────────────────────────────────────────────────────
# Impacts are modelled, not tonal: a pitch-dropping "body" (_thump), a band-limited
# noise transient (the slap/crack, _nband), and tanh saturation for punch (_sat).
func _build_sfx() -> void:
	var spike := _sat(_mix([
		_scale(_nband(0.05, 58, 1, true), 0.70),
		_scale(_thump(220, 90, 0.12, 26, 60), 0.85)]), 1.7)
	var waves := {
		"dig": _sat(_mix([
			_scale(_thump(255, 130, 0.12, 22, 55), 0.70),
			_scale(_nband(0.04, 50, 6, false), 0.25)]), 1.1),
		"set": _mix([
			_scale(_nband(0.025, 85, 2, false), 0.22),
			_scale(_thump(680, 470, 0.035, 70, 90), 0.16)]),
		"serve": _sat(_mix([
			_scale(_thump(330, 150, 0.12, 20, 52), 0.70),
			_scale(_nband(0.03, 70, 3, false), 0.40)]), 1.3),
		"spike": spike,
		"perfect": _sat(_mix([
			_scale(_nband(0.05, 52, 1, true), 0.80),
			_scale(_thump(240, 95, 0.13, 24, 60), 0.95)]), 2.0),
		"block": _sat(_mix([
			_scale(_thump(165, 80, 0.16, 15, 42), 0.80),
			_scale(_nband(0.05, 34, 10, false), 0.30)]), 1.15),
		"tip": _mix([
			_scale(_nband(0.02, 95, 2, false), 0.18),
			_scale(_thump(600, 450, 0.03, 75, 85), 0.12)]),
		"blip": _scale(_thump(420, 360, 0.025, 70, 25), 0.35),   # dialogue typewriter
		"whistle": _whistle(),
		"cheer": _cheer(),
	}
	var quiet := {"cheer": 0.8, "blip": 0.5}     # these play a lot / sit in the background
	for k in waves:
		_banks[k] = _make_wav(waves[k], Config.SFX_VOLUME * float(quiet.get(k, 1.0)))
	# The recorded whistle (assets/whistle.ogg) is the LOUD one — reserved for the
	# overworld/plot (Matúš). The minigame keeps the unobtrusive synth 'whistle'.
	var loud = _music_stream("res://assets/whistle.ogg")
	if loud != null:
		_banks["whistle_loud"] = loud


func _thump(f0: float, f1: float, dur: float, decay: float, bend := 45.0, attack := 0.0015) -> PackedFloat32Array:
	# a damped sine whose pitch glides f0 -> f1: the "body" of an impact
	var n := int(_FREQ * dur)
	var out := PackedFloat32Array()
	out.resize(n)
	var acc := 0.0
	for i in n:
		var t := i * dur / n
		var inst: float = f1 + (f0 - f1) * exp(-bend * t)
		acc += inst
		out[i] = sin(TAU * acc / _FREQ) * _amp(t, decay, attack)
	return out


func _nband(dur: float, decay: float, lp := 1, hp := false, attack := 0.0008) -> PackedFloat32Array:
	# a noise burst, optionally low-passed (thud) or high-passed (crack)
	var n := int(_FREQ * dur)
	var noise := PackedFloat32Array()
	noise.resize(n)
	for i in n:
		noise[i] = randf_range(-1.0, 1.0)
	if lp > 1:
		noise = _box(noise, lp)
	if hp:
		var lo := _box(noise, 10)
		for i in n:
			noise[i] -= lo[i]
	var out := PackedFloat32Array()
	out.resize(n)
	for i in n:
		out[i] = noise[i] * _amp(i * dur / n, decay, attack)
	return out


func _whistle() -> PackedFloat32Array:
	var dur := 0.22
	var n := int(_FREQ * dur)
	var out := PackedFloat32Array()
	out.resize(n)
	var acc := 0.0
	for i in n:
		var t := i * dur / n
		var f: float = 3200.0 + 90.0 * sin(TAU * 22.0 * t)       # playful trill
		acc += f
		var phase := TAU * acc / _FREQ
		var tone := sin(phase) + 0.5 * sin(2.0 * phase) + 0.2 * sin(3.0 * phase)
		var breath := 0.10 * randf_range(-1.0, 1.0)
		var env: float = minf(1.0, t / 0.012) * minf(1.0, (dur - t) / 0.05)
		out[i] = 0.45 * (tone + breath) * env
	return out


func _cheer() -> PackedFloat32Array:
	var dur := 0.7
	var n := int(_FREQ * dur)
	var raw := PackedFloat32Array()
	var flu := PackedFloat32Array()
	raw.resize(n)
	flu.resize(n)
	for i in n:
		raw[i] = randf_range(-1.0, 1.0)
		flu[i] = 1.0 + 0.25 * randf_range(-1.0, 1.0)
	raw = _box(raw, 40)                          # heavy low-pass -> roar
	flu = _box(flu, 200)                         # slow crowd swell
	var out := PackedFloat32Array()
	out.resize(n)
	for i in n:
		var t := i * dur / n
		out[i] = 0.6 * raw[i] * flu[i] * pow(sin(PI * t / dur), 1.3)
	return out


func _amp(t: float, decay: float, attack := 0.0015) -> float:
	# near-instant attack (no speaker click) then exponential decay
	return minf(1.0, t / maxf(1e-6, attack)) * exp(-decay * t)


# Centred moving-average box filter, matching numpy convolve(x, ones(k)/k, 'same').
func _box(x: PackedFloat32Array, k: int) -> PackedFloat32Array:
	var n := x.size()
	var out := PackedFloat32Array()
	out.resize(n)
	var off := (k - 1) / 2
	for i in n:
		var s := 0.0
		for j in k:
			var idx := i + off - j
			if idx >= 0 and idx < n:
				s += x[idx]
		out[i] = s / k
	return out


func _scale(w: PackedFloat32Array, g: float) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	out.resize(w.size())
	for i in w.size():
		out[i] = w[i] * g
	return out


func _sat(w: PackedFloat32Array, drive := 1.0) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	out.resize(w.size())
	for i in w.size():
		out[i] = _tanh(drive * w[i])
	return out


func _mix(waves: Array) -> PackedFloat32Array:
	var n := 0
	for w in waves:
		n = maxi(n, w.size())
	var out := PackedFloat32Array()
	out.resize(n)
	for w in waves:
		for i in w.size():
			out[i] += w[i]
	return out


func _tanh(x: float) -> float:
	var e := exp(2.0 * x)
	return (e - 1.0) / (e + 1.0)


func _make_wav(samples: PackedFloat32Array, volume: float) -> AudioStreamWAV:
	var n := samples.size()
	var bytes := PackedByteArray()
	bytes.resize(n * 2)
	for i in n:
		var s := clampf(samples[i] * volume, -1.0, 1.0)
		bytes.encode_s16(i * 2, int(s * 32767.0))
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = int(_FREQ)
	wav.stereo = false
	wav.data = bytes
	return wav
