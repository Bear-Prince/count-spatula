## Why

Our bins are Gridfinity-compatible at the base but not at the top: they have no stacking lip, so nothing
can sit securely on top of them. The Gridfinity specification defines a stacking lip that mates with the
base profile of the bin above, and every bin we generate currently omits it.

The lip was considered and set aside during the divider work because it looked entangled with pocket and
divider geometry. That reading was wrong. The lip is a sweep along the bin's **outer top rim** — it never
touches the pocket, the dividers, or the base. Treating it as an independent step applied to the finished
rim decouples it from everything that made it look hard, and makes it available to *any* bin we generate,
including the chop-board preset.

Research also removes the main cost: `gridfinity_build123d` already ships a `StackingLip` class whose
constants (0.7 / 1.8 / 1.9 mm steps, 0.25 mm offset) match the published specification exactly. We compose
an existing, spec-conformant part rather than authoring profile geometry ourselves.

## What Changes

- Add an opt-in stacking lip to every bin type (`KitchenBin` and, by inheritance, `CutleryBin`), driven by
  a new `stacking_lip` parameter on `BinParameters` and a `--stacking-lip` CLI flag.
- Reuse `gridfinity_build123d.StackingLip` rather than reimplementing the profile, keeping us aligned with
  the upstream interpretation of the standard.
- Sweep the lip along the outer rim of the bin wall as a distinct build step, independent of pocket shape,
  pocket corner radius, and divider layout — so it applies uniformly to plain bins, cutlery bins, and presets.
- Extend the side-cutout depth so the handle slot cuts *through* the lip, leaving the lip only on the
  intact rim segments instead of bridging across an opening.
- Account for the lip in reported model height: a lipped bin is ~4.12 mm taller than the same bin without one
  (the standard's nominal 4.4 mm less the 0.2 mm apex fillet the upstream library applies).
- Default the lip to **off**, so every existing invocation, preset, and exported artifact is byte-for-byte
  unchanged unless the flag is passed. Not a breaking change.

## Capabilities

### New Capabilities

- `stacking-lip`: An opt-in Gridfinity-standard stacking lip swept along a bin's outer top rim, its
  interaction with side cutouts, its effect on overall model height, and the validation rules that keep it
  printable on thin walls.

### Modified Capabilities

None. The lip is additive and defaults to off:

- `print-bed-validation` already evaluates the model's **actual** bounding box, so the taller lipped model
  is measured correctly with no requirement change.
- `bin-presets` already specifies that overrides apply on top of a preset's defaults, so
  `--preset chop-board --stacking-lip` is covered by existing behaviour.
- `gridfinity-utensil-bin` keeps its current requirements; lip-specific validation lives with the new
  capability so the change stays cohesive.

## Impact

- **`cutlery_bin.py`**: new `stacking_lip` field and validation on `BinParameters`; a lip build step in
  `KitchenBin.__init__` placed before the cutout subtraction; `SideCutoutProfile` invoked with a cutout
  height that clears the lip.
- **`main.py`**: new `--stacking-lip` flag threaded into `BinParameters`.
- **Dependencies**: none added. Uses `StackingLip` from the already-pinned `gridfinity_build123d`.
- **Print-bed warnings**: a lipped bin reports ~4.12 mm more Z, which may newly trip the height warning for
  bins already close to the limit. Correct behaviour, but a visible change in output for lipped builds.
- **Licensing**: no change. The lip profile comes from the upstream library and the published standard, so
  it does not alter any preset's `Provenance`.
