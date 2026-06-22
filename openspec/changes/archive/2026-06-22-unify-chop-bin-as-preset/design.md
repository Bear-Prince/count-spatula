## Context

The repo has two bin classes that share most of their geometry. `ChopBin` (in `chop_bin.py`) builds a Gridfinity
base, extrudes walls around an explicitly-sized rounded pocket (chopping-board sized), and cuts a full-height slot
through two opposing walls. `UtensilBin` (in `utensil_bin.py`) builds a Gridfinity base and an open-top
compartmentalized interior via `gridfinity_build123d`'s `Bin` + `CompartmentsEqual`, with no cutouts.

Post-#16, the side-cutout geometry is pocket-independent: it only needs the inner-floor Z, the top Z, the grid
width to extrude through, and the `ChopProfile` dimensions. That makes it portable to any bin body.

Generic equal-compartment grids are already well served by `gridfinity_build123d` itself, so this change does not
reimplement them. The distinctive, project-specific geometry is an explicitly-sized pocket with full-height handle
cutouts. That becomes the base bin; a cutlery tray is that bin with straight dividers added.

## Goals / Non-Goals

**Goals:**

- A `KitchenBin` base: Gridfinity base + open-top walls + one explicitly-sized rounded pocket + optional full-height
  side cutouts (default on). The `chop-board` preset is a `KitchenBin`.
- A `CutleryBin(KitchenBin)` that adds straight, single-axis dividers splitting the pocket into equal columns, with
  the cutout running through the dividers.
- A preset mechanism shipping `chop-board`.
- Retire `chop_bin.py` and the `CompartmentsEqual`-based utensil bin; consolidate tests.

**Non-Goals:**

- Generic equal-compartment grids / a second division axis. Deferred to `gridfinity_build123d`.
- A configurable cutout height or a partial-height / retaining-lip variant. Cutouts are always full-height (inner
  floor to rim); there is no height option.
- Preserving the current CLI surface. Default behaviour may change (pre-1.0).

## Decisions

- **`CutleryBin` is-a `KitchenBin` plus dividers.** `KitchenBin` owns the full build via a template method —
  base → walls → pocket → (divider hook) → cutouts — where the divider hook is a no-op in `KitchenBin` and supplies
  the dividers in `CutleryBin`. This makes "adding dividers turns a KitchenBin into a CutleryBin" literal, while
  respecting the build order: the cutout must be cut *after* the dividers exist so the slot passes through them.
  *Alternative:* one class with an optional `divisions` field — rejected, the two named types better express the
  domain and keep `KitchenBin` free of divider concerns. *Acceptance:* a `CutleryBin(divisions=1)` is geometrically
  identical to a `KitchenBin`; `divisions≥2` adds attached dividers with the cutout running through.
- **Pocket base with a wall-thickness default, no `CompartmentsEqual`.** A `KitchenBin` has a single pocket. By
  default it is derived from a uniform `wall_thickness_mm` (default 2 mm) — so a plain bin has even 2 mm walls — and
  it can instead be given explicit length/width/corner-radius for non-uniform walls (the `chop-board` preset). The
  generic default is a `2×4`, 8-height-unit bin; it is **not** the chop bin. We do not wrap
  `gridfinity_build123d`'s `CompartmentsEqual`; `CutleryBin` dividers are hand-built straight walls inside our own
  pocket. *Acceptance:* the default bin has uniform 2 mm walls and a `2×4` footprint; an explicit pocket yields
  non-uniform walls; no generic grid capability is exposed.
- **Single `BinParameters`, standard Gridfinity orientation.** One parameter dataclass carrying grid size, height,
  base corner radius, pocket dimensions, and the cutout fields; `CutleryBin` adds `divisions` and a divider
  thickness. Use `grid_x`/`grid_y` (matching `BaseEqual`) rather than the chop bin's length/width swap.
  *Acceptance:* the `chop-board` preset's bounding box matches today's chop bin within tolerance.
