## Context

`check_print_bed()` already measures a generated model's bounding box and warns when it exceeds the
configured build volume, but it stops there - the user then splits the model by hand in a slicer's planar-cut
tool. That manual workflow (rotate onto the short edge, cut at a numeric position, rotate back) was worked
out during UAT of `add-blanking-plates` and has been used successfully in OrcaSlicer since.

The driving case is the `chop-board` preset. It measures **167.50 x 251.50 x 59.90 mm**, so its Y axis alone
exceeds a 220 mm bed and it cannot be printed as generated. Its pocket is explicitly sized
(`CHOP_POCKET_LENGTH = 220`, `CHOP_POCKET_WIDTH = 160`), so "half a chop-board bin" is not expressible as a
`BinParameters` footprint - a natively-generated 4x3 bin would derive an entirely different pocket. Slicing
the finished solid is therefore the only mechanism that can serve it. `cutlery_bin.py:68` already anticipated
this, noting the cutout offsets are *"Grid-aligned; splittable on the chop bin's +/-42 mm internal grid
lines."*

All measurements quoted in this document were taken from real generated geometry, not derived on paper.

## Goals / Non-Goals

**Goals:**

- Add an opt-in `--split` that cuts an oversized model into bed-fitting pieces along Gridfinity grid lines.
- Derive cut positions from the *nominal* grid rather than the model's bounding box.
- Default to pieces intended to be glued back into one model, with a standalone mode available.
- Work uniformly across product types (bins, cutlery bins, blanking plates, knife blocks) by operating on the
  built solid rather than on parameters.
- Leave every existing invocation byte-for-byte unchanged.

**Non-Goals:**

- Arbitrary, non-grid-aligned cut positions - a slicer's own cut tool already serves those.
- Splitting on Z. There is no grid pitch in Z to align to, and a horizontal cut through a bin's floor and
  pocket is a different problem with different failure modes.
- Rotating or reorienting a model to make it fit. `print-bed-validation` already forbids this, and that
  reasoning (overhangs, infill) is unchanged.
- Generating joinery - dowel holes, alignment pins, dovetails. First pass is butt-jointed glue surfaces.
- Automatically splitting when a model is oversized. See Decision 1.
- Emitting a single multi-object 3MF. See Decision 6.

## Decisions

### Decision 1: Splitting is opt-in via `--split`, and the bed warning suggests it

`check_print_bed()` keeps warning exactly as it does today; the warning text gains a pointer to `--split`.
Nothing splits unless asked.

The alternative - splitting automatically whenever a model exceeds the bed - was rejected because it silently
changes what an existing command produces. `uv run python main.py --preset chop-board` writes one file today;
under auto-split it would write several, breaking existing scripts, the `render_models.py` render set, and
the byte-for-byte export regression tests. Opt-in keeps the change purely additive.

*Preserves existing behaviour:* without `--split`, the build-measure-export path is untouched, so default
geometry and default output paths are bit-identical.

*Acceptance criteria:* "Oversized model is not split without the flag", "Bed warning names the split option".

### Decision 2: Cut positions come from the nominal grid, not the bounding box

A Gridfinity footprint applies its 0.5 mm clearance **once to the whole footprint, not per unit**: an
`N`-unit dimension measures `N*42 - 0.5` mm (verified at N = 3, 4, 6, 7). The model is therefore inset
0.25 mm per side, which means internal grid lines are *not* a whole multiple of 42 from the model's own edge.

The k-th internal grid line of an `N`-unit axis is:

```text
cut_k = PITCH * (k - N/2)        where PITCH = 42.0
```

