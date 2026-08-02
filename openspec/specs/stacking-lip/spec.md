# stacking-lip Specification

## Purpose

Allow any generated bin to carry a Gridfinity-standard stacking lip on its outer top rim, so that a bin
placed on top mates securely with the one below, while leaving every bin unchanged unless the lip is
explicitly requested.

## Requirements

### Requirement: Opt-in stacking lip on all bin types

The system SHALL accept a `stacking_lip` parameter on `BinParameters`, surfaced as a `--stacking-lip` CLI
flag, which adds a Gridfinity-standard stacking lip to the bin's outer top rim. The parameter SHALL default
to disabled, and SHALL apply to every bin type: plain `KitchenBin`, `CutleryBin`, and any preset.

#### Scenario: Lip is absent by default

- **WHEN** a user generates any bin without requesting a stacking lip
- **THEN** the system produces geometry identical to that produced before the lip capability existed

#### Scenario: Add a lip to a plain bin

- **WHEN** a user generates a `KitchenBin` with the stacking lip enabled
- **THEN** the system produces a bin whose outer top rim carries the stacking lip profile

#### Scenario: Add a lip to a bin with dividers

- **WHEN** a user generates a `CutleryBin` with two or more divisions and the stacking lip enabled
- **THEN** the system produces the lip on the outer top rim only, leaving the divider tops untouched

#### Scenario: Add a lip to a preset bin

- **WHEN** a user selects the `chop-board` preset and enables the stacking lip
- **THEN** the system produces the chopping-board bin with a stacking lip on its outer top rim

### Requirement: Lip conforms to the Gridfinity standard

The system SHALL generate the lip by sweeping the `BIN` stacking profile supplied by
`gridfinity_build123d` along the bin's outer top rim, rather than by defining profile geometry locally, so
that the lip tracks the upstream interpretation of the published Gridfinity specification. The lip SHALL
NOT alter the bin's footprint in X or Y.

#### Scenario: Lip preserves the bin footprint

- **WHEN** a bin is generated with the stacking lip enabled
- **THEN** the model's X and Y bounding-box dimensions are unchanged from the same bin without a lip

#### Scenario: Lip adds the standard profile height

- **WHEN** a bin is generated with the stacking lip enabled
- **THEN** the model's Z bounding-box dimension exceeds the same bin without a lip by approximately 4.12 mm,
  within a tolerance that accommodates the upstream profile's apex fillet

#### Scenario: Lipped bin is a valid solid

- **WHEN** a bin is generated with the stacking lip enabled
- **THEN** the resulting part is a valid, watertight solid suitable for export

### Requirement: Side cutouts pass through the stacking lip

Where a bin has side cutouts enabled, the system SHALL cut the handle slot through the stacking lip as well
as the wall, so that the lip is present only on the intact rim segments and never bridges across an open
cutout. A discontinuous lip on a cutout-bearing bin is correct behaviour, not a defect.

#### Scenario: Lip is interrupted by the handle slot

- **WHEN** a bin is generated with both side cutouts and the stacking lip enabled
- **THEN** no lip material spans the opening of either handle slot

#### Scenario: Lip is continuous when cutouts are disabled

- **WHEN** a bin is generated with the stacking lip enabled and side cutouts disabled
- **THEN** the lip forms a single uninterrupted loop around the outer top rim

#### Scenario: Handle slot remains open to the full wall height

- **WHEN** a bin is generated with both side cutouts and the stacking lip enabled
- **THEN** the handle slot remains open from the inner floor to above the top of the lip

#### Scenario: Lip terminates at the cutout's widest point

- **WHEN** a bin is generated with both side cutouts and the stacking lip enabled
- **THEN** the lip ends in a vertical face at the cutout's widest extent, rather than following the rim
  fillet's curve down into the opening

#### Scenario: Cutout does not narrow the opening at the wall top

- **WHEN** a bin is generated with both side cutouts and the stacking lip enabled
- **THEN** the handle slot's opening at the top of the wall is the same width as it is without a lip, so
  the rim fillet still reaches its widest at the wall top rather than within the lip

### Requirement: Lip height is included in print-bed evaluation

The system SHALL evaluate a lipped bin against the configured print volume using the model's actual
bounding box, so that the height added by the lip counts toward the height limit.

#### Scenario: Lip height counts toward the print-bed height check

- **WHEN** a bin with a stacking lip has a total height exceeding the configured bed height, but would fit
  without the lip
- **THEN** the system warns that the model exceeds the build volume height and reports the excess

### Requirement: Lip reach is validated against wall thickness

The lip profile extends 2.6 mm inward from the outer wall face. The system SHALL reject a bin whose wall is
too thin for the lip to be seated on, reporting which parameter is at fault. A wall thinner than the lip's
reach but still sufficient to seat it SHALL be permitted, since the resulting inward overhang narrows the
pocket mouth without making the geometry invalid, matching standard Gridfinity bins.

#### Scenario: Default wall thickness is accepted

- **WHEN** a user enables the stacking lip on a bin with the default 2 mm walls
- **THEN** the system generates the bin, accepting that the lip overhangs the pocket mouth by 0.6 mm

#### Scenario: Reject a wall too thin to seat the lip

- **WHEN** a user enables the stacking lip on a bin whose wall thickness cannot seat the lip profile
- **THEN** the system refuses geometry generation and reports that the wall is too thin for a stacking lip

#### Scenario: Thick-walled preset is unaffected

- **WHEN** a user enables the stacking lip on the `chop-board` preset, whose thinnest wall is 3.75 mm
- **THEN** the system generates the bin with no wall-thickness complaint
