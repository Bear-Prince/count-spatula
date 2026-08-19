# UAT checklist

Manual user-acceptance checks for the bin generator, complementing the automated suite
(`uv run pytest`). These cover what tests cannot: generating real STLs, eyeballing them in a slicer, and
printing/fitting them in a drawer. Footprints are given in grid units plus millimetre values; per the GridFinity spec a bin footprint is
`N×42 − 0.5` (the 0.5 mm clearance). Add rows as features land, and update the "last passed" date when
re-verified.

## Bins

### UAT-1: Default KitchenBin (2×4, cutouts)

- Command: `uv run python main.py --output build/bin.stl`
- Expect: 2×4 footprint (83.5×167.5 mm), ~56 mm tall; a single open pocket with 2 mm walls and a full-height
  handle slot on each long wall.
- Last passed: 2026-06-22 (slicer)

### UAT-2: chop-board preset

- Command: `uv run python main.py --preset chop-board --output build/chop.stl`
- Expect: 4×6 footprint (167.5×251.5 mm); a 222×162 mm rounded pocket sized for a chopping board (220×160 mm
  board plus a 1 mm per-side clearance); full-height handle slots.
- Last passed: 2026-08-19 (slicer) - pocket dimensions corrected from 220×160 to 222×162 by
  `fix-chop-board-pocket-clearance`; a physical board-fit reprint is deferred, not yet performed

### UAT-3: CutleryBin (2×4, 3 columns)

- Command: `uv run python main.py --divisions 3 --output build/cutlery.stl`
- Expect: cutouts enabled (the default); 2×4 footprint split into 3 equal columns by straight dividers; the
  full-height handle slot runs through every divider, with each divider still attached to both end walls.
- Last passed: 2026-06-22 (slicer)

### UAT-4: KitchenBin without cutouts (2×4)

- Command: `uv run python main.py --no-cutouts --output build/solid_2x4.stl`
- Expect: 2×4 footprint, solid side walls, no handle slots.
- Last passed: 2026-06-22 (slicer)

### UAT-5: KitchenBin without cutouts (3×3)

- Command: `uv run python main.py --grid-x 3 --grid-y 3 --no-cutouts --output build/solid_3x3.stl`
- Expect: 3×3 square footprint (125.5×125.5 mm), solid walls.
- Last passed: 2026-06-22 (slicer)

## Guards and error paths

### UAT-6: chop-board with cutouts disabled is rejected

- Command: `uv run python main.py --preset chop-board --no-cutouts`
- Expect: no file written; exit code 2; message that side cutouts cannot be disabled for the preset (the
  board would be trapped - the footgun).
- Last passed: 2026-06-22 (also covered by tests)

### UAT-7: cutout too large for the bin is rejected

- Command: `uv run python main.py --cutout-offset-mm 200`
- Expect: no file written; exit code 2; message that `cutout_offset_from_edge_mm` is too large for
  `grid_y`.
- Last passed: 2026-06-22 (also covered by tests)

### UAT-8: print-bed fit warning (default 220 × 220 × 240 mm volume)

- Command: `uv run python main.py --preset chop-board --output build/chop.stl`
- Expect: the model still exports (exit 0), but a warning is printed to stderr that the model **depth**
  (251.5 mm) exceeds the print volume depth (220 mm) - because the chop bin is 6 units long. Overriding with a
  larger `--bed-y` (≥ 252) clears the warning; a tight `--bed-y 100` warns on any bin.
- Last passed: 2026-06-22 (also covered by tests)

### UAT-9: CutleryBin with wave dividers (2×4, 3 columns)

- Command: `uv run python main.py --divisions 3 --divider-profile wave --divider-amplitude-mm 4 --output build/wave.stl`
- Expect: 2×4 footprint (83.5×167.5 mm) split into 3 equal columns by two dividers, each bending along a
  single S-curve (one sine period) over the pocket length with a 4 mm sideways swing; the two dividers are
  phase-mirrored, so the channel between them narrows where the outer channels widen (and vice versa),
  letting tapered cutlery nest head-to-tail. Each divider's centreline still meets both un-cut end walls at
  the nominal (straight-divider) spacing, and leaves a printable gap to its neighbour and the pocket walls
  at the widest point of its swing. The full-height handle slot still runs through the dividers' central
  band, and the wave shape adds no material below the inner floor (the Gridfinity base is unaffected).
- Last passed: not yet verified
