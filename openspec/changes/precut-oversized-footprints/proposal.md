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

## Library capability: `build123d` can slice, but that is probably not the mechanism to use

Checked against the pinned `build123d` 0.9.0. It does have a first-class planar cut, so "slice the finished
model" is a genuinely available implementation strategy:

- `split(objects, bisect_by=<Plane|Face>, keep=Keep.TOP|BOTTOM|BOTH)`, plus `Keep.ALL`, `Keep.INSIDE` and
  `Keep.OUTSIDE`. With `Keep.BOTH` it returns a single `Part` whose `.solids()` yields the separate pieces.
- Verified on real geometry, not just a toy: a generated 7x3 blanking plate cut at `Plane.YZ.offset(x)` on a
  whole-unit boundary produced two clean solids in ~1.6 s (against ~12.5 s to build the plate), with volume
  conserved exactly. Fillets, stacking feet and all.

**However, measurement suggests native re-generation is the better mechanism for grid-aligned splits.** The
Gridfinity 0.5 mm clearance is applied once to the whole footprint, not per unit — a native `N`x3 plate
measures `N*42 - 0.5` mm at every `N` tested (3, 4 and 7). So the two approaches do not agree:

| Approach | 3-unit piece | 4-unit piece |
| --- | --- | --- |
| Generate natively as 3x3 and 4x3 | 125.5 mm | 167.5 mm |
| Slice a 7x3 at the 3-unit boundary | 126.0 mm | 167.5 mm |

The sliced piece inherits no clearance on its cut face, leaving it 0.5 mm oversized across three cells —
enough to bind in a baseplate. Native generation gives each piece its own correct clearance and a properly
finished edge, which also matches what the "Why" section above already observes: two ordinary invocations
already produce the right parts today.

Consequences for the design:

- Prefer computing sub-footprints and generating each natively; treat `split()` as the fallback for cuts
  that cannot land on a unit boundary (which the non-goal below currently excludes anyway).
- If `split()` is ever used, the design must decide what happens to clearance on the cut face rather than
  inheriting the 0.5 mm error silently.
- `split()` remains the more plausible route for bins, whose walls and pockets have no meaning at a
  sub-footprint level — but a naive cut leaves an open-ended pocket that would need re-walling, so this does
  not by itself resolve the bins question raised above.
- The live `knife-blade-block` requirement "Block prints without splitting" explicitly promises the block
  needs none of this machinery; keep it that way, and note the `cleaver-block-variant` stub flags a deeper
  channel that should be re-checked against a typical bed.

## Non-goals

- Arbitrary, non-grid-aligned cut positions — the value of automation here is specifically deriving the grid-
  aligned split; a freeform cut is already served by a slicer's own cut tool.
