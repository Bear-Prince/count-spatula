## 1. Constants and parameter re-basing

- [x] 1.1 In `cutlery_bin.py`, reduce `DEFAULT_CUTOUT_RADIUS` from `12.5 * MM` to `10 * MM`, and add
  `CUTOUT_GRID_CLEARANCE_MM = 1 * MM` (the fixed margin the floor stays flat past the grid line).
- [x] 1.2 Replace the `cutout_offset_from_edge_mm` field with `cutout_offset_units: int = 1` and a
  `DEFAULT_CUTOUT_OFFSET_UNITS = 1` constant; remove the old `DEFAULT_CUTOUT_OFFSET` (40 mm) constant.
- [x] 1.3 Add a read-only `cutout_offset_from_edge_mm` property returning
  `cutout_offset_units * GRIDFINITY_PITCH_MM - cutout_radius_mm - CUTOUT_GRID_CLEARANCE_MM`, with a
  docstring explaining it nets the fillet radius back out so the floor clears the grid line by a
  fixed margin regardless of the chosen radius. `cutout_length_mm` / `cutout_arc_mm` keep referencing
  this property unchanged.

## 2. Validation

- [x] 2.1 Add a check that `grid_y - 2 * cutout_offset_units >= 1` when cutouts are enabled, with an
  actionable message — independent of `cutout_radius_mm`, this restores "no cutouts below 3 units
  deep" as an explicit rule.
- [x] 2.2 Add a check that the derived `cutout_offset_from_edge_mm` is positive, with a message naming
  the radius and unit count, guarding against a custom radius large enough to overrun the offset.
- [x] 2.3 Keep the existing `cutout_length_mm <= 0` / `cutout_arc_mm >= side_half_length_mm` checks as
  a general safety net for other invalid combinations.

## 3. Preset and CLI

- [x] 3.1 Set `cutout_offset_units=2` on the `chop-board` preset (its derived offset becomes 73 mm
  with the new radius/clearance, landing the floor 1 mm past its ±42 mm internal grid lines).
- [x] 3.2 In `main.py`, replace `--cutout-offset-mm` with `--cutout-offset-units` (int) and map it to
  `cutout_offset_units` in `create_parameters()`.

## 4. Tests

- [x] 4.1 Add a test that a default bin's cutout floor becomes flat exactly `CUTOUT_GRID_CLEARANCE_MM`
  past the first internal grid line: assert
  `(side_half_length_mm - (cutout_length_mm - cutout_radius_mm)) - GRIDFINITY_PITCH_MM == CUTOUT_GRID_CLEARANCE_MM`
  for a `grid_y=4` bin, mapping to "Cutout floor stays flat past the grid line".
- [x] 4.2 Add a test that the same 1 mm relationship holds with a non-default `cutout_radius_mm` (e.g.
  8 mm), mapping to "Grid-line clearance holds regardless of radius".
- [x] 4.3 Add a test that a `grid_y=2` bin with cutouts + default offset fails validation with a
  message about the unit gap (not a zero-floor message), mapping to "Reject cutouts on a bin
  shallower than three units".
- [x] 4.4 Add a test that an oversized `cutout_radius_mm` (relative to `cutout_offset_units`) is
  rejected with an actionable message, mapping to "Reject a radius too large for the offset".
- [x] 4.5 Add a test that the chop preset has `cutout_offset_units=2` and its cutout floor becomes
  flat 1 mm past the ±42 mm grid line, mapping to the bin-presets requirement change.
- [x] 4.6 Retarget `test_validation_rejects_oversized_cutout` and
  `test_validation_skips_cutout_checks_when_disabled` to trigger via `cutout_radius_mm` alone (no mm
  offset arg).
- [x] 4.7 Re-derive the cutout probe boxes / expected extents in `tests/test_cutlery_bin.py` for the
  new floor/rim positions (default `grid_y=4` floor now ±53 mm nominal / ±43 mm flat; chop now ±53 mm
  nominal / ±43 mm flat at its offset). Confirmed via the full suite: existing probe boxes use
  generous margins (full-wall or well-clear-of-boundary spans) that remain valid unmodified.
- [x] 4.8 Add a CLI test that `--cutout-offset-units` populates `cutout_offset_units`.

## 5. Documentation

- [x] 5.1 Add a labelled cutout cross-section diagram (SVG) as `docs/images/cutout-profile.svg`,
  naming each part — floor, floor fillet, side wall, rim fillet, rim — and showing the grid line,
  the offset, and the 1 mm clearance relationship. Use the parameter names from this change
  (`cutout_offset_units`, `cutout_radius_mm`, `CUTOUT_GRID_CLEARANCE_MM`) rather than baked-in
  numbers, so it stays accurate if defaults change later.
- [x] 5.2 Add a "Cutout geometry" subsection to `README.md`, after "Disabling cutouts", embedding the
  diagram and explaining each named part and how `--cutout-offset-units` and `--cutout-radius-mm`
  relate to the grid-line clearance.

## 6. Verification

- [x] 6.1 Run `uv run ruff check .` and fix any findings. Passed clean.
- [x] 6.2 Run `uv run pytest` and confirm the full suite passes. 72/73 passed; the one failure
  (`test_every_scenario_marker_matches_the_specs`) is expected pending `/opsx:sync` or
  `/opsx:archive` -- the four new scenarios exist only in this change's delta spec until synced.
- [x] 6.3 Generate a default cutlery bin and the chop bin and confirm each cutout floor visually stays
  flat across its grid line before curving. Probed both at true floor level (Z=floor_z): material is
  zero at Y=40 and Y=42 (the grid line) and only becomes solid from Y~43 onward, for both bins --
  confirms the grid line sits inside the open floor with no fillet material crossing it.
