## 1. Render script

- [x] 1.1 Add `render_models.py` at the repo root: a render manifest of `(name, BinParameters)` pairs covering
  the `UAT.md` example set (default 2×4, chop-board, cutlery ÷3, solid 2×4, solid 3×3) plus a wave-divider
  cutlery bin, built via the existing `create_kitchen_bin`/`create_cutlery_bin` factories.
- [x] 1.2 Implement PNG rendering: export each part to STL in a `tempfile` dir, wrap in a one-line `.scad`
  import, and invoke headless OpenSCAD (`--autocenter --viewall`, fixed camera and image size) writing to
  `docs/assets/<name>.png`.
- [x] 1.3 Implement GIF stitching: render the set's frames and stitch a looping GIF into `docs/assets/` with
  ImageMagick (`magick`, falling back to `convert` for IM6), with a sensible frame delay.
- [x] 1.4 Discover tools with `shutil.which`; when OpenSCAD or ImageMagick is missing, exit non-zero with a
  message naming the tool and how to install it (`apt install openscad imagemagick`), writing no partial output.

## 2. README and docs

- [x] 2.1 Add a README images section embedding the committed PNGs/GIF from `docs/assets/`, with the CC BY-SA
  4.0 caption for the rendered models per `LICENSING.md`.
- [x] 2.2 Extend the WORKFLOW.md UAT-models convention: regenerating the renders is part of the UAT step when a
  change affects geometry or the example set.

## 3. Tests

- [x] 3.1 Unit-test the script with mocked subprocess + mocked factories: manifest covers the example set;
  OpenSCAD/ImageMagick commands are built correctly; IM7→IM6 fallback works. **Note:** scenario markers cannot be
  added yet — `model-rendering` doesn't exist in `openspec/specs/` until archive (same as the licensing capability
  precedent); see task 4.6.
- [x] 3.2 Test the missing-tool path (patched `shutil.which`/`find_openscad`/`find_imagemagick`): non-zero exit,
  message names the tool, no work done (spied `render_manifest` never called).
- [x] 3.3 Test README embedding: parse README image references and assert each referenced `docs/assets/` file
  exists, with a CC BY-SA caption nearby. **Currently red** — `docs/assets/models.gif` doesn't exist until the
  real render runs (task 4.3); expected to stay red until then.

## 4. Verification and UAT

- [x] 4.1 Run `uv run ruff check .` and fix findings.
- [ ] 4.2 Run `uv run pytest` and confirm the full suite passes (blocked on 4.3 — the README-embedding test is
  red until real images exist).
- [ ] 4.3 **Blocked on the user**: install `openscad`/`imagemagick` (`sudo apt-get install -y openscad
  imagemagick`), then run `uv run python render_models.py` and commit `docs/assets/`.
- [ ] 4.4 UAT: eyeball every PNG and the GIF (camera angle, framing, frame timing, licence caption in README);
  also regenerate the `UAT.md` bin models to `build/` and confirm they are unchanged by this tooling-only change.
- [ ] 4.5 Archive the change so the spec delta folds into `openspec/specs/`.
- [ ] 4.6 After archiving, add `@pytest.mark.scenario("model-rendering", ...)` markers to the four tests in
  `tests/test_render_models.py` claiming: "Render the set to PNGs", "GIF cycles the example models", "Missing
  render tool fails with an actionable error", "README references existing committed images". Re-run
  `uv run pytest` to confirm the traceability guard passes with the new capability fully claimed.
