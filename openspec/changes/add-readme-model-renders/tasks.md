## 1. Render script

- [ ] 1.1 Add `render_models.py` at the repo root: a render manifest of `(name, BinParameters)` pairs covering
  the `UAT.md` example set (default 2×4, chop-board, cutlery ÷3, solid 2×4, solid 3×3) plus a wave-divider
  cutlery bin, built via the existing `create_kitchen_bin`/`create_cutlery_bin` factories.
- [ ] 1.2 Implement PNG rendering: export each part to STL in a `tempfile` dir, wrap in a one-line `.scad`
  import, and invoke headless OpenSCAD (`--autocenter --viewall`, fixed camera and image size) writing to
  `docs/assets/<name>.png`.
- [ ] 1.3 Implement GIF stitching: render the set's frames and stitch a looping GIF into `docs/assets/` with
  ImageMagick (`magick`, falling back to `convert` for IM6), with a sensible frame delay.
- [ ] 1.4 Discover tools with `shutil.which`; when OpenSCAD or ImageMagick is missing, exit non-zero with a
  message naming the tool and how to install it (`apt install openscad imagemagick`), writing no partial output.

## 2. README and docs

- [ ] 2.1 Add a README images section embedding the committed PNGs/GIF from `docs/assets/`, with the CC BY-SA
  4.0 caption for the rendered models per `LICENSING.md`.
- [ ] 2.2 Extend the WORKFLOW.md UAT-models convention: regenerating the renders is part of the UAT step when a
  change affects geometry or the example set.

## 3. Tests

- [ ] 3.1 Unit-test the script with mocked subprocess + mocked factories: manifest covers the example set;
  OpenSCAD/ImageMagick commands are built correctly; IM7→IM6 fallback works. Claim the "Render the set to PNGs"
  and "GIF cycles the example models" scenarios with `@pytest.mark.scenario("model-rendering", ...)` markers.
- [ ] 3.2 Test the missing-tool path (patched `shutil.which`): non-zero exit, message names the tool, no output
  written. Claim the "Missing render tool fails with an actionable error" scenario.
- [ ] 3.3 Test README embedding: parse README image references and assert each referenced `docs/assets/` file
  exists. Claim the "README references existing committed images" scenario.

## 4. Verification and UAT

- [ ] 4.1 Run `uv run ruff check .` and fix findings.
- [ ] 4.2 Run `uv run pytest` and confirm the full suite (including the traceability guard) passes.
- [ ] 4.3 Install `openscad`/`imagemagick` locally if needed, run the real render, and commit `docs/assets/`.
- [ ] 4.4 UAT: eyeball every PNG and the GIF (camera angle, framing, frame timing, licence caption in README);
  also regenerate the `UAT.md` bin models to `build/` and confirm they are unchanged by this tooling-only change.
- [ ] 4.5 Archive the change so the spec delta folds into `openspec/specs/`.
