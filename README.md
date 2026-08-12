# count-spatula

[![Tests](https://github.com/Bear-Prince/count-spatula/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Bear-Prince/count-spatula/actions/workflows/tests.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/Bear-Prince/count-spatula/branch/main/graph/badge.svg)](https://codecov.io/gh/Bear-Prince/count-spatula)

## Example models

![Cycling renders of the example model set: kitchen, cutlery and chopping-board bins, and the knife blade block](docs/assets/models.gif)

Renders of the models above are CC BY-SA 4.0 (see [Licensing](#licensing)); the generator code itself is
Apache 2.0. Regenerate them with `uv run python render_models.py` (requires `openscad` and `imagemagick`
on `PATH`). Without a display (headless CI, most containers, Codespaces) OpenSCAD's offscreen renderer
still needs a virtual one: install `xvfb` and prefix the command with `xvfb-run -a`, e.g.
`xvfb-run -a uv run python render_models.py` - without it, OpenSCAD dies with a `SIGSEGV` rather than a
readable error, so this is easy to lose time to.

## OpenSpec (local to this repo)

This repository uses the OpenSpec CLI as a local dev dependency.
Run it with `pnpm` so you do not depend on a global PATH setup.

### Common commands

```bash
pnpm exec openspec --version
pnpm exec openspec --help
pnpm exec openspec new change "my-change-name"
```

You can also use the package script alias.
When passing flags to the underlying CLI, include `--` so pnpm forwards
arguments to `openspec`:

```bash
pnpm run openspec -- --version
pnpm run openspec -- --help
```

## Generated files

Do not edit `pnpm-lock.yaml` directly.
Regenerate it with pnpm commands (for example, `pnpm install` or `pnpm install
--lockfile-only`) so it stays valid and reproducible.

## STL / 3MF CLI

The generator produces a `KitchenBin` (a Gridfinity bin with an explicitly-sized
rounded pocket and optional full-height side cutouts) or a `CutleryBin` (a
`KitchenBin` whose pocket is split into equal columns by straight dividers, with
the cutout running through them). Use `--output` to specify the path (format is
chosen by file extension), or `--format stl|3mf` to set the default extension
when `--output` is omitted.

Generic equal-compartment grids are out of scope here - use
[`gridfinity_build123d`](https://github.com/Ruudjhuu/gridfinity_build123d)
directly for those.

### KitchenBin (default)

Generate a default bin:

```bash
uv run python main.py
```

Generate with explicit parameters and a custom output path:

```bash
uv run python main.py \
  --grid-x 4 \
  --grid-y 6 \
  --height-mm 56 \
  --pocket-length-mm 220 \
  --pocket-width-mm 160 \
  --output build/kitchen_bin_custom.stl
```

### Presets

Seed parameters from a named preset (currently `chop-board`, which reproduces the
original chopping-board bin), overriding any field on top:

```bash
uv run python main.py --preset chop-board
uv run python main.py --preset chop-board --grid-x 5 --output build/wide_chop.stl
```

### CutleryBin (dividers)

Split the pocket into equal columns with `--divisions` (two or more makes a
`CutleryBin`):

```bash
uv run python main.py --divisions 4 --output build/cutlery_4.stl
```

### Disabling cutouts

Side cutouts are enabled by default. When bins sit in a drawer where the notches
do not line up, disable them with `--no-cutouts` to leave the walls (and any
dividers) solid:

```bash
uv run python main.py --no-cutouts
```

### Cutout geometry

![Cutout profile: sharp floor corner, side wall, filleted rim](docs/images/cutout-profile.svg)

Each side cutout is a scoop with a sharp floor corner and one filleted corner
(`--cutout-radius-mm`, default 10 mm):

- **floor** - the flat base of the slot.
- **sharp corner** - where the floor meets the side wall; unfilleted, so its position does not
  depend on the radius.
- **side wall** - the straight vertical section.
- **rim fillet** - rounds the side wall out to the wider top opening.
- **rim** - the widest point, where the slot meets the top of the wall.

`--cutout-offset-units` sets how many whole Gridfinity grid units of solid wall are reserved at each
end, as one value (applies to both ends, default 1) or two (`start end`, set independently - handy
for aligning bins of different lengths at a shared end, e.g. `--cutout-offset-units 1 2`). The
reserved solid wall is a fixed 1 mm shorter than that whole number of units, so the sharp floor
corner reaches 1 mm past the corresponding internal grid line - the line itself sits just inside the
open cutout, not the solid wall - regardless of the chosen radius.

### Other options

Export as 3MF using the default filename:

```bash
uv run python main.py --format 3mf
```

Warn when the bin footprint exceeds a print bed (export still proceeds):

```bash
uv run python main.py --grid-x 6 --grid-y 4 --bed-x 235 --bed-y 235
```

The CLI validates parameter ranges and returns a non-zero exit code with
actionable text when values are invalid (including an unknown `--preset`).

## Splitting models too large for the bed

Some models do not fit a typical bed - the `chop-board` preset is 167.5 × 251.5 mm, so its depth exceeds a
220 mm bed. `--split` cuts the model along its Gridfinity grid lines into bed-sized pieces, choosing the
fewest and most equal pieces that fit:

```bash
uv run python main.py --preset chop-board --split --output build/chop.stl
```

That writes `build/chop-part1.stl` and `build/chop-part2.stl`, each 167.5 × 125.75 mm. Without `--split`
the model still exports as one oversized file, exactly as before; the bed warning just points at the flag.

The pieces are **butt-jointed and need adhesive** - there are no dowels or alignment features. Cut faces are
left untouched, so the two halves sum back to the original 251.5 mm and the reassembled bin drops into the
same baseplate cells as an unsplit one. The pocket is cut through and becomes continuous again once glued.

Use `--split-mode standalone` instead when each piece should work as an independent model in its own cells -
for example a 7×3 blanking plate becoming a usable 4×3 and 3×3. That shaves 0.25 mm from every cut face so
each piece matches a natively-generated model of its size. It is the wrong mode for anything with a pocket,
which would be left open-ended, and the CLI warns if you ask for it there.

Splitting applies to the horizontal axes only. A model taller than the bed cannot be helped by a grid-aligned
cut, and the CLI says so rather than implying otherwise.

## Knife blade block

`--knife-block` builds a `KnifeBladeBlock` instead of a bin: a small Gridfinity module that holds
kitchen knives lying flat, edge-down, gripped by their blades rather than their handles. Knives
alternate head-to-toe so their handles fall to opposite ends, and every blade passes through the
same block, in a tapered slot that self-centres blades of different thickness and keeps the cutting
edge floating clear of the printed material.

```bash
uv run python main.py --knife-block
```

![The default 7-lane knife blade block](docs/assets/knife_block.png)

This render (like the example models above) is CC BY-SA 4.0 (see [Licensing](#licensing)). Regenerate
it by reusing `render_models.py`'s render helper:

```python
from render_models import find_openscad, render_png
from knife_block import KnifeBlockParameters, create_knife_blade_block

render_png(create_knife_blade_block(KnifeBlockParameters()), "docs/assets/knife_block.png", find_openscad())
```

Requires `openscad` on `PATH` (and, without a display - e.g. in a container - `xvfb-run` wrapping the
command).

### Lane geometry

![Knife blade block lane geometry: alternating handles, lane pitch, and the generated block](docs/images/knife-block-lanes.svg)

Because a handle (`handle_width_mm`) is wider than a blade, two knives with handles at the *same*
end must sit two lanes apart, not one - alternating head-to-toe is what makes that work. The lane
pitch is derived from that constraint:

```text
lane_pitch_mm = (handle_width_mm + handle_gap_mm) / 2
```

`handle_gap_mm` is the finger clearance left between two same-end handles once the pitch is applied.
The default (7 lanes, 26 mm handle width, 10 mm handle gap) is sized for a set of seven
similarly-lengthed kitchen knives with 2–3 mm spines - it produces a 3×2 Gridfinity module (126 mm
across seven 18 mm lanes). Override the layout with `--knife-count`, `--handle-width-mm`, and
`--handle-gap-mm`; `--grid-x`/`--grid-y` set the block's own footprint in this mode.

**Only the block is generated, and it is the only part needed.** Each slot grips its blade along the
full length of the block, so the knife is carried by the blade alone: the handle hangs clear at one
end and the run of blade projecting past the other counterbalances it. Nothing goes under the
handles.

A blade seats *below* the block's top face, by 5.14 mm for a 3 mm spine down to 8.57 mm for a 2 mm
one, so the block's own height is not a height to match anything to. It is available as a layout
figure:

```python
from knife_block import KnifeBlockParameters

KnifeBlockParameters().deck_height_mm  # 18.0 mm, the top face
```

**If a knife tips, it will be one whose blade tapers to a point.** A straight, even-depth blade (a
bread knife, a flat carving knife) is gripped along the block's whole length and sits steady. A blade
that narrows towards the tip drops away from the slot as it goes, so only a short run is held, and a
heavy handle out on the lever arm can tip it. Support that handle with a small riser -- an ordinary
bin works: `--grid-x 1 --grid-y 2 --height-mm 40 --no-cutouts`. The height depends on the knife, so
shim the handle with folded card until it sits still, then measure.

`--drawer-height-mm`, `--max-blade-depth-mm`, and `--drawer-clearance-mm` control a drawer-fit
check (in the same non-blocking, warn-and-still-export spirit as the print-bed check): it warns
when the block's height plus your tallest knife's blade depth plus a safety margin would exceed
your drawer's internal height. Defaults assume a 78 mm drawer and a 40 mm typical blade depth -
override `--max-blade-depth-mm` for anything taller, such as a cleaver (not part of the default
7-knife set; a cleaver needs its own, currently unimplemented, angled-slot variant).

This is an original design (our own measurements and profiles), CC BY-SA 4.0 like the project's
other original bins.

## Blanking plates

`--blanking-plate` builds a `BlankingPlate` instead of a bin: a thin, wall-less Gridfinity base used on
its own to cap leftover grid in a drawer lined with a baseplate. Three similarly named things mean
different objects here:

- **baseplate** - the grid that lines the drawer.
- **base** - a bin's own footed bottom, the part that mates with the baseplate.
- **blanking plate** - a base used on its own, with no bin built on top of it, to fill an otherwise
  empty baseplate cell.

```bash
uv run python main.py --blanking-plate
```

![The default 2x4 blanking plate](docs/assets/blanking_plate.png)

This render (like the example models above) is CC BY-SA 4.0 (see [Licensing](#licensing)). Regenerate it
by running `render_models.py` (see [Example models](#example-models)); it is part of the standard
manifest.

`--grid-x`/`--grid-y` set the plate's own footprint, matching the same baseplate cells as a bin of that
grid size. Bin-only options - pocket, cutout, divider and stacking-lip flags, and the height flags - do
not apply to a plate; only `grid_x`/`grid_y` are read, so those flags are silently ignored rather than
altering the plate. It exports and is checked against the print bed through the same paths as any other
model.

## Licensing

This project ships two kinds of work under two different licenses:

- **Generator code** → [Apache License 2.0](LICENSE).
- **Generated model files** (STL/STEP/3MF) → [CC BY-SA
  4.0](https://creativecommons.org/licenses/by-sa/4.0/) (full text in
  [`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt)).

All generated models are CC BY-SA 4.0: **derived** bins (those reproducing The
Next Layer's design) by the ShareAlike obligation, and **original** bins (our own
measurements and profiles, e.g. the `chop-board` IKEA bin) by deliberate choice.
Each preset records its `provenance` (`original` or `derived`) and model license.

See [CREDITS.md](CREDITS.md) for the full design lineage and per-model attribution
rules, and [NOTICE](NOTICE) for retained dependency notices.

### Dependency and source licenses (verified)

| Work | Author | License |
| --- | --- | --- |
| Gridfinity | Zack Freedman | MIT |
| `gridfinity_build123d` | Ruudjhuu | MIT |
| `build123d` | gumyr / contributors | Apache 2.0 |
| "Gridfinity Complete Kitchen Collection" | The Next Layer (JonathanLevi) | CC BY-SA 4.0 |
| "Gridfinity Blanks" | atmmilani (Thingiverse) | CC BY 4.0 |

### Attribution for derived models

Any **derived** bin must ship with the CC BY-SA 4.0 attribution block (credit The
Next Layer, link the Printables source, link the license, state that changes were
made, preserve prior notices, mark our version as also CC BY-SA 4.0). It must also
credit the upstream author atmmilani (CC BY 4.0), whose attribution requirement
persists downstream. The exact block lives in [CREDITS.md](CREDITS.md). The
repository currently contains no derived presets.

### Distribution constraint

Derived (CC BY-SA 4.0) models may only be published to platforms that preserve
CC BY-SA 4.0 (for example Printables and Thingiverse). They must **not** be
published under an exclusive or ShareAlike-incompatible platform license (for
example MakerWorld's exclusive Standard Digital File License). Any future upload
tooling must enforce this and respect each platform's terms of service.

This is a working understanding, not legal advice.
