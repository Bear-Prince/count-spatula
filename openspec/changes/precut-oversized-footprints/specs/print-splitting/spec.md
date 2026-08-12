# print-splitting Specification

## Purpose

Allow a model too large for the configured print bed to be cut into bed-fitting pieces along Gridfinity grid
lines, so oversized designs - notably the `chop-board` preset - can be printed without hand-editing the model
in a slicer.

## ADDED Requirements

### Requirement: Splitting is opt-in

The system SHALL split a model only when `--split` is given. Without the flag the system SHALL generate and
export a single file exactly as it does today, including when the model exceeds the configured build volume.

#### Scenario: Oversized model is not split without the flag

- **WHEN** a model exceeding the build volume is generated without `--split`
- **THEN** the system emits the oversize warning, exports one file, and exits zero

#### Scenario: Split produces bed-fitting pieces

- **WHEN** a model exceeding the build volume is generated with `--split`
- **THEN** the system exports two or more pieces, each of whose bounding box fits within the configured build
  volume

### Requirement: Cuts land on nominal Gridfinity grid lines

Cut positions SHALL be derived from the nominal Gridfinity grid, not from the model's bounding box. A
Gridfinity footprint applies its 0.5 mm clearance once to the whole footprint rather than per unit, so the
model is inset 0.25 mm per side and internal grid lines are NOT a whole multiple of the 42 mm pitch from the
model's own edge. The k-th internal grid line of an `N`-unit axis SHALL be at `PITCH * (k - N/2)`.

#### Scenario: Cut lands on the nominal grid line

- **WHEN** a 6-unit axis is cut at its third internal grid line
- **THEN** the cut is placed at 0.0 mm, and each resulting piece measures 125.75 mm on that axis

#### Scenario: Cut position is not derived from the bounding box

- **WHEN** a 7-unit axis is cut at its third internal grid line
- **THEN** the cut is placed at -21.0 mm, not at the 0.25 mm-offset position that measuring from the model's
  own edge would give

### Requirement: Fewest and most equal pieces

The system SHALL split an axis into the fewest pieces that each fit the bed, and SHALL distribute the units
as evenly as possible across those pieces. The maximum units per piece SHALL be `floor(bed_mm / PITCH)`.

#### Scenario: Six units split into two equal halves

- **WHEN** a 6-unit axis is split against a 220 mm bed
- **THEN** the system produces two pieces of 3 units each, from a single cut

#### Scenario: Seven units split unevenly only where necessary

- **WHEN** a 7-unit axis is split against a 220 mm bed
- **THEN** the system produces two pieces of 4 and 3 units, from a single cut

### Requirement: Glued reassembly is the default

`--split-mode` SHALL default to `glued`. In `glued` mode the system SHALL NOT shave the cut faces, so the
pieces reassemble to the original model's dimensions exactly.

#### Scenario: Glued pieces reassemble to the native dimension

- **WHEN** a `chop-board` bin is split with the default mode
- **THEN** the two pieces measure 125.75 mm each on the cut axis, summing to the original 251.50 mm

#### Scenario: Split conserves the model volume

- **WHEN** a model is split in `glued` mode
- **THEN** the combined volume of the pieces equals the volume of the unsplit model

### Requirement: Standalone mode shaves every cut face

In `--split-mode standalone` the system SHALL remove 0.25 mm from every cut face, so each piece matches the
dimensions of a natively-generated model of the same unit count. Because an end piece spans `m*42 - 0.25` and
an interior piece spans exactly `m*42`, this single rule lands both on the native `m*42 - 0.5`.

#### Scenario: Standalone pieces match native dimensions

- **WHEN** a 7-unit blanking plate is split in `standalone` mode against a 220 mm bed
- **THEN** the pieces measure 167.50 mm and 125.50 mm, matching natively-generated 4-unit and 3-unit plates

#### Scenario: Standalone mode warns on a pocketed model

- **WHEN** `--split-mode standalone` is applied to a model with a pocket
- **THEN** the system warns that the pieces will have open-ended pockets, and still exports them

### Requirement: Splitting applies to every product type

The system SHALL split any generated model - kitchen bins, cutlery bins, blanking plates and knife blocks -
by operating on the built solid rather than on its parameters. Splitting SHALL NOT require that a piece be
expressible as a set of generation parameters.

#### Scenario: A preset with an explicitly-sized pocket splits

- **WHEN** the `chop-board` preset, whose 220 mm pocket spans the join, is split
- **THEN** the system produces pieces cut through the pocket, without attempting to re-derive pocket
  dimensions for a smaller footprint

#### Scenario: A wall-less plate splits

- **WHEN** a blanking plate too large for the bed is split
- **THEN** the system produces bed-fitting plate pieces

### Requirement: Deterministic piece output paths

The system SHALL write each piece to `<stem>-part<n>.<ext>` alongside the requested output path, numbering
pieces in a stable order derived from their position (ascending X, then ascending Y), so repeated runs of the
same invocation map the same piece to the same filename.

#### Scenario: Pieces are written to predictable paths

- **WHEN** a model is split with `--output build/chop.stl`
- **THEN** the system writes `build/chop-part1.stl` and `build/chop-part2.stl` and reports each exported path

#### Scenario: Piece numbering is stable across runs

- **WHEN** the same split invocation is run twice
- **THEN** each piece is written to the same filename both times

### Requirement: Splitting covers both horizontal axes only

The system SHALL plan and apply cuts independently on X and Y, producing a grid of pieces when a model
exceeds the bed on both. The system SHALL NOT split on Z, and SHALL report that splitting cannot resolve a
Z-axis overflow.

#### Scenario: A model oversized on both axes splits on both

- **WHEN** a model exceeding the bed on X and on Y is split
- **THEN** the system produces pieces cut on both axes, each fitting the bed

#### Scenario: Z overflow is reported as unsplittable

- **WHEN** a model exceeding the maximum print height is split
- **THEN** the system warns that splitting cannot resolve a Z-axis overflow, and still exports the pieces its
  X and Y cuts produced
