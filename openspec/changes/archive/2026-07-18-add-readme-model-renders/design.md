## Context

The README has no visuals and the backlog has carried "screenshots of the example models" since 2026-07-11.
Upstream `gridfinity_build123d` solved the same problem with a headless pipeline (STL → one-line `.scad` import →
command-line OpenSCAD PNG → ImageMagick GIF) whose outputs are committed to the repo. We adapt that mechanism to
our example set. The repo's traceability guard (`tests/test_spec_traceability.py`) requires every new spec
scenario to be claimed by a test or allowlisted, which shapes the test approach.

## Goals / Non-Goals

**Goals:**

- One command regenerates every README image from the current code, headlessly.
- Committed outputs — the README must render on GitHub with no CI artifact plumbing.
- Script logic covered by fast tests that need neither OpenSCAD nor real geometry.

**Non-Goals:**

- Rendering in CI (system packages + slow geometry builds; regeneration happens at the UAT step instead).
- Turntable/rotation animations, user-parameterised renders, Thingiverse upload automation.
- Editing `.devcontainer/` (a concurrent session owns it; renders only *need* the tools when regenerating).

## Decisions

- **OpenSCAD + ImageMagick subprocesses, not a Python renderer.** Alternatives: `ocp_vscode` screenshots (needs a
  running viewer), VTK/OCP offscreen rendering (GPU/EGL headaches, heavy deps). The subprocess route is proven by
  upstream, trivially headless, and adds zero Python dependencies. *Acceptance:* renders succeed in a bare
  container with only `openscad` and `imagemagick` apt packages.
- **Tool discovery via `shutil.which`, supporting ImageMagick 6 and 7.** Upstream hardcodes `/usr/bin/convert`
  and `/usr/bin/openscad`; we look up `openscad`, then `magick` falling back to `convert` (IM7 renamed the
  binary). Missing tool → actionable error naming it, exit non-zero. *Acceptance:* the missing-tool scenario test
  passes with `PATH` stripped.
- **Script at repo root (`render_models.py`), outputs in `docs/assets/`.** Matches the flat `main.py` layout;
  `docs/assets/` mirrors upstream and sits beside `docs/publishing/`. The render manifest is a list of
  `(name, BinParameters)` pairs mirroring the `UAT.md` set plus a wave-divider bin — factories are reused, no
  geometry duplicated. *Acceptance:* adding a manifest entry is a one-line change.
- **`.gitignore` carve-out for committed renders.** The repo currently ignores `*.stl` globally and `build/`;
  renders are PNG/GIF so no conflict, but temp STL/scad files must go to a `tempfile` dir (as upstream does), not
  the repo. *Acceptance:* `git status` is clean after a render run apart from `docs/assets/` changes.
- **Tests mock `subprocess` and the bin factories.** The unit tests assert manifest coverage, command
  construction (camera args, image size, gif delay/loop), IM6/IM7 fallback, and the missing-tool error — all
  without real geometry or tools, keeping CI fast. Scenario markers claim the new capability's scenarios; the
  README-embedding scenario is claimed by a test that parses README image links and asserts the files exist.
  *Acceptance:* the traceability guard passes with no new allowlist entries.

## Risks / Trade-offs

- **Committed images go stale** when geometry changes. → Mitigated by folding regeneration into the existing
  "generate the UAT models before archive" convention (WORKFLOW.md); the README-embedding test catches deleted
  files but not stale pixels — accepted, same trade-off upstream made.
- **OpenSCAD render fidelity** (mesh import, no colours/materials). → Accepted; upstream's results look good, and
  a fixed colorscheme keeps output consistent. If we later want prettier renders, the manifest isolates that
  swap.
- **Repo size growth** from committed GIFs. → Bounded: a handful of 720×720 images; GIFs only regenerated when
  geometry actually changes.

## Migration Plan

1. Land the script + tests + README section + assets in one PR (archive before PR, per convention).
2. Regenerating renders becomes part of the standing UAT step for future changes.

Rollback: revert the PR; the README loses its images section, nothing else depends on the capability.

## Open Questions

- None blocking. GIF frame timing and camera angles are matters of taste, settled at UAT when we look at the
  actual output.
