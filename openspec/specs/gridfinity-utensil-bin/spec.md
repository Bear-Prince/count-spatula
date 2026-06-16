# gridfinity-utensil-bin Specification

## Purpose

Generate Gridfinity-compatible open-top kitchen utensil bins from validated parameters,
supporting both Gridfinity-standard and freeform heights and configurable compartment
divisions, while rejecting parameters that would produce non-printable geometry.

## Requirements

### Requirement: Parametric Gridfinity utensil bin geometry

The system SHALL generate Gridfinity-compatible open-top kitchen utensil bin geometry from
validated parameters, using the `gridfinity_build123d.Bin` class with `CompartmentsEqual`.

#### Scenario: Generate geometry from explicit valid parameters

- **WHEN** a user provides valid grid size, height, compartment divisions, and wall thickness
- **THEN** the system produces a bin geometry model matching those parameters without runtime errors

#### Scenario: Generate geometry from defaults

- **WHEN** a user omits optional parameters
- **THEN** the system applies documented defaults (2×4 grid, 7 height units, 1×1 compartments,
  2 mm walls) and produces a valid Gridfinity-compatible utensil bin geometry

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

### Requirement: Configurable compartment divisions

The system SHALL divide the bin interior into equal compartments according to the requested
`div_x` and `div_y` values, with wall thickness applied between and around compartments.

#### Scenario: Single open compartment (default)

- **WHEN** `div_x=1` and `div_y=1`
- **THEN** the bin interior is one open pocket with outer walls of the configured thickness

#### Scenario: Multiple compartments

- **WHEN** `div_x=2` and `div_y=1`
- **THEN** the bin interior is divided into two equal columns with divider walls of the
  configured thickness

### Requirement: Parameter validation for printable geometry

The system MUST validate all parameters before geometry construction and reject values outside
supported printable ranges with actionable error messages.

#### Scenario: Reject out-of-range grid size

- **WHEN** a user provides `grid_x` or `grid_y` outside the range 1–12
- **THEN** the system refuses geometry generation and reports which parameter is invalid

#### Scenario: Reject invalid compartment divisions

- **WHEN** a user provides `div_x` or `div_y` less than 1
- **THEN** the system refuses geometry generation with a clear validation message

#### Scenario: Reject non-positive wall thickness

- **WHEN** a user provides `wall_thickness_mm` of 0 or less
- **THEN** the system refuses geometry generation with a clear validation message
