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
enabled side cutouts, and (for a `CutleryBin`) the divider count, thickness, profile, and — for the `wave`
profile — the wave amplitude. For the `wave` profile the amplitude plus half the divider thickness MUST stay
within the per-column spacing with clearance, so a divider cannot collide with its neighbour or the pocket
wall. For side cutouts, each of `cutout_offset_start_units` and `cutout_offset_end_units` MUST be at least 1;
their combined gap in whole grid units (`grid_y − cutout_offset_start_units − cutout_offset_end_units`) MUST
be at least 1; the two rims MUST NOT meet in the middle
(`cutout_arc_start_mm + cutout_arc_end_mm < grid_y × 42`); and `cutout_radius_mm` MUST be less than the
effective bin height, so the rim fillet has room to complete within the wall.

#### Scenario: Reject out-of-range grid size

- **WHEN** a user provides `grid_x` or `grid_y` outside the range 1–12
- **THEN** the system refuses geometry generation and reports which parameter is invalid

#### Scenario: Reject a pocket that does not fit

- **WHEN** the pocket length or width is greater than or equal to the outer bin dimension on that axis
- **THEN** the system refuses geometry generation with an actionable validation message

#### Scenario: Reject invalid divider count

- **WHEN** a `CutleryBin` is requested with a division count less than 1
- **THEN** the system refuses geometry generation with a clear validation message

#### Scenario: Reject a wave amplitude that would collide

- **WHEN** the `wave` profile is selected and the amplitude plus half the divider thickness exceeds the
  per-column spacing clearance
- **THEN** the system refuses geometry generation with an actionable message identifying the amplitude

#### Scenario: Reject a non-positive wave amplitude

- **WHEN** the `wave` profile is selected with an amplitude of zero or less
- **THEN** the system refuses geometry generation with a message to set a positive amplitude or use the
  `straight` profile

#### Scenario: Reject cutouts on a bin shallower than three units

- **WHEN** cutouts are enabled with the default one-unit offsets on a bin with `grid_y` of 2
- **THEN** the system refuses geometry generation, because the combined gap in whole grid units
  (`grid_y − cutout_offset_start_units − cutout_offset_end_units`) is less than 1

#### Scenario: Reject an offset unit below one

- **WHEN** cutouts are enabled and either `cutout_offset_start_units` or `cutout_offset_end_units` is less
  than 1
- **THEN** the system refuses geometry generation with an actionable message

#### Scenario: Reject a radius too large for the wall height

- **WHEN** cutouts are enabled and `cutout_radius_mm` is at or beyond the bin's effective height
- **THEN** the system refuses geometry generation with an actionable message, because the rim fillet would
  not fit within the wall

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
dividers. Dividers are parallel to the two cut (handle) walls, evenly spaced on their centrelines, of a
configurable thickness, and span between the two un-cut walls so they are attached at both ends. The interior
is divided along a single axis only; there is no second division axis (generic grids are deferred to
`gridfinity_build123d`).

Dividers SHALL support a selectable profile. The `straight` profile (the default) produces flat dividers
exactly as before. The `wave` profile bends each divider along a single smooth S-curve (one sine period)
running the length of the pocket, displaced sideways by a configurable amplitude. A `wave` divider's
centreline SHALL stay on the same even spacing as the straight case and SHALL meet both un-cut end walls at
that nominal spacing, so the average column width is preserved and only the boundary undulates. Adjacent
`wave` dividers SHALL be phase-mirrored so neighbouring channels alternate orientation, letting tapered
cutlery nest head-to-tail. With the default `straight` profile the generated geometry SHALL be identical to
the previous straight-divider behaviour.

#### Scenario: Split the pocket into equal columns

- **WHEN** a `CutleryBin` is requested with 3 divisions
- **THEN** the pocket is split into three equal columns by two straight dividers parallel to the cut walls,
  each attached to both un-cut walls

#### Scenario: A single division is a plain KitchenBin pocket

- **WHEN** a `CutleryBin` is requested with 1 division
- **THEN** the interior is a single undivided pocket, identical to a `KitchenBin`

#### Scenario: Default profile preserves straight geometry

- **WHEN** a `CutleryBin` is requested without specifying a divider profile
- **THEN** the dividers are straight and the geometry is identical to the previous straight-divider behaviour

