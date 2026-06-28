## Context

`check_print_bed(grid_x, grid_y, bed_x, bed_y)` computes a footprint as `grid×42` and warns when it exceeds the bed
on X or Y. It never measures the real model, never checks height, and only makes sense for plain grid bins. `main.py`
calls it *before* building the part, using the grid. Its tests were lost when `test_utensil_bin.py` was deleted in
the unification. This change makes the fit check operate on the model's real bounding box (X, Y, Z) and restores
coverage — the dependable "does it fit?" foundation the later splitting work needs.

## Goals / Non-Goals

**Goals:**

- Check the model's actual bounding box (X, Y, Z) against bed X/Y and an optional max print height.
- Add a `--bed-z` flag; height is checked only when it is given.
- Keep behaviour non-blocking (warn to stderr, still export, exit 0).
- Restore and extend the print-bed tests.

**Non-Goals:**

- Rotating/reorienting the model to make it fit (risks overhangs and bad infill — explicitly excluded).
- Splitting an oversized model into parts, or arranging parts on the plate (later journey steps).

## Decisions

- **`check_print_bed` takes plain dimensions, not the part.** New signature
  `check_print_bed(model_x_mm, model_y_mm, model_z_mm, bed_x_mm, bed_y_mm, bed_z_mm) -> list[str]` (all millimetres).
  `main.py` measures `part.bounding_box().size` and passes the three numbers. *Alternative:* pass the build123d
  part and measure inside. Rejected — keeping it numeric means the tests stay fast (no geometry build) and the
  function is trivially unit-testable, which is how the old check was already structured. *Acceptance:* calling it
  with numbers yields the right warnings; no geometry build needed in its tests.
- **Default print volume, millimetres only.** Ship `DEFAULT_BED_X_MM = 220`, `DEFAULT_BED_Y_MM = 220`,
  `DEFAULT_BED_Z_MM = 240` as the `--bed-x`/`--bed-y`/`--bed-z` defaults, so all three axes are always checked. Bed
  dimensions are plain millimetres with **no unit conversion** — unlike the bin height, which keeps its unit option.
  *Acceptance:* a plain invocation checks against 220 × 220 × 240; an override replaces just that axis's value.
- **Build the part, then always run the bed check.** Because the print volume now has defaults, the check runs on
  every invocation: `main` builds the part, measures `part.bounding_box()`, runs the check, then exports. The
  existing CLI test fakes (which returned a bare `object()`) must return a stub part exposing a `bounding_box()`.
  *Acceptance:* an oversized model still exports (non-blocking) with a warning to stderr.
- **As-oriented evaluation, no rotation.** The check compares the model's X/Y/Z as generated; it never tries
  rotating to fit. *Acceptance:* a model that would only fit rotated is still reported as exceeding.

## Risks / Trade-offs

- **Bounding box vs nominal footprint.** [Risk] The real bbox (incl. base feet / any lip) differs slightly from
  `grid×42 − 0.5`. → That difference *is* the printed extent, which is exactly what a fit check should use, so this
  is an improvement, not a problem. The wall-vs-base regression test from the previous change already pins the
  footprint.
- **CLI ordering change.** [Risk] Building before the check means a build error surfaces before the warning. → The
  build already had to happen to export; the only change is the warning now follows the build. No real downside.
- **The default bed flags the chop-board.** [Risk] The `chop-board` preset is 251.5 mm long, so against the default
  220 mm depth it now warns by default. → That is correct — it genuinely does not fit a 220 mm bed, so the warning
  is the feature working (and it motivates the later splitting step). A user with a larger printer passes `--bed-y`.

## Migration Plan

1. Change `check_print_bed` to the dimension-based signature and add the Z check.
2. Reorder `main.py` to build, measure the bbox, check, then export; add `--bed-z`.
3. Restore/extend the print-bed tests (fits, exceeds X, exceeds Y, exceeds Z, no bed, height-only-when-configured).
4. Generate the UAT models, then archive.

All within one PR. Rollback is reverting the PR.

## Open Questions

- None. Auto-fit, splitting, and plate arrangement are deliberately deferred to later changes.
