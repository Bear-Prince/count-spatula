## Context

`CutleryBin._add_interior()` (in `cutlery_bin.py`) currently places `divisions - 1` straight `Box`
dividers, thin along X, spanning the full pocket length along Y, full height, evenly spaced to make equal
columns. The handle-slot cutout is sketched on a YZ plane and extruded through the full width with
`both=True`, so it already cuts through every divider. Tapered cutlery (spoons, forks) wastes space in
straight channels because each channel must be as wide as the widest part of the item.

This change adds a `wave` divider profile that bends each divider into a single S-curve and mirrors adjacent
dividers, so neighbouring channels alternate orientation and tapered items nest. The proposal and the
`gridfinity-utensil-bin` spec delta define the externally observable behaviour; this document fixes the
technical choices left open in the proposal.

## Goals / Non-Goals

**Goals:**

- Add a selectable `straight` | `wave` divider profile with a wave amplitude, defaulting to `straight`.
- Preserve average column widths, end-wall attachment, and cutout-through-divider behaviour.
- Keep default-profile geometry byte-identical to today (no change for existing callers, presets, or tests).
- Validate the amplitude so a wave divider cannot collide with a neighbour or the pocket wall.

**Non-Goals:**

- Multi-bump repeating waves, silhouette/contoured dividers, per-divider individual shapes, arbitrary
  splines (deferred).
- A second division axis or generic grids (remain deferred to `gridfinity_build123d`).
- A bundled "spoon-nest" preset (possible future follow-up, not in this change).

## Decisions

### 1. Curve shape: one full sine period, zero at both ends

The divider centreline is displaced in X as a function of position `t ∈ [0, 1]` along the pocket length:
`x_offset(t) = amplitude * sin(2π·t)`. This is a true "S": it bulges +X over the first half and −X over the
second, crossing the centreline at the midpoint, and is **zero at `t = 0` and `t = 1`** so each divider meets
both un-cut end walls at exactly its nominal spacing. That preserves end attachment and average column width
(maps to the spec scenarios "Wave profile bends the dividers" and "Default profile preserves straight
geometry").

*Alternative considered:* a half period (`sin(π·t)`, a single bulge). Rejected because it pushes the whole
divider to one side, biasing column widths and giving a less natural nesting boundary than the symmetric S.

### 2. Phase-mirror neighbours by negating amplitude

Divider `k` (0-indexed) uses `amplitude * (-1)**k`. With a full sine period, mirroring is simply sign
inversion, so adjacent channels alternate orientation (spec scenario "Adjacent wave dividers alternate
orientation"). No phase offset bookkeeping is needed.

### 3. Geometry: extrude a sampled wavy band, not a sweep

Build each divider as a 2D closed band in the XY plane — the region between two offset sampled polylines
(`centreline ± divider_thickness/2`), sampled at a fixed resolution (e.g. 64 points over the length) — then
extrude it to the wall height. Sampling the sine as a polyline avoids the boolean fragility of sweeping a
profile along a spline path and keeps the result a clean prism that the existing cutout `SUBTRACT` slices
without special handling.

*Alternative considered:* `sweep` a rectangle along a sine path. Rejected as more fragile (profile
orientation, self-intersection near high curvature) for no visual benefit at these amplitudes.

### 4. Cutout interaction: no special handling, but assert span

Because the cutout removes all material in its Y/Z footprint across the full width, it slices the wavy slab
wherever the slab crosses that Y range, exactly as for a straight divider. The band is built across the full
pocket length so its ends embed in the un-cut walls. A test asserts the slot still passes through wavy
dividers and that each divider remains attached at both ends (spec scenario "Cutout passes through dividers"
continues to hold).

### 5. Validation bound: `amplitude ≤ (column_pitch − divider_thickness − MIN_CHANNEL_GAP) / 2`

With `column_pitch = effective_pocket_width / divisions`, two mirrored neighbours approach each other most
closely where their offsets are extreme; the gap there is `column_pitch − 2·amplitude − divider_thickness`.
Requiring that to stay at or above a `MIN_CHANNEL_GAP` clearance gives the bound above. This is the tightest
applicable constraint and also keeps the outermost dividers clear of the pocket wall, so it is applied
whenever the `wave` profile is active. `MIN_CHANNEL_GAP` is a module constant (proposed 2.0 mm, tunable) so a
printed channel neck stays usable. A `wave` profile with amplitude `≤ 0` is rejected with a message to set a
positive amplitude or use `straight` (spec scenarios "Reject a wave amplitude that would collide" and "Reject
a non-positive wave amplitude").

### 6. Parameter and CLI surface

Add to `BinParameters`: `divider_profile: str = "straight"` (accepting `"straight"` | `"wave"`) and
`divider_amplitude_mm: float = 0.0`. Add CLI flags `--divider-profile` (choices `straight`/`wave`) and
`--divider-amplitude-mm`, wired through `create_parameters` in `main.py` exactly like the existing
`--divisions` / `--divider-thickness-mm`. The default `straight`/`0.0` pair reproduces current geometry, so
the STL/3MF export flow and any preset artifacts are unchanged.

## Risks / Trade-offs

- **Mesh/boolean fragility of the wavy slab** → Use a sampled polyline band extruded to a prism (Decision 3)
  rather than a swept spline; keep sampling resolution fixed and modest.
- **Faceting visible on the curve from polyline sampling** → Choose a sampling count that keeps chord error
  below typical slicer/printer resolution; expose only amplitude, not the sample count, to keep the surface
  simple.
- **Drift from default geometry** → The `straight` branch is left untouched and a regression test asserts a
  default `CutleryBin` is identical to the pre-change output, protecting existing callers and presets.
- **CLI / v1.0 packaging compatibility** → Both new flags are optional with backward-compatible defaults;
  no existing invocation or curated preset artifact changes, and the export path is unaffected.
- **Validation bound too conservative or too loose** → `MIN_CHANNEL_GAP` is a single named constant, so the
  clearance can be tuned from print feedback without reworking the formula.