#### Scenario: Wave profile bends the dividers

- **WHEN** a `CutleryBin` is requested with the `wave` profile and a positive amplitude
- **THEN** each divider follows a single S-curve along the pocket length, displaced sideways by that
  amplitude, while its centreline stays on the nominal spacing and meets both un-cut end walls

#### Scenario: Adjacent wave dividers alternate orientation

- **WHEN** a `CutleryBin` with the `wave` profile has two or more dividers
- **THEN** each divider is phase-mirrored relative to its neighbour, so the channels between them alternate
  orientation along the pocket length

### Requirement: Optional side cutouts

A bin SHALL provide a `cutouts_enabled` option, defaulting to enabled, that cuts a full-height slot through
the two opposing side walls perpendicular to the X axis — and through any `CutleryBin` dividers, which run
parallel to those walls — from the inner floor to the top of the walls, leaving the Gridfinity base intact.
When disabled, the side walls and dividers are solid.

The cutout profile's floor-to-wall corner SHALL be sharp (unfilleted) on each end; only the wall-to-rim
corner, where the wall flares out to its widest point, SHALL be rounded, with one shared radius
(`cutout_radius_mm`, default 10 mm). The cutout offset SHALL be independently configurable at each end, as a
whole number of Gridfinity units of solid wall (`cutout_offset_start_units` and `cutout_offset_end_units`,
each defaulting to 1), so bins of different lengths can align their cutouts at a shared end. The reserved
solid wall at each end SHALL be a fixed 1 mm (`CUTOUT_GRID_ALLOWANCE_MM`) shorter than that whole number of
grid units, so the sharp floor edge reaches 1 mm past that end's corresponding internal grid line — the line
itself sits just inside the open cutout, not the solid wall — matching a Gridfinity split convention where
the reserved unit is 1 mm undersized relative to the nominal grid pitch. Because the floor is unfilleted, its
position does not depend on `cutout_radius_mm`.

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

#### Scenario: Cutout floor reaches past the grid line

- **WHEN** a bin is generated with cutouts enabled and the default offset of one grid unit at each end
- **THEN** the sharp floor edge reaches exactly 1 mm past each end's internal grid line, so the line sits
  just inside the open cutout

#### Scenario: Grid-line overshoot holds regardless of radius

- **WHEN** a bin is generated with cutouts enabled and a non-default `cutout_radius_mm`
- **THEN** the floor still reaches exactly 1 mm past the target grid line on each end, because the floor's
  position does not depend on the radius

#### Scenario: Independent per-end cutout offsets

- **WHEN** a bin is generated with different `cutout_offset_start_units` and `cutout_offset_end_units`
- **THEN** the cutout's floor length differs on each end accordingly, and each end's edge still reaches 1 mm
  past its own target grid line

#### Scenario: Cutout passes through dividers

- **WHEN** cutouts are enabled on a `CutleryBin` with two or more columns
- **THEN** the full-height slot runs through every divider, and each divider remains attached to the two
  un-cut walls at both ends

#### Scenario: Reject cutouts too large for the side

- **WHEN** cutouts are enabled and the two ends' rims would meet in the middle of the wall
- **THEN** the system refuses geometry generation with an actionable validation message

#### Scenario: Skip cutout validation when disabled

- **WHEN** `cutouts_enabled=False` and the cutout dimensions would not fit
- **THEN** the cutout-fit checks are skipped and generation is not blocked by them

### Requirement: GridFinity dimensional conformance

The generated bin body SHALL conform to the GridFinity specification's outer dimensions. The outer footprint
SHALL be `N×42 mm − 0.5 mm` on each axis — the standard 0.5 mm total clearance per axis — so the bin matches the
Gridfinity base it is built on and seats in a baseplate without touching its neighbours. The outer corner radius
SHALL be 3.75 mm (the 4 mm baseplate radius less the 0.25 mm clearance per side).

#### Scenario: Footprint applies the GridFinity clearance

- **WHEN** a bin is generated on an N×M grid
- **THEN** its outer footprint is `(N×42 − 0.5)` mm by `(M×42 − 0.5)` mm

#### Scenario: Walls sit flush on the base

- **WHEN** a bin's walls are built on top of the Gridfinity base
- **THEN** the wall outline matches the base's top footprint within meshing tolerance, with no overhang

