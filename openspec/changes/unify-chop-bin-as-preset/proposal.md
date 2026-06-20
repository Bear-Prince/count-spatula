## Background: how this proposal evolved

This proposal began life as `utensil-bin-side-cutouts`, on the assumption that the generic utensil bin needed its
own side cutouts to match the chopping-board bin in a drawer. Exploring it surfaced a mistake in that framing:

- **The cutouts were never a generic-bin feature.** They exist on the chop bin to let you get a chopping
  board *out* of a snug pocket. They are intrinsic to the chop bin's job.
- **The toggle was pointed at the wrong bin.** An earlier branch added a `cutouts_enabled` switch to the chop bin.
  But disabling cutouts on a chop bin is a footgun: the board becomes trapped. The ability to turn cutouts *off*
  only makes sense for a generic bin, which still works without them.
- **The chop bin is not a separate kind of thing.** It is a generic open-top Gridfinity bin with two
  distinguishing traits: a full-height side cutout, and an interior opening sized to a chopping board rather
  than derived from a uniform wall thickness.

That last point reframes the whole effort. Rather than bolting cutouts onto the utensil bin as a parallel feature,
the cleaner move is to make the chop bin a *preset* of the generic bin, and let the cutout toggle live on the
generic bin where it belongs.

## Why

Two bin types (`ChopBin`, `UtensilBin`) duplicate the same skeleton — Gridfinity base, open-top walls, optional
side cutouts — and only differ in their interior. Maintaining them separately means the cutout fix (#16), the
cutout toggle, and any future change must be done twice and kept in sync. Unifying them removes that duplication,
puts the `cutouts_enabled` toggle on the bin where it is actually meaningful, and turns "the chop bin" into a named
preset rather than a bespoke class.

## What Changes

- **Generalize the bin geometry.** Give the generic bin two interior strategies:
  - *compartments* — N×M equal compartments with uniform walls (today's utensil bin), via `CompartmentsEqual`.
  - *explicit pocket* — one rounded-rectangle opening of an explicit size with potentially non-uniform walls
    (today's chop bin), hand-sketched. This is the new capability; it cannot be expressed by a single uniform
    `wall_thickness`, which is why the chop bin currently has its own class.
- **Move `cutouts_enabled` onto the generic bin.** The toggle and its fit validation become a property of the
  unified bin, not the chop bin. The toggle is meaningful for plain bins (drawer alignment / grip) and is simply
  pinned **on** by the chop preset.
- **Introduce presets.** Add named parameter bundles for the generic bin. Ship a `chop-board` preset that reproduces
  today's chop bin (explicit chopping-board pocket + cutouts on).
- **Retire `chop_bin.py`** once its geometry and defaults live in the generic bin and the `chop-board` preset.
- **Redesign the CLI around presets.** Default behaviour may change (we are pre-1.0, and the user has accepted a
  changed default), so the CLI is free to expose presets explicitly rather than preserving `python main.py` →
  chop bin.
- **Open question for design:** the default `cutouts_enabled` for a *plain* generic bin (enabled for drawer
  alignment vs. disabled to avoid loose contents escaping through a full-height slot). The chop preset answers this
  for itself (always on); only the plain-bin default is open.

## Capabilities

### New Capabilities

- `bin-presets`: named, ready-to-use parameter bundles for the generic bin, including a `chop-board` preset that
  reproduces the current chopping-board bin.

### Modified Capabilities

- `gridfinity-utensil-bin`: becomes the single bin type. Gains an explicitly-sized pocket interior mode (non-uniform
  walls), optional full-height side cutouts with a `cutouts_enabled` toggle and fit validation, and preset support —
  absorbing the standalone chop bin.

## Impact

- [chop_bin.py](../../../chop_bin.py): geometry, `BinParameters`, `ChopProfile`, and validation migrate into the
  generic bin; the module is retired.
- [utensil_bin.py](../../../utensil_bin.py): `UtensilBin`/`UtensilBinParameters` gain the explicit-pocket interior
  strategy, the cutout toggle + fit validation, and preset wiring.
- [main.py](../../../main.py): CLI restructured around presets; the standalone chop sub-command/flags are replaced.
- Tests under [tests/](../../../tests/): chop-bin and utensil-bin tests consolidate; preset and cutout-toggle
  coverage added.
- **Supersedes earlier framings**, neither of which is on `main`:
  - the cutout toggle that an earlier `feature/toggle-side-cutouts` branch added to the chop bin (the footgun
    framing). That branch was abandoned without merging; its `cutouts_enabled` mechanism is carried forward here, on
    the generic bin instead.
  - the original `utensil-bin-side-cutouts` framing (this change's prior identity) — cutouts as a separate
    utensil-bin feature.

## Status

Implemented as a single all-in-one change on `feature/unify-chop-bin-as-preset`: proposal first, then design,
specs, and tasks, then code, UAT, and archive in one PR. Supersedes the abandoned `feature/toggle-side-cutouts`
branch, whose chop-bin cutout toggle is carried forward here on the generic bin.
