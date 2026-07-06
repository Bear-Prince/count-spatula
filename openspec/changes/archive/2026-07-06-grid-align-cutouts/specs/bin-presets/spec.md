## MODIFIED Requirements

### Requirement: Named bin presets

The system SHALL provide named presets, each producing a fully-populated, valid set of bin parameters, so
common bins can be generated without specifying every dimension. The system SHALL ship a `chop-board`
preset: a `KitchenBin` reproducing the chopping-board bin — an explicit 220 mm × 160 mm pocket with a
35 mm corner radius and side cutouts enabled, on the established chop grid and height. The `chop-board`
preset SHALL set its cutout offset to two grid units at each end so its floor is grid-aligned and the bin can
be split cleanly on its ±42 mm internal grid lines. A preset MAY mark its side cutouts as required; disabling
them SHALL then be rejected. The `chop-board` preset requires cutouts, because without them the board is
trapped in the pocket.

#### Scenario: Generate a bin from a preset

- **WHEN** a user selects the `chop-board` preset
- **THEN** the system produces a `KitchenBin` reproducing the chopping-board pocket with its required,
  grid-aligned cutouts

#### Scenario: Disabling cutouts on a cutouts-required preset is rejected

- **WHEN** a user selects the `chop-board` preset and also disables side cutouts
- **THEN** the system reports an actionable error and does not generate a bin

#### Scenario: Reject an unknown preset

- **WHEN** a user selects a preset name that does not exist
- **THEN** the system reports an actionable error listing the available presets and does not generate a bin

#### Scenario: Override preset values

- **WHEN** a user selects a preset and also overrides a parameter (for example, grid size or height)
- **THEN** the override takes effect on top of the preset's defaults
