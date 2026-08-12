## 1. Cut planning (pure, no geometry)

- [x] 1.1 Reuse the existing `GRIDFINITY_PITCH_MM`/`GRIDFINITY_CLEARANCE_MM` constants (no new pitch constant
      was needed) and add `grid_line_offset(line_index, n_units)` plus
      `plan_grid_cuts(n_units, bed_mm) -> list[float]` to `cutlery_bin.py`, returning nominal-grid cut
      offsets via `PITCH * (k - n_units / 2)`; returns `[]` when the axis already fits.
- [x] 1.2 Implement the balanced planner inside it: `max_units = floor(bed_mm / PITCH)`,
      `n_pieces = ceil(n_units / max_units)`, units distributed as evenly as possible.
- [x] 1.3 Raise `ValueError` when a single grid unit cannot fit the bed, since no grid-aligned split can help.
- [x] 1.4 Unit-test cut positions against the measured values - `grid_line_offset(3, 6)` is `0.0` and
      `grid_line_offset(3, 7)` is `-21.0` (against the naive edge-derived `-20.75`), while the planner's own
      output for 7 units is `[21.0]` because it balances to runs of 4 and 3 - claiming *Cut lands on the
      nominal grid line* and *Cut position is not derived from the bounding box*.
- [x] 1.5 Unit-test the run distribution - 6 units gives `[3, 3]`, 7 gives `[4, 3]` - claiming *Six units
      split into two equal halves* and *Seven units split unevenly only where necessary*.
- [x] 1.6 Unit-test that an axis already fitting the bed produces no cuts, and that a sub-unit bed raises.

## 2. Geometry splitting

- [x] 2.1 Add `SplitMode` (`GLUED`, `STANDALONE`) and
      `split_for_print_bed(part, n_units_x, n_units_y, bed_x_mm, bed_y_mm, mode) -> list[Shape]` to
      `cutlery_bin.py`, using `build123d.split(..., keep=Keep.BOTH)` per axis in sequence.
- [x] 2.2 Sort the returned pieces by bounding-box position (ascending X, then ascending Y) so ordering is
      deterministic.
- [x] 2.3 Implement the `STANDALONE` shave: remove 0.25 mm from every cut face by offsetting the two
      half-space cuts rather than post-processing faces.
- [x] 2.4 Real-geometry test: split the `chop-board` preset and assert two pieces of 125.75 mm summing to
      251.50 mm, claiming *Glued pieces reassemble to the native dimension* and *A preset with an
      explicitly-sized pocket splits*.
- [x] 2.5 Real-geometry test: assert combined piece volume equals the unsplit model's volume, claiming *Split
      conserves the model volume*.
- [x] 2.6 Real-geometry test: split a 7x3 blanking plate in `STANDALONE` mode and assert 167.50 mm and
      125.50 mm against natively-generated 4x3 and 3x3 plates, claiming *Standalone pieces match native
      dimensions* and *A wall-less plate splits*.
- [x] 2.7 Real-geometry test: a model oversized on both axes yields pieces cut on both, each fitting the bed,
      claiming *A model oversized on both axes splits on both*.
- [x] 2.8 Confirm the new real-geometry tests are picked up as `slow` by the existing `tests/conftest.py`
      auto-marking, so `-m "not slow"` stays fast.

## 3. Print-bed warning

- [x] 3.1 Extend `check_print_bed()` so X and Y overflow warnings name `--split` and the Z warning does not,
      keeping the existing dimension-and-limit text intact.
- [x] 3.2 Test both, claiming *Horizontal overflow names the split remedy* and *Height overflow does not
      suggest splitting*.
- [x] 3.3 Confirm the four existing `print-bed-validation` scenarios still pass unchanged, since the MODIFIED
      delta keeps their names and their claiming tests.

## 4. CLI wiring

- [x] 4.1 Add `--split` (store_true) and `--split-mode {glued,standalone}` (default `glued`) to
      `build_parser()` in `main.py`.
- [x] 4.2 Branch the export path: without `--split` keep the current single-file behaviour untouched; with
      it, call `split_for_print_bed()` and export each piece.
- [x] 4.3 Write pieces to `<stem>-part<n>.<ext>` beside the requested output path and print each exported
      path.
- [x] 4.4 Warn, and still export, when `--split-mode standalone` is used on a model with a pocket.
- [x] 4.5 Warn that splitting cannot resolve a Z-axis overflow, while still exporting the X/Y pieces.
- [x] 4.6 Error with exit code 2 when `--split-mode` is given without `--split`, so the flag combination
      cannot silently do nothing.
- [x] 4.7 CLI tests with mocked factories and export, claiming *Splitting is opt-in*, *Split produces
      bed-fitting pieces*, *Pieces are written to predictable paths*, *Piece numbering is stable across
      runs*, *Standalone mode warns on a pocketed model*, and *Z overflow is reported as unsplittable*.

## 5. Traceability and specs

- [x] 5.1 Sync the delta specs into `openspec/specs/` (new `print-splitting`, merged `print-bed-validation`),
      then add `@pytest.mark.scenario("print-splitting", "<name>")` markers to every test above, and
      `("print-bed-validation", ...)` to the two new warning tests.
- [x] 5.2 Run `uv run pytest tests/test_spec_traceability.py` and confirm no scenario is unclaimed and no
      marker names a nonexistent scenario.
- [x] 5.3 Run `pnpm exec openspec validate` and confirm the change passes now that deltas exist.

## 6. Documentation

- [x] 6.1 Add a `--split` example to `CLAUDE.md`'s command list and to `README.md`.
- [x] 6.2 Document in `README.md` that `glued` pieces are butt-jointed and need adhesive, with the chop-board
      as the worked example (two 167.50 x 125.75 mm halves).
- [x] 6.3 Add the split chop-board to `UAT.md` as a case to regenerate and eyeball.

## 7. Verification

- [x] 7.1 `uv run ruff check .`
- [x] 7.2 `uv run pytest --cov --cov-report=term-missing`
- [x] 7.3 Byte-for-byte regression: regenerate a model without `--split` and confirm it is identical to the
      pre-change output, proving the default path is untouched.
- [ ] 7.4 UAT: export the split chop-board to `build/` and open both pieces in a slicer to confirm they fit
      the bed, the cut lands on the grid line, and the pocket halves meet cleanly. **Export done**
      (`build/chop-part1.stl`, `build/chop-part2.stl`; measured 167.50 x 125.75 x 59.90 mm each, meeting
      flush at Y=0). **Slicer eyeball still outstanding - this is the user's gate before archiving.**
- [x] 7.5 Confirm no README renders need regenerating, since this change adds no new model geometry to the
      example set.
