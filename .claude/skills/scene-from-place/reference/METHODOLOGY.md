# Failure log — why each gate exists

This is the institutional memory behind `SKILL.md`. The phases and gates there are the
method; this is the record of what went wrong when they weren't followed. **Read it before
weakening or removing a gate** — each one is a scar.

The method itself lives in `SKILL.md`. Don't restate it here; this file is *history*.

## Attempt 1 — "VALIDATION: OK" but the bar was in the wrong place

The render didn't look like the inside and the anchor was misplaced — yet the run reported
"VALIDATION: OK" and a 26-photo audit that "fully aligned." Causes:

1. **No spatial reconstruction.** The spec was authored from a gestalt impression straight
   into tile coordinates. "Central peninsula bar" was a *vibe*, not a derived fact.
   → gate: **Phase 2 reconstruct-before-transcribe.**
2. **`validate()` read as correctness.** It only checks reachability. "OK" meant "walkable,"
   never "correct." → gate: **two separate gates, topology vs `fidelity_warnings()`.**
3. **Confirmation-bias audit.** It checked *presence* ("is there a bar?" — always true),
   compared the render to its own source, and was framed to confirm alignment.
   → gate: **Phase 3.5 cold, falsification-first audit on independent artifacts.**

## Attempt 2 — reconstruction added, still wrong

Better, but the Salutation still came out with the wrong shape, centred doors, and a flat,
unrecognisable interior. New causes:

4. **One reconstruction, one author.** The agent that reconstructed also authored and
   half-audited; a single biased reconstruction renders perfectly and the audit "converges"
   on it. → gate: **Phase 2 independent ensemble; Phase 3.5 auditor never sees the recon.**
5. **Doors defaulted to wall-centre.** Nothing located the real entrances, so the renderer
   centred them — but the front door and rear route were off-centre in the facade evidence.
   → gate: **metric entrance derivation + `derived_from`; the defaulted-exit fidelity check.**
6. **Dirty data fused silently.** Photos from before and after a refit were treated as one
   layout. → gate: **Phase 1 capture-dating + trust tiers (`dirty-data.md`).**
7. **The axis-box footprint lied.** The axis-aligned bounding box over-stated size and could
   mislabel which wall is long. → gate: **oriented min-area rectangle in `resolve.py`.**
8. **No fidelity floor.** Success was "reachable + audit agrees," neither of which sees a
   flat, under-furnished room. → gate: **`fidelity_warnings()` as a Phase 3 gate.**

## Attempt 3 — the from-scratch run

Better again, but two lessons surfaced at human sign-off:

9. **The aerial was trusted for interior room shape.** A zone's width was inferred from the
   roofline; the aerial can't see internal walls, so the conservatory was first drawn
   full-width. Only the interior photo (gallery/07) showed it's a narrower lean-to.
   → rule: the aerial gives footprint/massing/garden/skylights ONLY; **room shapes and widths
   come from interior photos / a floor plan** (Phase 2 + the reconstruction template).
10. **Feedback was applied without re-reconciling.** A human note ("conservatory too wide,
    seating off") was patched straight into the spec by the author, who then got the
    conservatory banquette/prints side-swapped. → rule: treat human sign-off feedback like any
    other change — **re-check it against the refs and run a fresh cold audit**, don't
    self-certify a hand edit.

## Attempt 4 — the anchor shape oscillated (wrong → free-standing → wall-backed)

The bar was modelled three ways across three image batches: a square wall-backed L, then a
free-standing chamfered island, then (correctly) a wall-backed canted peninsula. Causes:

11. **The anchor was the worst-covered feature.** The official gallery had no clean bar shot
    and — critically — **no shot of behind the bar**. The single most important feature had
    the thinnest evidence, and no count-based check noticed (29 photos, anchor still wrong).
    → rule: coverage is scored **per feature**, and the anchor needs a footprint-resolving +
    a **behind** shot (Phase 1) before its shape is committed.
12. **Single-image over-fit.** Each better photo arrived alone and was over-read — "you can
    see past the bar to the garden" became "free-standing island," when behind it the spirits
    are shelved against the wall. → rule: **free-standing vs wall-backed is decided only by a
    behind shot**, never inferred from a front/oblique view; the audit must demand it.
13. **The schema couldn't express the real shape.** A canted/curved counter that returns to
    the wall needs more than a rectangle or one chamfer. → fix: explicit-polygon footprints
    (`footprint.poly`) + the deterministic rasteriser, collision still tile-based.

## The throughline

Every failure was a form of *agreement without independence* or *plausibility without
evidence*. The gates exist to force the opposite: derive from measured evidence, check it
with sources that never saw each other, and never let "passes the check" stand in for
"matches the place."
