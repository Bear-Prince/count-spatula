## ADDED Requirements

### Requirement: Named bin presets

The system SHALL provide named presets, each producing a fully-populated, valid set of bin parameters, so
common bins can be generated without specifying every dimension. The system SHALL ship a `chop-board`
preset: a `KitchenBin` reproducing the chopping-board bin — an explicit 220 mm × 160 mm pocket with a
35 mm corner radius, side cutouts enabled, on the established chop grid and height.

#### Scenario: Generate a bin from a preset

- **WHEN** a user selects the `chop-board` preset
- **THEN** the system produces a `KitchenBin` equivalent to the previous chopping-board bin geometry

#### Scenario: Reject an unknown preset

- **WHEN** a user selects a preset name that does not exist
- **THEN** the system reports an actionable error listing the available presets and does not generate a bin

#### Scenario: Override preset values

- **WHEN** a user selects a preset and also overrides a parameter (for example, grid size or height)
- **THEN** the override takes effect on top of the preset's defaults

### Requirement: Preset-oriented CLI

The CLI SHALL expose presets via a `--preset <name>` option and SHALL be able to list the available preset
names. A plain invocation without a preset SHALL generate a default `KitchenBin`; requesting one or more
divisions SHALL produce a `CutleryBin`.

#### Scenario: Generate a preset bin from the CLI

- **WHEN** the CLI is invoked with `--preset chop-board`
- **THEN** the chopping-board `KitchenBin` is generated and exported, returning a success exit code

#### Scenario: Plain invocation generates a default KitchenBin

- **WHEN** the CLI is invoked with no preset and no divisions
- **THEN** a default `KitchenBin` (with cutouts enabled) is generated and exported

#### Scenario: Requesting divisions generates a CutleryBin

- **WHEN** the CLI is invoked with a division count of two or more
- **THEN** a `CutleryBin` with that many columns is generated and exported

#### Scenario: Unknown preset is rejected at the CLI

- **WHEN** the CLI is invoked with `--preset` naming a preset that does not exist
- **THEN** the CLI exits with a non-zero status and an actionable message
