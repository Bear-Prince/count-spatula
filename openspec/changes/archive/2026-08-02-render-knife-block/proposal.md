## Why

The README's example-model GIF is the project's shop window, and it is now out of date: v0.2.0 shipped
the `KnifeBladeBlock`, which is the most distinctive thing this project makes, and it does not appear
in the renders at all. The same GIF is about to be used as the cover image for the Thingiverse
listing, where the knife block is the headline of the update — so a set that shows only bins actively
undersells it.

## What Changes

- Add the knife blade block to `render_models.py`'s render manifest, so it gets its own PNG and takes
  its place in the looping GIF alongside the bins.
- Regenerate `docs/assets/*.png` and `docs/assets/models.gif` from the current geometry.
- Widen the render-set requirement, which currently scopes the manifest to *bins* only. The knife
  block is not a bin, so the wording has to accommodate a model set that is no longer bins-only.

## Capabilities

### Modified Capabilities

- `model-rendering`: the "Render the example model set to images" requirement currently says the
  script renders "each **bin** in the example model set (the `UAT.md` bin cases, plus a wave-divider
  cutlery bin)". That enumeration excludes the knife block by construction. The requirement is
  reworded so the set is defined as the project's representative models rather than bins specifically.

## Impact

- **`render_models.py`** — one import and one manifest entry.
- **`tests/test_render_models.py`** — the manifest test monkeypatches the bin factories so it stays
  fast; it must patch the knife-block factory too, or adding the entry would make that test build real
  geometry.
- **`docs/assets/`** — regenerated PNGs plus a new frame in `models.gif`; committed images go stale
  silently, so they are refreshed in the same change.
- **Tooling note:** rendering needs `openscad` and ImageMagick on `PATH`, and `xvfb-run` where there
  is no display. No new Python dependencies.
- No geometry, CLI, or model-file changes: this is presentation only.
