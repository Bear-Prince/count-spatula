from pathlib import Path
from types import SimpleNamespace

import pytest

import main
from cutlery_bin import BinParameters, BlankingPlateParameters
from knife_block import KnifeBlockParameters


def _stub_part(x: float = 84.0, y: float = 168.0, z: float = 60.0) -> object:
    """A stand-in for a built part exposing the `bounding_box().size` the CLI measures (mm)."""
    return SimpleNamespace(bounding_box=lambda: SimpleNamespace(size=SimpleNamespace(X=x, Y=y, Z=z)))


def test_default_output_path_is_deterministic() -> None:
    """Default output file naming should be deterministic for a parameter set."""
    params = BinParameters(grid_x=4, grid_y=6, height_mm=56)
    output = main.default_output_path(params)
    assert output.name == "kitchen_bin_4x6_h56.stl"


def test_default_output_path_encodes_fractional_height() -> None:
    """Float heights should use 'p' as the decimal separator so the filename stays shell-safe."""
    params = BinParameters(grid_x=2, grid_y=3, height_mm=42.5)
    output = main.default_output_path(params)
    assert output.name == "kitchen_bin_2x3_h42p5.stl"


@pytest.mark.scenario("multi-format-export", "Export with default output path uses configured format extension")
def test_default_output_path_respects_format_flag() -> None:
    """Passing fmt='3mf' should produce a .3mf default filename."""
    params = BinParameters(grid_x=4, grid_y=6, height_mm=56)
    output = main.default_output_path(params, fmt="3mf")
    assert output.name == "kitchen_bin_4x6_h56.3mf"


def test_default_output_path_names_cutlery_bin_for_divisions() -> None:
    """Two or more divisions should produce a cutlery_bin filename."""
    params = BinParameters(grid_x=4, grid_y=6, height_mm=56, divisions=3)
    output = main.default_output_path(params)
    assert output.name == "cutlery_bin_4x6_h56.stl"


def test_default_output_path_for_knife_block() -> None:
    """A KnifeBlockParameters set should produce a knife_block filename, not a bin filename."""
    params = KnifeBlockParameters(knife_count=7, grid_x=3, grid_y=2)
    output = main.default_output_path(params)
    assert output.name == "knife_block_7knives_3x2.stl"


@pytest.mark.scenario("blanking-plates", "Deterministic default filename")
def test_default_output_path_for_blanking_plate() -> None:
    """A BlankingPlateParameters set should produce a blanking_plate filename naming its grid."""
    params = BlankingPlateParameters(grid_x=3, grid_y=5)
    output = main.default_output_path(params)
    assert output.name == "blanking_plate_3x5.stl"


def _capture_cli(monkeypatch: pytest.MonkeyPatch, argv: list[str], part: object | None = None) -> dict:
    """Run the CLI with geometry/export mocked, returning what was built."""
    captured: dict = {}
    stub = part if part is not None else _stub_part()

    def fake_kitchen(params: BinParameters) -> object:
        captured["params"] = params
        captured["kind"] = "kitchen"
        return stub

    def fake_cutlery(params: BinParameters) -> object:
        captured["params"] = params
        captured["kind"] = "cutlery"
        return stub

    monkeypatch.setattr(main, "create_kitchen_bin", fake_kitchen)
    monkeypatch.setattr(main, "create_cutlery_bin", fake_cutlery)
    monkeypatch.setattr(main, "export_bin", lambda _part, path: (path.touch(), path)[1])

    captured["exit_code"] = main.main(argv)
    return captured


