from pathlib import Path

import pytest

import main
from chop_bin import BinParameters


def test_bin_parameter_validation_rejects_range_errors() -> None:
    """Validation should report invalid parameter ranges with actionable names."""
    params = BinParameters(grid_length_units=0)
    with pytest.raises(ValueError, match="grid_length_units"):
        params.validate()


def test_bin_parameter_validation_rejects_incompatible_cutout() -> None:
    """Validation should reject cutout geometry that cannot fit in the bin body."""
    params = BinParameters(grid_length_units=2, cutout_offset_from_edge_mm=1, cutout_radius_mm=60)
    with pytest.raises(ValueError, match="incompatible"):
        params.validate()


def test_default_output_path_is_deterministic() -> None:
    """Default output file naming should be deterministic for a parameter set."""
    params = BinParameters(grid_length_units=6, grid_width_units=4, bin_height_mm=56)
    output = main.default_output_path(params)
    assert output.name == "chop_bin_6x4_h56.stl"


def test_cli_exports_stl_successfully(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """CLI should export to an explicit output path and return success."""

    def fake_create_chop_bin(_params: BinParameters) -> object:
        return object()

    def fake_export_stl(_part: object, output_path: str) -> None:
        Path(output_path).write_text("solid test\nendsolid test\n", encoding="utf-8")

    monkeypatch.setattr(main, "create_chop_bin", fake_create_chop_bin)
    monkeypatch.setattr(main, "export_stl", fake_export_stl)

    output_file = tmp_path / "sample.stl"
    exit_code = main.main(["--output", str(output_file)])

    assert exit_code == 0
    assert output_file.exists()


def test_cli_validation_failure_returns_non_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """CLI should return a non-zero status with actionable error text on invalid input."""
    exit_code = main.main(["--grid-length", "0"])
    output = capsys.readouterr()

    assert exit_code == 2
    assert "grid_length_units" in output.out


def test_cli_export_failure_returns_non_zero(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """CLI should fail when the output directory does not exist."""
    missing_dir = tmp_path / "missing"
    output_file = missing_dir / "blocked.stl"

    exit_code = main.main(["--output", str(output_file)])
    output = capsys.readouterr()

    assert exit_code == 2
    assert "Output directory does not exist" in output.out
