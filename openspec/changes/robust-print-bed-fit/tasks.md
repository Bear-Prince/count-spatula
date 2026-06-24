## 1. Bounding-box fit check

- [ ] 1.1 Change `check_print_bed` in `cutlery_bin.py` to
  `check_print_bed(model_x_mm, model_y_mm, model_z_mm, bed_x_mm, bed_y_mm, bed_z_mm)` (all millimetres), warning per
  axis whose model dimension exceeds its bed limit.
- [ ] 1.2 In `main.py`, add `DEFAULT_BED_X_MM = 220`, `DEFAULT_BED_Y_MM = 220`, `DEFAULT_BED_Z_MM = 240` constants
  and use them as the `--bed-x`/`--bed-y`/`--bed-z` defaults (millimetres, no unit conversion). After building the
  part, always measure `part.bounding_box()` and run the check; keep it non-blocking (warn to stderr, still export).

## 2. Tests

- [ ] 2.1 Restore/extend `check_print_bed` unit tests: fits within the volume; exceeds X; exceeds Y; exceeds Z; the
  warning names the dimension and the limit.
- [ ] 2.2 Update the existing CLI test fakes to return a stub part exposing a `bounding_box()` (the check now runs
  on every invocation, so `main` always measures it).
- [ ] 2.3 Add CLI tests: a normally-sized bin against the default volume produces no warning; an oversized model
  (or a tight `--bed-y`) warns to stderr, still exports, and exits 0.

## 3. Verification and UAT

- [ ] 3.1 Run `uv run ruff check .` and fix findings.
- [ ] 3.2 Run `uv run pytest` and confirm the full suite passes.
- [ ] 3.3 Add a `UAT.md` row exercising the bed-fit warning (a model with a deliberately small `--bed-x`/`--bed-y`/
  `--bed-z` prints a warning to stderr, names the axis, and still exports with exit 0).
- [ ] 3.4 Generate the UAT models (the `UAT.md` bin cases) to `build/` for slicer review, confirming the geometry is
  unchanged by this CLI-only change.
- [ ] 3.5 Archive the change so the spec delta folds into `openspec/specs/`.
