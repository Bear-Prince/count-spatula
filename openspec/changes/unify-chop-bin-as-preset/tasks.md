## 1. Unified parameter model

- [ ] 1.1 Create `cutlery_bin.py` with a `BinParameters` dataclass (grid_x, grid_y, height in units or mm,
  base corner radius, `cutouts_enabled`, cutout offset/radius) that holds an `interior` field.
- [ ] 1.2 Define the interior union: `CompartmentInterior(div_x, div_y, wall_thickness_mm)` and
  `PocketInterior(length_mm, width_mm, corner_radius_mm)`.
- [ ] 1.3 Implement `validate()` accumulating all errors: grid range, height, interior-specific checks
  (compartment divisions/wall thickness, or pocket-fits-footprint), base corner radius, and the cutout-fit checks
  gated by `cutouts_enabled`.

## 2. Unified geometry (CutleryBin)

- [ ] 2.1 Implement `CutleryBin` building the Gridfinity base and open-top walls, dispatching on the interior:
  compartments via `gridfinity_build123d` `Bin`/`CompartmentsEqual`, pocket via a hand-sketched rounded-rectangle
  subtraction.
- [ ] 2.2 Add a `create_cutlery_bin(params)` factory as the public entry point.

## 3. Side cutouts

- [ ] 3.1 Port `ChopProfile` into `cutlery_bin.py` as `SideCutoutProfile`.
- [ ] 3.2 Port the post-#16 YZ-plane through-cut into `CutleryBin`, gated by `cutouts_enabled`, cutting both
  X-perpendicular walls from the inner floor to the top.

## 4. Presets

- [ ] 4.1 Add a presets registry mapping names to `BinParameters` factories; implement `chop-board` (pocket
  220×160 mm, 35 mm radius, cutouts enabled, chop grid and height).
- [ ] 4.2 Implement preset resolution and listing: resolve by name, list available names, and raise an actionable
  error for an unknown name.

## 5. CLI

- [ ] 5.1 Replace the chop and `utensil-bin` parsers in `main.py` with a single preset-oriented parser: `--preset`,
  an interior selector, dimension overrides, `--no-cutouts`, and the existing `--format`/`--output`.
- [ ] 5.2 Wire behaviour: plain invocation → default plain compartment bin (cutouts on); `--preset chop-board` →
  chop bin; unknown preset → exit code 2 with actionable text.
- [ ] 5.3 Update the default output filename logic for the unified bin and presets.

## 6. Retire and consolidate

- [ ] 6.1 Delete `chop_bin.py`; ensure its geometry and defaults live in `cutlery_bin.py` / the `chop-board` preset.
- [ ] 6.2 Fold `utensil_bin.py`'s bin pieces into `cutlery_bin.py`, retaining `check_print_bed`.
- [ ] 6.3 Update all imports across `main.py` and `tests/`.

## 7. Tests

- [ ] 7.1 Port the #16 regression tests (walls slotted, base intact, slot starts at inner floor, symmetric) onto
  `CutleryBin` (covers "Optional side cutouts").
- [ ] 7.2 Test both interior strategies build valid geometry, and that the pocket yields non-uniform walls (covers
  "Explicit-pocket interior strategy", "Configurable compartment divisions").
- [ ] 7.3 Test `cutouts_enabled` default-on, `False` → solid walls, and that fit validation only fires when enabled
  (covers the cutout scenarios).
- [ ] 7.4 Test the `chop-board` preset reproduces the prior chop bin within tolerance (volume/bbox) (covers
  "Generate a bin from a preset").
- [ ] 7.5 Test preset resolution: unknown preset raises; an override applies on top of the preset.
- [ ] 7.6 Test the CLI: `--preset chop-board`, plain invocation, and unknown preset → exit 2 (covers "Preset-oriented
  CLI").
- [ ] 7.7 Test parameter validation rejections: grid range, compartment divisions, wall thickness, pocket-too-large.

## 8. Verification and UAT

- [ ] 8.1 Run `uv run ruff check .` and fix findings.
- [ ] 8.2 Run `uv run pytest` and confirm the full suite passes.
- [ ] 8.3 UAT: generate a plain bin, `--preset chop-board`, `--no-cutouts`, and a too-small-cutout error case; eyeball
  the exported STLs.
- [ ] 8.4 Update `README.md` for the preset-oriented CLI and note the changed default behaviour.
- [ ] 8.5 Archive the change so the spec deltas fold into `openspec/specs/`.
