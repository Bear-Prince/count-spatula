## Background: how this proposal evolved

This proposal began life as `utensil-bin-side-cutouts`, on the assumption that the generic utensil bin needed its
own side cutouts to match the chopping-board bin in a drawer. Exploring it surfaced a mistake in that framing:

- **The cutouts were never a generic-bin feature.** They exist on the chop bin to let you get a chopping
  board *out* of a snug pocket. They are intrinsic to the chop bin's job.
- **The toggle was pointed at the wrong bin.** An earlier branch added a `cutouts_enabled` switch to the chop bin.
  But disabling cutouts on a chop bin is a footgun: the board becomes trapped. The ability to turn cutouts *off*
  only makes sense for a bin that still works without them.
- **The chop bin is not a separate kind of thing.** It is a Gridfinity open-top bin with two distinguishing
  traits: a full-height side cutout, and an interior opening sized to a chopping board rather than derived from a
  uniform wall thickness.

A further realization while planning: generic equal-compartment grids are already well served by
`gridfinity_build123d`, so this change should not reimplement them. The project-specific value is an
explicitly-sized pocket with full-height handle cutouts — a base `KitchenBin` — and a cutlery tray is simply that
bin with straight dividers added (a `CutleryBin`).

## Why

`ChopBin` and `UtensilBin` duplicate the same skeleton — Gridfinity base, open-top walls, optional side cutouts —
and the cutout fix (#16) plus any future change must otherwise be done twice. Collapsing them into a `KitchenBin`
base (with a `CutleryBin` specialization) removes that duplication, puts the `cutouts_enabled` toggle where it is
meaningful, turns "the chop bin" into a named preset, and stops us maintaining generic compartment grids that the
library already provides.

## What Changes

- **Introduce `KitchenBin`.** A Gridfinity base, open-top walls up to the bin height, one explicitly-sized rounded
  pocket, and optional full-height side cutouts (default on). Replaces `ChopBin`.
- **Introduce `CutleryBin`.** A `KitchenBin` with straight, single-axis dividers that split the pocket into equal
  columns; the side cutout runs through the dividers. Adding dividers is what turns a `KitchenBin` into a
  `CutleryBin`.
- **Cutouts live on the base `KitchenBin`** as `cutouts_enabled` (default on, full-height) plus fit validation.
- **Defer generic compartment grids to `gridfinity_build123d`.** Retire the `CompartmentsEqual`-based utensil bin;
  there is no second division axis.
- **Introduce presets.** Ship a `chop-board` preset (a `KitchenBin` reproducing today's chop bin).
- **Retire `chop_bin.py`.** Host the geometry in `cutlery_bin.py`.
- **Redesign the CLI around presets and bin type.** A division count of two or more yields a `CutleryBin`. Default
  behaviour may change (pre-1.0).

## Capabilities

### New Capabilities

- `bin-presets`: named, ready-to-use parameter bundles, including a `chop-board` preset (a `KitchenBin`) that
  reproduces the current chopping-board bin.

### Modified Capabilities

- `gridfinity-utensil-bin`: re-centred on the `KitchenBin`/`CutleryBin` model — an explicitly-sized pocket bin with
  optional full-height side cutouts, and an optional single-axis divider split for cutlery. Removes the generic
  equal-compartment grid (deferred to `gridfinity_build123d`). The capability keeps its legacy name (OpenSpec has
  no capability rename).

## Impact

- [chop_bin.py](../../../chop_bin.py): geometry, `BinParameters`, `ChopProfile`, and validation move into
  `cutlery_bin.py`; the module is retired.
- [utensil_bin.py](../../../utensil_bin.py): the `CompartmentsEqual`-based bin is retired; `check_print_bed` is
  retained (moved alongside the new bin).
- New `cutlery_bin.py`: `BinParameters`, `SideCutoutProfile`, `KitchenBin`, `CutleryBin`, and `create_*` factories.
- [main.py](../../../main.py): CLI restructured around presets and bin type; the standalone chop sub-command/flags
  and the `utensil-bin` sub-command are replaced.
- Tests under [tests/](../../../tests/): chop-bin and utensil-bin tests consolidate; pocket, cutout, divider, and
  preset coverage added.
- **Supersedes earlier framings**, none of which is on `main`: the chop-bin cutout toggle from the abandoned
  `feature/toggle-side-cutouts` branch (its mechanism is carried forward here on `KitchenBin`), and the original
  `utensil-bin-side-cutouts` framing.

## Status

Implemented as a single all-in-one change on `feature/unify-chop-bin-as-preset`: proposal, design, specs, and tasks,
then code, UAT, and archive in one PR.
