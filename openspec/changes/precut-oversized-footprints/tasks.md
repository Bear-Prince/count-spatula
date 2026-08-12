## 1. Cut planning (pure, no geometry)

- [ ] 1.1 Add `GRID_PITCH_MM = 42.0` and `plan_grid_cuts(n_units, bed_mm) -> list[float]` to `cutlery_bin.py`,
      returning nominal-grid cut offsets via `PITCH * (k - n_units / 2)`; returns `[]` when the axis already
      fits.
- [ ] 1.2 Implement the balanced planner inside it: `max_units = floor(bed_mm / PITCH)`,
      `n_pieces = ceil(n_units / max_units)`, units distributed as evenly as possible.
- [ ] 1.3 Raise `ValueError` when a single grid unit cannot fit the bed, since no grid-aligned split can help.
- [ ] 1.4 Unit-test cut positions against the measured values - 6 units gives `[0.0]`, 7 gives `[-21.0]`,
      12 gives `[-84.0, 84.0]` - claiming *Cut lands on the nominal grid line* and *Cut position is not
      derived from the bounding box*.
- [ ] 1.5 Unit-test the run distribution - 6 units gives `[3, 3]`, 7 gives `[4, 3]` - claiming *Six units
      split into two equal halves* and *Seven units split unevenly only where necessary*.
- [ ] 1.6 Unit-test that an axis already fitting the bed produces no cuts, and that a sub-unit bed raises.

## 2. Geometry splitting

- [ ] 2.1 Add `SplitMode` (`GLUED`, `STANDALONE`) and
      `split_for_print_bed(part, n_units_x, n_units_y, bed_x_mm, bed_y_mm, mode) -> list[Shape]` to
      `cutlery_bin.py`, using `build123d.split(..., keep=Keep.BOTH)` per axis in sequence.
- [ ] 2.2 Sort the returned pieces by bounding-box position (ascending X, then ascending Y) so ordering is
      deterministic.
- [ ] 2.3 Implement the `STANDALONE` shave: remove 0.25 mm from every cut face by offsetting the two
      half-space cuts rather than post-processing faces.
- [ ] 2.4 Real-geometry test: split the `chop-board` preset and assert two pieces of 125.75 mm summing to
      251.50 mm, claiming *Glued pieces reassemble to the native dimension* and *A preset with an
      explicitly-sized pocket splits*.
- [ ] 2.5 Real-geometry test: assert combined piece volume equals the unsplit model's volume, claiming *Split
      conserves the model volume*.
- [ ] 2.6 Real-geometry test: split a 7x3 blanking plate in `STANDALONE` mode and assert 167.50 mm and
      125.50 mm against natively-generated 4x3 and 3x3 plates, claiming *Standalone pieces match native
      dimensions* and *A wall-less plate splits*.
- [ ] 2.7 Real-geometry test: a model oversized on both axes yields pieces cut on both, each fitting the bed,
      claiming *A model oversized on both axes splits on both*.
- [ ] 2.8 Confirm the new real-geometry tests are picked up as `slow` by the existing `tests/conftest.py`
      auto-marking, so `-m "not slow"` stays fast.

## 3. Print-bed warning

- [ ] 3.1 Extend `check_print_bed()` so X and Y overflow warnings name `--split` and the Z warning does not,
      keeping the existing dimension-and-limit text intact.
- [ ] 3.2 Test both, claiming *Horizontal overflow names the split remedy* and *Height overflow does not
      suggest splitting*.
- [ ] 3.3 Confirm the four existing `print-bed-validation` scenarios still pass unchanged, since the MODIFIED
      delta keeps their names and their claiming tests.

## 4. CLI wiring

- [ ] 4.1 Add `--split` (store_true) and `--split-mode {glued,standalone}` (default `glued`) to
      `build_parser()` in `main.py`.
- [ ] 4.2 Branch the export path: without `--split` keep the current single-file behaviour untouched; with
      it, call `split_for_print_bed()` and export each piece.
- [ ] 4.3 Write pieces to `<stem>-part<n>.<ext>` beside the requested output path and print each exported
      path.
- [ ] 4.4 Warn, and still export, when `--split-mode standalone` is used on a model with a pocket.
- [ ] 4.5 Warn that splitting cannot resolve a Z-axis overflow, while still exporting the X/Y pieces.
- [ ] 4.6 Error with exit code 2 when `--split-mode` is given without `--split`, so the flag combination
      cannot silently do nothing.
- [ ] 4.7 CLI tests with mocked factories and export, claiming *Splitting is opt-in*, *Split produces
      bed-fitting pieces*, *Pieces are written to predictable paths*, *Piece numbering is stable across
      runs*, *Standalone mode warns on a pocketed model*, and *Z overflow is reported as unsplittable*.

## 5. Traceability and specs

- [ ] 5.1 Add `@pytest.mark.scenario("print-splitting", "<name>")` markers to every test above, and
      `("print-bed-validation", ...)` to the two new warning tests.
- [ ] 5.2 Run `uv run pytest tests/test_spec_traceability.py` and confirm no scenario is unclaimed and no
      marker names a nonexistent scenario.
- [ ] 5.3 Run `pnpm exec openspec validate` and confirm the change passes now that deltas exist.

## 6. Documentation

- [ ] 6.1 Add a `--split` example to `CLAUDE.md`'s command list and to `README.md`.
- [ ] 6.2 Document in `README.md` that `glued` pieces are butt-jointed and need adhesive, with the chop-board
      as the worked example (two 167.50 x 125.75 mm halves).
- [ ] 6.3 Add the split chop-board to `UAT.md` as a case to regenerate and eyeball.

## 7. Verification

- [ ] 7.1 `uv run ruff check .`
- [ ] 7.2 `uv run pytest --cov --cov-report=term-missing`
- [ ] 7.3 Byte-for-byte regression: regenerate a model without `--split` and confirm it is identical to the
      pre-change output, proving the default path is untouched.
- [ ] 7.4 UAT: export the split chop-board to `build/` and open both pieces in a slicer to confirm they fit
      the bed, the cut lands on the grid line, and the pocket halves meet cleanly.
- [ ] 7.5 Confirm no README renders need regenerating, since this change adds no new model geometry to the
      example set.
