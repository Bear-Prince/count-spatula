## MODIFIED Requirements

### Requirement: Parametric Gridfinity utensil bin geometry

The system SHALL generate Gridfinity-compatible open-top kitchen bin geometry from validated
parameters using a selectable interior strategy: either equal compartments (via
`gridfinity_build123d`'s `Bin` with `CompartmentsEqual`) or a single explicitly-sized rounded pocket.
The bin is built as a Gridfinity base, open-top walls up to the bin height, the selected interior, and
optional side cutouts.

#### Scenario: Generate compartment-interior geometry from explicit valid parameters

- **WHEN** a user provides a valid grid size, height, and a compartment interior (a number of
  `divisions` and a wall thickness)
- **THEN** the system produces compartment bin geometry matching those parameters without runtime errors

#### Scenario: Generate pocket-interior geometry from explicit valid parameters

- **WHEN** a user provides a valid grid size, height, and a pocket interior (length, width, corner radius)
- **THEN** the system produces a single explicitly-sized rounded pocket matching those parameters

#### Scenario: Generate geometry from defaults

- **WHEN** a user omits optional parameters
- **THEN** the system applies documented defaults (2×4 grid, 7 height units, a single-column compartment
  interior with 2 mm walls) with side cutouts enabled, and produces a valid Gridfinity-compatible bin

### Requirement: Configurable compartment divisions

When the compartment interior strategy is selected, the system SHALL divide the bin interior into the
requested number of equal columns, using straight dividers that are parallel to the two cut (handle)
walls and evenly spaced, with wall thickness applied between and around compartments. Dividers span
between the two un-cut walls so they are attached at both ends. The interior is divided along a single
axis only; there is no second division axis.

#### Scenario: Single open compartment (default)

- **WHEN** the compartment interior has `divisions=1`
- **THEN** the bin interior is one open pocket with outer walls of the configured thickness

#### Scenario: Multiple equal columns

- **WHEN** the compartment interior has `divisions=2`
- **THEN** the bin interior is split into two equal columns by one straight divider parallel to the cut
  walls and attached to both un-cut walls

#### Scenario: Dividers are straight and parallel to the cut walls

- **WHEN** any compartment interior with two or more divisions is generated
- **THEN** every divider is straight, parallel to the two cut walls, and evenly spaced across the bin

### Requirement: Parameter validation for printable geometry

The system MUST validate all parameters before geometry construction and reject values outside
supported printable ranges with actionable error messages, including the selected interior strategy and
any enabled side cutouts.

#### Scenario: Reject out-of-range grid size

- **WHEN** a user provides `grid_x` or `grid_y` outside the range 1–12
- **THEN** the system refuses geometry generation and reports which parameter is invalid

#### Scenario: Reject invalid compartment divisions

- **WHEN** a compartment interior has `divisions` less than 1
- **THEN** the system refuses geometry generation with a clear validation message

#### Scenario: Reject non-positive wall thickness

- **WHEN** a compartment interior has `wall_thickness_mm` of 0 or less
- **THEN** the system refuses geometry generation with a clear validation message

## ADDED Requirements

### Requirement: Explicit-pocket interior strategy

The system SHALL support an interior strategy consisting of a single rounded-rectangle pocket of an
explicitly specified length, width, and corner radius, independent of a uniform wall thickness, so the
end and side walls may differ in thickness.

#### Scenario: Pocket sized independently of wall thickness

- **WHEN** a pocket interior of 220 mm × 160 mm with a 35 mm corner radius is requested on a 6×4 grid
- **THEN** the bin has an interior opening of those dimensions, with end and side walls of differing
  thickness

#### Scenario: Reject a pocket that does not fit

- **WHEN** the requested pocket length or width is greater than or equal to the outer bin dimension on
  that axis
- **THEN** the system refuses geometry generation with an actionable validation message

### Requirement: Optional side cutouts

The system SHALL provide a `cutouts_enabled` option, defaulting to enabled, that cuts a full-height slot
through the two opposing side walls perpendicular to the X axis — and through any compartment dividers,
which run parallel to those walls — from the inner floor to the top of the walls, leaving the Gridfinity
base intact. When disabled, the side walls and dividers are solid.

#### Scenario: Cutouts enabled by default

- **WHEN** a bin is generated without specifying `cutouts_enabled`
- **THEN** both side walls receive an identical full-height slot and the base is untouched

#### Scenario: Cutouts disabled

- **WHEN** a bin is generated with `cutouts_enabled=False`
- **THEN** both side walls are solid with no slot

#### Scenario: Cutouts are symmetric and leave the base intact

- **WHEN** cutouts are enabled
- **THEN** both opposing walls receive an identical slot, starting at the inner floor, removing no
  material from the base below it

#### Scenario: Cutout passes through dividers

- **WHEN** cutouts are enabled on a bin with two or more columns
- **THEN** the full-height slot runs through every divider, and each divider remains attached to the
  two un-cut walls at both ends

#### Scenario: Reject cutouts too large for the side

- **WHEN** cutouts are enabled and the cutout offset and radius cannot fit within the side's available
  length
- **THEN** the system refuses geometry generation with an actionable validation message

#### Scenario: Skip cutout validation when disabled

- **WHEN** `cutouts_enabled=False` and the cutout dimensions would not fit
- **THEN** the cutout-fit checks are skipped and generation is not blocked by them
