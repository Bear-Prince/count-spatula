## Context

`KitchenBin` draws its outer wall outline as a `RectangleRounded` of `grid_x×42` by `grid_y×42`, sitting on a
`gridfinity_build123d` `BaseEqual`. But `BaseEqual` emits a footprint of `N×42 − 0.5` (measured: 1×1 → 41.5 mm,
2×4 → 83.5 × 167.5 mm) — the GridFinity 0.5 mm total clearance per axis. So the walls overhang the base by 0.25 mm
per side. The grid pitch (42 mm), height unit (7 mm), and the 3.75 mm outer corner radius already match the spec;
only the footprint clearance is wrong.

## Goals / Non-Goals

**Goals:**

- Outer wall footprint = `N×42 − 0.5`, matching the Gridfinity base, with the clearance as a named constant.
- Validation bounds use the corrected outer dimensions.
- A regression test that the wall outline matches the `BaseEqual` footprint.

**Non-Goals:**

- Changing the base/foot profile (owned by `gridfinity_build123d`).
- Any CLI or parameter-contract change.
- Re-deriving pitch/height-unit/corner-radius (already spec-correct).

## Decisions

- **Subtract a named clearance constant.** Add `GRIDFINITY_CLEARANCE_MM = 0.5` and compute the outer outline as
  `grid×PITCH − GRIDFINITY_CLEARANCE_MM` per axis. *Alternative:* derive the outline from `base_top`'s bounding
  box at build time. Rejected — the spec value is the source of truth and an explicit constant is clearer and
  testable than reading back a generated face; the regression test still cross-checks against `BaseEqual`.
- **Clearance is total per axis, not per unit.** Confirmed by measurement (the gap is 0.5 mm whether N is 1 or 4),
  so subtract `0.5` once per dimension, not `0.5×N`.
- **Validation uses the corrected outer.** `max_outer_length`/`max_outer_width` and the base-corner-radius bound
  become `grid×PITCH − GRIDFINITY_CLEARANCE_MM`. The wall-derived default pocket already insets from the outer, so
  it follows automatically.
- **Corner radius unchanged at 3.75 mm.** It is the 4 mm baseplate radius minus the 0.25 mm per-side clearance.

## Risks / Trade-offs

- **Every bin's footprint shrinks 0.5 mm.** [Risk] All outputs (including the `chop-board` preset) change. → This
  is the intended correction toward spec, accepted pre-1.0. Mitigation: it is a fix, regression-tested; UAT.md
  footprints are refreshed.
- **Cutout through-extrude distance.** [Risk] The cutout extrudes `±(grid_x×42/2 + 1)`; with the footprint now
  0.5 mm smaller the `+1` margin still fully clears the wall, so no change is required — but the test suite must
  still confirm the slot passes fully through. → Mitigation: existing cutout regression tests cover this.

## Migration Plan

1. Add `GRIDFINITY_CLEARANCE_MM` and apply it to the outer outline and validation bounds in `cutlery_bin.py`.
2. Update the affected test expectations (footprints) and add the wall-vs-base regression test.
3. Run lint + the full suite; UAT-regenerate a couple of bins to confirm `83.5` / `167.5` footprints.
4. Refresh UAT.md footprints; archive.

All within one PR. Rollback is reverting the PR.

## Open Questions

- None — pitch, height unit, and corner radius are already spec-correct; only the footprint clearance changes.
