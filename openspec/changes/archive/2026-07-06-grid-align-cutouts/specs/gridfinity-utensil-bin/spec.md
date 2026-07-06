## MODIFIED Requirements

### Requirement: Optional side cutouts

A bin SHALL provide a `cutouts_enabled` option, defaulting to enabled, that cuts a full-height slot through
the two opposing side walls perpendicular to the X axis — and through any `CutleryBin` dividers, which run
parallel to those walls — from the inner floor to the top of the walls, leaving the Gridfinity base intact.
When disabled, the side walls and dividers are solid.

The cutout profile's floor-to-wall corner SHALL be sharp (unfilleted) on each end; only the wall-to-rim
corner, where the wall flares out to its widest point, SHALL be rounded, with one shared radius
(`cutout_radius_mm`, default 10 mm). The cutout offset SHALL be independently configurable at each end, as a
whole number of Gridfinity units of solid wall (`cutout_offset_start_units` and `cutout_offset_end_units`,
each defaulting to 1), so bins of different lengths can align their cutouts at a shared end. Each end's
offset's millimetre value SHALL be derived so the sharp floor edge stops a fixed 1 mm
(`CUTOUT_GRID_CLEARANCE_MM`) short of that end's corresponding internal grid line — not past it — so the
line itself, and a small margin around it, stays solid; a base split exactly on that grid line always cuts
through uninterrupted material. Because the floor is unfilleted, its position does not depend on
`cutout_radius_mm`. Each of `cutout_offset_start_units` and `cutout_offset_end_units` MUST be at least 1;
their combined gap in whole grid units (`grid_y − cutout_offset_start_units − cutout_offset_end_units`) MUST
be at least 1. The wider rim MAY still lap over the grid line — the floor is what governs a clean base cut.

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

#### Scenario: Cutout floor stops short of the grid line

- **WHEN** a bin is generated with cutouts enabled and the default offset of one grid unit at each end
- **THEN** the sharp floor edge stops exactly 1 mm short of each end's internal grid line, so a base split on
  that line cuts through solid, uninterrupted material

#### Scenario: Grid-line clearance holds regardless of radius

- **WHEN** a bin is generated with cutouts enabled and a non-default `cutout_radius_mm`
- **THEN** the floor still stops exactly 1 mm short of the target grid line on each end, because the floor's
  position does not depend on the radius

#### Scenario: Independent per-end cutout offsets

- **WHEN** a bin is generated with different `cutout_offset_start_units` and `cutout_offset_end_units`
- **THEN** the cutout's floor length differs on each end accordingly, and each end's edge still stops 1 mm
  short of its own target grid line

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
