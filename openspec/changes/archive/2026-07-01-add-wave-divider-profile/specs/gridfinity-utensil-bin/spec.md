## MODIFIED Requirements

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

### Requirement: Parameter validation for printable geometry

The system MUST validate all parameters before geometry construction and reject values outside supported
printable ranges with actionable error messages, covering grid size, height, the pocket dimensions, any
enabled side cutouts, and (for a `CutleryBin`) the divider count, thickness, profile, and — for the `wave`
profile — the wave amplitude. For the `wave` profile the amplitude plus half the divider thickness MUST stay
within the per-column spacing with clearance, so a divider cannot collide with its neighbour or the pocket
wall.

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
