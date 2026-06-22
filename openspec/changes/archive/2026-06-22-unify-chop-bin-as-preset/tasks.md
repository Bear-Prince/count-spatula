## 1. Parameter model

- [x] 1.1 Create `cutlery_bin.py` with a `BinParameters` dataclass: grid_x, grid_y, height (units or mm), base
  corner radius, pocket dimensions (length, width, corner radius), and the cutout fields (`cutouts_enabled`,
  cutout offset, cutout radius).
- [x] 1.2 Add the `CutleryBin` divider fields to the parameter model: a `divisions` count (default 1) and a
  divider thickness.
- [x] 1.3 Implement `validate()` accumulating all errors: grid range, height, pocket-fits-footprint, base/pocket
  corner radius, the cutout-fit checks gated by `cutouts_enabled`, and `divisions >= 1` / positive divider
  thickness.

## 2. KitchenBin geometry

- [x] 2.1 Implement `KitchenBin` with a template-method build: Gridfinity base → open-top walls → explicit rounded
  pocket → divider hook (no-op here) → cutouts. Expose the pre-cutout divider hook for subclasses.
- [x] 2.2 Port `ChopProfile` into `cutlery_bin.py` as `SideCutoutProfile`, and the post-#16 YZ-plane through-cut,
  gated by `cutouts_enabled`, cutting both X-perpendicular walls from the inner floor to the top.
- [x] 2.3 Add a `create_kitchen_bin(params)` factory.

## 3. CutleryBin geometry

- [x] 3.1 Implement `CutleryBin(KitchenBin)` that supplies straight, evenly-spaced dividers via the hook: parallel
  to the cut walls, spanning between the two un-cut walls, splitting the pocket into `divisions` equal columns.
- [x] 3.2 Confirm the cutout runs through the dividers (the hook adds them before the cutout step).
- [x] 3.3 Add a `create_cutlery_bin(params)` factory.

## 4. Presets

- [x] 4.1 Add a presets registry mapping names to `BinParameters` factories; implement `chop-board` (a `KitchenBin`:
  pocket 220×160 mm, 35 mm radius, cutouts enabled, chop grid and height).
- [x] 4.2 Implement preset resolution and listing: resolve by name, list available names, raise an actionable error
  for an unknown name.

## 5. CLI

- [x] 5.1 Replace the chop and `utensil-bin` parsers in `main.py` with a single preset-oriented parser: `--preset`,
  dimension/pocket overrides, a divisions option, `--no-cutouts`, and the existing `--format`/`--output`.
- [x] 5.2 Wire behaviour: plain invocation → default `KitchenBin`; `divisions >= 2` → `CutleryBin`;
  `--preset chop-board` → chop bin; unknown preset → exit code 2 with actionable text.
- [x] 5.3 Update the default output filename logic for the new bins and presets.

## 6. Retire and consolidate

- [x] 6.1 Delete `chop_bin.py`; ensure its geometry and defaults live in `cutlery_bin.py` / the `chop-board` preset.
- [x] 6.2 Retire the `CompartmentsEqual`-based bin in `utensil_bin.py`, moving `check_print_bed` alongside the new
  bin (or into a shared module).
- [x] 6.3 Update all imports across `main.py` and `tests/`.

## 7. Tests

- [x] 7.1 Port the #16 regression tests (walls slotted, base intact, slot starts at inner floor, symmetric) onto
  `KitchenBin` (covers "Optional side cutouts").
- [x] 7.2 Test the `KitchenBin` pocket builds valid geometry and yields non-uniform end/side walls (covers
  "Explicitly-sized pocket interior").
- [x] 7.3 Test `CutleryBin` dividers: straight, evenly spaced, attached to both un-cut walls; `divisions=1` matches
  a `KitchenBin`; `divisions>=2` adds the expected columns (covers "CutleryBin dividers").
- [x] 7.4 Test that with cutouts enabled and two or more columns, the slot runs through every divider and each stays
  attached at both ends (covers "Cutout passes through dividers").
- [x] 7.5 Test `cutouts_enabled` default-on, `False` → solid walls/dividers, and fit validation only fires when
  enabled.
- [x] 7.6 Test the `chop-board` preset reproduces the prior chop bin within tolerance (volume/bbox).
- [x] 7.7 Test preset resolution (unknown raises; override applies) and CLI behaviour (`--preset chop-board`, plain
  invocation, divisions → `CutleryBin`, unknown preset → exit 2).
- [x] 7.8 Test validation rejections: grid range, pocket-too-large, invalid divisions.

## 8. Verification and UAT

- [x] 8.1 Run `uv run ruff check .` and fix findings.
- [x] 8.2 Run `uv run pytest` and confirm the full suite passes.
- [x] 8.3 UAT: generate a default `KitchenBin`, the `chop-board` preset, a multi-division `CutleryBin`,
  `--no-cutouts`, and a too-small-cutout error case; eyeball the exported STLs.
- [x] 8.4 Update `README.md` for the preset-oriented CLI and the `KitchenBin`/`CutleryBin` model; note the changed
  default behaviour.
- [x] 8.5 Archive the change so the spec deltas fold into `openspec/specs/`.
