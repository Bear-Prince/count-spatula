# bin-presets Specification

## Purpose

TBD - created by archiving change unify-chop-bin-as-preset. Update Purpose after archive.

## Requirements

### Requirement: Named bin presets

The system SHALL provide named presets, each producing a fully-populated, valid set of bin parameters, so
common bins can be generated without specifying every dimension. The system SHALL ship a `chop-board`
preset: a `KitchenBin` reproducing the chopping-board bin - an explicit 222 mm × 162 mm pocket with a
35 mm corner radius and side cutouts enabled, on the established chop grid and height. The pocket carries a
1 mm clearance per side over the board's own 220 mm × 160 mm dimensions, confirmed against a real printed
board fit; a pocket sized to the board's exact dimensions binds against normal manufacturing tolerance
(IKEA's boards vary more than the printer does) and traps the board rather than releasing it. The
`chop-board` preset SHALL set its cutout offset to two grid units at each end so its floor is grid-aligned
and the bin can be split cleanly on its ±42 mm internal grid lines. A preset MAY mark its side cutouts as
required; disabling them SHALL then be rejected. The `chop-board` preset requires cutouts, because without
them the board is trapped in the pocket.

#### Scenario: Generate a bin from a preset

- **WHEN** a user selects the `chop-board` preset
- **THEN** the system produces a `KitchenBin` reproducing the chopping-board pocket with its required,
  grid-aligned cutouts

#### Scenario: Disabling cutouts on a cutouts-required preset is rejected

- **WHEN** a user selects the `chop-board` preset and also disables side cutouts
- **THEN** the system reports an actionable error and does not generate a bin

#### Scenario: Preset pocket clears the board it is sized for

- **WHEN** a `chop-board` preset bin is generated
- **THEN** its pocket measures 222 mm × 162 mm, a 1 mm per-side clearance over the 220 mm × 160 mm board
  dimension, not the board's exact dimensions

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
