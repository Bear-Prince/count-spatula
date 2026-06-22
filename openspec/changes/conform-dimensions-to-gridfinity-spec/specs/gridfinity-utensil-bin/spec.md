## ADDED Requirements

### Requirement: GridFinity dimensional conformance

The generated bin body SHALL conform to the GridFinity specification's outer dimensions. The outer footprint
SHALL be `N×42 mm − 0.5 mm` on each axis — the standard 0.5 mm total clearance per axis — so the bin matches the
Gridfinity base it is built on and seats in a baseplate without touching its neighbours. The outer corner radius
SHALL be 3.75 mm (the 4 mm baseplate radius less the 0.25 mm clearance per side).

#### Scenario: Footprint applies the GridFinity clearance

- **WHEN** a bin is generated on an N×M grid
- **THEN** its outer footprint is `(N×42 − 0.5)` mm by `(M×42 − 0.5)` mm

#### Scenario: Walls sit flush on the base

- **WHEN** a bin's walls are built on top of the Gridfinity base
- **THEN** the wall outline matches the base's top footprint within meshing tolerance, with no overhang
