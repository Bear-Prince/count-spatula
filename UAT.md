# UAT checklist

Manual user-acceptance checks for the bin generator, complementing the automated suite
(`uv run pytest`). These cover what tests cannot: generating real STLs, eyeballing them in a slicer, and
printing/fitting them in a drawer. Footprints are given in grid units plus today's millimetre values
(those mm values will drop by 0.5 mm once the GridFinity-clearance change lands). Add rows as features
land, and update the "last passed" date when re-verified.

## Bins

### UAT-1: Default KitchenBin (2×4, cutouts)

- Command: `uv run python main.py --output build/bin.stl`
- Expect: 2×4 footprint (≈84×168 mm), ~56 mm tall; a single open pocket with 2 mm walls and a full-height
  handle slot on each long wall.
- Last passed: 2026-06-22 (slicer)

### UAT-2: chop-board preset

- Command: `uv run python main.py --preset chop-board --output build/chop.stl`
- Expect: 4×6 footprint (≈168×252 mm); a 220×160 mm rounded pocket sized for a chopping board; full-height
  handle slots.
- Last passed: 2026-06-22 (slicer)

### UAT-3: CutleryBin (2×4, 3 columns)

- Command: `uv run python main.py --divisions 3 --output build/cutlery.stl`
- Expect: 2×4 footprint split into 3 equal columns by straight dividers; the handle slot runs through the
  dividers, each still attached to both end walls.
- Last passed: 2026-06-22 (slicer)

### UAT-4: KitchenBin without cutouts (2×4)

- Command: `uv run python main.py --no-cutouts --output build/solid_2x4.stl`
- Expect: 2×4 footprint, solid side walls, no handle slots.
- Last passed: 2026-06-22 (slicer)

### UAT-5: KitchenBin without cutouts (3×3)

- Command: `uv run python main.py --grid-x 3 --grid-y 3 --no-cutouts --output build/solid_3x3.stl`
- Expect: 3×3 square footprint (≈126×126 mm), solid walls.
- Last passed: 2026-06-22 (slicer)

## Guards and error paths

### UAT-6: chop-board with cutouts disabled is rejected

- Command: `uv run python main.py --preset chop-board --no-cutouts`
- Expect: no file written; exit code 2; message that side cutouts cannot be disabled for the preset (the
  board would be trapped — the footgun).
- Last passed: 2026-06-22 (also covered by tests)

### UAT-7: cutout too large for the bin is rejected

- Command: `uv run python main.py --cutout-offset-mm 200`
- Expect: no file written; exit code 2; message that `cutout_offset_from_edge_mm` is too large for
  `grid_y`.
- Last passed: 2026-06-22 (also covered by tests)
