## 1. Prototype the tapered slot (notebook, de-risk first)

- [ ] 1.1 In a notebook, build a single tapered V-slot cross-section and extrude it; confirm the profile is valid (`is_valid()`), mirroring the side-cutout de-risking approach
- [ ] 1.2 Verify self-centring physically: probe a thick (3 mm) and a thin (<1 mm) blade proxy and confirm each centres on the slot centreline, thicker higher and thinner deeper
- [ ] 1.3 Verify the apex relief: confirm the blade edge floats above the slot apex (no contact with block material)
- [ ] 1.4 Record the chosen default slot mouth width, taper angle, and depth from caliper measurements of the Prima set

## 2. Parameters and validation

- [ ] 2.1 Add a `KnifeBlockParameters` dataclass (slotted, mirroring `BinParameters`) with knife/lane count, `handle_width_mm`, `handle_gap_mm`, block footprint (units wide × long), slot geometry (mouth width, taper angle, depth), deck/rest height, and drawer internal height
- [ ] 2.2 Add a derived `lane_pitch` = `(handle_width_mm + handle_gap_mm) / 2`, with defaults giving 7 lanes at 18 mm = 126 mm (3 units)
- [ ] 2.3 Write failing tests for `validate()` error cases: lane count < 1, pitch below `(handle_width + min_gap)/2`, invalid Gridfinity footprint, slot mouth too narrow for max spine
- [ ] 2.4 Implement accumulating `validate()` (single `ValueError` aggregating all errors) to pass 2.3

## 3. Block geometry

- [ ] 3.1 Write a failing test that `create_knife_blade_block(params)` builds one watertight solid with one slot per lane on a valid Gridfinity `BaseEqual` base
- [ ] 3.2 Implement a `KnifeBladeBlock` part (sibling of `KitchenBin`): `BaseEqual` base + the slotted block top, promoting the prototyped slot to a `BaseSketchObject`/feature
- [ ] 3.3 Implement the alternating head-to-toe lane layout; test that consecutive lanes place handles at opposite ends and blades overlap through the block
- [ ] 3.4 Add `create_knife_blade_block` factory (thin, mirroring `create_kitchen_bin`)
- [ ] 3.5 Test grid alignment: default parameters give seven lanes spanning exactly 126 mm (3 units)
- [ ] 3.6 Test the block prints without splitting: default bounding box fits within 220 × 220 mm

## 4. Drawer clearance check

- [ ] 4.1 Write a failing test for `check_drawer_clearance(...)`: warns when `deck_height + max_blade_depth + clearance` exceeds internal height, silent otherwise, evaluated upright
- [ ] 4.2 Implement `check_drawer_clearance` paralleling `check_print_bed` to pass 4.1
- [ ] 4.3 Expose the effective deck/rest height so a matching blank height can be chosen; test it is reported

## 5. CLI wiring

- [ ] 5.1 Write failing CLI tests (mocking the factory/export, per existing CLI test style) for building and exporting a block, including the drawer-clearance warning path
- [ ] 5.2 Add the block mode/subcommand and argument wiring in `main.py`, mirroring how `KitchenBin`/`CutleryBin` are selected and exported
- [ ] 5.3 Confirm existing CLI defaults and the current default output are unchanged (regression test)

## 6. Traceability, docs, and verification

- [ ] 6.1 Add `@pytest.mark.scenario("knife-blade-block", "<scenario>")` markers so every spec scenario is claimed (satisfy the traceability guard); allowlist any deliberately-untested scenario with a reason
- [ ] 6.2 Decide and record whether to add the named 7-knife Prima preset now or after first print (Open Question); if now, add it with ORIGINAL provenance and a preset test
- [ ] 6.3 Update README with a "Knife blade block" section, including the compose-with-blanks note and the deck-height/blank interface
- [ ] 6.4 Run `uv run ruff check .` and `uv run pytest` (with coverage) and confirm all green before raising the PR