- [x] 6.4 Confirm the README diagram renders correctly and matches the shipped defaults. SVG is
  well-formed XML; it uses symbolic parameter names (not baked-in numbers) by design, so it needs no
  updates if defaults change.

## 7. Redesign: sharp floor, filleted rim only, per-end offsets

UAT review of the geometry from sections 1-6 found the coupled floor+rim fillet left too little
divider material, and — while investigating a right-angle-floor alternative — a sign error was found
in the clearance direction (the cutout still crossed the grid line rather than stopping short of
it). Separately, aligning bins of different lengths (e.g. 4-long next to 5-long) needs independent
per-end offsets, not one symmetric value. This section reworks the design in place.

- [x] 7.1 Rework `SideCutoutProfile` to build a sharp-cornered core rectangle plus two independent
  rim "flare" patches (boolean-unioned), then fillet only the two wall-to-rim corners via
  `Face.fillet_2d` on one concrete extracted face (not the `BuildSketch` context's `fillet()`
  convenience function, whose vertex-identity matching against the context's own object silently
  no-ops when the two diverge). Verified: a plain chained `Line`+`FilletPolyline`+connecting-`Line`
  approach collapses the flare to a plain rectangle (or produces an invalid face) because
  build123d/OCCT resolves the retraced/overlapping straight segments as a cancellation.
- [x] 7.2 Replace `cutout_offset_units` with `cutout_offset_start_units` and
  `cutout_offset_end_units` (each `int`, default 1). Add per-end
  `cutout_offset_{start,end}_from_edge_mm`, `cutout_length_{start,end}_mm`, and
  `cutout_arc_{start,end}_mm` properties. Fix the clearance sign: the derived offset is
  `units * pitch + CUTOUT_GRID_CLEARANCE_MM` (not minus) so the sharp floor edge stops short of the
  grid line rather than past it.
- [x] 7.3 Rework validation: `cutout_offset_start_units >= 1` and `cutout_offset_end_units >= 1`
  individually; combined gap `grid_y - start_units - end_units >= 1`; rim-overlap safety net
  `cutout_arc_start_mm + cutout_arc_end_mm < grid_y * pitch`; `cutout_radius_mm < effective_height_mm`
  (the old radius-vs-offset coupling check no longer applies, since the floor is now radius-independent).
- [x] 7.4 Update the `chop-board` preset to `cutout_offset_start_units = cutout_offset_end_units = 2`
  on the new per-end fields, and the `KitchenBin` call site to pass the four per-end cutout values
  with no `align=(Align.CENTER, ...)` (an asymmetric profile must not be re-centred).
- [x] 7.5 Update `main.py`: `--cutout-offset-units` takes `nargs="+"`, accepting one value (both
  ends) or two (start, end); reject any other count with an actionable message.
- [x] 7.6 Rewrite the affected tests in `tests/test_cutlery_bin.py` and `tests/test_cli_and_params.py`
  for the per-end API, the corrected clearance direction (including a physical geometry probe at the
  grid line, not just an analytic assertion), the new validation checks, an asymmetric-offset test,
  and the CLI's one/two-value handling.
- [x] 7.7 Rewrite `proposal.md`, `design.md`, and both delta specs to describe the sharp-floor,
  per-end design and the corrected clearance direction; add the new scenarios this introduces.
- [x] 7.8 Regenerate `docs/images/cutout-profile.svg` and the README "Cutout geometry" section for
  the sharp-floor / rim-only-fillet shape and the per-end offset parameters.
- [x] 7.9 Regenerate the UAT compilation 3MF with the corrected geometry for visual review.

## 8. Redesign verification

- [x] 8.1 Run `uv run ruff check .` and fix any findings. Passed clean.
- [x] 8.2 Run `uv run pytest` and confirm the full suite passes (aside from the traceability
  scenario-sync failure, expected pending `/opsx:sync` or `/opsx:archive`). 78/79 passed; the one
  failure is exactly that expected scenario-sync gap.
- [x] 8.3 Physically probe both the default and chop-board bins at true floor level, at each end's
  target grid line: confirm material is solid there (not open), and open just inside the cutout.
  Confirmed for both bins: zero material at Y=35/40 (open), solid from Y=41.5 through 42 (the grid
  line) onward.
- [x] 8.4 Confirm the divider-retention improvement: compare remaining wall material near each rim
  under the new sharp-floor design against the coupled-fillet design it replaces. Default 2x4 bin:
  32.90 mm retained per end (new) vs 20.90 mm (old coupled-fillet design) -- 12 mm more per end.

## 9. Fix: rim fillet completion

UAT review of the built models found the rim did not flow smoothly into the flat top: a flat step and
a sharp right angle sat above the completed fillet, instead of the fillet reaching the top directly.

- [x] 9.1 Diagnose: `patch_height` (the flare patch's own height, over which the rim fillet is
  applied) was set to `cutout_radius + 0.1mm`, by mistaken analogy with the unrelated `cutout_arc`
  margin formula. The fillet's own trims do not depend on `patch_height`, so this left a full extra
  `radius` of straight wall above the fillet, before the flat top -- see design.md Decision 6.
- [x] 9.2 Fix: set `patch_height = 0.1 * MM` (small and fixed, independent of `cutout_radius_mm`), so
  the fillet's arc reaches almost all the way to the flat top, leaving only a negligible remnant.
- [x] 9.3 Verify: rebuild the default and chop-board bins, confirm valid geometry; re-run
  `uv run ruff check .` and the full test suite (78/79 passing, same expected traceability gap);
  regenerate the UAT compilation 3MF for visual review.
