## 1. Resolve the open question

- [x] 1.1 Decide with the user whether the blanking plate joins the rendered example set in
      `render_models.py` and the README gallery, or stays out of it because a flat plate is visually dull
      (design.md Open Questions). One line either way, but it changes the UAT step. Resolved: it joins the
      gallery (design.md Open Questions)

## 2. Parameters and validation

- [x] 2.1 Add a `BlankingPlateParameters` dataclass to `cutlery_bin.py` carrying `grid_x` and `grid_y` only,
      with a `validate()` accumulating errors in the same style as `BinParameters` (design Decision 2)
- [x] 2.2 Write the unit test for grid-range rejection first, covering AC "reject an out-of-range grid size"
- [x] 2.3 Confirm `BinParameters`, `KitchenBin` and `CutleryBin` are untouched by this change, covering AC
      "existing bin invocation produces unchanged geometry"

## 3. Plate geometry

- [x] 3.1 Add `create_blanking_plate(params)` building `BaseEqual` alone with no `Bin` wrapper
      (design Decision 1)
- [x] 3.2 Real-geometry test: the plate is one Gridfinity base tall, asserted with a tolerance rather than a
      literal 7.804, covering AC "exactly one base tall". Register the fixture name in
      `tests/conftest.py`'s `_REAL_GEOMETRY_FIXTURES` so it is auto-marked slow
- [x] 3.3 Real-geometry test: no material exists above the top of the base, covering AC "no walls and no
      pocket". Probe by intersecting a Box and measuring volume, per the project's geometry-verification habit
- [x] 3.4 Real-geometry test: the plate's X and Y footprint match a bin of the same grid, covering AC
      "drops into the same baseplate cells"
- [x] 3.5 Real-geometry test: the plate is a valid solid

## 4. CLI

- [x] 4.1 Add a `--blanking-plate` flag to the parser, mirroring `--knife-block`, with help text stating that
      bin-only options and the height flags do not apply (design Risks)
- [x] 4.2 Branch the build path so `--blanking-plate` builds a plate, and add the deterministic default
      filename rule
- [x] 4.3 CLI tests using the existing mocked-factory convention, covering the flag, the default filename, and
      that bin-only flags leave the plate unchanged, covering the AC on bin-only options
- [x] 4.4 Test that a height flag does not resize the plate
- [x] 4.5 Confirm the plate exports through the unchanged `export_bin()` path for STL and 3MF, covering the
      AC on export
- [x] 4.6 Confirm the print-bed check measures the plate's actual bounding box, covering that AC

## 5. Traceability and docs

- [x] 5.1 Mark every new test with `@pytest.mark.scenario("blanking-plates", "<scenario name>")`
- [x] 5.2 Sync the delta spec into `openspec/specs/` alongside the tests, since the traceability guard rejects
      markers naming scenarios that exist only in a delta, then run `tests/test_spec_traceability.py`
- [x] 5.3 Add a "Blanking plates" section to `README.md` stating the baseplate / base / blanking plate
      distinction explicitly, since the three are easy to confuse
- [x] 5.4 Add the `--blanking-plate` flag to the command examples and the Architecture section of `CLAUDE.md`

## 6. Verification and UAT

- [x] 6.1 Run `uv run ruff check .` and the full `uv run pytest --cov`
- [x] 6.2 Confirm an existing bin regenerates byte for byte against a pre-change build, covering the AC that
      bin geometry is unchanged
- [x] 6.3 Export a blanking plate and send it to the user for UAT, checking it sits flush in a baseplate
      alongside a printed bin. Confirmed: printed face down for finish, no rocking, sits flush next to a bin
- [x] 6.4 If task 1.1 decided the plate joins the example set, regenerate the README renders with
      `xvfb-run -a uv run python render_models.py` and eyeball them, per WORKFLOW.md
- [x] 6.5 Sync and archive the change once UAT passes. Delta spec was already synced at task 5.2, so the
      spec was already identical to the living truth by archive time; archived with `--skip-specs` to avoid
      re-applying an already-applied delta
