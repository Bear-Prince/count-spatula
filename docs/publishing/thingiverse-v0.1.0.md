# Thingiverse listing — v0.1.0 beta set

Paste-ready copy for the first (manual) Thingiverse upload, per the publishing plan: CI/local
builds attach the model set to a GitHub Release; the Thingiverse listing is created by hand.
Everything between the `---` rules in each section below is intended to be pasted as-is.

## Listing metadata

- **Title:** Gridfinity Kitchen & Cutlery Bins — drawer bins with handle cutouts (parametric)
- **License (Thingiverse dropdown):** Creative Commons - Attribution - Share Alike
- **Category:** Kitchen & Dining (or Organization)
- **Tags:** `gridfinity`, `kitchen`, `cutlery`, `drawer_organizer`, `bin`, `storage`,
  `parametric`, `chopping_board`, `cutlery_tray`, `openscad_alternative`
- **Images to add before publishing:** two or three slicer screenshots (one showing the
  chop-board bin split on a grid line), plus photos of printed bins as they become available.

## Description

---

A set of Gridfinity-compatible kitchen and cutlery drawer bins with full-height handle
cutouts in the side walls, so you can lift contents out without tipping the bin. Generated
parametrically with [count-spatula](https://github.com/Bear-Prince/count-spatula) — if none
of these sizes fit your drawer, the free generator can make one that does.

**Print bins bigger than your bed.** The handle cutouts are aligned to the Gridfinity 42 mm
grid: the cutout floor reaches 1 mm past its internal grid line, so you can cut the model on
a grid line in your slicer and print an oversized bin in clean sections. The chopping-board
bin (251.5 mm long) prints on a 220 mm bed this way.

### The bins

- **Chopping-board bin (4×6, 8U)** — holds a small chopping board upright (220 × 160 mm
  pocket, 35 mm corner radius). Footprint 167.5 × 251.5 mm; split on a grid line for smaller
  beds.
- **Cutlery bin, 3 columns (2×4, 8U)** — the everyday cutlery-drawer bin: one pocket split
  into three equal columns by straight dividers. The handle cutout runs through the dividers.
  Footprint 83.5 × 167.5 mm.
- **Wave cutlery bin, 3 columns (2×4, 8U)** — the same bin with S-curve wave dividers
  (6 mm amplitude). Adjacent channels alternate orientation so tapered cutlery nests
  head-to-tail.
- **Kitchen bin (2×4, 8U)** — the plain undivided bin with handle cutouts; the simplest one
  to try first.

All bins sit on a standard Gridfinity base (footprint N×42 mm − 0.5 mm) and have 56 mm
(8-unit) interior walls.

### Printing

No supports, no raft, no brim needed — the bins print flat on their base as oriented.
PLA or PETG, 0.2 mm layers, 2 walls, 10–15% infill all work fine.

To split a bin for a smaller bed: cut on any 42 mm grid line in your slicer. The cutout
geometry is designed so a grid-line cut passes through the open cutout, never through a
side wall.

### Version

This is a **0.1.0 beta** release — the designs are printable and in daily use, but feedback
is very welcome, especially on fit and printability. Generated files (STL and 3MF) are also
attached to the [GitHub release](https://github.com/Bear-Prince/count-spatula/releases).

### Credits & license

These are original designs (our own measurements and profiles), published under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Remix away — keep the
license and credit the chain.

With thanks to the Gridfinity lineage this builds on:

- [Gridfinity](https://www.youtube.com/watch?v=ra_9zU-mnl8) by Zack Freedman (MIT)
- ["Gridfinity Blanks"](https://www.thingiverse.com/thing:5758082) by atmmilani (CC BY 4.0)
- ["Gridfinity Complete Kitchen Collection"](https://www.printables.com/model/719729-gridfinity-complete-kitchen-collection-w-modular-e)
  by The Next Layer (JonathanLevi) (CC BY-SA 4.0) — the inspiration for kitchen bins with
  handle cutouts (these models use their own independently designed profiles)
- [`gridfinity_build123d`](https://github.com/Ruudjhuu/gridfinity_build123d) by Ruudjhuu
  (MIT) and [`build123d`](https://github.com/gumyr/build123d) (Apache 2.0), which the
  generator is built on

---

## Files to upload

From the GitHub Release (or `build/release/` locally):

| File | Model |
| --- | --- |
| `chop_board_bin_4x6.stl` / `.3mf` | Chopping-board bin, 4×6, 8U |
| `cutlery_bin_2x4_3col.stl` / `.3mf` | Cutlery bin, 3 straight columns, 2×4, 8U |
| `cutlery_bin_2x4_3col_wave.stl` / `.3mf` | Cutlery bin, 3 wave columns (6 mm amplitude), 2×4, 8U |
| `kitchen_bin_2x4.stl` / `.3mf` | Plain kitchen bin, 2×4, 8U |

## Print settings (Thingiverse fields)

- **Rafts:** No
- **Supports:** No
- **Resolution:** 0.2 mm
- **Infill:** 10–15%
- **Filament:** PLA or PETG

## GitHub release notes (v0.1.0)

---

First public beta of count-spatula's generated model set: four Gridfinity kitchen/cutlery
bins with grid-aligned handle cutouts (STL + 3MF attached). The cutouts align to the 42 mm
grid so oversized bins can be split on a grid line in the slicer and printed in sections.

Models are CC BY-SA 4.0; the generator code is Apache 2.0. See `CREDITS.md` for lineage.

---
