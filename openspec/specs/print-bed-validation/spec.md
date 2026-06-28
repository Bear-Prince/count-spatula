# print-bed-validation Specification

## Purpose

Allow users to configure their printer's bed dimensions and warn when a requested bin's
footprint would exceed those dimensions, without blocking generation or export.
## Requirements
### Requirement: Print-bed size configuration

The system SHALL provide a default print volume of 220 mm width × 220 mm depth × 240 mm height, and SHALL accept
CLI overrides for each axis — `--bed-x`, `--bed-y`, `--bed-z`. All print-volume dimensions are expressed in
millimetres; the system SHALL NOT apply any unit conversion to them.

#### Scenario: Default print volume applied

- **WHEN** a user provides none of `--bed-x`, `--bed-y`, `--bed-z`
- **THEN** the system checks the model against the default 220 × 220 × 240 mm build volume

#### Scenario: Override the print volume via CLI

- **WHEN** a user provides `--bed-x 235` (and/or `--bed-y`, `--bed-z`)
- **THEN** the system uses the overridden millimetre value(s) for the corresponding axis

### Requirement: Warn when bin footprint exceeds print bed

The system SHALL measure the generated model's **actual bounding box** and emit a warning to stderr when any
dimension exceeds the configured build volume — width against bed X, depth against bed Y, and height against the
maximum print height (Z) — and MUST still generate and export the output file. The model SHALL be evaluated in
its as-generated (printed) orientation; the system SHALL NOT rotate or reorient the model to make it fit, since
doing so could introduce overhang or infill problems.

#### Scenario: Model exceeds the build volume on an axis

- **WHEN** the model's bounding box on X, Y, or Z exceeds the corresponding configured limit
- **THEN** the system prints a warning identifying which axis is exceeded and by how much, then continues to export
  the file and exits zero

#### Scenario: Model fits within the build volume

- **WHEN** the model's bounding box is within the bed (and within the max height when one is configured)
- **THEN** the system generates and exports the file with no warning

#### Scenario: Warning message is actionable

- **WHEN** a warning is emitted for an oversized model
- **THEN** the message includes the model's dimension and the configured limit so the user can compare them directly

#### Scenario: A model is not rotated to fit

- **WHEN** a model would fit only if rotated, but exceeds a limit in its as-generated orientation
- **THEN** the system still warns that it exceeds the build volume, evaluating the model as-oriented

