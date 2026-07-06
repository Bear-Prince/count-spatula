## Context

`SideCutoutProfile` in `cutlery_bin.py` builds the slot cut through each side wall. An earlier draft
of this change filleted both the floor-to-wall corner and the wall-to-rim corner with one shared
radius (`FilletPolyline` fillets every interior vertex of a polyline with a single radius). UAT
review of the built models found two problems: (1) coupling the floor's position to the radius left
too little solid divider material at each wall end, and (2) the derived offset's clearance sign was
backwards, so the cutout still crossed the target grid line rather than stopping short of it.
Separately, the offset was a single value symmetric about the wall's centre, which cannot align two
different-length bins' cutouts at a shared end (e.g. a 4-long and a 5-long bin in the same drawer).

This design keeps the floor sharp (independent of the radius) and rounds only the rim, and replaces
the single offset with independent per-end offsets in whole grid units.

## Goals / Non-Goals

**Goals:**

- The cutout's sharp floor edge stops a fixed clearance (1 mm) *short* of its target internal grid
  line on each end, so a base split on that line always cuts through solid material.
- The floor's position does not depend on `cutout_radius_mm`; only the rim's shape does.
- Each end's offset (in whole grid units) is independently configurable, so two bins of different
  lengths can align their cutouts at a shared end.
- Chop-board preset unchanged in intent (2 units each end), rebuilt on the corrected design.

**Non-Goals:**

