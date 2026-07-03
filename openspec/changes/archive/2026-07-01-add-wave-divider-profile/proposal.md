## Why

Cutlery such as spoons and forks is narrow at the handle and wide at the business end, so straight,
evenly-spaced dividers waste space: every channel must be as wide as the widest part of the item.
A curved ("S-curve") divider whose neighbours alternate orientation lets adjacent items nest
head-to-tail, packing more cutlery into the same Gridfinity footprint. This mirrors the popular
"Teaspoons (2 Types)" Gridfinity insert, but as a parametric option rather than a fixed model.

## What Changes

- Add an optional **wave** divider profile to `CutleryBin`, selectable alongside the existing
  **straight** dividers. Straight remains the default, so existing behaviour is unchanged.
- Each wave divider follows a single smooth S-curve (one sine period) along the pocket length (Y),
  undulating sideways (X) by a configurable amplitude. The divider centreline still sits at the
  current even spacing and still meets both un-cut end walls, so average column widths are preserved.
- Adjacent dividers are phase-mirrored, so neighbouring channels alternate orientation — the nesting
  behaviour that delivers the space saving.
- Add two `BinParameters` fields (a divider-profile selector defaulting to straight, and a wave
  amplitude in mm) and matching CLI flags on `main.py`, following the existing
  `--divisions` / `--divider-thickness-mm` style.
- Extend parameter validation to reject wave amplitudes that would collide a divider with its
  neighbour or the pocket wall, with an actionable message.
- The handle-slot side cutout must continue to pass through every divider (now wavy), and each
  divider must remain attached to both un-cut end walls.

Non-goals (explicitly deferred to possible future work): multi-bump repeating waves,
silhouette/contoured dividers, per-divider individual shapes, and arbitrary spline profiles.

## Capabilities

### New Capabilities
<!-- None: this extends the existing divider behaviour rather than introducing a new capability. -->

### Modified Capabilities
- `gridfinity-utensil-bin`: the "CutleryBin dividers" requirement currently mandates straight
  dividers; it changes to allow a selectable straight-or-wave profile. The divider-related
  parameter-validation requirement extends to cover the new profile selector and amplitude bound.

## Impact

- **Code**: `cutlery_bin.py` (`BinParameters` fields and validation; `CutleryBin._add_interior`
  gains wave geometry) and `main.py` (new CLI flags wired into `create_parameters`).
- **Tests**: `tests/test_cutlery_bin.py` and `tests/test_cli_and_params.py` for the new
  parameters/flags, validation bounds, backward-compatible default geometry, and the cutout
  still cutting through wavy dividers.
- **Dependencies**: none added; uses existing `build123d` primitives.
- **Backward compatibility**: with the default profile, generated geometry is unchanged.
