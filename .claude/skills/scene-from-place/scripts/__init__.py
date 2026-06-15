"""Place pipeline (dev-only) — derive a game scene from online sources of truth.

Stages:
  0 resolve  — geocode + building footprint + aerial + facade  -> manifest.json
  1 gather   — interior/exterior reference photos               -> refs/<slug>/
  2 spec     — author scene_spec.json from the gathered evidence
  3 render   — plan / blocked views (render.py) + the in-game render (render_ingame.py)
  4 compile  — scene_spec -> config.SCENE_CONFIGS + scene draw

Source of truth is ONLINE ONLY. Nothing in this repo's existing scenes is
treated as reference.
"""
