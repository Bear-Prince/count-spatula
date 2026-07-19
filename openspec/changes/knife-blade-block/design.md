## Context

count-spatula generates Gridfinity-compatible kitchen bins. `cutlery_bin.py` is the geometry source of
truth: `BinParameters` (a slotted dataclass with an accumulating `validate()`), `KitchenBin` (a
`BaseEqual` Gridfinity base plus an explicitly-sized pocket and optional side cutouts), `CutleryBin`
(dividers), thin `create_*` factories, and `check_print_bed`. `main.py` wires those into a CLI.

The knife-blade block is the last piece needed to finish the target cutlery drawer. Its design was worked
out during `/opsx:explore` against a real knife set (seven similar-length Prima knives, 2–3 mm spines,
~26 mm max handle width) and a real drawer (≈78 mm internal height, a confirmed 3 × 10-unit free area).
The key realisation is that only a small central *block* needs custom geometry; the handle-rest zones are
generic and are filled with stock `gridfinity_build123d` blanks.

## Goals / Non-Goals

**Goals:**

- A `KnifeBladeBlock` model that holds knives flat, edge-down, by their blades, in one block of tapered
  self-centring slots, arranged alternating head-to-toe.
- Reuse the existing architecture: `BaseEqual` base + a custom top feature, a parameter dataclass with an
  accumulating `validate()`, a thin `create_*` factory, and CLI wiring — all mirroring `KitchenBin`.
- A drawer-clearance check that parallels `check_print_bed`.
- Preserve all existing default geometry: this is additive; `BinParameters`, `KitchenBin`, `CutleryBin`,
  and every current preset/CLI default remain byte-for-byte unchanged.

**Non-Goals:**

- Generating the handle-zone decks (use `gridfinity_build123d` blanks directly — same boundary the project
  already draws for generic equal-compartment grids).
- Print-splitting the block (it is bed-sized; the grid-align/split machinery is intentionally not reused).
- The cleaver (a future angled-slot variant), and the roasting fork / cheese knife / non-Prima ProCook
  knife (ordinary divided bins).

## Decisions

### Decision 1: Hold knives by the blade, alternating head-to-toe

Store knives lying flat, edge-down, blades through a central block, handles alternating to opposite ends.
*Rationale:* handles are ~26 mm wide but blades only 2–3 mm; alternating puts same-end handles two lanes
apart, so `lane_pitch = (handle_width_mm + handle_gap_mm) / 2` — roughly half the pitch a handle would
otherwise force. *Alternative considered:* holding by the handle (wastes the long blade length) and
non-alternating lanes (pitch forced by handle width, ~2× wider). *Maps to:* "Alternating head-to-toe lane
arrangement" and its pitch scenario.

### Decision 2: One central block, not per-end blocks

Alternated knives share a long central blade-overlap zone; a single block there catches every blade.
*Rationale:* one part instead of two complementary castellated end-blocks; no phase-shift bookkeeping;
insensitive to mixed blade heights because nothing at the ends must fit a specific blade. *Alternative
considered:* two complementary end-blocks (more parts, more constraints, worse divider material). *Maps
to:* "Single central block holds every blade".

### Decision 3: Tapered self-centring V-slot

Each slot is a V — wide at the mouth, narrowing to the deck — with a relief at the apex so the edge floats.
*Rationale:* a 3:1 spine range (<1 mm to 3 mm) would otherwise force per-slot widths or leave thin blades
rattling; a taper self-centres any thickness by wedging its faces, and the apex relief keeps the cutting
edge off the plastic. This is what makes the block agnostic to blade thickness (and largely to blade
height/width), so the only per-block constraints are similar knife *length* and `handle_width ≤ pitch`.
*Alternative considered:* fixed-width slots (rattle or won't admit the cleaver) and per-slot widths (fussy,
hard-codes the arrangement). *Maps to:* "Tapered self-centring slot" scenarios.

### Decision 4: Generate only the block; compose handle zones with blanks

count-spatula emits just the block; users fill the handle zones with `gridfinity_build123d` blanks.
*Rationale:* the handle zones are generic — the same reasoning behind the project's existing "generic
equal-compartment grids are out of scope — use `gridfinity_build123d` directly" boundary. This shrinks the
custom part to ~3 × 2 units. The single interface is the block's effective **deck/rest height**: a blank of
that height under the handles keeps knives level. *Alternative considered:* generating the whole 3 × 10
deck (large, must be split to print, reinvents blanks). *Maps to:* "Generate only the block; compose handle
zones with blanks".

### Decision 5: No print-splitting for the block

The default block (3 wide × 2 long ≈ 126 × 84 mm) prints flat in one piece, so the grid-align/split
feature is not applied here. *Rationale:* composing with blanks already removed the oversized deck; adding
split logic would be dead complexity. *Trade-off accepted:* honestly *not* reusing the split machinery,
even though it exists. *Maps to:* "Block prints without splitting".

### Decision 6: Architecture — a `KitchenBin` sibling

Implement as a sibling of `KitchenBin`: a `BaseEqual` base plus a custom slotted top, with a
`KnifeBlockParameters` dataclass (accumulating `validate()`), a `create_knife_blade_block` factory, and
CLI wiring mirroring the bins. Default footprint 3 wide × 2 long; default 7 lanes at 18 mm pitch = 126 mm =
exactly 3 units (grid-aligned). Drawer clearance via a `check_drawer_clearance` helper paralleling
`check_print_bed` (`deck_height + max_blade_depth + clearance` vs internal height). *Rationale:* maximum
reuse, minimum surprise; keeps the geometry source of truth cohesive. *Open point:* whether to add a named
Prima-set preset now or after the first physical print (see Open Questions).

## Risks / Trade-offs

- **Boolean-heavy slot construction may be fragile in build123d/OCCT** (the side-cutout work hit exactly
  this). → Prototype the single tapered slot in a notebook and verify with physical volume probing before
  wiring the full block, as was done for the cutouts.
- **Blade seats deeper for thin blades, so the handle end could foul the deck.** → Verify on a one-slot
  test print; expose slot depth and deck height so the rest angle is tunable.
- **Handles have no lateral retention on a flat blank.** → Acceptable: the blade is locked in the block, so
  the handle end can only pivot slightly; revisit a scalloped rest only if it annoys in use.
- **CLI / export compatibility:** the block adds a new mode/subcommand and factory; existing CLI defaults,
  the `export_bin` flow, and every current preset must remain unchanged. → Cover with tests that assert the
  existing default output is untouched, and keep the new surface strictly additive.
- **Future v1.0 packaging:** a new top-level module and CLI surface must not complicate eventual
  library/CLI packaging. → Keep the block in the same geometry module or a clearly-scoped sibling, exported
  through the same public factory pattern as the bins.

## Open Questions

- Add the named 7-knife Prima preset now, or after the first successful physical print (UAT)?
- Should the drawer-clearance check *warn* (like `check_print_bed`) or *reject* in `validate()` — or both,
  as it is genuinely a fit constraint rather than only advisory?
- Confirm the exact default slot mouth width / taper angle / depth from caliper measurements before the
  first print.