Worked through: N=6, k=3 gives 0.0 (the chop-board's centreline); N=7, k=3 gives -21.0.

The naive `bounding_box().min + k*42` lands 0.25 mm off every time. This was found the hard way while
investigating the stub, and it is the single most likely thing to get wrong in implementation - hence a
dedicated acceptance criterion rather than a comment.

*Acceptance criteria:* "Cut lands on the nominal grid line".

### Decision 3: Balanced piece planner

Given `n_units` on an axis and that axis's bed limit:

```text
max_units = floor(bed_mm / PITCH)
n_pieces  = ceil(n_units / max_units)
runs      = n_units distributed as evenly as possible over n_pieces
```

Verified against the real cases: N=6 on a 220 mm bed gives `[3, 3]` (one cut at 0.0); N=7 gives `[4, 3]` (one
cut at +21.0); N=12 gives `[4, 4, 4]` (cuts at -84.0 and +84.0).

Balanced rather than greedy-fill (which would give `[5, 1]` for N=6) because equal pieces print more
predictably, warp more symmetrically, and give a join at the model's centreline where it is easiest to
disguise. Minimising piece count first keeps the number of glue joints down.

*Acceptance criteria:* "Split uses the fewest, most equal pieces that fit".

### Decision 4: Slice the built solid; do not re-generate sub-footprints

`build123d` 0.9.0 provides `split(objects, bisect_by=<Plane|Face>, keep=Keep.TOP|BOTTOM|BOTH)`. With
`Keep.BOTH` it returns a `Part` whose `.solids()` yields the pieces. Verified on real geometry: a 7x3
blanking plate cut in ~1.6 s against ~12.5 s to build it, and the chop-board bin behaved identically, with
volume conserved exactly and fillets and stacking feet intact.

The alternative - computing sub-footprints and generating each natively - produces cleaner pieces and is
genuinely better *for blanking plates*, where both routes exist. It was rejected as the primary mechanism
because it cannot express the chop-board case at all (see Context), and having one mechanism that works for
every product type is worth more than a second, better one that works for a subset. Native sub-footprint
generation remains available to users today as two ordinary invocations, and is noted as possible future
work.

*Acceptance criteria:* "Every product type can be split", "Split pieces reassemble to the original volume".

### Decision 5: `--split-mode {glued,standalone}`, defaulting to `glued`

The two modes differ by exactly one rule, and which is correct depends on what the pieces are *for*:

| Mode | Rule | Result |
| --- | --- | --- |
| `glued` (default) | no shave | halves sum to exactly the native width (measured 125.75 + 125.75 = 251.50) |
| `standalone` | shave 0.25 mm off **every** cut face | each piece matches its native equivalent exactly |

The shave rule is uniform because of how the inset falls out: an end piece spans `m*42 - 0.25` (it keeps one
original outer edge) and an interior piece spans exactly `m*42`. Taking 0.25 mm off each cut face lands both
on `m*42 - 0.5`, which is the native `m`-unit dimension. One rule, no special cases.

`glued` is the default because that is what cutting is *for*: a bin cut through its pocket only makes sense
reassembled, and the chop-board - the case driving this change - has a pocket spanning the join. Shaving a
glued assembly would leave it 0.5 mm undersized: loose rather than binding, so harmless, but pointless.

Making the mode a required choice was considered and rejected as friction on the common case. A default plus
an override gives the same explicitness where it matters.

A note on magnitude: field experience cutting these models in OrcaSlicer without adding any clearance has
worked fine, and cutting on the true grid line leaves only 0.25 mm of excess in the standalone case. The
shave is correctness for the standalone case, not a fix for an observed failure.

*Acceptance criteria:* "Glued pieces reassemble to native dimensions", "Standalone pieces match native
dimensions".

### Decision 6: One file per piece, deterministically named and ordered

Pieces are written as `<stem>-part1.<ext>`, `<stem>-part2.<ext>`, ... alongside the requested output path,
ordered by piece position (ascending X, then ascending Y) so a given invocation always maps the same piece to
the same filename. The repo already treats deterministic output paths as a tested property
(`test_default_output_path_is_deterministic`), and a nondeterministic mapping would make UAT and any future
release artifacts unreproducible.

3MF can hold multiple objects in one file, which would be a tidier single artifact. Rejected for this pass:
it would make `--format 3mf` and `--format stl` behave structurally differently, and every slicer handles
separate files identically. Worth revisiting when packaging release artifacts for v1.0.

*Acceptance criteria:* "Pieces are written to deterministic, predictable paths".

### Decision 7: Split on X and Y independently, applied in sequence

Cut positions are planned per axis and applied one axis after the other, so a model oversized on both axes
yields a grid of pieces. This falls directly out of `split()` composing, and needs no special handling.

Z is out of scope (see Non-Goals). A model exceeding bed Z still warns and still exports whole, because
`--split` cannot help it - the design must not silently imply otherwise.

*Acceptance criteria:* "A model oversized on both axes splits on both", "Z-oversized model warns that split
cannot help".

## Risks / Trade-offs

**Cut pieces have open pocket cross-sections at the join.** → Correct and expected in `glued` mode; the
pocket becomes continuous once assembled. In `standalone` mode on a *bin* it is a genuine defect (an
open-ended pocket), so `--split-mode standalone` warns when applied to a model with a pocket. Blanking plates
are unaffected, having no pocket.

**The 0.25 mm nominal-grid offset is easy to reimplement wrongly.** → It has its own spec scenario and unit
test with the measured expected values, so a regression fails loudly rather than producing pieces that are
subtly 0.25 mm out.

**Split adds build time.** → Measured at ~1.6 s against a 12-25 s model build, so it is noise. Real-geometry
split tests are auto-marked `slow` by the existing `tests/conftest.py` convention and stay out of the fast
loop.

**CLI compatibility.** → `--split` and `--split-mode` are new optional flags; no existing flag changes
meaning. The only user-visible change on an existing path is additional text in the bed warning, which
`print-bed-validation` requires to be actionable anyway - so the MODIFIED delta strengthens that requirement
rather than weakening it.

**Export-flow compatibility.** → `export_bin()` keeps its current single-part signature and behaviour; the
multi-piece path wraps it in a loop rather than changing it. Anything calling `export_bin()` directly is
unaffected.

**Future v1.0 packaging.** → Release artifacts become one-to-many for oversized presets: the chop-board
ships as two files plus an assembly note, not one. Worth settling naming before publishing, since renaming
released artifacts is worse than choosing well now. The single-multi-object-3MF option above is the likely
revisit point.

**`knife-blade-block` interaction.** → Its "Block prints without splitting" requirement says the split
machinery SHALL NOT be *required* for the block. An opt-in flag the block does not need does not violate
that, and the requirement is untouched by this change. The `cleaver-block-variant` stub separately flags that
a deeper cleaver channel should be re-checked against the bed.
