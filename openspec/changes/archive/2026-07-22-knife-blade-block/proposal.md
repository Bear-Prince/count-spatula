## Why

The cutlery-drawer project has bins for cutlery and a chopping board, but the kitchen knives still have
no home — the last thing standing between the current bin set and a finished drawer. Off-the-shelf knife
racks hold knives by their handles and waste the long blade length; storing knives *by the blade*, lying
down and alternated head-to-toe, packs a full set into a fraction of the space and lets each knife lift
straight out.

Now, because the design has crystallised into something small and buildable: only a single central
*block* needs custom geometry — the rest of the footprint is stock Gridfinity blanks — so this is a
tightly scoped, one-part addition rather than a whole bespoke deck.

## What Changes

- Add a new `KnifeBladeBlock` model: a Gridfinity module that holds kitchen knives horizontally by their
  blades. Knives lie edge-down; each blade drops into a tapered, self-centring V-slot in one block.
- Knives are arranged **alternating head-to-toe**, so handles fall to opposite ends and all blades
  overlap in the centre where the single block sits. This halves the lane pitch a wide handle would
  otherwise force.
- The block is a sibling of `KitchenBin` in the existing architecture: a `gridfinity_build123d.BaseEqual`
  base plus a custom slotted top feature (in place of a pocket). Expose it via a factory
  (`create_knife_blade_block`) and CLI wiring that mirror `KitchenBin`/`CutleryBin`.
- Add a parameter dataclass (mirroring `BinParameters`) with an accumulating `validate()`: lane count and
  pitch, block footprint, tapered-slot geometry (mouth width, taper angle, depth), and an effective
  deck/rest height.
- Add a **drawer-clearance check** in the spirit of `check_print_bed`: warn when
  `deck_height + max_blade_depth + clearance` exceeds the drawer's internal height.
- Only the block is generated. The handle-rest zones at each end are filled by generic
  `gridfinity_build123d` blanks — deliberately out of scope, mirroring the project's existing "generic
  equal-compartment grids are out of scope — use `gridfinity_build123d` directly" boundary.
- Optionally add a named preset for the target 7-knife Prima set (an original design), pending a decision
  on whether to land the preset now or after the first physical print.

## Capabilities

### New Capabilities

- `knife-blade-block`: A parametric Gridfinity module that stores kitchen knives lying flat, held by
  their blades in a single block of tapered self-centring slots, arranged alternating head-to-toe.
  Covers the block geometry, its parameters and validation (including the drawer-clearance check), the
  compose-with-blanks boundary, and the model/factory/CLI surface.

### Modified Capabilities

<!-- None. This is a new, self-contained capability. It reuses the BaseEqual foundation and the
     check_print_bed pattern but does not change any existing spec's requirements. -->

## Impact

- **New code**: a `KnifeBladeBlock` part class, its parameter dataclass + `validate()`, a
  `create_knife_blade_block` factory, and a drawer-clearance helper. Likely a new module (e.g.
  `knife_block.py`) alongside `cutlery_bin.py`, or a clearly separated section within it.
- **CLI (`main.py`)**: new subcommand or mode and argument wiring to build and export a block.
- **Tests**: geometry, parameter validation, drawer-clearance, and CLI behaviour, linked to the new
  spec's scenarios via `@pytest.mark.scenario` (per the traceability guard).
- **Dependencies**: none new — reuses `build123d` and `gridfinity_build123d`.
- **Out of scope (no impact)**: the grid-align/print-split machinery (the block is bed-sized), the
  handle-zone decks (stock blanks), and the deferred cleaver / fork / cheese-knife / ProCook items.
