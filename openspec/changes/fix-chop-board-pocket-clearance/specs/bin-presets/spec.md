# bin-presets Specification

## MODIFIED Requirements

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
