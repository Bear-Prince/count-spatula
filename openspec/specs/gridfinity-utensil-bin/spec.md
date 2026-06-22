# gridfinity-utensil-bin Specification

## Purpose

Generate Gridfinity-compatible open-top kitchen utensil bins from validated parameters,
supporting both Gridfinity-standard and freeform heights and configurable compartment
divisions, while rejecting parameters that would produce non-printable geometry.

## Requirements

### Requirement: Parametric Gridfinity utensil bin geometry

The system SHALL generate Gridfinity-compatible open-top bin geometry from validated parameters as a
`KitchenBin`: a Gridfinity base, open-top walls up to the bin height, a single rounded pocket (derived from
a uniform wall thickness by default, or given explicit dimensions), and optional side cutouts. The system
SHALL NOT provide generic equal-compartment grids; those are deferred to `gridfinity_build123d`.

#### Scenario: Generate a KitchenBin from explicit valid parameters

- **WHEN** a user provides a valid grid size, height, and pocket dimensions (length, width, corner radius)
- **THEN** the system produces a `KitchenBin` matching those parameters without runtime errors

#### Scenario: Generate geometry from defaults

- **WHEN** a user omits optional parameters
- **THEN** the system applies the documented defaults (a 2×4 grid, 8 height units, uniform 2 mm walls) and
  produces a valid `KitchenBin` with side cutouts enabled

### Requirement: Gridfinity-standard and freeform height support

The system SHALL accept bin height either as Gridfinity height units (integer multiples of 7 mm)
or as a freeform millimetre value, but not both simultaneously.

#### Scenario: Generate bin with Gridfinity height units

- **WHEN** a user specifies `height_in_units=7`
- **THEN** the system generates a bin with an effective height of 49 mm

#### Scenario: Generate bin with freeform millimetre height

- **WHEN** a user specifies `height_mm=55.0` and omits `height_in_units`
- **THEN** the system generates a bin with a height of 55.0 mm

#### Scenario: Reject combined height specification

- **WHEN** a user specifies both `height_in_units` and `height_mm`
- **THEN** the system raises a validation error identifying the conflict

### Requirement: Parameter validation for printable geometry

The system MUST validate all parameters before geometry construction and reject values outside supported
printable ranges with actionable error messages, covering grid size, height, the pocket dimensions, any
enabled side cutouts, and (for a `CutleryBin`) the divider count and thickness.

#### Scenario: Reject out-of-range grid size

- **WHEN** a user provides `grid_x` or `grid_y` outside the range 1–12
- **THEN** the system refuses geometry generation and reports which parameter is invalid

#### Scenario: Reject a pocket that does not fit

- **WHEN** the pocket length or width is greater than or equal to the outer bin dimension on that axis
- **THEN** the system refuses geometry generation with an actionable validation message

#### Scenario: Reject invalid divider count

- **WHEN** a `CutleryBin` is requested with a division count less than 1
- **THEN** the system refuses geometry generation with a clear validation message

### Requirement: Pocket interior

A `KitchenBin` SHALL have a single interior rounded pocket. By default the pocket is derived from a uniform
`wall_thickness_mm` (default 2 mm), producing equal walls. The pocket MAY instead be given explicit length,
width, and corner radius, independent of any uniform wall thickness, so the end and side walls may differ —
as the `chop-board` preset does.

#### Scenario: Default pocket derived from wall thickness

- **WHEN** a bin is generated with default parameters (no explicit pocket dimensions)
- **THEN** the pocket is the footprint inset by the wall thickness on every side, giving uniform walls

#### Scenario: Explicit pocket with non-uniform walls

- **WHEN** a pocket of 220 mm × 160 mm with a 35 mm corner radius is requested on the chop grid
- **THEN** the bin has an interior opening of those dimensions, with end and side walls of differing thickness

### Requirement: CutleryBin dividers

A `CutleryBin` SHALL be a `KitchenBin` with the pocket split into the requested number of equal columns by
straight dividers. Dividers are parallel to the two cut (handle) walls, evenly spaced, of a configurable
thickness, and span between the two un-cut walls so they are attached at both ends. The interior is divided
along a single axis only; there is no second division axis (generic grids are deferred to
`gridfinity_build123d`).

#### Scenario: Split the pocket into equal columns

- **WHEN** a `CutleryBin` is requested with 3 divisions
- **THEN** the pocket is split into three equal columns by two straight dividers parallel to the cut walls,
  each attached to both un-cut walls

#### Scenario: A single division is a plain KitchenBin pocket

- **WHEN** a `CutleryBin` is requested with 1 division
- **THEN** the interior is a single undivided pocket, identical to a `KitchenBin`

### Requirement: Optional side cutouts

A bin SHALL provide a `cutouts_enabled` option, defaulting to enabled, that cuts a full-height slot through
the two opposing side walls perpendicular to the X axis — and through any `CutleryBin` dividers, which run
parallel to those walls — from the inner floor to the top of the walls, leaving the Gridfinity base intact.
When disabled, the side walls and dividers are solid.

#### Scenario: Cutouts enabled by default

- **WHEN** a bin is generated without specifying `cutouts_enabled`
- **THEN** both side walls receive an identical full-height slot and the base is untouched

#### Scenario: Cutouts disabled

- **WHEN** a bin is generated with `cutouts_enabled=False`
- **THEN** both side walls (and any dividers) are solid with no slot

#### Scenario: Cutouts are symmetric and leave the base intact

- **WHEN** cutouts are enabled
- **THEN** both opposing walls receive an identical slot, starting at the inner floor, removing no material
  from the base below it

#### Scenario: Cutout passes through dividers

- **WHEN** cutouts are enabled on a `CutleryBin` with two or more columns
- **THEN** the full-height slot runs through every divider, and each divider remains attached to the two
  un-cut walls at both ends

#### Scenario: Reject cutouts too large for the side

- **WHEN** cutouts are enabled and the cutout offset and radius cannot fit within the side's available length
- **THEN** the system refuses geometry generation with an actionable validation message

#### Scenario: Skip cutout validation when disabled

- **WHEN** `cutouts_enabled=False` and the cutout dimensions would not fit
- **THEN** the cutout-fit checks are skipped and generation is not blocked by them
