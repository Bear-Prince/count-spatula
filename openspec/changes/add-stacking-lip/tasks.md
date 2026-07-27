## 1. Resolve the open question

- [x] 1.1 Confirmed with the user: `--height-mm` / `height_in_units` on a lipped bin mean wall height with
      the lip added above it (matching upstream `Bin`), not total height including the lip. Recorded as
      Decision 5 in `design.md`.

## 2. Parameters and validation

- [x] 2.1 Add `stacking_lip: bool = False` to `BinParameters` in `cutlery_bin.py`
- [x] 2.2 Add a `STACKING_LIP_REACH_MM = 2.6` module constant (0.7 + 1.9, derived from the upstream
      `gridfinity_standard.stacking_lip` constants) with a comment naming its source
- [x] 2.3 Extend `BinParameters.validate()` to reject a wall too thin to seat the lip when `stacking_lip` is
      enabled, accumulating the error alongside the existing ones; explicitly keep the default 2 mm wall valid
- [x] 2.4 Add unit tests for the new validation rule, including the default-wall accept case and the
      chop-board accept case

## 3. Lip geometry

- [x] 3.1 Import `StackingLip` from `gridfinity_build123d` in `cutlery_bin.py`
- [x] 3.2 In `KitchenBin.__init__`, after `_add_interior` and **before** the cutout subtraction, sweep the lip
      along the top face's outer wire when `params.stacking_lip` is set (per design Decision 1)
- [x] 3.3 Verify the lip step reads only the top outer wire, taking no dependency on pocket dimensions,
      pocket corner radius, or divider layout
- [x] 3.4 Add a real-geometry test asserting the X/Y footprint is unchanged and Z grows by ~4.12 mm, using a
      tolerance rather than exact equality (per design Risks)
- [x] 3.5 Add a real-geometry test asserting a lipped bin is a valid solid

## 4. Cutout interaction

- [x] 4.1 Extend `SideCutoutProfile` with a straight-sided section above the existing profile, spanning the
      full arc width and running from the wall top past the top of the lip. Do **not** simply raise
      `cutout_height` — the flare patches are anchored to the profile's top, so raising it drags the flare
      up into the lip (per design Decision 2)
- [x] 4.2 Add a regression test pinning the wall-top opening at the full arc width (106.2 mm on chop-board),
      so a future change that moves the flare off the wall top fails loudly rather than silently costing
      hand access
- [x] 4.3 Add a test asserting no lip material spans either handle slot opening on a cutout-bearing lipped bin
- [x] 4.4 Add a test asserting the lip forms one uninterrupted loop when cutouts are disabled
- [x] 4.5 Add a test asserting the handle slot stays open from the inner floor to above the lip
- [x] 4.6 Add a test asserting the lip terminates at the rim's widest point (±`cutout_arc_*`), confirming it
      does not follow the flare's curve down into the opening

## 5. CLI

- [x] 5.1 Add a `--stacking-lip` flag to the parser in `main.py` and thread it into `BinParameters`
- [x] 5.2 Add CLI tests (mocking the bin factories, per existing convention) covering the flag on a plain bin,
      a divided bin, and `--preset chop-board --stacking-lip`
- [x] 5.3 Verify the print-bed check reports the taller lipped model, and add a test for a bin that fits
      without a lip but exceeds the bed height with one

## 6. Traceability and docs

- [x] 6.1 Mark every new test with `@pytest.mark.scenario("stacking-lip", "<scenario name>")` so each of the
      spec's scenarios has a claiming test
- [x] 6.2 Run `uv run pytest tests/test_spec_traceability.py` and confirm no scenario is unclaimed and no
      marker names a non-existent scenario
- [x] 6.3 Update the `KitchenBin` docstring and the Architecture section of `CLAUDE.md` to mention the
      optional stacking lip, defaulting to disabled
- [x] 6.4 Add the `--stacking-lip` flag to the command examples in `CLAUDE.md`
- [x] 6.5 Add a "Stacking lip" section to `README.md` (alongside the existing "Cutout geometry" /
      "Other options" sections), and state explicitly, per design Decision 5: the lip is swept on
      *after* the bin's wall height is built, so a lipped bin's total height is the requested
      `--height-mm` / `height_in_units` **plus** ~4.12 mm, not equal to it — and that the lip is off by
      default, so this only applies when `--stacking-lip` is passed
- [x] 6.6 Cross-reference the same additive-height point from `CLAUDE.md`'s command examples (task 6.4) so
      it is not stated only in the README

## 7. Verification and UAT

- [x] 7.1 Run `uv run ruff check .` and the full `uv run pytest --cov`
- [x] 7.2 Confirm the no-lip path is byte-for-byte unchanged by regenerating a default bin and the chop-board
      preset and diffing against artifacts built before the change
- [x] 7.3 Export a lipped chop-board bin and a lipped 2×4 cutlery bin, and send both to the user for UAT in a
      slicer — checking the lip mates with a base, that the handle slots are clear, and specifically that
      the lip's termination above the rim fillet's tangent point slices cleanly (per design Risks)
- [x] 7.4 Sync the delta spec into `openspec/specs/` (done alongside the tests: the traceability guard
      rejects markers naming scenarios that are still only in the delta)
- [x] 7.5 Archive the change once UAT passes (UAT confirmed in a slicer; archived with `--skip-specs`
      because the delta was already synced into `openspec/specs/` alongside the tests)
