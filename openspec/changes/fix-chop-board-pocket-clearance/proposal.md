## Why

**Epic:** Chopping boards that fit the bin they were designed for.

**User story:** As a person printing the `chop-board` preset, I want the pocket sized to actually clear an
IKEA chopping board, so that the finished bin holds my board instead of rejecting it.

The `chop-board` preset's pocket has always shipped at 220 mm x 160 mm, in both `cutlery_bin.py` and the
`bin-presets` spec that names it. That is the *pre-tolerance* dimension. On 2026-02-22, prototyping in
`notebooks/chop_block.ipynb` (commit `56db5de`) found IKEA's boards do not hold to the printer's own
tolerance and relaxed the pocket to 222 mm x 162 mm - a 1 mm clearance per side. That fix never left the
notebook: `cutlery_bin.py` was written from scratch four months later (`85ff232`, "unify chop & utensil bins
into KitchenBin/CutleryBin with presets") using the original 220 x 160 figures, because notebooks are
explicitly out of scope for the supported interface (`CLAUDE.md`: "prototyping only ... not part of the
supported interface") and nothing else recorded the fix. The regression was invisible until a board was
printed against the un-relaxed pocket and did not fit.

**The relaxed dimension is independently confirmed, not just recovered from history.** Measuring the working
bin currently in service (printed before the regression was noticed) with calipers and back-solving through
the known wall geometry:

- Side walls (the walls carrying the handle cutouts, governed by `pocket_width`): measured 2.7 mm ->
  `pocket_width = 167.5 - 2*2.7 = 162.1 mm`.
- End walls (plain walls, governed by `pocket_length`): measured 14.6 mm ->
  `pocket_length = 251.5 - 2*14.6 = 222.3 mm`.

Both land within 0.1-0.3 mm of the notebook's 222 x 162, well inside the stated printer-vs-caliper variation.
This also resolves the one loose end in the notebook's own history: the commit immediately after the
relaxation (`790ad16`) printed it and noted it was "too snug for some of the chopping blocks" - but the
working bin confirms 222 x 162 does fit a real board, so that note was about board-to-board variation, not a
defect in the number.

## What Changes

Restore the pocket to 222 mm x 160 -> 162 mm x 222 mm (width x length) in `cutlery_bin.py`'s
`CHOP_POCKET_WIDTH`/`CHOP_POCKET_LENGTH`, and in the `bin-presets` spec requirement that names the exact
dimensions, per this repo's own bug-fix convention (`WORKFLOW.md`: a bug in shipped behaviour is a new change
with a `MODIFIED` requirement, not a silent edit). Every test and doc that currently hardcodes 220 x 160 for
the chop-board preset moves to 222 x 162 alongside it, and a regression test pins the new figures down so
this cannot silently drift a third time.

The outer footprint (167.5 x 251.5 mm, 4x6 grid), height (8 units), corner radius (35 mm), and cutout
geometry are unaffected - only the pocket's two dimensions change.

## Capabilities

### Modified Capabilities

- `bin-presets`: the `chop-board` preset's pocket dimensions change from 220 mm x 160 mm to 222 mm x 162 mm.

## Impact

- `cutlery_bin.py`: `CHOP_POCKET_WIDTH` 160 -> 162, `CHOP_POCKET_LENGTH` 220 -> 222.
- `openspec/specs/bin-presets/spec.md`: the requirement text naming "220 mm x 160 mm" updates to
  "222 mm x 162 mm" via a `MODIFIED` delta.
- Tests asserting the old figures: `tests/test_cutlery_bin.py::test_chop_board_preset_reproduces_chop_bin`,
  `tests/test_cli_and_params.py::test_cli_preset_seeds_parameters`,
  `tests/test_cli_and_params.py::test_cli_preset_override_applies`.
- Docs: `README.md`'s explicit-parameters example (which spells out the chop-board's own dimensions),
  `UAT.md`'s chop-board and split-chop-board cases.
- Not touched: `docs/publishing/thingiverse-v0.1.0.md` is a dated snapshot of what v0.1.0 actually shipped
  with: correct history, not current documentation, so it is left as-is rather than rewritten.
- Wall thickness changes as a consequence, not a goal: side walls (X axis, cutout walls) go from 3.75 mm to
  2.75 mm; end walls (Y axis, plain) go from 15.75 mm to 14.75 mm - both consistent with the caliper
  measurements above within print tolerance.
- No effect on the outer footprint, so `precut-oversized-footprints`' chop-board split (167.5 x 125.75 mm
  halves at the Y=0 grid line) is unaffected; this change's own UAT reprints and re-splits the bin to confirm
  that directly rather than assuming it.

## Non-goals

- Re-deriving the relaxation from first principles (e.g., a formal per-board tolerance study). The 222 x 162
  figure is adopted because it is the one already confirmed by a real printed, real-board fit - not because
  it is provably optimal.
- Changing `notebooks/chop_block.ipynb`. It already holds the correct figures and is explicitly out of scope
  for the supported interface; nothing there is wrong.
- Touching any other preset or the default `KitchenBin`/`CutleryBin` pocket derivation, both of which were
  never affected by this regression.

## Test Strategy

- Unit: `_chop_board_preset()` returns `pocket_width_mm=162`, `pocket_length_mm=222`.
- Real-geometry: the built chop-board bin's wall thicknesses match the new pocket (side 2.75 mm, end
  14.75 mm) within the existing test suite's tolerance conventions.
- CLI: `--preset chop-board` seeds 222/162; an explicit override still takes precedence over the preset.
- Traceability: the `bin-presets` delta's scenario stays claimed by the updated tests; no scenario is
  orphaned by the rename.
- UAT: reprint the chop-board (whole and split) at the new dimensions and confirm a real board fits - the
  actual gate this change exists to pass.
