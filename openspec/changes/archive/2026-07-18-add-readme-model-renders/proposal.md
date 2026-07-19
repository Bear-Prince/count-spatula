## Why

The README describes the bins but never shows one — and the Thingiverse listings need photos regardless. This has
been on the backlog since 2026-07-11 ("generate screenshots of the example models for the README"). Upstream
`gridfinity_build123d` proves a simple, fully headless mechanism (`docs/assets/image_gen.py`): export each part to
STL, render PNGs with command-line OpenSCAD, stitch sequences into GIFs with ImageMagick — no GPU, display, or
viewer automation, so it works on any dev machine and in the dev container.

## What Changes

- Add a render script that builds the example bins (the `UAT.md` model set, plus a wave-divider cutlery bin) and
  renders each to a **PNG**, and at least one **animated GIF** that cycles through the set, using headless
  OpenSCAD + ImageMagick found via `shutil.which` (actionable error naming the missing tool otherwise).
- Commit the rendered images to `docs/assets/` and embed them in a new README section, so GitHub renders them
  without any CI artifact plumbing (same approach as upstream).
- Renders are regenerated at the **UAT step** of each change (extending the existing convention), not in CI — CI
  stays fast and free of system-package dependencies.
- Add an attribution caption for the images per `LICENSING.md` (renders of the models are derived from CC BY-SA
  4.0 models and carry that licence, unlike the Apache-2.0 code).

Out of scope: rendering user-parameterised bins on demand, video/turntable animations, and wiring the renders
into the Thingiverse listing files (they can simply be reused there later).

## Capabilities

### New Capabilities

- `model-rendering`: render the example model set to committed PNGs and a looping GIF for the README, headlessly,
  with graceful failure when the external tools are absent.

## Impact

- New script (repo root, alongside `main.py`): builds the example set via the existing factories/presets — no
  geometry changes.
- `docs/assets/`: new committed PNG/GIF files.
- `README.md`: new images section with licence caption.
- `openspec/WORKFLOW.md` / `UAT.md`: fold render regeneration into the existing UAT-models convention.
- Tests: script logic tested with mocked subprocess + mocked bin factories (no OpenSCAD needed in CI), linked to
  the new capability's scenarios per the traceability guard.
- Dev container / local machines: need `openscad` and `imagemagick` installed to *regenerate* (not to build or
  test anything else). Note: the dev container is being actively fixed in a concurrent session — coordinate
  rather than editing `.devcontainer/` here.
