## 1. Resolve the open question

- [x] 1.1 Confirmed with the user: `--height-mm` / `height_in_units` on a lipped bin mean wall height with
      the lip added above it (matching upstream `Bin`), not total height including the lip. Recorded as
      Decision 5 in `design.md`.

## 2. Parameters and validation

- [ ] 2.1 Add `stacking_lip: bool = False` to `BinParameters` in `cutlery_bin.py`
- [ ] 2.2 Add a `STACKING_LIP_REACH_MM = 2.6` module constant (0.7 + 1.9, derived from the upstream
      `gridfinity_standard.stacking_lip` constants) with a comment naming its source
- [ ] 2.3 Extend `BinParameters.validate()` to reject a wall too thin to seat the lip when `stacking_lip` is
      enabled, accumulating the error alongside the existing ones; explicitly keep the default 2 mm wall valid
- [ ] 2.4 Add unit tests for the new validation rule, including the default-wall accept case and the
      chop-board accept case

## 3. Lip geometry

- [ ] 3.1 Import `StackingLip` from `gridfinity_build123d` in `cutlery_bin.py`
- [ ] 3.2 In `KitchenBin.__init__`, after `_add_interior` and **before** the cutout subtraction, sweep the lip
      along the top face's outer wire when `params.stacking_lip` is set (per design Decision 1)
- [ ] 3.3 Verify the lip step reads only the top outer wire, taking no dependency on pocket dimensions,
      pocket corner radius, or divider layout
- [ ] 3.4 Add a real-geometry test asserting the X/Y footprint is unchanged and Z grows by ~4.12 mm, using a
      tolerance rather than exact equality (per design Risks)
- [ ] 3.5 Add a real-geometry test asserting a lipped bin is a valid solid

## 4. Cutout interaction

- [ ] 4.1 Raise the `cutout_height` passed to `SideCutoutProfile` so the slot cuts above the top of the lip
      when a lip is present (per design Decision 2)
- [ ] 4.2 Confirm the cutout's rim fillet geometry is unchanged by the added height, since the flare is
      anchored to floor-relative dimensions
- [ ] 4.3 Add a test asserting no lip material spans either handle slot opening on a cutout-bearing lipped bin
- [ ] 4.4 Add a test asserting the lip forms one uninterrupted loop when cutouts are disabled
- [ ] 4.5 Add a test asserting the handle slot stays open from the inner floor to above the lip

## 5. CLI

- [ ] 5.1 Add a `--stacking-lip` flag to the parser in `main.py` and thread it into `BinParameters`
- [ ] 5.2 Add CLI tests (mocking the bin factories, per existing convention) covering the flag on a plain bin,
      a divided bin, and `--preset chop-board --stacking-lip`
- [ ] 5.3 Verify the print-bed check reports the taller lipped model, and add a test for a bin that fits
      without a lip but exceeds the bed height with one

## 6. Traceability and docs

- [ ] 6.1 Mark every new test with `@pytest.mark.scenario("stacking-lip", "<scenario name>")` so each of the
      spec's scenarios has a claiming test
- [ ] 6.2 Run `uv run pytest tests/test_spec_traceability.py` and confirm no scenario is unclaimed and no
      marker names a non-existent scenario
- [ ] 6.3 Update the `KitchenBin` docstring and the Architecture section of `CLAUDE.md` to mention the
      optional stacking lip, defaulting to disabled
- [ ] 6.4 Add the `--stacking-lip` flag to the command examples in `CLAUDE.md`
- [ ] 6.5 Add a "Stacking lip" section to `README.md` (alongside the existing "Cutout geometry" /
      "Other options" sections), and state explicitly, per design Decision 5: the lip is swept on
      *after* the bin's wall height is built, so a lipped bin's total height is the requested
      `--height-mm` / `height_in_units` **plus** ~4.12 mm, not equal to it — and that the lip is off by
      default, so this only applies when `--stacking-lip` is passed
- [ ] 6.6 Cross-reference the same additive-height point from `CLAUDE.md`'s command examples (task 6.4) so
      it is not stated only in the README

## 7. Verification and UAT

- [ ] 7.1 Run `uv run ruff check .` and the full `uv run pytest --cov`
- [ ] 7.2 Confirm the no-lip path is byte-for-byte unchanged by regenerating a default bin and the chop-board
      preset and diffing against artifacts built before the change
- [ ] 7.3 Export a lipped chop-board bin and a lipped 2×4 cutlery bin, and send both to the user for UAT in a
      slicer — checking the lip mates with a base and that the handle slots are clear
- [ ] 7.4 Sync the delta spec into `openspec/specs/` and archive the change once UAT passes
