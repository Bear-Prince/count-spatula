## RENAMED Requirements

- FROM: `### Requirement: Generate only the block; compose handle zones with blanks`
- TO: `### Requirement: Generate only the block; handles are unsupported`

## MODIFIED Requirements

### Requirement: Knife blade block holds knives by the blade

The system SHALL generate a `KnifeBladeBlock`: a Gridfinity module that stores kitchen knives lying flat,
edge-down, held by their blades. Each blade passes through a slot in a single block, which grips it along
the full length of the block and carries the whole knife: the handle hangs clear at one end and the run of
blade projecting past the other counterbalances it. Nothing supports the handle. The block SHALL sit on a
standard `gridfinity_build123d.BaseEqual` Gridfinity base, matching the footprint conventions of the
existing bins.

#### Scenario: Generate a block from valid parameters

- **WHEN** a `KnifeBladeBlock` is generated with valid default parameters
- **THEN** the system produces a single watertight solid comprising a Gridfinity base and a slotted block,
  with one slot per knife lane

#### Scenario: Base is a standard Gridfinity footprint

- **WHEN** a block is generated on an `N × M` grid
- **THEN** its outer footprint follows the Gridfinity convention (`N × 42 mm − 0.5 mm` on each axis), so it
  seats in the same baseplate as the other bins

### Requirement: Generate only the block; handles are unsupported

The system SHALL generate only the central block module. The handle zones at each end are out of scope and
require no part at all: the knife is carried entirely by the blade in its slot. A blade seats below the
block's top face by an amount that depends on its spine thickness, so the block's top height does NOT
define a height at which a handle should be supported. Where an individual knife does need a riser under
its handle - because a blade that tapers to a point engages the slot over a shorter run and can be tipped
by a heavy handle - that riser's height is a property of that knife and is found by measurement, not
derived from the block. The block SHALL expose the height of its top face as a value for layout purposes.

#### Scenario: Only the block is produced

- **WHEN** a `KnifeBladeBlock` is generated
- **THEN** the output contains the slotted block and its base only - no handle-zone deck is generated

#### Scenario: Top-face height is exposed for layout

- **WHEN** a block is generated
- **THEN** the height of its top face above the Gridfinity floor is available as a value, without implying
  a matching height for anything placed under the handles
