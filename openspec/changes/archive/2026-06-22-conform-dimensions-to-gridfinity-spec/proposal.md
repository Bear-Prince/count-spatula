## Why

Generated bins are 0.5 mm too large on each footprint axis. The wall outline is drawn at `N×42`, but the
GridFinity spec — and `gridfinity_build123d`'s `BaseEqual`, which we build on — use `N×42 − 0.5`: a 0.5 mm total
clearance per axis so a bin seats in a baseplate and does not touch its neighbours. So our walls overhang the
Gridfinity base by 0.25 mm per side, which is visible in real output and would affect drawer fit. Confirmed by
measuring `BaseEqual`: a 1×1 footprint is 41.5 mm and a 2×4 is 83.5 × 167.5 mm, while our walls are 42 / 84 / 168.

## What Changes

- Draw the outer wall outline at `N×42 − 0.5` (matching the base footprint) instead of `N×42`, via a named
  clearance constant for spec traceability.
- Update the pocket-fit and base-corner-radius validation bounds to use the corrected outer dimensions.
- Keep the outer corner radius at 3.75 mm — already spec-correct (4 mm baseplate radius − 0.25 mm clearance).
- Add a regression test asserting the wall outline matches `BaseEqual`'s footprint within tolerance.

## Capabilities

### Modified Capabilities

- `gridfinity-utensil-bin`: add a dimensional-conformance requirement pinning the outer bin footprint to
  `N×42 − 0.5` and the outer corner radius to the GridFinity spec, so the bin body matches the Gridfinity base it
  sits on.

## Impact

- [cutlery_bin.py](../../../cutlery_bin.py): the outer wall outline in `KitchenBin`, the validation bounds in
  `BinParameters.validate()`, and a new clearance constant.
- Tests: footprint expectations updated to `N×42 − 0.5`; a regression test that the wall outline matches the
  `BaseEqual` footprint.
- [UAT.md](../../../UAT.md): refresh the millimetre footprints (each drops 0.5 mm; the file already flags this).
- No CLI or parameter-contract change; geometry only.
