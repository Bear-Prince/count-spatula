## Why

The print-bed check exists but is thin. `check_print_bed` compares the **grid footprint** (`grid×42`) against
`--bed-x`/`--bed-y`, so it only reasons about plain grid bins, ignores the model's real dimensions, and never
checks **height (Z)** — often the binding constraint on a printer. Its tests were also lost when the utensil bin
was retired, so the capability currently has a spec but no coverage. As the foundation for later "split a too-long
model so it fits the bed" work, the fit check needs to be based on the model's **actual bounding box**.

## What Changes

- Base the print-bed check on the model's **actual bounding box** (X, Y, Z) rather than the grid footprint.
- Ship a **default print volume of 220 × 220 × 240 mm** (width × depth × height) so the check runs by default;
  override any axis with `--bed-x` / `--bed-y` / `--bed-z`. Warn when the model is too tall as well as too wide/deep.
- **Print-volume dimensions are millimetres only — no unit conversion** (that is how manufacturers quote build
  volumes, so it avoids a needless conversion layer). The bin *height* keeps its existing unit option; the *bed*
  does not.
- **Evaluate the model in its as-generated orientation only** — no rotation or reorientation. Rotating a model to
  make it "fit" risks overhangs and awkward infill, so we deliberately do not do it.
- Restore and extend the print-bed **test coverage** lost with `test_utensil_bin.py`.
- Keep the behaviour **non-blocking**: warn to stderr, still export, exit 0.

Out of scope (later steps on the journey): auto-fitting, splitting a model into bed-sized parts, and arranging
parts on the plate.

## Capabilities

### Modified Capabilities

- `print-bed-validation`: check the model's actual bounding box (including height) instead of the grid footprint;
  add a printer-height dimension; state that the model is evaluated in its printed orientation (no rotation).

## Impact

- [cutlery_bin.py](../../../cutlery_bin.py): `check_print_bed` takes the model's X/Y/Z dimensions and the bed
  X/Y plus optional Z, rather than the grid.
- [main.py](../../../main.py): build the part first, then check its bounding box; add a `--bed-z` flag.
- Tests: restore and extend the print-bed checks (fits, exceeds X, exceeds Y, exceeds Z, no bed configured).
- No change to the generated geometry; behaviour stays non-blocking.
