## 1. Code fix

- [x] 1.1 In `cutlery_bin.py`, change `CHOP_POCKET_WIDTH` from `160 * MM` to `162 * MM` and
      `CHOP_POCKET_LENGTH` from `220 * MM` to `222 * MM`, keeping the existing comment style.
- [x] 1.2 Confirm no other constant derives from these two (grep for `CHOP_POCKET_WIDTH`/`CHOP_POCKET_LENGTH`
      usage) so the change is a pure two-value edit with no second-order effect.

## 2. Spec sync

- [x] 2.1 Sync the `bin-presets` delta into `openspec/specs/bin-presets/spec.md` (`openspec-sync-specs` or
      manual merge), landing the `MODIFIED` requirement text and the new "Preset pocket clears the board it
      is sized for" scenario.
- [x] 2.2 Confirm the two existing scenarios ("Generate a bin from a preset", "Disabling cutouts on a
      cutouts-required preset is rejected") are untouched in content, since their behaviour did not change.

## 3. Test updates

- [x] 3.1 Update `tests/test_cutlery_bin.py::test_chop_board_preset_reproduces_chop_bin`'s assertion from
      `(160, 220)` to `(162, 222)`.
- [x] 3.2 Update `tests/test_cli_and_params.py::test_cli_preset_seeds_parameters` and
      `test_cli_preset_override_applies` from 220/160 to 222/162.
- [x] 3.3 Add a real-geometry regression test asserting the built chop-board's wall thicknesses: side walls
      (X axis, the cutout walls) at 2.75 mm, end walls (Y axis, plain) at 14.75 mm - the actual failure mode
      this change fixes, not just the parameter values.
- [x] 3.4 Add `@pytest.mark.scenario("bin-presets", "Preset pocket clears the board it is sized for")` to the
      new test from 3.3 (or to 3.1, whichever asserts the pocket dimensions directly).
- [x] 3.5 Run `uv run pytest tests/test_spec_traceability.py` and confirm the new scenario is claimed and no
      marker is dangling.

## 4. Documentation

- [x] 4.1 Update `README.md`'s explicit-parameters example (`--pocket-length-mm 220 --pocket-width-mm 160`)
      to 222/162, so it still matches what `--preset chop-board` actually produces.
- [x] 4.2 Update `UAT.md`'s UAT-2 (chop-board preset) pocket figure from 220×160 to 222×162. **Scope note:**
      this branch is cut from `origin/main`, which does not yet have `precut-oversized-footprints` merged, so
      `UAT.md` has no UAT-10 (split chop-board) entry here and `--split` does not exist on this branch. That
      task is deferred to 5.6 rather than done now.
- [x] 4.3 Leave `docs/publishing/thingiverse-v0.1.0.md` untouched - it is a dated historical snapshot of what
      v0.1.0 actually shipped, not current documentation.

## 5. Verification

- [x] 5.1 `uv run ruff check .`
- [x] 5.2 `uv run pytest --cov --cov-report=term-missing`
- [x] 5.3 `pnpm exec openspec validate` - confirm the change and the synced `bin-presets` spec both pass.
- [x] 5.4 Regenerate the chop-board (`uv run python main.py --preset chop-board --output build/chop.stl`) and
      confirm the exported bounding box's pocket-derived wall thicknesses measure 2.75 mm / 14.75 mm from the
      STL geometry (not just from the parameter values), so the fix is confirmed in the actual output file.
- [x] 5.5 UAT: **downgraded from a physical reprint to a slicer eyeball**, per explicit user call - printing
      the same bin twice costs real filament and time for a change that is a confirmed numeric correction
      (notebook history + caliper back-solve + STL-geometry measurement all agree already), not new,
      unvalidated geometry. Verified by loading `build/chop.stl` in OrcaSlicer and confirming the pocket and
      wall proportions look correct. This is the same tier `UAT.md` already accepts elsewhere (most entries
      are `(slicer)`, not `(printed)`) - recorded as such, not oversold as a physical fit test.
- [ ] 5.6 **Deferred until `precut-oversized-footprints` merges to main and this fix is available alongside
      it** (either by merge order or a rebase): reprint the chop-board split (`--split`) at the corrected
      pocket dimensions and confirm the two halves still glue into a bin that holds the board, since the
      split was verified against the old, incorrect pocket. Not actionable on this branch today - `--split`
      does not exist here.
