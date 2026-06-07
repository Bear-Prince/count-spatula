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

## STL CLI

Generate a bin with defaults:

```bash
uv run python main.py
```

Generate with explicit parameters and output path:

```bash
uv run python main.py \
 --grid-length 6 \
 --grid-width 4 \
 --height-mm 56 \
 --chop-length-mm 220 \
 --chop-width-mm 160 \
 --output build/chop_bin_custom.stl
```

The CLI validates parameter ranges and returns a non-zero exit code with
actionable text when values are invalid.
