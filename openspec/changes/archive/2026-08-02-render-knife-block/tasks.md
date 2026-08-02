## 1. Manifest and tests

- [x] 1.1 Patch `create_knife_blade_block` in `test_render_manifest_covers_the_uat_set_and_wave_divider` and assert the block is in the manifest (fails until 1.2)
- [x] 1.2 Import the knife-block factory in `render_models.py` and add its manifest entry
- [x] 1.3 Confirm the manifest test still runs without building real geometry (no new `slow` marker) -- 11 tests in 1.3s, no `slow` marker added

## 2. Regenerate the images

- [x] 2.1 Run `xvfb-run -a uv run python render_models.py` and confirm one PNG per model plus the GIF -- 7 PNGs, GIF now 7 frames (was 6)
- [x] 2.2 Eyeball the new frame and the GIF (the knife block should read clearly at the shared camera angle) -- all seven slots and the tapered walls read clearly

## 3. Verify and archive

- [x] 3.1 `uv run ruff check .` and `uv run pytest` green -- 134 passed
- [x] 3.2 `pnpm exec openspec validate --all` green -- 8/8
- [x] 3.3 Archive the change so the delta folds into `openspec/specs/model-rendering/spec.md`
