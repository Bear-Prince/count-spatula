# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the STL generator (default parameters)
uv run python main.py

# Run with explicit parameters
uv run python main.py --grid-length 6 --grid-width 4 --height-mm 56 --output build/out.stl

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

**`chop_bin.py`** is the source of truth for all geometry.

- `BinParameters` — a `@dataclass(slots=True)` holding every configurable dimension. Call `.validate()` before building; it accumulates all errors and raises a single `ValueError`.
- `ChopProfile(BaseSketchObject)` — the side cutout profile (a mirrored fillet polyline). Used internally by `ChopBin`.
- `ChopBin(BasePartObject)` — the full 3D bin. Builds on top of `gridfinity_build123d.BaseEqual` for the Gridfinity base, then extrudes the chopping-board pocket and subtracts side cutouts.
- `create_chop_bin(params)` — thin factory; the public entry point from tests and `main.py`.

**`main.py`** is the CLI layer. It parses args into a `BinParameters`, calls `export_bin()` (which calls `create_chop_bin` then `export_stl`), and returns process exit codes. Tests mock `create_chop_bin` and `export_stl` to avoid real geometry builds.

**`gridfinity_build123d`** is pulled from a private GitHub repo over SSH (`git@github.com:Ruudjhuu/gridfinity_build123d`). Requires Linux x86_64.

## OpenSpec change workflow

Changes are proposed, designed, and tracked via OpenSpec (local dev dependency, run via `pnpm`). Active changes live under `openspec/changes/`. The workflow skills `/opsx:explore`, `/opsx:propose`, `/opsx:apply`, `/opsx:sync`, and `/opsx:archive` drive the lifecycle.

See [openspec/WORKFLOW.md](openspec/WORKFLOW.md) for practical recipes — how to raise an issue, abandon or supersede a change, walk back shipped behaviour, and the tool's known rough edges.

Branch conventions: `feature/<slug>`, `fix/<slug>`, `docs/<slug>`, `refactor/<slug>`, `chore/<slug>`. Open a PR after branch work is complete; do not merge without user review. Any PR with AI-generated code must disclose the coding agent and model used.

## Style conventions

- Python: 4 spaces, 120-char line length, UTF-8, LF endings.
- YAML/JSON: 2 spaces per indent level.
- Comments must be grammatically complete sentences.
- Use `pathlib.Path` instead of `os.path`.
- `notebooks/` are prototyping only — excluded from ruff and not part of the supported interface.