- Aligning the rim to the grid (it still overhangs a little; the floor is what matters for a clean
  base split — unchanged from the earlier draft's position, still deferred).
- Any split/combine tooling, or aligning divider positions to the grid.
- A configurable grid-clearance parameter (`CUTOUT_GRID_CLEARANCE_MM` stays a fixed module constant).

## Decisions

### 1. Sharp floor, filleted rim, built as sharp-rectangle-plus-patches rather than one filleted polyline

`FilletPolyline` fillets *every* interior vertex it is given with one radius — there is no way to
leave one corner sharp and round another within a single call. Attempting to chain a plain `Line`
for the floor corner with a `FilletPolyline` for the rim corner, plus a long connecting line across
the top spanning both ends, produces an invalid or degenerate face: build123d/OCCT resolves two
straight segments that retrace the same range in opposite directions as a cancellation (the retraced
portion vanishes), collapsing the intended flare back to a plain rectangle. Mirroring a single
filleted half (as the very first draft did) sidesteps this via a boolean-style merge, but only works
for a *symmetric* shape — not usable once the two ends can differ.

The working construction: build the sharp-cornered core as a plain rectangle (`(-length_start, 0)` to
`(length_end, height)`), then boolean-union two small rectangular "flare patches" onto it — one per
end, spanning from the wall's `x` position out to the rim's `x` position, over a height range
`[height − patch_height, height]`. This produces a single valid face with two new sharp corners
(where each patch's inner edge meets the main rectangle), which are then rounded with
`Face.fillet_2d(radius, [those two vertices])`, operating on one concrete `Face` object extracted
after the unions (not through the `BuildSketch` context's own `fillet()` convenience function, whose
vertex-identity matching against the context's internal object silently no-ops when the two diverge).

`patch_height` is a small fixed value (0.1 mm), **independent of `radius`** — this needed a
correction during UAT (see Decision 6): the fillet's own trims (into the patch horizontally by
`radius`, and down into the wall by `radius`) don't depend on the patch's height at all, so sizing
`patch_height` to match `radius` (an early draft's mistake, reusing the unrelated `cutout_arc`
margin formula) left a full extra `radius` of straight wall sitting *above* the completed fillet,
before the flat top — visible as a flat step and a sharp right angle where the rim should smoothly
continue. With `patch_height` small and independent, the fillet's arc reaches almost all the way to
the flat top, leaving only a negligible (0.1 mm) straight remnant — functionally indistinguishable
from the arc reaching the top directly, and invisible at print resolution.

*Alternative considered:* keep floor-fillet + rim-fillet (the original design) and just fix the
clearance sign. Rejected per the UAT finding — it leaves materially less divider at the wall ends
and keeps the floor's position needlessly coupled to the radius.

### 2. Per-end offset in whole grid units: `cutout_offset_start_units` / `cutout_offset_end_units`

Each end independently reserves a whole number of grid units of solid wall (default 1). This is the
parameter the project owner asked for directly: "the distance between the end of the bin and the
edge of the cutout, in grid squares" per end, not a single symmetric width. It also removes the
gap-parity trap a centred "gap width" parameterisation would have had (a centred even/odd-square gap
only lands on grid lines when its parity matches the bin depth); per-end offsets have no such trap —
any combination of whole units on each end keeps both edges grid-aligned.

### 3. Clearance direction: floor edge stops short of the line, not past it

`cutout_offset_{start,end}_from_edge_mm = units × pitch + CUTOUT_GRID_CLEARANCE_MM` (note the `+`,
not `-`). Deriving the real floor position:
`cutout_length_mm = side_half_length_mm − (units·pitch + clearance) = (side_half_length_mm − units·pitch) − clearance`,
i.e. exactly `clearance` mm *short of* the target grid line (`side_half_length_mm − units·pitch`).
Because the floor is now sharp, there is no fillet-radius term to net out — the offset depends only
on the unit count and the fixed clearance, decoupled from `cutout_radius_mm` entirely.

*Correction recorded:* an earlier version of this property subtracted the clearance instead of adding
it, which computes a *smaller* reserved margin — pushing the cutout edge *closer* to the wall's outer
edge than the grid line, i.e. past the line rather than short of it. Caught by direct geometry probing
(material was absent, not present, at the target grid line) before this change was applied.

### 4. Validation: per-end minimums, combined gap, rim-overlap safety net, radius-vs-height

- `cutout_offset_start_units ≥ 1` and `cutout_offset_end_units ≥ 1` individually.
- `grid_y − start_units − end_units ≥ 1` (at least one whole unit of clean gap between the two
  reserved margins) — the direct generalisation of the earlier symmetric `grid_y − 2×units ≥ 1`
  check, restoring "no cutouts below 3 units deep" for a symmetric bin as a deliberate, radius-
  independent rule.
- `cutout_arc_start_mm + cutout_arc_end_mm < grid_y × pitch` — the two rims must not meet in the
  middle. Replaces the earlier draft's radius-vs-offset coupling check (moot now the floor doesn't
  depend on the radius) with the equivalent "cutout too large for the side" safety net.
- `cutout_radius_mm < effective_height_mm` — the rim fillet (plus its 0.1 mm patch margin) needs
  room within the wall height to complete.

### 5. Realign the chop-board preset

`cutout_offset_start_units = cutout_offset_end_units = 2` (unchanged value from the previous draft),
rebuilt on the corrected per-end, sharp-floor design. Splittable at its ±42 mm internal grid lines,
as intended.

### 6. `patch_height` is a small fixed value, decoupled from `cutout_radius_mm`

Found during UAT review of the first build of this redesign: `patch_height` (the flare patch's own
vertical extent, over which the wall-to-rim fillet is applied) was set to `radius + 0.1mm`, by
analogy with the unrelated `cutout_arc = cutout_length + radius + 0.1` margin. But the fillet's own
trims (horizontally into the patch by `radius`, and vertically down into the wall by `radius`) do not
depend on `patch_height` at all — that value only sets how much of the patch's own straight outer
wall remains *above* the completed fillet, before the flat top. Sizing it to `radius + 0.1mm` left a
full extra `radius` of straight wall there, visible as a flat step and a sharp right angle where the
rim should continue smoothly into the flat top. Setting `patch_height = 0.1mm` (small and fixed,
independent of `radius`) fixes this: the fillet's arc now reaches almost all the way to the flat top,
leaving only a negligible straight remnant, matching the intended "smooth rim" shape.

## Risks / Trade-offs

- **Boolean-patch construction is more code than a single `FilletPolyline` call** → Documented
  in-line with the "why" (Decision 1); covered by a direct geometry probe (material solid at the
  grid line) so a future refactor that reintroduces the retrace/cancellation bug fails a test rather
  than shipping silently.
- **Two offset fields instead of one** → More parameters, but directly matches the real use case
  (aligning bins of different lengths) that a single symmetric offset could not serve.
- **Existing cutout probe-box tests assume prior extents** → Re-derive affected probe boxes/expected
  values; confirmed via the full suite that the wall/divider probe boxes (built with generous
  margins) remain valid unmodified.
- **CLI contract**: `--cutout-offset-units` changes arity (was a single int, now `nargs="+"` taking
  1 or 2 values) → Documented in the proposal as a pre-publication breaking change; a 3+-value input
  is rejected with an actionable message.