@pytest.mark.scenario("bin-presets", "Plain invocation generates a default KitchenBin")
def test_cli_plain_invocation_builds_kitchen_bin(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A plain invocation builds a KitchenBin with cutouts enabled."""
    result = _capture_cli(monkeypatch, ["--output", str(tmp_path / "plain.stl")])
    assert result["exit_code"] == 0
    assert result["kind"] == "kitchen"
    assert result["params"].cutouts_enabled is True


@pytest.mark.scenario("bin-presets", "Requesting divisions generates a CutleryBin")
def test_cli_divisions_builds_cutlery_bin(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Requesting two or more divisions builds a CutleryBin."""
    result = _capture_cli(monkeypatch, ["--divisions", "3", "--output", str(tmp_path / "cut.stl")])
    assert result["exit_code"] == 0
    assert result["kind"] == "cutlery"
    assert result["params"].divisions == 3


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutouts disabled")
def test_cli_no_cutouts_flag_disables_cutouts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The --no-cutouts flag builds parameters with cutouts disabled."""
    result = _capture_cli(monkeypatch, ["--no-cutouts", "--output", str(tmp_path / "solid.stl")])
    assert result["params"].cutouts_enabled is False


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutout floor reaches past the grid line")
def test_cli_cutout_offset_units_single_value_applies_to_both_ends(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A single --cutout-offset-units value sets both the start and end offsets."""
    # grid_y=6 leaves a valid 2-unit gap (6 - 2 - 2 = 2); the default grid_y=4 would reject units=2.
    result = _capture_cli(
        monkeypatch,
        ["--grid-y", "6", "--cutout-offset-units", "2", "--output", str(tmp_path / "units.stl")],
    )
    assert result["params"].cutout_offset_start_units == 2
    assert result["params"].cutout_offset_end_units == 2


@pytest.mark.scenario("gridfinity-utensil-bin", "Independent per-end cutout offsets")
def test_cli_cutout_offset_units_two_values_set_start_and_end(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Two --cutout-offset-units values set the start and end offsets independently."""
    result = _capture_cli(
        monkeypatch,
        ["--grid-y", "5", "--cutout-offset-units", "1", "2", "--output", str(tmp_path / "asym.stl")],
    )
    assert result["params"].cutout_offset_start_units == 1
    assert result["params"].cutout_offset_end_units == 2


def test_cli_cutout_offset_units_rejects_three_values(capsys: pytest.CaptureFixture[str]) -> None:
    """Passing more than two --cutout-offset-units values is rejected with an actionable message."""
    exit_code = main.main(["--cutout-offset-units", "1", "2", "3"])
    output = capsys.readouterr()
    assert exit_code == 2
    assert "takes 1 or 2 values" in output.err


def test_cli_wave_profile_flags_set_parameters(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The wave divider flags populate the corresponding parameters and build a CutleryBin."""
    result = _capture_cli(
        monkeypatch,
        ["--divisions", "3", "--divider-profile", "wave", "--divider-amplitude-mm", "4",
         "--output", str(tmp_path / "wave.stl")],
    )
    assert result["exit_code"] == 0
    assert result["kind"] == "cutlery"
    assert result["params"].divider_profile == "wave"
    assert result["params"].divider_amplitude_mm == 4.0


@pytest.mark.scenario("gridfinity-utensil-bin", "Default profile preserves straight geometry")
def test_cli_defaults_to_straight_divider_profile(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Omitting the divider flags leaves the straight profile with no amplitude."""
    result = _capture_cli(monkeypatch, ["--divisions", "3", "--output", str(tmp_path / "s.stl")])
    assert result["params"].divider_profile == "straight"
    assert result["params"].divider_amplitude_mm == 0.0


@pytest.mark.scenario("bin-presets", "Generate a preset bin from the CLI")
def test_cli_preset_seeds_parameters(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The chop-board preset seeds the chopping-board pocket dimensions."""
    result = _capture_cli(monkeypatch, ["--preset", "chop-board", "--output", str(tmp_path / "chop.stl")])
    assert result["exit_code"] == 0
    assert result["params"].pocket_length_mm == 220
    assert result["params"].pocket_width_mm == 160


@pytest.mark.scenario("bin-presets", "Override preset values")
def test_cli_preset_override_applies(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """An explicit override takes effect on top of a preset's defaults."""
    result = _capture_cli(
        monkeypatch, ["--preset", "chop-board", "--grid-x", "5", "--output", str(tmp_path / "o.stl")]
    )
    assert result["params"].grid_x == 5
    assert result["params"].pocket_length_mm == 220


@pytest.mark.scenario("multi-format-export", "Default format is STL when no format flag is given")
def test_cli_default_naming_uses_stl_by_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Default output filename should use .stl when no --format flag is given."""
    monkeypatch.chdir(tmp_path)
    result = _capture_cli(monkeypatch, [])
    assert result["exit_code"] == 0
    assert any(p.suffix == ".stl" for p in tmp_path.iterdir())


@pytest.mark.scenario("multi-format-export", "Export with default output path uses configured format extension")
def test_cli_default_naming_uses_3mf_with_format_flag(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Default output filename should use .3mf when --format 3mf is given."""
    monkeypatch.chdir(tmp_path)
    result = _capture_cli(monkeypatch, ["--format", "3mf"])
    assert result["exit_code"] == 0
    assert any(p.suffix == ".3mf" for p in tmp_path.iterdir())


@pytest.mark.scenario("bin-presets", "Disabling cutouts on a cutouts-required preset is rejected")
def test_cli_no_cutouts_rejected_for_chop_board(capsys: pytest.CaptureFixture[str]) -> None:
    """Disabling cutouts on the chop-board preset is a footgun and must be rejected."""
    exit_code = main.main(["--preset", "chop-board", "--no-cutouts"])
    output = capsys.readouterr()
    assert exit_code == 2
    assert "cannot be disabled" in output.err


@pytest.mark.scenario("bin-presets", "Unknown preset is rejected at the CLI")
def test_cli_unknown_preset_returns_non_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """An unknown preset name exits non-zero with an actionable message."""
    exit_code = main.main(["--preset", "nope"])
    output = capsys.readouterr()
    assert exit_code == 2
    assert "Unknown preset" in output.err


@pytest.mark.scenario("gridfinity-utensil-bin", "Reject out-of-range grid size")
def test_cli_validation_failure_returns_non_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """CLI should return a non-zero status with actionable error text on invalid input."""
    exit_code = main.main(["--grid-x", "0"])
    output = capsys.readouterr()
    assert exit_code == 2
    assert "grid_x" in output.err


@pytest.mark.scenario("multi-format-export", "Missing output directory")
def test_cli_export_failure_returns_non_zero(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """CLI should fail when the output directory does not exist."""
    output_file = tmp_path / "missing" / "blocked.stl"
    exit_code = main.main(["--output", str(output_file)])
    output = capsys.readouterr()
    assert exit_code == 2
    assert "Output directory does not exist" in output.err


def test_cli_rejects_conflicting_format_and_output_extension(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """An explicit --format that disagrees with --output's extension is rejected."""
    result = _capture_cli(
        monkeypatch, ["--format", "3mf", "--output", str(tmp_path / "mismatch.stl")]
    )
    output = capsys.readouterr()
    assert result["exit_code"] == 2
    assert "--format 3mf conflicts with --output's extension" in output.err


def test_cli_allows_matching_format_and_output_extension(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An explicit --format that matches --output's extension is accepted."""
    result = _capture_cli(
        monkeypatch, ["--format", "3mf", "--output", str(tmp_path / "match.3mf")]
    )
    assert result["exit_code"] == 0


@pytest.mark.scenario("print-bed-validation", "Default print volume applied")
def test_cli_default_volume_emits_no_warning(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """A normally-sized bin against the default 220x220x240 volume produces no warning."""
    _capture_cli(monkeypatch, ["--output", str(tmp_path / "ok.stl")])
    assert "Warning" not in capsys.readouterr().err


@pytest.mark.scenario("print-bed-validation", "Override the print volume via CLI")
def test_cli_bed_override_applies(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Overriding the bed size via --bed-x/--bed-y/--bed-z is honoured by the fit check."""
    result = _capture_cli(
        monkeypatch,
        ["--bed-x", "50", "--bed-y", "50", "--bed-z", "50", "--output", str(tmp_path / "tiny_bed.stl")],
    )
    err = capsys.readouterr().err
    assert result["exit_code"] == 0
    assert "exceeds the print volume" in err


@pytest.mark.scenario("print-bed-validation", "Model exceeds the build volume on an axis")
@pytest.mark.scenario("print-bed-validation", "Warning message is actionable")
def test_cli_warns_when_model_exceeds_bed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """An oversized model warns to stderr, still exports, and exits 0 (non-blocking)."""
    result = _capture_cli(
        monkeypatch, ["--output", str(tmp_path / "big.stl")], part=_stub_part(250.0, 100.0, 60.0)
    )
    err = capsys.readouterr().err
    assert result["exit_code"] == 0
    assert "exceeds the print volume width" in err
    assert (tmp_path / "big.stl").exists()


def _capture_knife_block_cli(monkeypatch: pytest.MonkeyPatch, argv: list[str], part: object | None = None) -> dict:
    """Run the CLI with knife-block geometry/export mocked, returning what was built."""
    captured: dict = {}
    stub = part if part is not None else _stub_part(x=125.5, y=83.5, z=18.0)

    def fake_knife_block(params: KnifeBlockParameters) -> object:
        captured["params"] = params
        return stub

    monkeypatch.setattr(main, "create_knife_blade_block", fake_knife_block)
    monkeypatch.setattr(main, "export_bin", lambda _part, path: (path.touch(), path)[1])

    captured["exit_code"] = main.main(argv)
    return captured


@pytest.mark.scenario("knife-blade-block", "Generate a block from valid parameters")
def test_cli_knife_block_flag_builds_a_block(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """--knife-block builds a KnifeBlockParameters set with the default 7-knife layout."""
    result = _capture_knife_block_cli(monkeypatch, ["--knife-block", "--output", str(tmp_path / "kb.stl")])
    assert result["exit_code"] == 0
    assert isinstance(result["params"], KnifeBlockParameters)
    assert result["params"].knife_count == 7


def test_cli_knife_block_count_and_handle_flags_apply(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """--knife-count/--handle-width-mm/--handle-gap-mm override the knife block defaults."""
    result = _capture_knife_block_cli(
        monkeypatch,
        [
            "--knife-block",
            "--knife-count", "5",
            "--handle-width-mm", "20",
            "--handle-gap-mm", "8",
            "--output", str(tmp_path / "kb.stl"),
        ],
    )
    assert result["params"].knife_count == 5
    assert result["params"].handle_width_mm == 20.0
    assert result["params"].handle_gap_mm == 8.0


def test_cli_knife_block_reuses_grid_flags(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """--grid-x/--grid-y apply to the knife block's own footprint in --knife-block mode."""
    result = _capture_knife_block_cli(
        monkeypatch,
        ["--knife-block", "--grid-x", "4", "--grid-y", "3", "--output", str(tmp_path / "kb.stl")],
    )
    assert result["params"].grid_x == 4
    assert result["params"].grid_y == 3


def test_cli_knife_block_default_output_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Omitting --output in --knife-block mode names the file after the knife block, not a bin."""
    monkeypatch.chdir(tmp_path)
    result = _capture_knife_block_cli(monkeypatch, ["--knife-block"])
    assert result["exit_code"] == 0
    assert any(p.name == "knife_block_7knives_3x2.stl" for p in tmp_path.iterdir())


@pytest.mark.scenario("knife-blade-block", "Warn when the tallest knife will not clear the drawer")
def test_cli_knife_block_drawer_clearance_warns(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """A shallow --drawer-height-mm triggers the drawer clearance warning, still exports."""
    result = _capture_knife_block_cli(
        monkeypatch,
        ["--knife-block", "--drawer-height-mm", "50", "--output", str(tmp_path / "kb.stl")],
    )
    err = capsys.readouterr().err
    assert result["exit_code"] == 0
    assert "exceeds the drawer's internal height" in err
    assert (tmp_path / "kb.stl").exists()


@pytest.mark.scenario("knife-blade-block", "No warning when everything clears")
def test_cli_knife_block_default_drawer_height_emits_no_warning(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """The default drawer height and blade depth for the target set produce no warning."""
    _capture_knife_block_cli(monkeypatch, ["--knife-block", "--output", str(tmp_path / "kb.stl")])
    assert "drawer" not in capsys.readouterr().err.lower()


def test_cli_regular_bin_defaults_are_unchanged(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Omitting --knife-block leaves the existing default KitchenBin behaviour untouched."""
    result = _capture_cli(monkeypatch, ["--output", str(tmp_path / "plain.stl")])
    assert result["exit_code"] == 0
    assert result["kind"] == "kitchen"
    assert isinstance(result["params"], BinParameters)


def _capture_blanking_plate_cli(monkeypatch: pytest.MonkeyPatch, argv: list[str], part: object | None = None) -> dict:
    """Run the CLI with blanking-plate geometry/export mocked, returning what was built."""
    captured: dict = {}
    stub = part if part is not None else _stub_part(x=83.5, y=167.5, z=7.804)

    def fake_blanking_plate(params: BlankingPlateParameters) -> object:
        captured["params"] = params
        return stub

    monkeypatch.setattr(main, "create_blanking_plate", fake_blanking_plate)
    monkeypatch.setattr(main, "export_bin", lambda _part, path: (path.touch(), path)[1])

    captured["exit_code"] = main.main(argv)
    return captured


@pytest.mark.scenario("blanking-plates", "Generate a blanking plate")
def test_cli_blanking_plate_flag_builds_a_plate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """--blanking-plate builds a BlankingPlateParameters set with the default 2x4 grid."""
    result = _capture_blanking_plate_cli(
        monkeypatch, ["--blanking-plate", "--output", str(tmp_path / "plate.stl")]
    )
    assert result["exit_code"] == 0
    assert isinstance(result["params"], BlankingPlateParameters)
    assert (result["params"].grid_x, result["params"].grid_y) == (2, 4)


def test_cli_blanking_plate_reuses_grid_flags(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """--grid-x/--grid-y apply to the plate's own footprint in --blanking-plate mode."""
    result = _capture_blanking_plate_cli(
        monkeypatch,
        ["--blanking-plate", "--grid-x", "3", "--grid-y", "5", "--output", str(tmp_path / "plate.stl")],
    )
    assert (result["params"].grid_x, result["params"].grid_y) == (3, 5)


def test_cli_blanking_plate_default_output_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Omitting --output in --blanking-plate mode names the file after the plate, not a bin."""
    monkeypatch.chdir(tmp_path)
    result = _capture_blanking_plate_cli(monkeypatch, ["--blanking-plate"])
    assert result["exit_code"] == 0
    assert any(p.name == "blanking_plate_2x4.stl" for p in tmp_path.iterdir())


@pytest.mark.scenario("blanking-plates", "Bin-only flags leave the plate unchanged")
def test_cli_blanking_plate_ignores_bin_only_flags(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Bin-only flags (pocket, cutout, divider) passed alongside --blanking-plate do not alter the plate."""
    baseline = _capture_blanking_plate_cli(
        monkeypatch, ["--blanking-plate", "--output", str(tmp_path / "a.stl")]
    )
    with_bin_flags = _capture_blanking_plate_cli(
        monkeypatch,
        [
            "--blanking-plate",
            "--pocket-length-mm", "50",
            "--no-cutouts",
            "--divisions", "3",
            "--output", str(tmp_path / "b.stl"),
        ],
    )
    assert with_bin_flags["exit_code"] == 0
    assert with_bin_flags["params"] == baseline["params"]


@pytest.mark.scenario("blanking-plates", "Height flags do not resize the plate")
def test_cli_blanking_plate_ignores_height_flags(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A height flag passed alongside --blanking-plate does not resize the plate (no height field exists)."""
    baseline = _capture_blanking_plate_cli(
        monkeypatch, ["--blanking-plate", "--output", str(tmp_path / "a.stl")]
    )
    with_height = _capture_blanking_plate_cli(
        monkeypatch,
        ["--blanking-plate", "--height-mm", "100", "--output", str(tmp_path / "b.stl")],
    )
    assert with_height["exit_code"] == 0
    assert with_height["params"] == baseline["params"]


@pytest.mark.scenario("blanking-plates", "Export a blanking plate")
def test_cli_blanking_plate_exports_through_the_standard_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A blanking plate exports through the unchanged export_bin() path, for both STL and 3MF."""
    stl_result = _capture_blanking_plate_cli(
        monkeypatch, ["--blanking-plate", "--output", str(tmp_path / "plate.stl")]
    )
    threemf_result = _capture_blanking_plate_cli(
        monkeypatch, ["--blanking-plate", "--output", str(tmp_path / "plate.3mf")]
    )
    assert stl_result["exit_code"] == 0
    assert threemf_result["exit_code"] == 0
    assert (tmp_path / "plate.stl").exists()
    assert (tmp_path / "plate.3mf").exists()


@pytest.mark.scenario("blanking-plates", "Print-bed check applies to a blanking plate")
def test_cli_blanking_plate_print_bed_check_uses_actual_bounding_box(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """The print-bed check measures the plate's actual bounding box, warning when it is oversized."""
    result = _capture_blanking_plate_cli(
        monkeypatch,
        ["--blanking-plate", "--output", str(tmp_path / "big.stl")],
        part=_stub_part(x=250.0, y=100.0, z=7.804),
    )
    err = capsys.readouterr().err
    assert result["exit_code"] == 0
    assert "exceeds the print volume width" in err


def _split_stub(pieces: int = 2) -> list[object]:
    """Stand-ins for split pieces, each exposing the bounding box the CLI orders and measures."""
    return [_stub_part(x=167.5, y=125.75, z=59.9) for _ in range(pieces)]


def _capture_split_cli(
    monkeypatch: pytest.MonkeyPatch, argv: list[str], part: object | None = None, pieces: int = 2
) -> dict:
    """Run the CLI with geometry, splitting and export mocked, recording the split call and exports."""
    captured: dict = {"exports": []}
    stub = part if part is not None else _stub_part(x=167.5, y=251.5, z=59.9)

    def fake_kitchen(params: BinParameters) -> object:
        captured["params"] = params
        return stub

    def fake_split(_part: object, n_x: int, n_y: int, bed_x: float, bed_y: float, mode: object) -> list[object]:
        captured["split_args"] = (n_x, n_y, bed_x, bed_y, mode)
        return _split_stub(pieces)

    def fake_export(_part: object, path: Path) -> Path:
        captured["exports"].append(path)
        path.touch()
        return path

    monkeypatch.setattr(main, "create_kitchen_bin", fake_kitchen)
    monkeypatch.setattr(main, "create_cutlery_bin", fake_kitchen)
    monkeypatch.setattr(main, "split_for_print_bed", fake_split)
    monkeypatch.setattr(main, "export_bin", fake_export)

    captured["exit_code"] = main.main(argv)
    return captured


@pytest.mark.scenario("print-splitting", "Oversized model is not split without the flag")
def test_cli_does_not_split_without_the_flag(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """An oversized model exports as a single file unless --split is given."""
    oversized = _stub_part(x=167.5, y=251.5, z=59.9)
    result = _capture_split_cli(monkeypatch, ["--output", str(tmp_path / "chop.stl")], part=oversized)
    assert result["exit_code"] == 0
    assert "split_args" not in result
    assert result["exports"] == [tmp_path / "chop.stl"]


@pytest.mark.scenario("print-splitting", "Split produces bed-fitting pieces")
def test_cli_split_passes_grid_and_bed_to_the_splitter(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """--split hands the model's grid size and the configured bed to the splitter."""
    result = _capture_split_cli(
        monkeypatch, ["--preset", "chop-board", "--split", "--output", str(tmp_path / "chop.stl")]
    )
    assert result["exit_code"] == 0
    n_x, n_y, bed_x, bed_y, mode = result["split_args"]
    assert (n_x, n_y) == (result["params"].grid_x, result["params"].grid_y)
    assert (bed_x, bed_y) == (220.0, 220.0)
    assert mode is main.SplitMode.GLUED


@pytest.mark.scenario("print-splitting", "Pieces are written to predictable paths")
def test_cli_split_writes_numbered_piece_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Each piece is written beside the requested output path with a -partN suffix."""
    result = _capture_split_cli(
        monkeypatch, ["--preset", "chop-board", "--split", "--output", str(tmp_path / "chop.stl")]
    )
    assert result["exports"] == [tmp_path / "chop-part1.stl", tmp_path / "chop-part2.stl"]


@pytest.mark.scenario("print-splitting", "Piece numbering is stable across runs")
def test_cli_split_piece_paths_are_stable_across_runs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Re-running the same split invocation maps pieces to the same filenames."""
    argv = ["--preset", "chop-board", "--split", "--output", str(tmp_path / "chop.stl")]
    first = _capture_split_cli(monkeypatch, argv)
    second = _capture_split_cli(monkeypatch, argv)
    assert first["exports"] == second["exports"]


@pytest.mark.scenario("print-splitting", "Standalone mode warns on a pocketed model")
def test_cli_standalone_split_warns_on_a_pocketed_model(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """Standalone pieces of a bin have open-ended pockets, which the CLI warns about but still exports."""
    result = _capture_split_cli(
        monkeypatch,
        ["--preset", "chop-board", "--split", "--split-mode", "standalone", "--output", str(tmp_path / "c.stl")],
    )
    assert result["exit_code"] == 0
    assert "open-ended pocket" in capsys.readouterr().err
    assert len(result["exports"]) == 2


@pytest.mark.scenario("print-splitting", "Z overflow is reported as unsplittable")
def test_cli_split_warns_that_height_overflow_is_unsplittable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """A model taller than the bed still splits on X and Y, with a warning that Z cannot be resolved."""
    too_tall = _stub_part(x=167.5, y=251.5, z=300.0)
    result = _capture_split_cli(
        monkeypatch, ["--split", "--output", str(tmp_path / "tall.stl")], part=too_tall
    )
    assert result["exit_code"] == 0
    assert "cannot resolve a height overflow" in capsys.readouterr().err
    assert len(result["exports"]) == 2


def test_cli_split_mode_without_split_is_an_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """--split-mode without --split would silently do nothing, so it is rejected."""
    result = _capture_split_cli(
        monkeypatch, ["--split-mode", "standalone", "--output", str(tmp_path / "x.stl")]
    )
    assert result["exit_code"] == 2
