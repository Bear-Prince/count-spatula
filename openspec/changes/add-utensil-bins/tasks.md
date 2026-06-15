## 1. Unified Export Helper

- [x] 1.1 Introduce `export_bin(part, output_path)` in `main.py` using `build123d.mesher.Mesher` (AC: STL and 3MF export via extension)
- [x] 1.2 Update the chopping board bin export path in `main.py` to use `export_bin()` instead of `export_stl()` (AC: chop bin gains 3MF support)
- [x] 1.3 Add `--format` CLI flag (`stl`/`3mf`) that sets the default output extension when `--output` is omitted (AC: default format selection)
- [x] 1.4 Update `test_cli_and_params.py` to mock `export_bin` instead of `export_stl` and `create_chop_bin`; verify STL and 3MF default-naming paths (AC: export failure and default naming)

## 2. Utensil Bin Parameter Model

- [x] 2.1 Create `utensil_bin.py` with `UtensilBinParameters` dataclass (`grid_x`, `grid_y`, `height_in_units`, `height_mm`, `div_x`, `div_y`, `wall_thickness_mm=2.0`) (AC: parametric geometry from explicit params)
- [x] 2.2 Implement `UtensilBinParameters.validate()` covering: grid range 1–12, mutually exclusive height fields, at least one height field set, `div_x`/`div_y` ≥ 1, `wall_thickness_mm` > 0 (AC: parameter validation scenarios)
- [x] 2.3 Implement `effective_height_mm` property resolving the active height value (AC: Gridfinity and freeform height scenarios)
- [x] 2.4 Write unit tests in `tests/test_utensil_bin.py` for valid defaults, explicit parameters, each height mode, and all validation error paths (AC: all utensil bin parameter scenarios)

## 3. Utensil Bin Geometry

- [x] 3.1 Implement `UtensilBin` class in `utensil_bin.py` using `gridfinity_build123d.Bin` + `BaseEqual` + `CompartmentsEqual`, passing `wall_thickness_mm` to both `outer_wall` and `inner_wall` (AC: geometry from defaults and explicit params)
- [x] 3.2 Implement `create_utensil_bin(params)` factory function (AC: geometry from defaults)
- [x] 3.3 Add geometry tests asserting `volume > 0` and bounding box dimensions for a representative parameter set (AC: explicit valid parameters produce valid geometry)

## 4. Print-Bed Validation

- [x] 4.1 Implement `check_print_bed(grid_x, grid_y, bed_x_mm, bed_y_mm)` helper that returns a list of warning strings (empty if no overflow) (AC: warning message content)
- [x] 4.2 Add unit tests for `check_print_bed`: fits both axes (no warnings), exceeds X only, exceeds Y only, exceeds both (AC: all bed-validation scenarios)

## 5. Utensil Bin CLI

- [x] 5.1 Add utensil bin subcommand (or `utensil-bin` entry) to `main.py` with options: `--grid-x`, `--grid-y`, `--height-units`, `--height-mm`, `--div-x`, `--div-y`, `--wall-thickness-mm`, `--bed-x`, `--bed-y`, `--output`, `--format` (AC: CLI-driven export)
- [x] 5.2 Wire `check_print_bed()` into the CLI flow, emitting warnings to `stderr` before export when bed size is configured (AC: warning emitted but exit zero)
- [x] 5.3 Add CLI tests: successful export to tmp path, default naming with `.stl` extension, default naming with `--format 3mf`, validation failure exits non-zero, missing output directory exits non-zero, bed overflow warns but exits zero (AC: all CLI scenarios)

## 6. Verification

- [x] 6.1 Run `uv run ruff check .` and resolve all lint findings
- [x] 6.2 Run `uv run pytest` and ensure all new and existing tests pass
- [x] 6.3 Update README with utensil bin CLI examples covering height units, freeform height, multiple compartments, and 3MF output
