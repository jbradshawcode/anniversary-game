# Reconstruction template (Phase 2)

Copy to `refs/<slug>/reconstruction.md` and fill from the photos + footprint + aerial,
**before** authoring the tile spec. Cite every claim by filename. Ban "looks like" — make an
explicit spatial claim or mark it unknown.

> In an ensemble run, each cold subagent fills sections 1–4 from the photos alone (no shared
> state). The lead then fills section 5 (reconcile) and section 6 (draft plan).

## Worked micro-example — turning a photo into a tile claim

This is the move the whole method hinges on; do it explicitly, like this:

> **Anchor, from `gallery/02` + `gallery/21`.** In `02` the camera looks down the room from
> the entrance; the bar's panelled front runs left-to-right across ~⅔ of the frame and the
> back-gantry of bottles is *behind* it against the left wall. In `21`, shot from the far end,
> the same gantry is on the right with a column at the bar's open corner — so the two angles
> agree the gantry backs the **same long wall**, servery faces *into* the room.
> Footprint long side ≈ 25 m ≈ 25 tiles; the bar spans ~⅔ → **~11 tiles**, starting ~⅓ along.
> *Claim:* gantry on the top wall cols 9–19; servery faces down; column at the open (right) end.
>
> **Door, from `facade.jpg` + `gallery/01`.** The King St frontage is the short (≈11 m) wall.
> The entrance is **not centred** — it sits right-of-centre with a carriage arch further right.
> Right-of-centre on an 11-tile wall ≈ tile 7 of 11. *Claim:* front door at the street wall,
> offset ~7 — **not** the mid-wall default.

Note what makes these usable: each cites ≥2 photos, converts a fraction-of-frame into a
tile count via the footprint, and ends in a concrete tile claim — never "looks like a bar".

## 1. Compass frame (derive, don't guess)

- Footprint oriented dims (from `manifest.footprint`): long ____ m × short ____ m,
  `long_axis_bearing` ____°.
- Therefore the building runs ____ (e.g. bearing ~3° → N–S). Frontage faces ____ (facade
  heading from manifest).
- Rear / onward space is: ____   Neighbours: ____ (which side).
- Source images: ____

## 2. Zones along the long axis (front → back)

List zones in order, then the tile columns they map to. **The aerial gives footprint extent,
massing, garden/extensions and skylights — it does NOT give interior room shapes or widths
(you can't see internal walls; roof structure is ambiguous).** Take each zone's shape and
relative width from the **interior photos** (and a floor plan if found); cite the photo, not
the roof. Flag any zone whose width you could only guess.

| Zone | Order/rough split (long axis) | → tile cols | Shape/width from (photo) |
|------|-------------------------------|-------------|--------------------------|
| | | | |

## 3. Anchor: the dominant fixed feature (resolve FIRST, most carefully)

The single thing the photos are *about* — e.g. a bar/servery, altar, counter, stage,
fountain, staircase. Place everything else relative to it.

- What is the anchor? ____
- Which wall / position does it sit against or in? ____  (cite ≥2 photos, different angles)
- Which way does its "front" face (the side people approach)? ____
- Shape & size (along a wall / L / peninsula / island / central)? ____
- Cite: ____

## 4. Entrances & other major features (each cited; entrances located, not centred)

**Entrances — the #1 past failure. Locate each on the facade/aerial, give a tile position,
and this becomes the spec's `derived_from`.**

| Entrance / route | Where on facade/aerial | → wall + tiles | Evidence |
|------------------|------------------------|----------------|----------|
| Main entrance | | | |
| Rear / onward access | | | |
| Secondary / service door | | | |

Generic categories — fill the rows that apply, add place-specific ones, delete the rest:

| Feature category | Wall / location | Backs onto / faces | Photos |
|------------------|-----------------|--------------------|--------|
| Major fixed features (e.g. fireplace, conservatory, stage) | | | |
| Vertical structure (columns, stairs, mezzanine) | | | |
| Fixed seating / fittings (e.g. banquettes, pews, shelving) | | | |
| Glazing / openings (windows, bays, rooflights) | | | |
| Surface treatment (panelling, wainscot, tiling, brick) | | | |

## 4b. Seating arrangements (classify the ARCHETYPE — don't list loose furniture)

Seating reads right only if you capture the *pattern*, not the atoms. For each seating area
name its archetype + how it's composed; this maps straight to the spec encoding:

| Archetype | What to capture | Encodes as |
|-----------|-----------------|------------|
| **Banquette run** (bench fixed along a wall, tables in front, chairs on the room side only) | which wall, run length (tiles), # tables, which side the chairs are | a long `banquette` along the wall + `table`s with `against: <that wall>` + `seats` |
| **Booth** (bench both sides of a table) | wall, # bays | two `banquette`s either side of a `table` |
| **Free-standing set** (chairs all round) | # tables, seats each | `table` + `seats: N` (no `against`) |
| **Counter / window stools** | along which edge, # stools | stools along the bar/window edge |
| **Lounge cluster** (sofas/armchairs round a low table) | where | low `table` + `armchair`s |
| **Pew / fixed rows** | orientation, # rows | repeated benches |

Default failure to avoid: a wall bench decomposed into a short block + symmetric table-settings.
If a bench runs along a wall, it's a **run** — say so here.

**MANDATORY fixtures count — measure it, don't eyeball it.** Detail is the dimension runs
keep getting wrong because it's captured as prose and invented by the author. Apply the same
measure→tile move you used for the anchor: per zone, count the furniture from the photos and
state the numbers. A uniform comb of identical tables is the failure mode — real rooms mix
types (dining / poseur / cast-iron bistro / lounge) and spacing.

| Zone | Archetype | Wall/area | Span (tiles) | # tables | pitch/spacing | table type(s) + seats | mix notes | cite |
|------|-----------|-----------|--------------|----------|---------------|-----------------------|-----------|------|
| | | | | | | | | |

## 5. Reconcile (lead only — across the independent passes)

- **Agree** (locked, high confidence): ____
- **Disagree** → ambiguity or dirty data. For each: which read wins and why (footprint /
  floor plan / newest+highest-trust photo), or "flag for audit": ____
- Dirty-data conflicts carried from Phase 1 (feature, sources, winner): ____

## 6. Draft plan

Compass-labelled ASCII sketch at the chosen grid size (may exceed 20×15 and scroll — size to
the place), anchor placed first, doors at their derived positions. **An exterior/street need
not be enclosed** — buildings line one or more edges, the open ends are exits, and anything
off-map stays black; don't draw walls you can't see.

```
Interior (enclosed):              Street/exterior (open):
        N                          [== building frontages ==]  <- wall (facade)
  +----------------------+      ===                          ===   <- open ends (exits)
W |                      | E        carriageway / pavement
  |                      |       [== frontages / off-map (black) ==]
  +----------------------+
        S
(label each edge from YOUR compass frame: front/entrance, rear/onward, neighbour)
```

## 7. Open questions / low-confidence items

Anything not corroborated by ≥2 photos, or where the ensemble disagreed and the footprint
didn't settle it — flag for the audit, do not invent.
