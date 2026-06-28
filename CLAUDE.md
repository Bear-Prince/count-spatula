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

# Run tests
uv run pytest

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

Pre-commit hooks run `ruff check`, `markdownlint`, and `yamllint` on commit; `pytest` runs on push. Install hooks with `uv run pre-commit install`.

## Architecture

**`cutlery_bin.py`** is the source of truth for all geometry.

- `BinParameters` — a `@dataclass(slots=True)` holding every configurable dimension. Call `.validate()` before building; it accumulates all errors and raises a single `ValueError`. Pocket dimensions default to a uniform-wall-thickness derivation but can be set explicitly (e.g. for the chop-board preset).
- `SideCutoutProfile(BaseSketchObject)` — the side cutout profile (a mirrored fillet polyline). Used internally by `KitchenBin`.
- `KitchenBin(BasePartObject)` — a Gridfinity bin with a single explicitly-sized rounded pocket and optional full-height side cutouts. Builds on top of `gridfinity_build123d.BaseEqual` for the Gridfinity base.
- `CutleryBin(KitchenBin)` — adds straight, single-axis dividers that split the pocket into equal columns (`params.divisions >= 2`); the side cutout runs through the dividers. Generic equal-compartment grids are out of scope here — use `gridfinity_build123d` directly for those.
- `create_kitchen_bin(params)` / `create_cutlery_bin(params)` — thin factories; the public entry points from tests and `main.py`.
- `PRESETS` / `resolve_preset(name)` / `preset_requires_cutouts(name)` — named parameter presets (e.g. `"chop-board"`, which reproduces the original chopping-board bin and forbids disabling its cutouts).
- `check_print_bed(model_x_mm, model_y_mm, model_z_mm, bed_x_mm, bed_y_mm, bed_z_mm)` — checks the model's
  actual bounding box (all mm) against the print-bed volume and returns warning strings for each axis that exceeds
  its limit. The model is evaluated as-generated (no rotation).

**`main.py`** is the CLI layer. It parses args into a `BinParameters` (optionally seeded from `--preset`), calls `export_bin()` to write STL or 3MF (selected by `--format` or the output extension), and returns process exit codes. `--divisions >= 2` builds a `CutleryBin`; otherwise a `KitchenBin`. Tests mock the bin factories and export to avoid real geometry builds.

**`gridfinity_build123d`** is pulled from a private GitHub repo over SSH (`git@github.com:Ruudjhuu/gridfinity_build123d`). Requires Linux x86_64.

## OpenSpec change workflow

Changes are proposed, designed, and tracked via OpenSpec (local dev dependency, run via `pnpm`). Active changes live under `openspec/changes/`. The workflow skills `/opsx:explore`, `/opsx:propose`, `/opsx:apply`, `/opsx:sync`, and `/opsx:archive` drive the lifecycle.

See [openspec/WORKFLOW.md](openspec/WORKFLOW.md) for practical recipes — how to raise an issue, abandon or supersede a change, walk back shipped behaviour, and the tool's known rough edges. See [CONTRIBUTING.md](CONTRIBUTING.md) for how sessions, changes, branches, and PRs map together (including when to use a proposal-only PR).

Branch conventions: `feature/<slug>`, `fix/<slug>`, `docs/<slug>`, `refactor/<slug>`, `chore/<slug>`. Open a PR after branch work is complete; do not merge without user review. Any PR with AI-generated code must disclose the coding agent and model used.

## Style conventions

- Python: 4 spaces, 120-char line length, UTF-8, LF endings.
- YAML/JSON: 2 spaces per indent level.
- Comments must be grammatically complete sentences.
- Use `pathlib.Path` instead of `os.path`.
- `notebooks/` are prototyping only — excluded from ruff and not part of the supported interface.

## Licensing & attribution

Code is Apache 2.0; generated models are CC BY-SA 4.0 (derived bins by obligation,
original bins by choice). Before adding licenses, headers, presets, or upload tooling,
read [LICENSING.md](LICENSING.md) for the full rules (code-vs-models split, provenance
test, attribution requirements, and the distribution constraint). See also
[CREDITS.md](CREDITS.md) for lineage and [NOTICE](NOTICE) for dependency notices.
