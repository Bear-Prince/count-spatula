## 1. Parameters and validation

- [x] 1.1 Add `divider_profile: str = "straight"` and `divider_amplitude_mm: float = 0.0` to `BinParameters`
  in `cutlery_bin.py`, and a `MIN_CHANNEL_GAP` module constant (proposed 2.0 mm).
- [x] 1.2 Extend `BinParameters.validate()` to reject an unknown `divider_profile`, a non-positive amplitude
  when the profile is `wave`, and an amplitude exceeding
  `(column_pitch − divider_thickness_mm − MIN_CHANNEL_GAP) / 2`, each with an actionable message.
- [x] 1.3 Add tests in `tests/test_cutlery_bin.py` for the new fields' defaults and for each validation
  rejection (unknown profile, non-positive amplitude, amplitude too large), mapping to the spec's
  "Reject a wave amplitude that would collide" and "Reject a non-positive wave amplitude" scenarios.

## 2. Wave divider geometry

- [x] 2.1 In `CutleryBin._add_interior()`, branch on `divider_profile`: keep the existing straight `Box` path
  unchanged for `straight`, and add a `wave` path.
- [x] 2.2 Implement the `wave` path: for divider `k`, displace the centreline by
  `amplitude * (-1)**k * sin(2π·t)` over `t ∈ [0, 1]` along the pocket length, build a sampled closed band
  (`centreline ± divider_thickness/2`) and extrude it to the wall height (per design Decisions 1–3).
- [x] 2.3 Build each wave divider across the full pocket length so its ends embed in the un-cut walls at the
  nominal spacing (end-attachment and average-column-width preservation).

## 3. CLI wiring

- [x] 3.1 Add `--divider-profile` (choices `straight`/`wave`) and `--divider-amplitude-mm` to `build_parser()`
  in `main.py`, following the existing `--divisions` / `--divider-thickness-mm` style.
- [x] 3.2 Map the new flags through `create_parameters()` so they populate the corresponding
  `BinParameters` fields.
- [x] 3.3 Add tests in `tests/test_cli_and_params.py` covering the new flags and that omitting them yields the
  straight defaults.

## 4. Behaviour and regression tests

- [x] 4.1 Add a test asserting a default-profile `CutleryBin` produces geometry identical to the pre-change
  straight output (spec scenario "Default profile preserves straight geometry").
- [x] 4.2 Add a test that a `wave` `CutleryBin` builds valid geometry with the divider centreline meeting both
  end walls and adjacent dividers phase-mirrored (spec scenarios "Wave profile bends the dividers" and
  "Adjacent wave dividers alternate orientation").
- [x] 4.3 Add a test that with cutouts enabled the full-height slot still passes through wavy dividers and each
  divider stays attached at both ends (spec scenario "Cutout passes through dividers").

## 5. Verification

- [x] 5.1 Run `uv run ruff check .` and fix any findings.
- [x] 5.2 Run `uv run pytest` and confirm the full suite passes.
- [x] 5.3 Generate a sample wave bin via `main.py` and visually confirm the dividers nest as intended.
