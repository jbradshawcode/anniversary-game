# Adversarial audit checklist (Phase 3.5)

For the **cold subagent**. You are given: the photos, `ingame.png`, the spec JSON, and the
manifest footprint. You are **NOT** given `reconstruction.md` — that is the authoring
rationale, and reading it would make this check circular.

Your job is to **break the spec**, not bless it. Reconstruct the place from the photos
yourself *first*, then compare. Find disagreements.

## How to score

Each line below: **agree** / **disagree** / **unknown**, and **cite the photo(s)** that
prove or disprove it. "agree" with no citation is invalid. A vibe is "unknown."

## Relationship checks (the layout)

- [ ] Compass frame matches the oriented footprint (`long_axis_bearing`): which way does the
      building run, and does the spec's long axis agree?
- [ ] Anchor **shape & free-standing-ness** (do NOT assume it backs a wall): is it
      free-standing with circulation on several sides, or genuinely wall-backed? Trace its
      footprint — straight run / L / U / chamfered-angled peninsula / island? Count its tile
      run on each side and state which way the working face(s) point. **Disagree if the spec
      backs it onto a wall the photos show open, or squares off a shape the photos show
      chamfered/angled/curved.** A **free-standing** claim REQUIRES a photo of *behind* the
      feature (shelving-against-a-wall = wall-backed); do not accept "free-standing" inferred
      from a front/oblique view alone. (cite ≥2 photos, including a corner/oblique + a behind view)
- [ ] Each zone is in the right order along the long axis (e.g. the rearmost room is at the
      rear end, not the front).
- [ ] Each major fixed feature is on the wall the photos put it on.
- [ ] Vertical structure (columns / stairs) in plausible positions.

## Entrance checks (the #1 past failure — the scripts CANNOT catch this)

The fidelity gate only flags a door dead-centre; a door at the *wrong off-centre* tile passes
every script. You are the only check. For each door, **estimate its offset-from-corner in
tiles from the facade/aerial, then compare to the spec's exit tiles** — disagree on any gap
greater than ~2 tiles, and reject a `derived_from` that doesn't actually show the door there.

- [ ] Main entrance — your tile estimate vs the spec's; same wall? same offset?
- [ ] Rear / onward access — your tile estimate vs the spec's.
- [ ] Any secondary / service door present in the photos but missing from the spec?

## Fidelity checks (does it read as the place)

- [ ] Surface materials per zone match the photos (e.g. a different floor in one room).
- [ ] Surface treatment present where the photos show it (panelling / tiling / brick / bays).
- [ ] Furnishing density and seating plausible — tables have chairs; room isn't a bare hall.
- [ ] Seating **arrangements** match the photos, not just the count: a bench running along a
      wall is a continuous **banquette run** (tables fronting it, chairs on the room side
      only) — NOT isolated symmetric table-settings. Check booths / counter stools / lounge
      clusters likewise.
- [ ] Seating **counts & composition** (numeric, like the doors): from the photos, estimate
      per zone the # tables over its tile span, the table-type mix, and the spacing. Compare
      to the spec — **disagree** if it's a uniform comb of identical tables where the photos
      show a mixed, irregular set, or if a count is off by more than ~1.
- [ ] Nothing in the render is unrecognisable as its real-world referent.

## Currency check

- [ ] Are any spec features contradicted by the **most recent** high-trust photos (i.e. the
      spec encodes an old, since-refurbished layout)?

## Verdict

- List every **disagree** with its citation. These drive the next convergence round.
- State **unknowns** the human should resolve.
- Do **not** soften a disagreement into agreement to "converge." Disagreements are the
  product of this stage.
