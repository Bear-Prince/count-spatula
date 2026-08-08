## Why

A blanking plate's rounded corners come from `gridfinity_build123d`'s `BaseEqual`, and on a wall-less plate
those corners are directly visible where a bin's walls would normally hide them (see the archived
`add-blanking-plates` change). Squaring one or more corners was attempted directly on that change
(`feature/add-blanking-plates`, commits since dropped), then abandoned pre-archive per
[WORKFLOW.md](../../WORKFLOW.md)'s "built something complete but conceptually wrong" recipe, after UAT on a
real print found the squared corner sits proud of the baseplate grid instead of lying flat.

Transcribing the root-cause finding forward, per WORKFLOW.md's "transcribe learnings forward" convention:

Traced into the pinned `gridfinity_build123d` fork (`base.py`, `Base.__init__`):

```python
top_face = base.faces().sort_by(Axis.Z)[-1]
edges = base.edges().filter_by(Axis.Z).filter_by(
    lambda edge: any(v in top_face.vertices() for v in edge.vertices())
)
fillet(objects=edges, radius=gridfinity_standard.grid.radius)
```

The corner rounding is a fillet on the *vertical* edges that reach the top face, so it runs the entire height
of the base — from the bottom of the stacking foot up through the platform. There is no shallow,
top-slab-only version of this fillet to mirror. The abandoned attempt subtracted a small square patch
spanning the plate's full thickness at each named corner, which squares off the bottom stacking-foot profile
along with the visible top edge. That foot no longer nests correctly in a baseplate cell at that corner, so
the plate rocks or sits proud there — a real defect, not a cosmetic one.

## What this backlog stub is not

This is a "tracked problem, not yet designed" stub per WORKFLOW.md's "Keeping a backlog item" recipe. It
intentionally has no design, deltas or tasks yet, and will not pass `openspec validate` until those are
written. Do not attempt a straightforward box-subtraction implementation again without first working out how
to keep the stacking-foot mating profile intact — that is precisely what went wrong last time.

## Shape a real design will need to address

- Squaring the outer edge only above the stacking-foot's mating depth (`gridfinity_standard.bottom.platform_height`
  plus the stacking-lip profile height in the pinned fork), so the foot geometry stays untouched and grid-compliant.
- Keeping the flat platform slab square at each requested corner above that depth.
- This likely means a swept/profile-aware corner replacement rather than a single box subtraction against
  the whole part.
- Independent per-corner control (as the abandoned attempt had) is still the right shape for the flag itself,
  since an irregular drawer opening is a plausible real case, not merely a symmetric one.

## Non-goals (carried forward from the abandoned attempt)

- Changing corner rounding on bins with walls — walls already hide the base's rounding, so this is
  plate-only.
- Changing the pinned `gridfinity_build123d` fork's own fillet behaviour — this stays a composition on top
  of it, per CLAUDE.md's "never diverge it" rule for the fork.
