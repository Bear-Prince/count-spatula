## 1. Bounding-box fit check

- [ ] 1.1 Change `check_print_bed` in `cutlery_bin.py` to take the model's dimensions and the bed limits —
  `check_print_bed(model_x_mm, model_y_mm, model_z_mm, bed_x_mm, bed_y_mm, bed_z_mm=None)` — warning per axis that
  exceeds its limit, and checking height only when `bed_z_mm` is given.
- [ ] 1.2 In `main.py`, after building the part, measure `part.bounding_box()` and run the check only when
  `--bed-x`/`--bed-y` are provided; add a `--bed-z` flag. Keep it non-blocking (warn to stderr, still export).

## 2. Tests

- [ ] 2.1 Restore/extend `check_print_bed` unit tests: fits; exceeds X; exceeds Y; exceeds Z; height not checked
  when `bed_z_mm` is `None`; the warning names the dimension and the limit.
- [ ] 2.2 Add a CLI test (with a stub part exposing a bounding box) that an oversized model with `--bed-x`/`--bed-y`
  warns to stderr, still exports, and exits 0.
- [ ] 2.3 Confirm the existing CLI tests (no bed flags) still pass — the bbox is only measured when a bed is given.

## 3. Verification and UAT

- [ ] 3.1 Run `uv run ruff check .` and fix findings.
- [ ] 3.2 Run `uv run pytest` and confirm the full suite passes.
- [ ] 3.3 Add a `UAT.md` row exercising the bed-fit warning (a model with a deliberately small `--bed-x`/`--bed-y`/
  `--bed-z` prints a warning to stderr, names the axis, and still exports with exit 0).
- [ ] 3.4 Generate the UAT models (the `UAT.md` bin cases) to `build/` for slicer review, confirming the geometry is
  unchanged by this CLI-only change.
- [ ] 3.5 Archive the change so the spec delta folds into `openspec/specs/`.
