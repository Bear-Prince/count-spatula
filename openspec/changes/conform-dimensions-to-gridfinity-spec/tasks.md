## 1. Apply the GridFinity clearance

- [x] 1.1 Add a `GRIDFINITY_CLEARANCE_MM = 0.5` constant to `cutlery_bin.py`.
- [x] 1.2 In `KitchenBin`, draw the outer wall outline at `grid_x×PITCH − GRIDFINITY_CLEARANCE_MM` by
  `grid_y×PITCH − GRIDFINITY_CLEARANCE_MM` instead of the full `grid×PITCH`.
- [x] 1.3 Update `BinParameters.validate()` so `max_outer_length`/`max_outer_width` and the base-corner-radius
  bound use the corrected outer dimensions.

## 2. Tests

- [x] 2.1 Update existing footprint expectations to `N×42 − 0.5` (default 2×4 → 83.5 × 167.5; chop-board 4×6 →
  167.5 × 251.5).
- [x] 2.2 Add a regression test asserting the bin's outer footprint matches a `BaseEqual` of the same grid within
  meshing tolerance (no overhang).
- [x] 2.3 Confirm the cutout/divider regression tests still pass (the slot still clears the slightly smaller wall).

## 3. Verification and UAT

- [x] 3.1 Run `uv run ruff check .` and fix findings.
- [x] 3.2 Run `uv run pytest` and confirm the full suite passes.
- [x] 3.3 Regenerate a default bin and the `chop-board` preset; confirm footprints are 83.5 × 167.5 and
  167.5 × 251.5.
- [x] 3.4 Refresh the millimetre footprints in `UAT.md`.
- [ ] 3.5 Archive the change so the spec delta folds into `openspec/specs/`.
