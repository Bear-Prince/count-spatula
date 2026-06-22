from pathlib import Path

import pytest

import main
from cutlery_bin import BinParameters


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


def _capture_cli(monkeypatch: pytest.MonkeyPatch, argv: list[str]) -> dict:
    """Run the CLI with geometry/export mocked, returning what was built."""
    captured: dict = {}

    def fake_kitchen(params: BinParameters) -> object:
        captured["params"] = params
        captured["kind"] = "kitchen"
        return object()

    def fake_cutlery(params: BinParameters) -> object:
        captured["params"] = params
        captured["kind"] = "cutlery"
        return object()

    monkeypatch.setattr(main, "create_kitchen_bin", fake_kitchen)
    monkeypatch.setattr(main, "create_cutlery_bin", fake_cutlery)
    monkeypatch.setattr(main, "export_bin", lambda _part, path: (path.touch(), path)[1])

    captured["exit_code"] = main.main(argv)
    return captured


def test_cli_plain_invocation_builds_kitchen_bin(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A plain invocation builds a KitchenBin with cutouts enabled."""
    result = _capture_cli(monkeypatch, ["--output", str(tmp_path / "plain.stl")])
    assert result["exit_code"] == 0
    assert result["kind"] == "kitchen"
    assert result["params"].cutouts_enabled is True


def test_cli_divisions_builds_cutlery_bin(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Requesting two or more divisions builds a CutleryBin."""
    result = _capture_cli(monkeypatch, ["--divisions", "3", "--output", str(tmp_path / "cut.stl")])
    assert result["exit_code"] == 0
    assert result["kind"] == "cutlery"
    assert result["params"].divisions == 3


def test_cli_no_cutouts_flag_disables_cutouts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The --no-cutouts flag builds parameters with cutouts disabled."""
    result = _capture_cli(monkeypatch, ["--no-cutouts", "--output", str(tmp_path / "solid.stl")])
    assert result["params"].cutouts_enabled is False


def test_cli_preset_seeds_parameters(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The chop-board preset seeds the chopping-board pocket dimensions."""
    result = _capture_cli(monkeypatch, ["--preset", "chop-board", "--output", str(tmp_path / "chop.stl")])
    assert result["exit_code"] == 0
    assert result["params"].pocket_length_mm == 220
    assert result["params"].pocket_width_mm == 160


def test_cli_preset_override_applies(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """An explicit override takes effect on top of a preset's defaults."""
    result = _capture_cli(
        monkeypatch, ["--preset", "chop-board", "--grid-x", "5", "--output", str(tmp_path / "o.stl")]
    )
    assert result["params"].grid_x == 5
    assert result["params"].pocket_length_mm == 220


def test_cli_default_naming_uses_stl_by_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Default output filename should use .stl when no --format flag is given."""
    monkeypatch.chdir(tmp_path)
    result = _capture_cli(monkeypatch, [])
    assert result["exit_code"] == 0
    assert any(p.suffix == ".stl" for p in tmp_path.iterdir())


def test_cli_default_naming_uses_3mf_with_format_flag(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Default output filename should use .3mf when --format 3mf is given."""
    monkeypatch.chdir(tmp_path)
    result = _capture_cli(monkeypatch, ["--format", "3mf"])
    assert result["exit_code"] == 0
    assert any(p.suffix == ".3mf" for p in tmp_path.iterdir())


def test_cli_no_cutouts_rejected_for_chop_board(capsys: pytest.CaptureFixture[str]) -> None:
    """Disabling cutouts on the chop-board preset is a footgun and must be rejected."""
    exit_code = main.main(["--preset", "chop-board", "--no-cutouts"])
    output = capsys.readouterr()
    assert exit_code == 2
    assert "cannot be disabled" in output.out


def test_cli_unknown_preset_returns_non_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """An unknown preset name exits non-zero with an actionable message."""
    exit_code = main.main(["--preset", "nope"])
    output = capsys.readouterr()
    assert exit_code == 2
    assert "Unknown preset" in output.out


def test_cli_validation_failure_returns_non_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """CLI should return a non-zero status with actionable error text on invalid input."""
    exit_code = main.main(["--grid-x", "0"])
    output = capsys.readouterr()
    assert exit_code == 2
    assert "grid_x" in output.out


def test_cli_export_failure_returns_non_zero(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """CLI should fail when the output directory does not exist."""
    output_file = tmp_path / "missing" / "blocked.stl"
    exit_code = main.main(["--output", str(output_file)])
    output = capsys.readouterr()
    assert exit_code == 2
    assert "Output directory does not exist" in output.out
