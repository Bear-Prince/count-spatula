## Context

`cutlery_bin.py`'s `_chop_board_preset()` has shipped the `chop-board` pocket at 220 mm x 160 mm since the
preset was created (`85ff232`). A 2026-02-22 prototype (`notebooks/chop_block.ipynb`, commit `56db5de`)
found IKEA boards don't hold to the printer's own tolerance and relaxed the pocket to 222 mm x 162 mm - but
that fix lived only in the notebook, which is explicitly out of scope for the supported interface, and was
never carried into `cutlery_bin.py` when it was written four months later. The bug was invisible until a
board printed against the un-relaxed pocket didn't fit.

## Goals / Non-Goals

**Goals:**

- The shipped `chop-board` preset produces a pocket that actually clears a real IKEA board, matching the
  dimension already confirmed by the working bin in service.
- The correction is recorded as a change, so the archive shows "we shipped this, then knew better" (the same
  convention as `2026-08-02-fix-knife-block-rest-guidance`).

**Non-Goals:**

- A formal tolerance study across boards. See Decision 1.
- Any change to the outer footprint, height, corner radius, or cutout geometry - only the two pocket
  dimensions move.
- Touching `notebooks/chop_block.ipynb` or `docs/publishing/thingiverse-v0.1.0.md`. The former already has
  the right numbers; the latter is a dated historical snapshot of what actually shipped, not current
  documentation, and rewriting it would misrepresent that history.

## Decisions

### Decision 1: Adopt the notebook's 222 x 162, not a freshly derived tolerance

*Rationale:* this figure has now been arrived at twice independently - once as a deliberate prototype fix,
once by back-solving caliper measurements off the bin currently in service - and the two agree to within
0.1-0.3 mm, inside the stated printer/caliper variation. That is stronger evidence than a fresh derivation
would produce, and re-deriving it from scratch would discard a real, working data point in favour of a
theoretical one. *Alternative considered:* measure a batch of IKEA boards directly and compute a margin from
that population - more rigorous, but this change exists to fix a regression, not to open a new
measurement study; nothing here forecloses that later if 222 x 162 turns out to be too tight for a
differently-sized board.

### Decision 2: A `MODIFIED` delta on `bin-presets`, not a silent constant edit

*Rationale:* the 220 x 160 figure is written directly into the `bin-presets` spec's requirement text
(`openspec/specs/bin-presets/spec.md:13`), so this is a spec bug, not only a code bug - editing the constant
alone would leave the spec asserting a pocket size the code no longer produces. `WORKFLOW.md`'s own
convention for shipped-behaviour bugs is a `MODIFIED` delta; this is a textbook case; there was no live
alternative to consider.

### Decision 3: Pin the new figures down with a regression assertion, not just update the old one

*Rationale:* the bug that motivated this change was not a wrong value being asserted - it was the *right*
value existing only in a notebook nothing checks. Updating `test_chop_board_preset_reproduces_chop_bin`'s
assertion to 162/222 fixes the immediate drift, but the same failure mode (a correction made somewhere the
test suite can't see) is what let this regress silently for four months the first time. The fix is
procedural as much as numeric: this preset's dimensions must never again be correct only in a place tests
don't reach.

## Risks / Trade-offs

- **The 222 x 162 figure is only confirmed against one physical board.** → Acceptable for this fix: it
  corrects a known regression back to a previously-validated state, not a new, unvalidated design (contrast
  with the `cleaver-block-variant` stub, which is unprinted and explicitly gated on UAT before proposing).
  If a different board doesn't fit, that is new information for a future change, not evidence this one is
  wrong.
- **Existing printed bins at the old 220 x 160 are now off-spec relative to the corrected preset.** →
  Acceptable: those bins were already the ones failing to hold a board; nobody is worse off, and there is no
  migration needed for a generated, not distributed, physical part.
- **Wall thickness on both axes decreases** (side 3.75 -> 2.75 mm, end 15.75 -> 14.75 mm). → Both remain well
  above typical minimum wall guidance for FDM printing at usual nozzle/wall-count settings; this change's UAT
  reprints and re-splits the bin specifically to confirm the thinner walls still print and hold together.
