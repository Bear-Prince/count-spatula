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

The generator produces a `KitchenBin` (a Gridfinity bin with an explicitly-sized
rounded pocket and optional full-height side cutouts) or a `CutleryBin` (a
`KitchenBin` whose pocket is split into equal columns by straight dividers, with
the cutout running through them). Use `--output` to specify the path (format is
chosen by file extension), or `--format stl|3mf` to set the default extension
when `--output` is omitted.

Generic equal-compartment grids are out of scope here — use
[`gridfinity_build123d`](https://github.com/Ruudjhuu/gridfinity_build123d)
directly for those.

### KitchenBin (default)

Generate a default bin:

```bash
uv run python main.py
```

Generate with explicit parameters and a custom output path:

```bash
uv run python main.py \
  --grid-x 4 \
  --grid-y 6 \
  --height-mm 56 \
  --pocket-length-mm 220 \
  --pocket-width-mm 160 \
  --output build/kitchen_bin_custom.stl
```

### Presets

Seed parameters from a named preset (currently `chop-board`, which reproduces the
original chopping-board bin), overriding any field on top:

```bash
uv run python main.py --preset chop-board
uv run python main.py --preset chop-board --grid-x 5 --output build/wide_chop.stl
```

### CutleryBin (dividers)

Split the pocket into equal columns with `--divisions` (two or more makes a
`CutleryBin`):

```bash
uv run python main.py --divisions 4 --output build/cutlery_4.stl
```

### Disabling cutouts

Side cutouts are enabled by default. When bins sit in a drawer where the notches
do not line up, disable them with `--no-cutouts` to leave the walls (and any
dividers) solid:

```bash
uv run python main.py --no-cutouts
```

### Other options

Export as 3MF using the default filename:

```bash
uv run python main.py --format 3mf
```

Warn when the bin footprint exceeds a print bed (export still proceeds):

```bash
uv run python main.py --grid-x 6 --grid-y 4 --bed-x 235 --bed-y 235
```

The CLI validates parameter ranges and returns a non-zero exit code with
actionable text when values are invalid (including an unknown `--preset`).
