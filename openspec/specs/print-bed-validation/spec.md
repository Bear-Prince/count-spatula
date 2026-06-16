# print-bed-validation Specification

## Purpose

Allow users to configure their printer's bed dimensions and warn when a requested bin's
footprint would exceed those dimensions, without blocking generation or export.

## Requirements

### Requirement: Print-bed size configuration

The system SHALL accept optional print bed dimensions as CLI parameters so that generated bin
footprints can be checked against the user's printer constraints.

#### Scenario: Configure print bed via CLI

- **WHEN** a user provides `--bed-x 235` and `--bed-y 235`
- **THEN** the system stores those dimensions and uses them to evaluate the bin footprint

#### Scenario: No bed size configured

- **WHEN** a user omits `--bed-x` and `--bed-y`
- **THEN** the system performs no footprint check and generates the bin without warnings

### Requirement: Warn when bin footprint exceeds print bed

The system SHALL emit a warning to stderr when the requested bin's footprint exceeds the
configured print bed size, and MUST still generate and export the output file.

#### Scenario: Bin footprint exceeds bed in one axis

- **WHEN** the bin footprint on either axis exceeds the configured bed dimension for that axis
- **THEN** the system prints a warning identifying which axis is exceeded and by how much,
  then continues to export the file and exits zero

#### Scenario: Bin footprint fits within bed

- **WHEN** the bin footprint on both axes is within the configured bed dimensions
- **THEN** the system generates and exports the file with no warning

#### Scenario: Warning message is actionable

- **WHEN** a warning is emitted for an oversized bin
- **THEN** the message includes the bin footprint dimensions and the configured bed dimensions
  so the user can compare them directly