- **Cutouts lifted verbatim from the post-#16 chop bin.** Reuse the YZ-plane, `both=True` through-cut and the
  profile (renamed `SideCutoutProfile`); keep `cutout_offset_from_edge_mm` + `cutout_radius_mm` + the fit validation,
  gated by `cutouts_enabled` (default `True`). Cutouts sit on the two walls perpendicular to X and pass through any
  dividers. *Acceptance:* the #16 regression guarantees hold; the slot passes through `CutleryBin` dividers, which
  remain attached at both ends.
- **Presets are named bundles that return a fully-populated `BinParameters`.** Ship `chop-board` (pocket
  220×160 r35, base corner radius, cutouts on, height 56) as a `KitchenBin`. *Acceptance:* the `chop-board` preset
  reproduces the current chop bin's volume/bbox; presets are listable.
- **CLI redesigned around presets and bin type.** A single entry takes `--preset <name>` (seeds defaults) plus
  overrides; a division count of ≥2 produces a `CutleryBin`, otherwise a `KitchenBin`. The chop default and the
  `utensil-bin` sub-command are removed. `--no-cutouts` is supported for generic bins but rejected for presets that
  mark cutouts as required (the `chop-board` preset), since a chop bin without cutouts traps the board.
  *Acceptance:* `--preset chop-board` reproduces chop output; `--preset chop-board --no-cutouts` exits non-zero; an
  unknown preset exits non-zero.
- **Module/class naming.** Host the unified geometry in `cutlery_bin.py` with classes `KitchenBin` and
  `CutleryBin`, and `SideCutoutProfile`. Retire `chop_bin.py` and the generic pieces of `utensil_bin.py` (retain
  `check_print_bed`). The `gridfinity-utensil-bin` capability spec keeps its legacy name (OpenSpec has no capability
  rename) but its content now describes the `KitchenBin`/`CutleryBin` model.

## Risks / Trade-offs

- **Drops generic compartment grids.** [Risk] The current utensil bin allows `div_x`/`div_y` 2D grids; this removes
  them. → Accepted: generic grids are deferred to `gridfinity_build123d`, and a divided cutlery tray is served by
  `CutleryBin`. Captured in the spec as a `REMOVED` requirement with a migration note.
- **Default output changes.** [Risk] The default bin and orientation change from today's utensil bin. → Accepted
  (pre-1.0). Mitigation: the `chop-board` preset reproduces the chop bin exactly (locked by a regression test);
  the change is noted in the README.
- **build123d sensitivity.** [Risk] The cut depends on the #16 YZ-plane technique and pinned build123d 0.9.0. →
  Mitigation: port the geometry and the #16 wall/base/floor/symmetry tests onto the new bin; keep the pins.
- **Template-method build order.** [Risk] If a subclass adds dividers after the cutout, the slot would not pass
  through them. → Mitigation: `KitchenBin` fixes the order and exposes only a pre-cutout divider hook.

## Migration Plan

1. Build `cutlery_bin.py` with `BinParameters`, `SideCutoutProfile`, `KitchenBin` (base → walls → pocket → hook →
   cutouts), and `CutleryBin(KitchenBin)` supplying dividers via the hook.
2. Port the cutout geometry/validation and the #16 regression tests onto `KitchenBin`.
3. Add the preset mechanism and the `chop-board` preset; lock chop equivalence with a regression test.
4. Switch `main.py` to the preset-oriented CLI (`--preset`, divisions → `CutleryBin`).
5. Delete `chop_bin.py` and the generic pieces of `utensil_bin.py`; consolidate tests.
6. UAT (default `KitchenBin`, `chop-board`, a multi-division `CutleryBin`, `--no-cutouts`, a too-small-cutout
   error), then archive.

All within one PR. Rollback is reverting the PR.

## Open Questions

- **Resolved:** plain-bin cutout default → enabled, full-height; module/class names → `cutlery_bin.py`,
  `KitchenBin`, `CutleryBin`; generic compartments → deferred to `gridfinity_build123d`; default footprint →
  `2×4`, 8 height units, uniform 2 mm walls (informed by the user's real bin collection); `chop-board` carries the
  explicit chop pocket (it is no longer the default).
- Exact divider thickness default for `CutleryBin` — reasonable default chosen in implementation (matches the
  former utensil wall thickness); confirm at review if it matters.
