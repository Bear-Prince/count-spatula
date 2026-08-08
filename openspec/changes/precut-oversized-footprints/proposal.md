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
- Which product types this applies to: blanking plates today; bins and cutlery bins have walls and pockets
  that a naive grid split would cut through, so they need their own consideration, or may be out of scope
  for a first pass.
- Interaction with `square-corner-support` (see that stub): pieces produced this way have genuinely new
  outer edges at the cut lines, which is a different situation from that stub's problem (squaring an edge
  that was never meant to be cut). Newly-created cut edges are plausibly fine to square, or leave rounded, as
  a documented choice — decide during design rather than assuming.

## Non-goals

- Arbitrary, non-grid-aligned cut positions — the value of automation here is specifically deriving the grid-
  aligned split; a freeform cut is already served by a slicer's own cut tool.
