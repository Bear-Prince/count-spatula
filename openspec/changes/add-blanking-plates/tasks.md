## 1. Resolve the open question

- [ ] 1.1 Decide with the user whether the blanking plate joins the rendered example set in
      `render_models.py` and the README gallery, or stays out of it because a flat plate is visually dull
      (design.md Open Questions). One line either way, but it changes the UAT step

## 2. Parameters and validation

- [ ] 2.1 Add a `BlankingPlateParameters` dataclass to `cutlery_bin.py` carrying `grid_x` and `grid_y` only,
      with a `validate()` accumulating errors in the same style as `BinParameters` (design Decision 2)
- [ ] 2.2 Write the unit test for grid-range rejection first, covering AC "reject an out-of-range grid size"
- [ ] 2.3 Confirm `BinParameters`, `KitchenBin` and `CutleryBin` are untouched by this change, covering AC
      "existing bin invocation produces unchanged geometry"

## 3. Plate geometry

- [ ] 3.1 Add `create_blanking_plate(params)` building `BaseEqual` alone with no `Bin` wrapper
      (design Decision 1)
- [ ] 3.2 Real-geometry test: the plate is one Gridfinity base tall, asserted with a tolerance rather than a
      literal 7.804, covering AC "exactly one base tall". Register the fixture name in
      `tests/conftest.py`'s `_REAL_GEOMETRY_FIXTURES` so it is auto-marked slow
- [ ] 3.3 Real-geometry test: no material exists above the top of the base, covering AC "no walls and no
      pocket". Probe by intersecting a Box and measuring volume, per the project's geometry-verification habit
- [ ] 3.4 Real-geometry test: the plate's X and Y footprint match a bin of the same grid, covering AC
      "drops into the same baseplate cells"
- [ ] 3.5 Real-geometry test: the plate is a valid solid

## 4. CLI

- [ ] 4.1 Add a `--blanking-plate` flag to the parser, mirroring `--knife-block`, with help text stating that
      bin-only options and the height flags do not apply (design Risks)
- [ ] 4.2 Branch the build path so `--blanking-plate` builds a plate, and add the deterministic default
      filename rule
- [ ] 4.3 CLI tests using the existing mocked-factory convention, covering the flag, the default filename, and
      that bin-only flags leave the plate unchanged, covering the AC on bin-only options
- [ ] 4.4 Test that a height flag does not resize the plate
- [ ] 4.5 Confirm the plate exports through the unchanged `export_bin()` path for STL and 3MF, covering the
      AC on export
- [ ] 4.6 Confirm the print-bed check measures the plate's actual bounding box, covering that AC

## 5. Traceability and docs

- [ ] 5.1 Mark every new test with `@pytest.mark.scenario("blanking-plates", "<scenario name>")`
- [ ] 5.2 Sync the delta spec into `openspec/specs/` alongside the tests, since the traceability guard rejects
      markers naming scenarios that exist only in a delta, then run `tests/test_spec_traceability.py`
- [ ] 5.3 Add a "Blanking plates" section to `README.md` stating the baseplate / base / blanking plate
      distinction explicitly, since the three are easy to confuse
- [ ] 5.4 Add the `--blanking-plate` flag to the command examples and the Architecture section of `CLAUDE.md`

## 6. Verification and UAT

- [ ] 6.1 Run `uv run ruff check .` and the full `uv run pytest --cov`
- [ ] 6.2 Confirm an existing bin regenerates byte for byte against a pre-change build, covering the AC that
      bin geometry is unchanged
- [ ] 6.3 Export a blanking plate and send it to the user for UAT, checking it sits flush in a baseplate
      alongside a printed bin
- [ ] 6.4 If task 1.1 decided the plate joins the example set, regenerate the README renders with
      `xvfb-run -a uv run python render_models.py` and eyeball them, per WORKFLOW.md
- [ ] 6.5 Sync and archive the change once UAT passes
