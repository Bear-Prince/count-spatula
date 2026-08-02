## Context

`render_models.py` builds a fixed manifest of models, renders each through headless OpenSCAD at one
camera position, and stitches the frames into `docs/assets/models.gif` with ImageMagick. The manifest
predates the knife blade block, so it lists six bins and nothing else.

## Goals / Non-Goals

**Goals:**

- The knife blade block appears in the rendered set and the GIF.
- The GIF stays reproducible from the script, not hand-assembled from loose PNGs.
- The manifest test stays fast.

**Non-Goals:**

- Changing camera position, image size, or GIF timing — the existing frames stay visually consistent.
- Any geometry, CLI, or model-file change.

## Decisions

### Decision 1: Extend the existing manifest rather than add a second one

Add one entry to `render_manifest()` using `create_knife_blade_block(KnifeBlockParameters())`, exactly
as the bins use their own factories. *Rationale:* the whole point of the manifest is that one list
drives both the PNGs and the GIF; a separate path for the block would let the two drift, which is the
failure mode the committed-images convention already guards against. *Alternative considered:* render
the block separately and stitch it in — rejected, as `docs/assets/knife_block.png` was produced that
way once already and promptly went stale relative to the GIF.

### Decision 2: Widen the requirement's wording rather than redefine "bin"

The requirement enumerates *bins*. Rather than stretch "bin" to cover a slotted block, the requirement
now describes the set as the project's representative models. *Rationale:* the project is explicit that
a `KnifeBladeBlock` is a sibling of `KitchenBin`, not a kind of bin; blurring that in a spec would
undermine the distinction the knife-block spec relies on.

### Decision 3: Patch the block factory in the manifest test

`test_render_manifest_covers_the_uat_set_and_wave_divider` monkeypatches `create_kitchen_bin` and
`create_cutlery_bin` so no real geometry is built. The new entry needs the same treatment.
*Rationale:* without it, that test silently becomes a slow geometry build — the exact cost the existing
patching exists to avoid. The test's assertion is a subset check, so it keeps passing as the set grows.

## Risks / Trade-offs

- **The GIF gets longer with each model added.** → Acceptable at seven frames; revisit only if the set
  grows enough that the loop becomes tedious to watch.
- **Renders need `openscad`, ImageMagick, and (headless) `xvfb-run`.** → Already true, already
  documented in the script's docstring and the README; the devcontainer installs all three.
- **Committed images go stale silently.** → Regenerated within this change, per the repo convention
  that UAT/regeneration happens before archive.
