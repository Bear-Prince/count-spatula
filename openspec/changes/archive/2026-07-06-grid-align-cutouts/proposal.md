## Why

Splitting a bin on a Gridfinity grid line is the one slicer cut that leaves both halves as
foot-complete, re-seatable Gridfinity pieces — it is how over-bed-size bins get printed. Two problems
prevented that from working cleanly:

1. The cutout's floor-to-wall corner was filleted along with its rim, coupling the cutout's position
   to `cutout_radius_mm`. UAT review found this left too little solid divider material at each wall
   end (e.g. ~18.75 mm on a default 2×4 bin) and, when first corrected, a sign error left the cutout
   still crossing the grid line rather than stopping short of it.
2. The cutout was a single, symmetric-about-centre offset. Real drawers mix bin lengths (e.g. 4-long
   and 5-long bins side by side); a symmetric cutout on a 5-long bin cannot align its slot with a
   4-long bin's slot at a shared end without an asymmetric offset per end.

## What Changes

- **Right-angle floor, filleted rim only.** The cutout's floor-to-wall corner is now sharp (built as
  a plain rectangle); only the wall-to-rim corner is filleted (`cutout_radius_mm`, default 10 mm).
  The floor's position no longer depends on the radius, and considerably more divider material
  remains at each wall end (e.g. ~33 mm vs ~21 mm on a default 2×4 bin, at default settings).
- **Per-end offsets, not a single symmetric one.** `cutout_offset_units: int` is replaced by
  `cutout_offset_start_units: int` and `cutout_offset_end_units: int` (each in whole Gridfinity
  units, default 1), so a bin's two ends can align independently with neighbouring bins of different
  lengths.
- **Corrected clearance direction.** The cutout's sharp floor edge now stops `CUTOUT_GRID_CLEARANCE_MM`
  (1 mm) *short* of its target internal grid line (not past it, as an earlier draft of this change
  had backwards), so the line itself — and a small margin around it — stays solid. A base split
  exactly on that line always cuts through uninterrupted material.
- **BREAKING (pre-publication, internal):** `cutout_offset_units` is replaced by the two per-end
  fields; `--cutout-offset-units` now takes one value (applies to both ends) or two (start and end
  independently, e.g. `--cutout-offset-units 1 2`).
- Add an explicit per-end minimum: each of `cutout_offset_start_units` / `cutout_offset_end_units`
  must be at least 1. The combined gap check (`grid_y − start − end ≥ 1` whole unit) generalises the
  earlier symmetric version and still restores "no cutouts below 3 units deep" as a deliberate rule.
- Add a check that the two rims cannot meet in the middle
  (`cutout_arc_start_mm + cutout_arc_end_mm < grid_y × pitch`), replacing the earlier
  radius-vs-offset coupling check (no longer applicable, since the floor no longer depends on the
  radius) with the equivalent "too large for the side" safety net.
- Add a check that `cutout_radius_mm` is less than the effective bin height, so the rim fillet has
  room to complete within the wall.
- Realign the **chop-board preset** to `cutout_offset_start_units = cutout_offset_end_units = 2`
  (unchanged from the previous draft's intent), now built on the corrected, per-end, right-angle-floor
  design.
- Establish the general principle: **default feature placement aligns to the Gridfinity grid**, and
  a feature's position and its cosmetic fillet radius should be decoupled wherever practical, so
  changing one does not silently move the other.

## Capabilities

### New Capabilities
<!-- None: this refines existing cutout behaviour rather than introducing a new capability. -->

### Modified Capabilities
- `gridfinity-utensil-bin`: the "Optional side cutouts" requirement changes to per-end grid-unit
  offsets with a sharp floor and a filleted rim, and the parameter-validation requirement changes to
  validate both ends independently, the combined gap, the rim-overlap safety net, and the
  radius-vs-wall-height check.
- `bin-presets`: the chop-board preset's cutout offset requirement is restated in per-end terms
  (unchanged value, 2 units each end).

## Impact

- **Code**: `cutlery_bin.py` (`cutout_offset_start_units` / `cutout_offset_end_units` fields,
  per-end offset/length/arc properties, the reworked `SideCutoutProfile` construction, validation,
  chop preset), `main.py` (`--cutout-offset-units` accepting one or two values).
- **Tests**: `tests/test_cutlery_bin.py` and `tests/test_cli_and_params.py` — the corrected
  grid-clearance direction (now physically probed, not just asserted analytically), asymmetric
  per-end offsets, the per-end and combined validation checks, the rim-overlap and
  radius-vs-height checks, and the CLI's one-or-two-value flag.
- **Docs**: the cutout cross-section diagram and README section are revised for the right-angle
  floor / filleted-rim shape and the per-end offset parameters.
- **Backward compatibility**: changes the cutout parameter contract and default geometry; safe
  pre-publication. No published models exist to break.
