## Why

`check_print_bed()` already warns when a generated model's bounding box exceeds the configured bed volume,
but the user still has to split the model themselves. In practice that has meant a slicer's manual planar-cut
tool: rotating the model onto its short edge so the cut axis lines up with the tool's numeric position field,
cutting, then rotating the pieces back flat (worked out during UAT of `add-blanking-plates` on a 7x3 blanking
plate too large for the print bed, split by hand into a 3x3 and a 4x3).

For grid-based footprints, the tool already knows the exact per-unit pitch, since it generates the geometry
itself — a 7x3 plate can already be produced directly as separate 3x3 and 4x3 outputs via two ordinary
invocations. What's missing is a single command that, given a footprint too large for the configured bed,
works out and emits a compliant set of smaller pieces automatically, instead of the user doing the split by
hand in a slicer.

## What this backlog stub is not

This is a "tracked problem, not yet designed" stub per [WORKFLOW.md](../../WORKFLOW.md)'s "Keeping a backlog
item" recipe. It intentionally has no design, deltas or tasks yet, and will not pass `openspec validate`
until those are written.

## Shape a real design will need to address

- Given `--grid-x`/`--grid-y` and a bed size (`--bed-x`/`--bed-y`), compute a split of the grid into
  sub-footprints that each fit the bed, and export each as a separate file (naming scheme TBD, e.g.
  `<output>-part1.stl`, `<output>-part2.stl`, ...).
- Splits should land on whole-grid-unit boundaries, consistent with how a manual slicer cut needs to for a
  clean result on Gridfinity's per-unit pitch.
- Which product types this applies to. Blanking plates can go either route (native sub-footprints or a
  slice). The chop-board preset is a driving case rather than a deferrable one: at 251.50 mm in Y it exceeds
  a 220 mm bed today, and native re-generation cannot express half of it (see the library-capability section
  below), so it can only be served by slicing. Cutting through its walls and pocket is correct here, not a
  defect, because the halves are glued back into one bin.
- Interaction with `square-corner-support` (see that stub): pieces produced this way have genuinely new
  outer edges at the cut lines, which is a different situation from that stub's problem (squaring an edge
  that was never meant to be cut). Newly-created cut edges are plausibly fine to square, or leave rounded, as
  a documented choice — decide during design rather than assuming.

## Library capability: `build123d` can slice, and slicing is the required mechanism for presets

Checked against the pinned `build123d` 0.9.0. It has a first-class planar cut:

- `split(objects, bisect_by=<Plane|Face>, keep=Keep.TOP|BOTTOM|BOTH)`, plus `Keep.ALL`, `Keep.INSIDE` and
  `Keep.OUTSIDE`. With `Keep.BOTH` it returns a single `Part` whose `.solids()` yields the separate pieces.
- Verified on real geometry, not a toy: a 7x3 blanking plate cut at `Plane.YZ.offset(x)` produced two clean
  solids in ~1.6 s (against ~12.5 s to build the plate), volume conserved exactly, fillets and stacking feet
  intact. A chop-board bin cut at `Plane.XZ` behaved the same.

**Native re-generation cannot serve the chop-board preset at all.** Its pocket is explicitly sized
(`CHOP_POCKET_LENGTH = 220`, `CHOP_POCKET_WIDTH = 160`), so "half a chop-board bin" is not expressible as a
`BinParameters` footprint — a natively-generated 4x3 bin would derive a different pocket entirely, and the
220 mm pocket spans the join in any case. The preset measures 167.50 x 251.50 x 59.90 mm, so only Y exceeds a
220 mm bed; one cut at `Y=0` yields two 167.50 x 125.75 mm pieces that both fit. Note `cutlery_bin.py:68`
already anticipates exactly this: *"Grid-aligned; splittable on the chop bin's +/-42 mm internal grid lines."*

### Cut position, and the clearance question

The Gridfinity 0.5 mm clearance is applied once to the whole footprint, not per unit: a native `N`-unit
dimension measures `N*42 - 0.5` mm (verified at N = 3, 4, 6 and 7). The footprint is therefore inset 0.25 mm
per side, which means **the true internal grid line is not offset from the model's own edge by a whole
multiple of 42**. Cutting at `min + n*42` lands 0.25 mm off the grid line; the correct cut is at
`nominal_min + n*42`, i.e. 0.25 mm further in. Measured on the chop-board at its true grid line `Y=0`:

| | piece width | pair total |
| --- | --- | --- |
| Raw halves, cut on the grid line | 125.75 mm each | **251.50 mm — exactly native** |
| Each cut face shaved by 0.25 mm | **125.50 mm — exactly native 4x3** | 251.00 mm |

So which is correct depends entirely on what the pieces are *for*, and the design must distinguish the two:

- **Pieces glued back into one item** (the chop-board case, forced by its spanning pocket): do not shave. The
  raw halves already sum to the native width. Shaving would leave the assembly 0.5 mm undersized — loose
  rather than binding, so harmless, but pointless.
- **Pieces standing alone in their own baseplate cells** (a 7x3 plate becoming a 3x3 and a 4x3): shave
  0.25 mm off each cut face and each piece matches its native equivalent exactly.

A note on how much this matters in practice: field experience cutting these models in OrcaSlicer without
adding any clearance has worked well so far, and cutting on the true grid line leaves only 0.25 mm of excess
in the standalone case rather than the 0.5 mm first assumed here. Treat the shave as correctness for the
standalone case, not as a fix for an observed failure.

Consequences for the design:

- Slicing is not merely a fallback — for presets with explicitly-sized pockets it is the only mechanism.
  Native sub-footprint generation stays the better route for plates, where both approaches are available.
- Derive cut positions from the nominal grid, not from the model's bounding box, or every cut lands 0.25 mm
  off.
- The glued-versus-standalone distinction determines whether to shave, so it needs to be an explicit input
  (a flag, or implied by product type) rather than a silent assumption.
- Bins cut this way still have an open-ended pocket at the join. For a glued assembly that is correct and
  needs no re-walling; for standalone pieces it would, which is a further reason the two cases differ.
- The live `knife-blade-block` requirement "Block prints without splitting" explicitly promises the block
  needs none of this machinery; keep it that way, and note the `cleaver-block-variant` stub flags a deeper
  channel that should be re-checked against a typical bed.

## Non-goals

- Arbitrary, non-grid-aligned cut positions — the value of automation here is specifically deriving the grid-
  aligned split; a freeform cut is already served by a slicer's own cut tool.
