# Spawning subagents — ensemble reconstruction (Phase 2) & cold audit (Phase 3.5)

Both stages live or die on **independence**: subagents reconstruct from the photo *pixels*
with no shared state and no authoring rationale. A vague spawn defeats the point.

## Ensemble reconstruction (Phase 2)

Spawn **≥2 fresh `general-purpose` agents in the SAME message** (so they can't see each
other). Each prompt MUST:
- list the exact files and say *"open every one with the Read tool — reconstruct from the
  pixels, not the filenames"*: `refs/<slug>/gallery/*`, `refs/<slug>/_resolve/facade*.jpg`,
  `refs/<slug>/_resolve/aerial*.png` (+ any `floorplan/`, `interior360/`);
- give the oriented footprint (`long_m`/`short_m`/`long_axis_bearing`) and the dirty-data notes;
- require it to fill sections 1–4 of `reconstruction-template.md`, **citing each claim by a
  filename it actually opened** (≥2 photos for the anchor) — including §4b's **numeric
  fixtures count** per zone (# tables, types, spacing), not just prose;
- forbid reading `reconstruction.md`, `recon-pass-*.md`, or any spec.

Save each return to `refs/<slug>/recon-pass-N.md`; you (the lead) reconcile — **never average**,
pick the evidenced read; flag genuine disagreements for the audit.

## Cold audit (Phase 3.5)

Spawn **ONE fresh `general-purpose` agent per round** (never one that saw the reconstruction).
Tell it to **Read**: every `refs/<slug>/gallery/*` photo, `refs/<slug>/_render/detail.png`, the
spec JSON, `audit-checklist.md`, and the manifest footprint — but **NOT** `reconstruction.md`
or `recon-pass-*.md`.

It reconstructs from the photos itself, then tries to **break** the spec: falsification-first,
each line citing a photo it opened, scored agree / disagree / unknown. **Require numeric
estimates** (each door's offset-from-corner in tiles; the anchor's wall + run length in tiles)
and disagree on any mismatch — this is where a wrong off-centre door is caught, since the
scripts can't. Log findings to `refs/<slug>/audit-round-N.md`.
