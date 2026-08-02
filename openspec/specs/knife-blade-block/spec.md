# knife-blade-block Specification

## Purpose

Generate a parametric Gridfinity module that stores kitchen knives lying flat, held by their blades in a
single block of tapered, self-centring slots, arranged alternating head-to-toe -- so a full knife set
packs into a fraction of the space a handle-held rack would need, and each knife lifts straight out.

## Requirements

### Requirement: Knife blade block holds knives by the blade

The system SHALL generate a `KnifeBladeBlock`: a Gridfinity module that stores kitchen knives lying flat,
edge-down, held by their blades. Each blade passes through a slot in a single block; the block locates the
blades laterally while the knives rest along their length. The block SHALL sit on a standard
`gridfinity_build123d.BaseEqual` Gridfinity base, matching the footprint conventions of the existing bins.

#### Scenario: Generate a block from valid parameters

- **WHEN** a `KnifeBladeBlock` is generated with valid default parameters
- **THEN** the system produces a single watertight solid comprising a Gridfinity base and a slotted block,
  with one slot per knife lane

#### Scenario: Base is a standard Gridfinity footprint

- **WHEN** a block is generated on an `N × M` grid
- **THEN** its outer footprint follows the Gridfinity convention (`N × 42 mm − 0.5 mm` on each axis), so it
  seats in the same baseplate as the other bins

### Requirement: Alternating head-to-toe lane arrangement

Knife lanes SHALL be arranged so that adjacent knives point in alternating directions, placing their
handles at opposite ends of the module. Because handles are wider than blades, the achievable lane pitch is
governed by same-end handles, which sit two lanes apart; the lane pitch SHALL therefore be
`(handle_width_mm + handle_gap_mm) / 2`. Each lane's slot SHALL be symmetric along its length, so the
alternation is realised entirely by how a person loads knives into the assembled rack (which end each
handle faces) -- the block's own geometry does not encode a direction per lane, and any lane accepts a
blade facing either way.

#### Scenario: Each lane accepts a blade facing either direction

- **WHEN** a block is generated for two or more knives
- **THEN** every lane's slot is symmetric along its length, so a blade can be inserted facing either end and
  adjacent lanes can be loaded with handles at opposite ends

#### Scenario: Pitch derives from handle width and gap

- **WHEN** `handle_width_mm` and `handle_gap_mm` are given
- **THEN** the lane pitch equals `(handle_width_mm + handle_gap_mm) / 2`, so two same-end handles clear each
  other by `handle_gap_mm`

### Requirement: Single central block holds every blade

All knife blades SHALL be held by one block positioned in the central zone where the alternated blades
overlap. The design SHALL NOT use separate per-end blocks.

#### Scenario: One block spans all lanes

- **WHEN** a block is generated for `N` knives
- **THEN** a single block carries all `N` slots, located in the shared blade-overlap zone

### Requirement: Tapered self-centring slot

Each slot SHALL be a tapered V, wider at its mouth and narrowing toward the deck, so a blade drops until its
faces wedge against the taper and self-centre on the slot centreline regardless of blade thickness. The slot
SHALL admit blade spines from the thinnest to the thickest in the target range, and the cutting edge SHALL
float clear of the slot apex (a relief so the edge never rests on the block).

#### Scenario: Thick and thin blades both centre

- **WHEN** two blades of different spine thickness (within the supported range) are seated in identical slots
- **THEN** each blade centres on its slot centreline, the thicker one wedging higher and the thinner one
  sinking deeper

#### Scenario: Cutting edge does not bottom out

- **WHEN** a blade is seated in a slot
- **THEN** the cutting edge floats above the slot apex and is not supported on the block material

### Requirement: Generate only the block; compose handle zones with blanks

The system SHALL generate only the central block module. The handle-rest zones at each end are generic and
are explicitly out of scope; they SHALL be filled by the user with `gridfinity_build123d` blanks. The block
SHALL expose an effective deck/rest height so a matching blank height keeps the knives resting level (or with
the handle slightly raised).

#### Scenario: Only the block is produced

- **WHEN** a `KnifeBladeBlock` is generated
- **THEN** the output contains the slotted block and its base only - no handle-zone deck is generated

#### Scenario: Deck height is exposed for blank matching

- **WHEN** a block is generated
- **THEN** its effective deck/rest height is available as a value, so a blank of that height can be placed
  under the handles

### Requirement: Block prints without splitting

The default block footprint SHALL be small enough to print flat, in one piece, on a typical print bed; the
grid-align/print-split machinery used for oversized bins SHALL NOT be required for the block.

#### Scenario: Default block fits a typical bed

- **WHEN** a block is generated with default parameters
- **THEN** its bounding box fits within a typical 220 mm × 220 mm print bed with no splitting

### Requirement: Grid-aligned default footprint

Default parameters SHALL place seven knife lanes at an 18 mm pitch, so the lanes span exactly three
Gridfinity units (126 mm) and the module aligns to the grid.

#### Scenario: Seven-lane default spans three units

- **WHEN** a block is generated with default parameters
- **THEN** it has seven lanes whose combined pitch spans 126 mm (three Gridfinity units)

### Requirement: Parameter validation for printable, usable geometry

The system MUST validate all parameters before geometry construction and reject values outside supported
ranges with actionable error messages, accumulating all errors into a single failure. Validation SHALL
cover: a lane count of at least one; a lane pitch that leaves at least the minimum handle gap; a block
footprint that is a valid Gridfinity grid; and slot geometry whose mouth admits the maximum supported spine
thickness with clearance and whose taper reaches a floating apex.

#### Scenario: Reject a pitch that cannot clear the handles

- **WHEN** the lane pitch is smaller than `(handle_width_mm + minimum_gap) / 2`
- **THEN** the system refuses geometry generation with a message identifying the pitch/handle conflict

#### Scenario: Reject an invalid lane count

- **WHEN** the knife (lane) count is less than one
- **THEN** the system refuses geometry generation with an actionable message

#### Scenario: Reject a slot too narrow for the blade spine

- **WHEN** the slot mouth cannot admit the maximum supported spine thickness with clearance
- **THEN** the system refuses geometry generation with an actionable message

### Requirement: Drawer clearance check

The system SHALL provide a drawer-clearance check, in the spirit of the existing print-bed check, that
compares the module's occupied height against a drawer's internal height. The occupied height SHALL be taken
as `deck_height + max_blade_depth + clearance`, and the check SHALL return a warning for the vertical axis
when that height exceeds the drawer's internal height. The module is evaluated as-generated (upright, not
rotated).

#### Scenario: Warn when the tallest knife will not clear the drawer

- **WHEN** `deck_height + max_blade_depth + clearance` exceeds the drawer's internal height
- **THEN** the check returns a warning naming the vertical overage

#### Scenario: No warning when everything clears

- **WHEN** the occupied height is within the drawer's internal height
- **THEN** the check returns no warning
