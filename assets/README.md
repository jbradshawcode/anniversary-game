# assets/

Game audio. Music is streamed one track at a time via `systems/audio.py`
(`MusicPlayer`); paths are defined in `config.py`.

Use **`.ogg`** (Vorbis) — `pygame.mixer.music` supports it reliably across
platforms; MP3 support is patchy on older SDL_mixer builds.

## Expected files

- `vb_theme.ogg` — volleyball minigame background music (`VB_MUSIC`).
  Loops while the 3v3 is running, fades out when it ends.

The game runs fine without these files: `MusicPlayer` silently no-ops when a
track is missing or no audio device is available.

## Converting a track to .ogg

Install ffmpeg (`brew install ffmpeg`) then — note the Homebrew bottle ships the
native `vorbis` encoder, not `libvorbis`:

```sh
ffmpeg -i your_track.mp3 -c:a vorbis -strict experimental -q:a 5 assets/vb_theme.ogg
```
