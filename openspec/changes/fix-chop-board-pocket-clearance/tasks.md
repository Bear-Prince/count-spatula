## 1. Code fix

- [ ] 1.1 In `cutlery_bin.py`, change `CHOP_POCKET_WIDTH` from `160 * MM` to `162 * MM` and
      `CHOP_POCKET_LENGTH` from `220 * MM` to `222 * MM`, keeping the existing comment style.
- [ ] 1.2 Confirm no other constant derives from these two (grep for `CHOP_POCKET_WIDTH`/`CHOP_POCKET_LENGTH`
      usage) so the change is a pure two-value edit with no second-order effect.

## 2. Spec sync

- [ ] 2.1 Sync the `bin-presets` delta into `openspec/specs/bin-presets/spec.md` (`openspec-sync-specs` or
      manual merge), landing the `MODIFIED` requirement text and the new "Preset pocket clears the board it
      is sized for" scenario.
- [ ] 2.2 Confirm the two existing scenarios ("Generate a bin from a preset", "Disabling cutouts on a
      cutouts-required preset is rejected") are untouched in content, since their behaviour did not change.

## 3. Test updates

- [ ] 3.1 Update `tests/test_cutlery_bin.py::test_chop_board_preset_reproduces_chop_bin`'s assertion from
      `(160, 220)` to `(162, 222)`.
- [ ] 3.2 Update `tests/test_cli_and_params.py::test_cli_preset_seeds_parameters` and
      `test_cli_preset_override_applies` from 220/160 to 222/162.
- [ ] 3.3 Add a real-geometry regression test asserting the built chop-board's wall thicknesses: side walls
      (X axis, the cutout walls) at 2.75 mm, end walls (Y axis, plain) at 14.75 mm - the actual failure mode
      this change fixes, not just the parameter values.
- [ ] 3.4 Add `@pytest.mark.scenario("bin-presets", "Preset pocket clears the board it is sized for")` to the
      new test from 3.3 (or to 3.1, whichever asserts the pocket dimensions directly).
- [ ] 3.5 Run `uv run pytest tests/test_spec_traceability.py` and confirm the new scenario is claimed and no
      marker is dangling.

## 4. Documentation

- [ ] 4.1 Update `README.md`'s explicit-parameters example (`--pocket-length-mm 220 --pocket-width-mm 160`)
      to 222/162, so it still matches what `--preset chop-board` actually produces.
- [ ] 4.2 Update `UAT.md`'s UAT-2 (chop-board preset) and UAT-10 (split chop-board) expected dimensions from
      220×160 / 251.5 / 125.75 references to the new pocket figures where they describe the pocket itself;
      leave outer-footprint and split-piece figures alone since the footprint didn't change.
- [ ] 4.3 Leave `docs/publishing/thingiverse-v0.1.0.md` untouched - it is a dated historical snapshot of what
      v0.1.0 actually shipped, not current documentation.

## 5. Verification

- [ ] 5.1 `uv run ruff check .`
- [ ] 5.2 `uv run pytest --cov --cov-report=term-missing`
- [ ] 5.3 `pnpm exec openspec validate` - confirm the change and the synced `bin-presets` spec both pass.
- [ ] 5.4 Regenerate the chop-board (`uv run python main.py --preset chop-board --output build/chop.stl`) and
      confirm the exported bounding box's pocket-derived wall thicknesses measure 2.75 mm / 14.75 mm from the
      STL geometry (not just from the parameter values), so the fix is confirmed in the actual output file.
- [ ] 5.5 UAT: reprint the whole chop-board and confirm a real IKEA board fits without binding - the gate
      this change exists to pass.
- [ ] 5.6 UAT: reprint the chop-board split (`--split`, per `precut-oversized-footprints`) at the corrected
      pocket dimensions and confirm the two halves still glue into a bin that holds the board, since the
      split was verified against the old, incorrect pocket.
