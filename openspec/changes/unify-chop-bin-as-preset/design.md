## Context

The repo has two bin classes that share most of their geometry. `ChopBin` (in `chop_bin.py`) builds a Gridfinity
base, extrudes walls around an explicitly-sized rounded pocket (chopping-board sized), and cuts a full-height slot
through two opposing walls. `UtensilBin` (in `utensil_bin.py`) builds a Gridfinity base and an open-top
compartmentalized interior via `gridfinity_build123d`'s `Bin` + `CompartmentsEqual`, with no cutouts.

Post-#16, the side-cutout geometry is pocket-independent: it only needs the inner-floor Z, the top Z, the grid
width to extrude through, and the `ChopProfile` dimensions. That makes it portable to any bin body. The two classes
differ only in their **interior**: a uniform-wall compartment grid versus a single explicitly-sized pocket (whose
walls are deliberately non-uniform — e.g. a 6×4 chop bin has 16 mm end walls and 4 mm side walls, which a single
`wall_thickness` cannot express).

This change unifies them into one bin type with a selectable interior, moves the cutout toggle onto that bin, and
expresses the chop bin as a preset.

## Goals / Non-Goals

**Goals:**

- One bin type and one parameter contract, with a selectable interior strategy.
- `cutouts_enabled` (and the fit validation) as a property of the unified bin; default **on, full-height**, for
  plain bins; the chop preset pins it on.
- A preset mechanism with a `chop-board` preset that reproduces today's chop bin geometry.
- Retire `chop_bin.py`; consolidate tests.

**Non-Goals:**

- Choosing *which* walls get cutouts, or per-side cutout sizing (cutouts stay on the same opposing pair as today).
  Deferred.
- A configurable cutout height or a partial-height / retaining-lip variant. Cutouts are always full-height
  (inner floor to rim); there is no height option.
- Preserving the current CLI surface. Default behaviour may change (pre-1.0).

## Decisions

- **One bin, two interior strategies modelled as a small union.** Add `CompartmentInterior(div_x, div_y,
  wall_thickness_mm)` and `PocketInterior(length_mm, width_mm, corner_radius_mm)` dataclasses; the unified
  `BinParameters` holds exactly one as an `interior` field. *Alternative:* a `mode` enum plus optional fields —
  rejected, it invites invalid field combinations and weak validation. *Alternative:* subclasses per bin —
  rejected, that is the duplication we are removing. *Acceptance:* building with each interior yields the expected
  geometry; a missing/unknown interior is rejected by `validate()`.
- **Single `BinParameters`, standard Gridfinity orientation.** Replace both parameter classes with one, using
  `grid_x`/`grid_y` (matching `BaseEqual` and the utensil bin) rather than the chop bin's
  `grid_length`/`grid_width` swap. *Acceptance:* utensil dimensions and chop dimensions are both reproducible; the
  `chop-board` preset's bounding box matches today's chop bin within tolerance.
- **Cutouts become a generic feature, lifted verbatim from the post-#16 chop bin.** Reuse the YZ-plane,
  `both=True` through-cut and the `ChopProfile`; keep `cutout_offset_from_edge_mm` + `cutout_radius_mm` + the fit
  validation, gated by `cutouts_enabled`. Cutouts sit on the two walls perpendicular to X (as today). Default
  `cutouts_enabled=True`. *Acceptance:* the #16 regression guarantees (material removed from walls, base intact,
  starts at inner floor, symmetric) hold for the unified bin; `cutouts_enabled=False` leaves solid walls; fit
  validation only fires when enabled.
- **Presets are named bundles that return a fully-populated `BinParameters`.** Ship `chop-board` (pocket
  220×160 r35, base corner radius, cutouts on, height 56). *Acceptance:* the `chop-board` preset reproduces the
  current chop bin's volume/bbox; presets are discoverable/listable.
- **CLI redesigned around presets.** A single generation entry takes `--preset <name>` (seeds defaults) plus
  explicit overrides and an interior selector; the chop default and the `utensil-bin` sub-command are removed. A
  plain invocation produces a plain compartment bin (cutouts on). *Acceptance:* `--preset chop-board` reproduces
  chop output; an unknown preset exits non-zero with actionable text. Exact flag surface is part of this design's
  review.
- **Retire `chop_bin.py`; generalize the module.** Move the unified geometry into a neutrally-named module
  (proposed `kitchen_bin.py` with class `KitchenBin`; `ChopProfile` → `SideCutoutProfile`), since both "chop" and
  "utensil" undersell it. The `gridfinity-utensil-bin` capability spec keeps its name (history) but its content
  generalizes. *Acceptance:* `chop_bin.py` is gone, imports updated, the test suite consolidated and green.

## Risks / Trade-offs

- **Full-height cutouts only.** [Risk] A floor-to-rim slot could let loose items escape a plain bin sideways. →
  The product owner considers this a non-issue in practice: contents get piled in regardless, and a bin is printed
  to fit its cutlery so items are held at both ends. Cutouts are therefore always full-height, with no
  partial-height option. Mitigation: none required; the changed default is noted in the README.
- **Default output changes.** [Risk] Plain utensil bins now have cutouts and a standardized orientation, so prior
  outputs change. → Accepted (pre-1.0). Mitigation: the `chop-board` preset reproduces the chop bin exactly (locked
  by a regression test); note the change in README.
- **build123d sensitivity.** [Risk] The cut depends on the #16 YZ-plane technique and pinned build123d 0.9.0. →
  Mitigation: port the geometry and the #16 wall/base/floor/symmetry tests verbatim onto the unified bin; keep the
  pins.
- **Two interior code paths.** [Risk] Compartment vs pocket interiors could drift. → Mitigation: share the
  base + walls + cutout pipeline; only the interior sketch differs between strategies.

## Migration Plan

1. Build the unified `BinParameters` + interior union + `KitchenBin` geometry alongside the existing code.
2. Port the cutout geometry/validation and the #16 regression tests onto it.
3. Add the preset mechanism and the `chop-board` preset; lock chop equivalence with a regression test.
4. Switch `main.py` to the preset-oriented CLI.
5. Delete `chop_bin.py` and `utensil_bin.py`'s superseded pieces; consolidate tests.
6. UAT (generate plain bin, `chop-board`, `--no-cutouts`, a too-small-cutout error), then archive.

All within one PR. Rollback is reverting the PR.

## Open Questions

- **Resolved:** plain-bin cutout default → enabled, full-height.
- Module/class naming (`kitchen_bin.py` / `KitchenBin`, `SideCutoutProfile`) — reasonable default; confirm at
  design review.
- Whether to keep a `utensil`-style preset/alias for familiarity, or rely solely on explicit flags. Proposed: no
  alias (pre-1.0).
