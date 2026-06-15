# count-spatula

## OpenSpec (local to this repo)

This repository uses the OpenSpec CLI as a local dev dependency.
Run it with `pnpm` so you do not depend on a global PATH setup.

### Common commands

```bash
pnpm exec openspec --version
pnpm exec openspec --help
pnpm exec openspec new change "my-change-name"
```

You can also use the package script alias.
When passing flags to the underlying CLI, include `--` so pnpm forwards
arguments to `openspec`:

```bash
pnpm run openspec -- --version
pnpm run openspec -- --help
```

## Generated files

Do not edit `pnpm-lock.yaml` directly.
Regenerate it with pnpm commands (for example, `pnpm install` or `pnpm install
--lockfile-only`) so it stays valid and reproducible.

## STL / 3MF CLI

Both bin types support STL and 3MF output. Use `--output` to specify the path
(format is chosen by file extension), or `--format stl|3mf` to set the default
extension when `--output` is omitted.

### Chopping-board bin

Generate with defaults:

```bash
uv run python main.py
```

Generate with explicit parameters and a custom output path:

```bash
uv run python main.py \
  --grid-length 6 \
  --grid-width 4 \
  --height-mm 56 \
  --chop-length-mm 220 \
  --chop-width-mm 160 \
  --output build/chop_bin_custom.stl
```

Export as 3MF using the default filename:

```bash
uv run python main.py --format 3mf
```

### Utensil bin

Generate with defaults (2x4 grid, 7 height units, single compartment):

```bash
uv run python main.py utensil-bin
```

Generate with Gridfinity height units and multiple compartments:

```bash
uv run python main.py utensil-bin \
  --grid-x 2 \
  --grid-y 4 \
  --height-units 9 \
  --div-x 2 \
  --div-y 1 \
  --output build/utensil_bin_2x4_2compartments.stl
```

Generate with a freeform millimetre height:

```bash
uv run python main.py utensil-bin \
  --grid-x 1 \
  --grid-y 3 \
  --height-mm 120 \
  --output build/utensil_bin_tall.stl
```

Export as 3MF:

```bash
uv run python main.py utensil-bin --format 3mf
```

Warn when the bin footprint exceeds a print bed (export still proceeds):

```bash
uv run python main.py utensil-bin \
  --grid-x 6 \
  --grid-y 4 \
  --bed-x 235 \
  --bed-y 235
```

The CLI validates parameter ranges and returns a non-zero exit code with
actionable text when values are invalid.
