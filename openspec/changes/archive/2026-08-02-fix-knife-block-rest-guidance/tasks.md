## 1. Correct the prose

- [x] 1.1 Fix the `deck_height_mm` docstring in `knife_block.py` so it states what the value is, not a blank-matching interface
- [x] 1.2 Fix the README's knife-block section: no blank under the handles, cantilever + counterbalance, riser only for tapering blades and sized by measurement
- [x] 1.3 Rename the `@pytest.mark.scenario` marker in `tests/test_knife_block.py` to follow the renamed scenario (assertion unchanged)

## 2. Verify and archive

- [x] 2.1 `uv run ruff check .` and `uv run pytest` green, including the traceability guard -- 134 passed
- [x] 2.2 `pnpm exec openspec validate --all` green -- 7/7
- [x] 2.3 Archive so both MODIFIED deltas fold into `openspec/specs/knife-blade-block/spec.md` -- needed a RENAMED delta alongside, since MODIFIED matches on the existing header
- [x] 2.4 No model regeneration needed: this change touches no geometry, so the UAT/regeneration step in `openspec/WORKFLOW.md` does not apply
