## 1. Prototype the tapered slot (notebook, de-risk first)

- [x] 1.1 In a notebook, build a single tapered V-slot cross-section and extrude it; confirm the profile is valid (`is_valid()`), mirroring the side-cutout de-risking approach
- [x] 1.2 Verify self-centring physically: probe a thick (3 mm) and a thin (1.5 mm) blade proxy and confirm each centres on the slot centreline, thicker higher and thinner deeper (narrowed from the original `<1 mm` framing now that the default target set is the 2-3 mm Prima knives, not the excluded sub-1 mm utility knife)
- [x] 1.3 Verify the apex relief: confirm the blade edge floats above the slot apex (no contact with block material)
- [x] 1.4 Record the chosen default slot mouth width, taper angle, and depth from caliper measurements of the Prima set

## 2. Parameters and validation

- [x] 2.1 Add a `KnifeBlockParameters` dataclass (slotted, mirroring `BinParameters`) with knife/lane count, `handle_width_mm`, `handle_gap_mm`, block footprint (units wide × long), slot geometry (mouth clearance, apex clearance, taper depth, relief depth), and a derived deck/rest height (drawer internal height is a call-time argument to `check_drawer_clearance`, not a stored parameter -- it mirrors `check_print_bed`, which likewise isn't tied to `BinParameters`)
- [x] 2.2 Add a derived `lane_pitch_mm` = `(handle_width_mm + handle_gap_mm) / 2`, with defaults giving 7 lanes at 18 mm = 126 mm (3 units)
- [x] 2.3 Write failing tests for `validate()` error cases: lane count < 1, handle gap below the minimum, invalid Gridfinity footprint, slot mouth/apex too narrow for the spine range, lanes too wide for the footprint
- [x] 2.4 Implement accumulating `validate()` (single `ValueError` aggregating all errors) to pass 2.3

## 3. Block geometry

- [x] 3.1 Write a failing test that `create_knife_blade_block(params)` builds one watertight solid with one slot per lane on a valid Gridfinity `BaseEqual` base
- [x] 3.2 Implement a `KnifeBladeBlock` part (sibling of `KitchenBin`): `BaseEqual` base + the slotted block top, promoting the prototyped slot to a `BaseSketchObject`/feature (in a new sibling module, `knife_block.py`; promoted `cutlery_bin._rounded_panel` to a shared public `rounded_panel` since both modules need it)
- [x] 3.3 Implement the lane layout; test that every lane is open, evenly spaced, and symmetric along its length -- implementation revealed that "alternating head-to-toe" is realised entirely by how a person loads knives into the finished assembly, not by the block's own geometry (each lane's slot is direction-agnostic by construction), so spec.md's "Handles alternate ends" scenario was corrected to "Each lane accepts a blade facing either direction" and tested as a Y-symmetry check instead
- [x] 3.4 Add `create_knife_blade_block` factory (thin, mirroring `create_kitchen_bin`)
- [x] 3.5 Test grid alignment: default parameters give seven lanes at 18 mm pitch fitting within the 3-unit-wide footprint (confirmed physically: lane centres -54..54 mm, footprint ±62.75 mm)
- [x] 3.6 Test the block prints without splitting: default bounding box (125.5 x 83.5 mm) fits within 220 × 220 mm

## 4. Drawer clearance check

- [x] 4.1 Write a failing test for `check_drawer_clearance(...)`: warns when `deck_height + max_blade_depth + clearance` exceeds internal height, silent otherwise, evaluated upright
- [x] 4.2 Implement `check_drawer_clearance` in `knife_block.py`, paralleling `check_print_bed`, to pass 4.1
- [x] 4.3 Expose the effective deck/rest height (`KnifeBlockParameters.deck_height_mm`, added in 2.1/2.2) so a matching blank height can be chosen; covered by `test_deck_height_is_taper_plus_relief_plus_min_deck`

## 5. CLI wiring

- [x] 5.1 Write failing CLI tests (mocking the factory/export, per existing CLI test style) for building and exporting a block, including the drawer-clearance warning path
- [x] 5.2 Add the `--knife-block` mode and argument wiring in `main.py` (reusing `--grid-x`/`--grid-y` for the block's own footprint, plus `--knife-count`, `--handle-width-mm`, `--handle-gap-mm`, and the drawer-clearance flags), mirroring how `KitchenBin`/`CutleryBin` are selected and exported
- [x] 5.3 Confirm existing CLI defaults and the current default output are unchanged (`test_cli_regular_bin_defaults_are_unchanged`)

Also synced the new `knife-blade-block` capability into `openspec/specs/` (via `/opsx:sync`) so the scenario markers added throughout implementation satisfy the traceability guard, rather than deferring that to task 6.1.

## 6. Traceability, docs, and verification

- [x] 6.1 Add `@pytest.mark.scenario("knife-blade-block", "<scenario>")` markers so every spec scenario is claimed (satisfy the traceability guard); no allowlist entries needed -- every scenario is claimed. Synced the delta spec into `openspec/specs/knife-blade-block/spec.md` via `/opsx:sync` so the guard has a live spec to check against.
- [x] 6.2 Decide and record whether to add the named 7-knife Prima preset now or after first print (Open Question) -- resolved in design.md: no separate preset; `KnifeBlockParameters`'s defaults already *are* the Prima 7-knife set, and a parallel `Preset`/`PRESETS` registry (currently typed to `BinParameters`) would add plumbing without adding capability. Provenance (ORIGINAL, CC BY-SA 4.0) recorded in the README instead.
- [x] 6.3 Update README with a "Knife blade block" section, including the compose-with-blanks note and the deck-height/blank interface
- [x] 6.4 Run `uv run ruff check .` and `uv run pytest` (with coverage) and confirm all green before raising the PR -- 122 passed, `knife_block.py` at 100% coverage; also added `knife_block` to `pyproject.toml`'s `[tool.coverage.run] source` list, which had only listed `cutlery_bin`/`main` and would otherwise have silently skipped measuring the new module
