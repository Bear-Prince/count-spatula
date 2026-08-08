# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the STL generator (default parameters)
uv run python main.py

# Run with explicit parameters
uv run python main.py --grid-x 4 --grid-y 6 --height-mm 56 --output build/out.stl

# Run a named preset (e.g. the chopping-board bin), optionally overriding a field
uv run python main.py --preset chop-board --output build/chop.stl

# Build a cutlery bin (pocket split into equal columns) and export to 3MF
uv run python main.py --grid-x 2 --grid-y 4 --divisions 3 --format 3mf

# Build a blanking plate (wall-less, caps leftover baseplate grid) on a 3x3 footprint
uv run python main.py --blanking-plate --grid-x 3 --grid-y 3

# Run tests
uv run pytest

# Fast test run (skips the slow real-geometry builds)
uv run pytest -m "not slow"

# Run tests with a coverage report
uv run pytest --cov --cov-report=term-missing

# Run a single test file
uv run pytest tests/test_cli_and_params.py

# Run a single test by name
uv run pytest -k test_default_output_path_is_deterministic

# Lint
uv run ruff check .

# OpenSpec CLI (change management)
pnpm exec openspec --help
pnpm exec openspec new change "my-change-name"
```

Pre-commit hooks run `ruff check`, `markdownlint`, and `yamllint` on commit; `pytest` (with a coverage summary) runs on push. Install hooks with `uv run pre-commit install`. CI (`.github/workflows/tests.yml`) runs ruff and the full suite with coverage on every PR and push to main, uploading to Codecov.

## Testing conventions

- Tests are linked to OpenSpec scenarios with `@pytest.mark.scenario("<capability>", "<scenario name>")`. The guard in `tests/test_spec_traceability.py` fails when a spec scenario has no claiming test (unless allowlisted in `UNTESTED_SCENARIOS` with a reason) or a marker names a scenario that does not exist - so syncing specs and adding tests must move together.
- Tests that build real geometry are auto-marked `slow` (see `tests/conftest.py`); use `-m "not slow"` for a fast loop.

## Architecture

**`cutlery_bin.py`** is the source of truth for all geometry.

- `BinParameters` - a `@dataclass(slots=True)` holding every configurable dimension. Call `.validate()` before building; it accumulates all errors and raises a single `ValueError`. Pocket dimensions default to a uniform-wall-thickness derivation but can be set explicitly (e.g. for the chop-board preset).
- `SideCutoutProfile(BaseSketchObject)` - the side cutout profile (a mirrored fillet polyline). Used internally by `KitchenBin`.
- `KitchenBin(BasePartObject)` - a Gridfinity bin with a single explicitly-sized rounded pocket and optional full-height side cutouts. Builds on top of `gridfinity_build123d.BaseEqual` for the Gridfinity base.
- `CutleryBin(KitchenBin)` - adds straight, single-axis dividers that split the pocket into equal columns (`params.divisions >= 2`); the side cutout runs through the dividers. Generic equal-compartment grids are out of scope here - use `gridfinity_build123d` directly for those.
- `create_kitchen_bin(params)` / `create_cutlery_bin(params)` - thin factories; the public entry points from tests and `main.py`.
- `BlankingPlateParameters` / `BlankingPlate(BasePartObject)` / `create_blanking_plate(params)` - a thin,
  wall-less Gridfinity base (`grid_x`/`grid_y` only, no height/pocket/cutout/divider fields) used on its own
  to cap leftover baseplate grid; built from `gridfinity_build123d.BaseEqual` alone, with no `Bin` wrapper.
- `PRESETS` / `resolve_preset(name)` / `preset_requires_cutouts(name)` - named parameter presets (e.g. `"chop-board"`, which reproduces the original chopping-board bin and forbids disabling its cutouts).
- `check_print_bed(model_x_mm, model_y_mm, model_z_mm, bed_x_mm, bed_y_mm, bed_z_mm)` - checks the model's
  actual bounding box (all mm) against the print-bed volume and returns warning strings for each axis that exceeds
  its limit. The model is evaluated as-generated (no rotation).

**`main.py`** is the CLI layer. It parses args into a `BinParameters` (optionally seeded from `--preset`), calls `export_bin()` to write STL or 3MF (selected by `--format` or the output extension), and returns process exit codes. `--divisions >= 2` builds a `CutleryBin`; otherwise a `KitchenBin`. `--blanking-plate` builds a `BlankingPlate` instead, reusing `--grid-x`/`--grid-y` for the plate's own footprint and ignoring bin-only flags (pocket, cutout, divider, height). Tests mock the bin/plate factories and export to avoid real geometry builds.

**`gridfinity_build123d`** is pulled over HTTPS from our mirror fork (`https://github.com/Bear-Prince/gridfinity_build123d`, upstream `Ruudjhuu/gridfinity_build123d`), pinned to a specific commit in `pyproject.toml`. The fork exists only so builds survive upstream disappearing - never diverge it; to pick up upstream changes, sync the fork and bump the pin deliberately (geometry can change, so UAT applies). Requires Linux x86_64.

## OpenSpec change workflow

Changes are proposed, designed, and tracked via OpenSpec (local dev dependency, run via `pnpm`). Active changes live under `openspec/changes/`. The workflow skills `/opsx:explore`, `/opsx:propose`, `/opsx:apply`, `/opsx:sync`, and `/opsx:archive` drive the lifecycle.

See [openspec/WORKFLOW.md](openspec/WORKFLOW.md) for practical recipes - how to raise an issue, abandon or supersede a change, walk back shipped behaviour, and the tool's known rough edges. See [CONTRIBUTING.md](CONTRIBUTING.md) for how sessions, changes, branches, and PRs map together (including when to use a proposal-only PR).

Branch conventions: `feature/<slug>`, `fix/<slug>`, `docs/<slug>`, `refactor/<slug>`, `chore/<slug>`. Open a PR after branch work is complete; do not merge without user review. Any PR with AI-generated code must disclose the coding agent and model used.

**Reviewing a change's artifacts:** the markdown files under `openspec/changes/<name>/` (`proposal.md`,
`design.md`, `specs/**/*.md`, `tasks.md`) remain the source of truth - `openspec validate`, the
traceability guard, and archiving all operate on them directly, so they always get written regardless.
When asked to publish, present, or otherwise make a change's artifacts easier to review, render them as a
single designed Artifact page (via Claude Code's `Artifact` tool) restructuring the same content into a
scannable review packet - not on every propose/apply, only on request.

## Style conventions

- Python: 4 spaces, 120-char line length, UTF-8, LF endings.
- YAML/JSON: 2 spaces per indent level.
- Comments must be grammatically complete sentences.
- Use `pathlib.Path` instead of `os.path`.
- `notebooks/` are prototyping only - excluded from ruff and not part of the supported interface.

## Licensing & attribution

Code is Apache 2.0; generated models are CC BY-SA 4.0 (derived bins by obligation,
original bins by choice). Before adding licenses, headers, presets, or upload tooling,
read [LICENSING.md](LICENSING.md) for the full rules (code-vs-models split, provenance
test, attribution requirements, and the distribution constraint). See also
[CREDITS.md](CREDITS.md) for lineage and [NOTICE](NOTICE) for dependency notices.
