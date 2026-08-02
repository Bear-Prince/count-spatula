## Context

Three facts were measured against the pinned `gridfinity_build123d` before writing this design, rather than
assumed.

1. **`BaseEqual` alone is 7.804 mm tall** and a valid solid, with the expected footprint (83.5 mm square at
   2x2, which is `2 x 42 - 0.5`). That is the whole blanking plate.
2. **The height floor really does block it.** `BinParameters.validate()` rejects `height_mm=0`,
   `height_in_units=1` and even `height_mm=7.0`, because the rule is strictly greater than one height unit.
   Nothing thinner than a 7 mm wall can be requested today.
3. **`Bin(compartments=None)` is not the near-solid trap it was thought to be at this height.** Measured
   percent-solid against the bounding box:

   | `height_in_units` | Height | Volume | Percent solid |
   | --- | --- | --- | --- |
   | 1 | 7.804 mm | 48685.5 mm3 | 89.5% |
   | 2 | 14.0 mm | 91813.9 mm3 | 94.1% |
   | 3 | 21.0 mm | 140535.2 mm3 | 96.0% |

   At one height unit it produces **exactly** the same volume as `BaseEqual` alone, 48685.5 mm3. The reason
   is that `Bin` computes `bin_height = units * 7 - base_height`, which here is `7 - 7.804 = -0.804`, a
   negative extrude that happens to do nothing. The near-solid figure belongs to taller bins, where the slab
   above the base genuinely is solid.

Fact 3 does not change the conclusion, but it changes the reason, and the reason is what a future reader
needs.

## Goals / Non-Goals

**Goals:**

- A plate that is exactly one Gridfinity base tall, with no walls and no pocket.
- The same footprint as the equivalent bin, so it drops into the same baseplate cells.
- Reuse of the existing export, print-bed and filename machinery.
- Zero change to any existing bin's geometry.

**Non-Goals:**

- A stacking lip. A drawer filler never stacks. Settled, not deferred.
- Walls, pockets, cutouts or dividers at any height. That is a bin.
- Baseplate generation.
- Plates taller than one base. A taller solid filler is a bin with `--no-cutouts`.

## Decisions

### Decision 1: Build from `BaseEqual` alone, not `Bin(compartments=None)`

Both produce identical geometry at this height, so the choice is about robustness rather than output.
`Bin(base=..., height_in_units=1)` only works because its internal `bin_height` comes out negative and the
extrude quietly does nothing. That is an accident of arithmetic, not a contract. A future bump of the pinned
fork could make a negative extrude cut material or raise, and the failure would be silent or confusing.

`BaseEqual` alone states the intent directly: a blanking plate *is* a Gridfinity base and nothing else.

Supports the acceptance criterion that the part is exactly one base tall with no walls and no pocket.

**Alternative considered:** `Bin(compartments=None)`. Rejected for the reason above, not for solidity, which
is identical at one height unit.

### Decision 2: A separate `BlankingPlateParameters`, not a relaxed `BinParameters`

The obvious route is to relax `validate()`'s height floor and teach `KitchenBin` to skip its walls. This
design does not do that.

Almost every field on `BinParameters` is meaningless for a plate: pocket length, pocket width, pocket corner
radius, wall thickness, all six cutout fields, all four divider fields, and the stacking lip. Threading a
plate through that dataclass means each of those fields needs either a "not applicable here" guard in
`validate()` or a silent-ignore rule, and the height floor that protects bins would have to be weakened for
everything.

The project already has the right precedent: the knife blade block is a distinct product with its own
`KnifeBlockParameters` in its own module, selected by its own `--knife-block` flag. A blanking plate is the
same shape of thing, only smaller.

This also directly satisfies the acceptance criterion that bin-only options are rejected or ignored
explicitly rather than silently altering the plate: options that do not exist on the type cannot be passed
to it at all.

Supports the acceptance criteria on bin-only options and on existing bin geometry being unchanged: because
`BinParameters` and `KitchenBin` are not touched, no bin can change behaviour.

**Alternative considered:** relax `BinParameters.validate()` and add a wall-less path to `KitchenBin`. This
is what the original brief described. Rejected because it weakens a guard that exists to protect bins, in
order to serve a product that shares almost none of the dataclass, and because it puts a permanent
`if not walls` branch through the middle of the most heavily tested geometry in the project.

### Decision 3: Live in `cutlery_bin.py`, not a new module

The plate is roughly a dataclass and a three-line factory. It shares `GRIDFINITY_PITCH_MM`,
`GRIDFINITY_CLEARANCE_MM` and the grid-range validation idiom with the bins, and it is conceptually a bin
accessory rather than a separate product line like the knife block. A new module would be mostly imports.

**Alternative considered:** a `blanking_plate.py` module mirroring `knife_block.py`. Reasonable, and worth
revisiting if plates grow options. Not worth it for the current size.

### Decision 4: Fixed height, not a parameter

The plate's height is whatever `BaseEqual` builds, currently 7.804 mm. It is not exposed as a parameter and
not asserted as a literal in the code, only in tests with a tolerance, so a library bump surfaces as a
failing test rather than a wrong constant.

Supports the acceptance criterion that the plate is exactly one base tall.

## Risks / Trade-offs

- **Two parameter types that both carry `grid_x` and `grid_y`** goes to three, counting the knife block.
  Mitigated by the CLI already owning this pattern: `--grid-x` and `--grid-y` are read into whichever
  product was selected.
- **The 7.804 mm figure belongs to the pinned fork, not the Gridfinity standard** as such. Asserted with a
  tolerance, and a shift is exactly the UAT signal the pin policy in CLAUDE.md already calls for.
- **A user may expect `--blanking-plate` to honour `--height-mm`.** It does not, by Decision 4. The CLI must
  say so rather than silently ignoring the flag, or the failure is invisible until the print.
- **Terminology confusion between baseplate, base and blanking plate** is likely, and would produce the
  wrong object. Mitigated by stating all three in the README, and by naming the flag `--blanking-plate` in
  full rather than something shorter like `--plate`.

## Compatibility

- **CLI**: purely additive. `--blanking-plate` is a new flag; every existing invocation parses and behaves
  identically. The flag follows `--knife-block`'s established shape, so the mental model is unchanged.
- **Export flow**: unchanged. The plate is a `Shape` like any other and goes through `export_bin()` and the
  Mesher path as-is, so STL and 3MF both work with no new code. If STEP export lands as the other v0.3.0
  item, the plate inherits it for free.
- **Print-bed check**: unchanged, since it measures the model's actual bounding box.
- **Future v1.0 packaging**: the plate becomes another artifact in the released model set, which means the
  release tooling and the Thingiverse listing copy will need it added. It is CC BY-SA 4.0 like the other
  generated models, and being our own composition it is original rather than derived, so it introduces no
  new licence obligation.

## Migration Plan

No migration. The feature is additive and reachable only through a new flag. Rollback is removing the flag.

## Open Questions

- Should the plate be added to the rendered example set in `render_models.py` and the README gallery? It is
  visually dull, being a flat plate, and the gallery exists to show what the project makes. Leaving it out
  keeps the gallery interesting; putting it in makes the set complete. Deferred to implementation, since it
  is a one-line change either way and does not affect the geometry.
