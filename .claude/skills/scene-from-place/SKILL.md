---
name: scene-from-place
description: Build a pygame game scene from a real building, street, or interior — from online evidence (floor plans, oriented footprint, aerial, Street View, dated photos), an independently-triangulated reconstruction, and an adversarial cold audit. Use when creating or rebuilding a scene of a real-world location.
---

# Scene from a real place

Turn a real place into a game scene grounded in evidence, not guesswork. Work in
**phases; each is a gate**. Do not skip a phase, and do not start the next until the
current gate passes — every documented failure (see `reference/METHODOLOGY.md`) came from
jumping ahead.

The screen is 20×15 tiles, but the **map may be larger and scroll** (like King St or the
garden). Size the grid to the place to capture detail; keep everything tile-aligned.

## What governs everything

1. **Online evidence is the only truth.** The repo's existing scenes are *suspect* — never
   reference them. Re-derive from scratch each run.
2. **The deliverable is a layout-accurate plan, not a photo.** This is a top-down tile game;
   the render will never *look* like a photograph. "Good" means the **shape, zones, door
   positions, materials, and major-feature relationships are right** — judged against the
   evidence. Calibrate the human sign-off to that, not to photorealism.
3. **The gates prove different things — don't conflate them.**
   - `validate()` = TOPOLOGY only (reachable). A wrong-but-walkable layout passes it.
   - `fidelity_warnings()` = cheap heuristics (uncited objects, centre-defaulted doors,
     sparse/flat). It catches *laziness*, not *wrongness*: it cannot tell a correct
     off-centre door from a wrong one. Any warning you accept must be **waived in
     `meta.fidelity_waivers` with a justification** — never silently shipped. Each waiver's
     `match` must be a distinctive substring of **exactly one** warning (a broad/short match
     is rejected and itself becomes an active warning, so a waiver can't launder the gate).
     `[non-waivable]` warnings — no evidence on disk, or a cite to a file that doesn't exist —
     **cannot be waived at all**; fix the evidence, don't rubber-stamp. A waiver is a
     human-accountable override: the script can't judge the `why`, so don't rubber-stamp one.
   - **The cold audit (Phase 3.5) is the real fidelity gate.** Door correctness, anchor
     placement, and "does it read as the place" are decided there and by the human — not by
     a script passing. The first attempt failed because "VALIDATION: OK" was read as "correct."

## Phase 0 — Resolve (geometry + currency)

```
PYTHONPATH=$SK python3 $SK/resolve.py "<Name>" --address "<full address>"
```

This geocodes, pulls the OSM footprint (axis box **and** the oriented minimum-area
rectangle), the aerial, and a 5-heading Street View fan.

**Gate:**
- [ ] `manifest.footprint` has `long_m` / `short_m` / `long_axis_bearing` — use the
      *oriented* dims, not the axis box (buildings are rarely compass-aligned).
- [ ] Facade fan downloaded; note where the main entrance and any secondary / service
      doors sit on the facade (usually **off-centre**, not at the midpoint).
- [ ] `manifest.currency.street_view` recorded (you'll compare it to photo dates next).

## Phase 1 — Gather (dated, ranked evidence)

**Search before you harvest.** Spend effort here in priority order — a real plan one-shots
the shape:

1. **A published floor plan** — planning-portal drawings, estate-agent / listing sites, the
   operator's own site, curated guides (e.g. CAMRA for pubs). Save with `--category floorplan`.
2. **Interior 360s** — Google "see inside" / business photospheres. `--category interior360`.
3. **Oblique / 45° aerial** — Bing Bird's Eye (manual; no clean API) for roofline + massing.
4. **Cast a WIDE net for photos** — the official gallery is rarely enough and is biased
   (flattering wide shots, no clean view of the anchor). Pull from **Google Images / image
   search, review & travel blogs (TripAdvisor, food/pub blogs), Google Maps "photos by
   visitors", Street View interior** — not just `--category gallery` from one site. The
   official gallery missed both a clean bar shot and a whole front-room banquette in the
   Salutation run; the good shots came from image search.

Harvest URLs via the Playwright MCP, then download:

```
PYTHONPATH=$SK python3 $SK/gather.py <slug> --urls /tmp/urls.txt \
    --source official-website --category gallery --captured <YYYY> --trust official
```

**Always pass `--captured` and `--trust`.** Then do a dirty-data pass
(`reference/dirty-data.md`): photos may predate a refurbishment — newest + highest-trust
wins, and conflicts get flagged, not silently fused.

**Coverage check — score per FEATURE, not just total count.** The total can look fine while
the one feature that matters is barely seen — the Salutation bar was mis-shaped because the
gallery had only flattering frontal shots of it and no view resolving its footprint/back.
List the major features (zones + the anchor) and confirm each is seen from **≥2 *distinct*
angles** (vantage differing by >~30°; two near-duplicate frontal shots count as ONE). The
**anchor needs a shot that resolves its footprint AND a shot of what's BEHIND it** —
free-standing vs wall-backed is decided by what's behind the feature, which a front/oblique
view *cannot* show. **Never infer free-standing from "you can see past it"** — that may be
circulation past the *end*, while the back is shelved against a wall. (The Salutation bar
flipped wrong→free-standing→wall-backed across three image batches precisely because no
behind-the-bar shot existed until late.) Also capture the **front profile** — bars/counters
are often canted or curved, not a single rectangle. A feature that fails this is the trigger
to **go gather more** (the wide net above) before Phase 2.

**Evidence floor.** If after widening you still have **no floor plan, no interior 360, and
<~6 interior photos** (or the anchor lacks a footprint-resolving angle): do **not** silently
proceed — flag the scene **low-confidence** in `meta.notes`, force the Phase-2 ensemble to
mark the under-covered features *ambiguous* rather than lock them, and treat them as
stylized. Sparse evidence is a result to report, not a gap to paper over.

**Gate:**
- [ ] A floor plan was searched for (found, or explicitly recorded "none exists").
- [ ] Photos pulled from **more than the official gallery** (image search / reviews / maps).
- [ ] Coverage scored per feature: each zone + the **anchor** seen from ≥2 distinct angles,
      and the anchor from a **footprint-resolving** (corner/behind) vantage — or flagged.
- [ ] Every image has a capture date (or is flagged undated) and a trust tier.
- [ ] Dirty-data conflicts listed; under-covered features marked low-confidence.

## Phase 2 — Reconstruct **(THIS IS THE SKILL)**

Everything else is transcription. A wrong reconstruction renders perfectly and passes
topology — accuracy is won or lost *here*. Output `refs/<slug>/reconstruction.md` from
`reference/reconstruction-template.md` **before** touching the tile grid.

The **anchor** is the place's single dominant fixed feature — resolve it first and most
carefully, then place everything relative to it. It's whatever the photos are *about*:
a bar/servery in a pub, an altar in a church, a counter in a shop, a stage, a fountain,
a ticket hall, a central staircase.

**Run it as an ensemble of independent cold passes.** Spawn ≥2 fresh `general-purpose`
subagents (same message, so none sees the others or any authoring rationale); each derives a
compass frame, zone apportionment, and anchor placement from the pixels. **Exact spawn recipe
(and the cold-audit recipe): `reference/spawning.md`.**

Then **reconcile** (you, the lead):
- All passes agree → lock it, high confidence.
- They disagree → genuine ambiguity *or* dirty data. Resolve with the footprint / floor
  plan, or flag for the audit. **Never average — pick the evidenced read.**

Derive metrically, not by vibe:
- **Compass frame** from `long_axis_bearing` + facade heading (e.g. "long axis bears ~3° →
  runs N–S; frontage faces S").
- **Zone boundaries** — get the *order* and rough split of zones along the long axis, then
  convert to tile columns. **The aerial is for footprint extent, massing, locating the
  garden/extensions and skylights/rooflines — NOT for interior room shapes or widths.** You
  cannot see internal walls from above and roof structure is ambiguous, so a room's
  shape/relative width comes from the **interior photos** (and a real floor plan if found),
  never from "the roof looks narrower there." (This run: the aerial couldn't tell the
  conservatory was a narrower lean-to — only the interior photo did.)
- **Entrances** located on the facade / aerial — main and secondary doors are usually
  off-centre. This is the fix for "the entrance/exit are in the wrong place."
- **Anchor** triangulated across ≥2 photos: which wall it backs onto, which way it faces,
  how long/large it is.
- **Fixtures, measured not eyeballed** — detail is the dimension runs keep getting wrong
  because it's the one thing left un-measured. Per zone, *count* the seating from the photos
  (run length in tiles, # tables, spacing, table types + seats) and record the numbers
  (reconstruction §4b). Real rooms mix types/spacing; a uniform comb of identical tables is
  the failure mode.

**Gate:**
- [ ] ≥2 independent reconstructions produced; disagreements reconciled or flagged.
- [ ] Compass frame justified from the bearing.
- [ ] Every zone boundary and **every entrance** tied to aerial/facade evidence — not centred
      by default.
- [ ] Anchor triangulated from ≥2 photos; backs-onto / faces / size stated.
- [ ] Fixtures **counted** per zone (numbers, types, spacing) — not left to the author's guess.

## Phase 3 — Author the spec

Transcribe the reconciled plan to `specs/<slug>.scene.json`. Set `meta.kind`
(interior/exterior/street) — it tunes the fidelity gate so it doesn't flag an open street
as "sparse." You may stylize shape/size for gameplay (the footprint guides, it doesn't
dictate) — but the **relationships and door positions from Phase 2 are fixed**.

- Put a `cite` (the photos that place it) on **every** object and `derived_from` on **every**
  exit. Express what makes the place *recognisable* — per-zone `material`, wall `treatments`,
  detail `objects` with a `palette` (or `color: "#hex"` off the cited photo); unknown types
  take a `shape` (round/tall/low/planted) so they read as a silhouette, never a bare box.
  **Full field list lives in `scripts/spec.py` — don't restate it; read it.**
- **Seating = arrangements, not loose furniture.** A wall **banquette run** = a long
  `banquette` + tables with `against:<wall>` + `seats` (chairs room-side only), NOT a short
  bench plus symmetric settings; same for booths / counter stools / lounge clusters
  (reconstruction §4b). Author the **measured counts/spacing** from §4b and **vary the table
  types** (`table` / `poseur` / `table` + `shape:round` for bistro / low table + `armchair`s)
  — a uniform comb of identical tables fails the fidelity gate. A flat render fails it too.
- **Shape that doesn't fit the grid** (an angled/chamfered free-standing bar, a feature that
  spans part-tiles) → give the object a `footprint` (float `pos`/`size` + `angle`/`chamfer`).
  Collision stays tile-based — it rasterises to whole blocked tiles — but the render and
  audit see the true shape. Place a free-standing feature **off the wall** so BFS proves the
  walk-behind. Use it for the anchor + a few hero pieces; `rect` stays the default for the rest.

```
SDL_VIDEODRIVER=dummy PYTHONPATH=$SK python3 $SK/render.py <slug> --mode all     # plan + reachability
SDL_VIDEODRIVER=dummy PYTHONPATH=$SK python3 $SK/render_ingame.py <slug>          # fast fidelity gate
SDL_VIDEODRIVER=dummy PYTHONPATH=$SK python3 $SK/render_detail.py <slug>          # high-detail sign-off
```

**Gate:**
- [ ] `render.py` reports TOPOLOGY reachable.
- [ ] **FIDELITY: 0 *active* warnings.** Each accepted warning must be a `meta.fidelity_waivers`
      entry with a real `why` — the renderer prints `~ waived: … [why: …]`. A silent warning
      is a fail. (Citations are checked against files on disk; `derived_from` must name real
      evidence — an empty string no longer clears the gate.)
- [ ] `detail.png` (the high-detail supersampled render) is the artifact you carry into the
      audit + human sign-off — it shows true-to-life shapes/colours; `ingame.png` is the quick check.

## Phase 3.5 — Adversarial cold audit

Spawn a **fresh `general-purpose` subagent each round** (never one that saw the
reconstruction) — full recipe in `reference/spawning.md`. It reconstructs from the photos
itself, then tries to **break** the spec: falsification-first, each line citing a photo, scored
agree / disagree / unknown, with **numeric** door/anchor estimates (`reference/audit-checklist.md`).
This is where a wrong off-centre door is caught — the scripts can't.

Convergence: any substantive `disagree` → fix the spec, re-render, spawn a **new** cold
audit. Repeat until it agrees. Adjudicate — the measured footprint overrides a vision guess
about wall length; the human decides ambiguous minors. Log each round to
`refs/<slug>/audit-round-N.md`. Stop when *structure* is stable; don't loop on cosmetics.

**Gate:**
- [ ] Zero unresolved substantive disagreements.
- [ ] Side-by-side `detail.png` vs 3–4 representative photos, **human-approved**.

## Phase 4 — Compile

Only after the human approves `detail.png`. Emit `config.SCENE_CONFIGS` +
`scenes/<scene>.py`; `static_blocked` = `spec.blocked_tiles(spec)` (footprints are already
rasterised to whole tiles, so collision stays purely tile-based). For larger-than-screen maps
emit `map_cols` + scrolling/camera config. Follow the project CLAUDE.md "New scene checklist."

Keep **exits on the map's outer border** (col 0 / col max / row 0 / row max). The renderer
and the centre-default door check both key off the grid edge, so a mid-map exit threshold
passes topology but draws no door and dodges the centre check. Put internal thresholds in as
walls/regions, not exits.

## Files

```
SK=.claude/skills/scene-from-place/scripts   # root auto-detected via .git
```

- `reference/METHODOLOGY.md` — the failure log: why each gate exists (read before editing them).
- `reference/reconstruction-template.md` — the Phase 2 artifact template.
- `reference/spawning.md` — exact subagent spawn recipes (ensemble + cold audit).
- `reference/dirty-data.md` — recency / trust conflict resolution.
- `reference/audit-checklist.md` — the Phase 3.5 falsification checklist.
- `scripts/spec.py` — schema, `validate()` (topology) + `fidelity_warnings()` (fidelity).
- `scripts/render_ingame.py` — fast fidelity render; `scripts/render_detail.py` — high-detail
  supersampled sign-off render (photo-derived palette, `seats`/`against` settings, `color` override).
- `_synthetic.scene.json` in `specs/` is the renderer test fixture. Run `ruff check $SK`
  before committing.
