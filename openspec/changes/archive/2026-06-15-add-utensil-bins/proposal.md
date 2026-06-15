## Why

The project generates chopping board bins but has no support for the other half of the kitchen
drawer story: the upright bins that hold spatulas, ladles, whisks, and other utensils. Users
need a parametric, CLI-driven way to generate these bins as printable STL or 3MF artifacts,
with enough flexibility to fit their specific printer and drawer.

## What Changes

- Introduce a parametric model for Gridfinity-compatible kitchen utensil bins (open-top, upright
  storage) with configurable grid size, height, compartment divisions, and wall thickness.
- Add support for both Gridfinity-standard heights (multiples of 7 mm) and freeform mm heights.
- Add a CLI entrypoint for utensil bin generation, following the same pattern as the existing
  chopping-board bin CLI.
- Replace `export_stl()` with `build123d.mesher.Mesher` throughout, enabling both STL and 3MF
  output selected by file extension.
- Add optional print-bed size parameters (`--bed-x`, `--bed-y`) that warn the user when the
  requested bin footprint exceeds the configured bed dimensions.

## Capabilities

### New Capabilities

- `gridfinity-utensil-bin`: Generate Gridfinity-compatible open-top utensil bin geometry from
  validated parameters, with configurable grid size, height, compartment divisions, and wall
  thickness.
- `multi-format-export`: Export generated geometry to STL or 3MF based on the output file
  extension, using `build123d.mesher.Mesher`.
- `print-bed-validation`: Warn the user when a requested bin footprint exceeds configured print
  bed dimensions.

### Modified Capabilities

- None

## Impact

- Affected code: new `utensil_bin.py` geometry module; `main.py` extended with utensil bin
  subcommand and Mesher-based export; existing STL export path replaced with Mesher.
- Affected tests: new tests in `tests/` for utensil bin parameter validation, compartment
  defaults, CLI behaviour, format selection, and bed-size warning.
- Dependencies: `build123d.mesher.Mesher` and `py-lib3mf` (already a `build123d` transitive
  dependency, no new runtime dependency needed).
- User-facing behaviour: utensil bins become a first-class CLI output; STL and 3MF are both
  supported for all bin types.
