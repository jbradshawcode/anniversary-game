# Dirty data — when the evidence disagrees

Online photos are not a clean snapshot. A venue may have been refurbished, rebranded,
extended, or reconfigured between shots. Treating a 2018 blog photo and a 2024 official
gallery image as one consistent layout is how you reconstruct a building that no longer
exists. Handle it explicitly.

## Date everything (Phase 1)

`gather.py` stamps each image with `capture_date` (from `--captured`, else EXIF, else
`unknown`) and a `trust` tier. `resolve.py` records `manifest.currency.street_view`.

**Pass `--captured` — treat it as mandatory.** EXIF is stripped from almost all web images
(CDNs, social, most CMSes re-encode and drop it), so the EXIF fallback rarely fires; relying
on it leaves everything `unknown`. Get the date from the page/source context (post date,
"refurbished 2023" copy, review timestamp) and pass it. Undated images can't be
conflict-resolved — so in practice the **trust tier does the heavy lifting**, with dates as a
tie-breaker when you actually have them.

## Trust tiers

| Tier | Source | Notes |
|------|--------|-------|
| 3 | `official`, `estate-agent` | operator's own site, sales/letting listing with plans |
| 2 | `camra`, `review` | curated guides (e.g. CAMRA for pubs), recent review-site galleries |
| 1 | `blog` | personal posts; often old |
| 0 | `unknown` | undated / unsourced — corroborate before trusting |

## Conflict resolution

When two sources disagree about a feature (the anchor's shape, a wall, a room's use):

1. **Newest wins**, if dates are known and far apart — the layout changed.
2. **Highest trust wins**, when dates are close or unknown.
3. **The footprint / floor plan overrides any photo** for shape and wall positions.
4. If it still won't resolve, **flag it** in `reconstruction.md` §5 and §7 and hand it to
   the audit — do not silently pick one and move on.

**Never average two layouts.** A blend of two real configurations is a third, fake one.

## Tells that the layout changed between photos

- The anchor in a different position / shape across two galleries.
- A wall present in one set, absent in another (knock-through).
- Different flooring, surface colour, or signage era in the same room.
- An extension / conservatory in the aerial but not in older interior shots (or vice-versa).

When you see these, anchor to the **most recent high-trust set** and the **current
footprint**, and note the discrepancy.
