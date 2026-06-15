"""Tests for utensil bin parameters, geometry, CLI, and bed-size validation."""

from pathlib import Path

import pytest
from build123d.mesher import Mesher

import main
from utensil_bin import UtensilBinParameters, check_print_bed, create_utensil_bin

# ---------------------------------------------------------------------------
# 2.4  Parameter model tests
# ---------------------------------------------------------------------------


def test_default_parameters_are_valid() -> None:
    """Default UtensilBinParameters should pass validation without errors."""
    params = UtensilBinParameters()
    params.validate()  # Must not raise.


def test_explicit_parameters_are_valid() -> None:
    """Explicitly provided in-range parameters should pass validation."""
    params = UtensilBinParameters(
        grid_x=3,
        grid_y=2,
        height_in_units=5,
        height_mm=None,
        div_x=2,
        div_y=1,
        wall_thickness_mm=1.5,
    )
    params.validate()  # Must not raise.


def test_height_in_units_effective_height() -> None:
    """effective_height_mm should return height_in_units * 7 when height_mm is unset."""
    params = UtensilBinParameters(height_in_units=7, height_mm=None)
    assert params.effective_height_mm == 49.0


def test_height_mm_effective_height() -> None:
    """effective_height_mm should return height_mm directly when set."""
    params = UtensilBinParameters(height_in_units=None, height_mm=55.0)
    assert params.effective_height_mm == 55.0


def test_validate_rejects_grid_x_out_of_range() -> None:
    """Validation should reject grid_x outside 1-12."""
    with pytest.raises(ValueError, match="grid_x"):
        UtensilBinParameters(grid_x=0).validate()


def test_validate_rejects_grid_y_out_of_range() -> None:
    """Validation should reject grid_y outside 1-12."""
    with pytest.raises(ValueError, match="grid_y"):
        UtensilBinParameters(grid_y=13).validate()


def test_validate_rejects_both_height_fields_set() -> None:
    """Validation should reject parameters with both height_in_units and height_mm set."""
    with pytest.raises(ValueError, match="mutually exclusive"):
        UtensilBinParameters(height_in_units=4, height_mm=30.0).validate()


def test_validate_rejects_neither_height_field_set() -> None:
    """Validation should reject parameters with neither height field set."""
    with pytest.raises(ValueError, match="one of"):
        UtensilBinParameters(height_in_units=None, height_mm=None).validate()


def test_validate_rejects_div_x_less_than_one() -> None:
    """Validation should reject div_x less than 1."""
    with pytest.raises(ValueError, match="div_x"):
        UtensilBinParameters(div_x=0).validate()


def test_validate_rejects_div_y_less_than_one() -> None:
    """Validation should reject div_y less than 1."""
    with pytest.raises(ValueError, match="div_y"):
        UtensilBinParameters(div_y=0).validate()


def test_validate_rejects_non_positive_wall_thickness() -> None:
    """Validation should reject wall_thickness_mm of 0 or less."""
    with pytest.raises(ValueError, match="wall_thickness_mm"):
        UtensilBinParameters(wall_thickness_mm=0).validate()


# ---------------------------------------------------------------------------
# 3.3  Geometry tests
# ---------------------------------------------------------------------------


def test_create_utensil_bin_default_produces_valid_geometry() -> None:
    """create_utensil_bin with defaults should produce a non-empty solid."""
    part = create_utensil_bin()
    assert part.volume > 0


def test_create_utensil_bin_explicit_params_bounding_box() -> None:
    """Explicit parameters should produce geometry matching the requested grid footprint."""
    params = UtensilBinParameters(grid_x=2, grid_y=3, height_in_units=4)
    part = create_utensil_bin(params)
    bbox = part.bounding_box()
    assert part.volume > 0
    # Gridfinity unit is 42 mm; allow 1 mm tolerance for base tolerances.
    assert abs(bbox.size.X - (2 * 42)) < 1.0, f"X size {bbox.size.X} unexpected"
    assert abs(bbox.size.Y - (3 * 42)) < 1.0, f"Y size {bbox.size.Y} unexpected"


def test_create_utensil_bin_freeform_height() -> None:
    """Freeform height_mm should produce geometry at approximately the requested height."""
    params = UtensilBinParameters(height_in_units=None, height_mm=55.0)
    part = create_utensil_bin(params)
    assert part.volume > 0
    bbox = part.bounding_box()
    # Bin.height is extruded above the Gridfinity base (~7 mm), so total Z > requested height.
    assert params.height_mm < bbox.size.Z, f"Z size {bbox.size.Z} should exceed height_mm"
    assert params.height_mm + 15.0 > bbox.size.Z, f"Z size {bbox.size.Z} unexpectedly large"


# ---------------------------------------------------------------------------
# Real export round-trip (exercises export_bin -> Mesher, not a mock)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def small_part() -> object:
    """Build a small utensil bin once and reuse it across export round-trip tests."""
    params = UtensilBinParameters(grid_x=1, grid_y=1, height_in_units=2)
    return create_utensil_bin(params)


@pytest.mark.parametrize("extension", ["stl", "3mf"])
def test_export_bin_writes_valid_mesh(small_part: object, tmp_path: Path, extension: str) -> None:
    """export_bin should write a non-empty file that reads back as a single valid mesh."""
    output_path = tmp_path / f"bin.{extension}"

    returned = main.export_bin(small_part, output_path)

    assert returned == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0

    # Re-open the written file to confirm it is parseable mesh geometry, not just bytes on disk.
    shapes = Mesher().read(output_path)
    assert len(shapes) == 1, f"Expected one shape in {extension}, got {len(shapes)}"


# ---------------------------------------------------------------------------
# 4.2  Print-bed validation tests
# ---------------------------------------------------------------------------


def test_check_print_bed_no_warnings_when_fits() -> None:
    """No warnings should be returned when the bin footprint fits the bed on both axes."""
    warnings = check_print_bed(2, 4, bed_x_mm=200, bed_y_mm=200)
    assert warnings == []


def test_check_print_bed_warns_x_only() -> None:
    """A warning should be returned when the footprint exceeds bed X only."""
    # grid_x=5 → footprint 210 mm, bed_x=200 mm
    warnings = check_print_bed(5, 2, bed_x_mm=200, bed_y_mm=200)
    assert len(warnings) == 1
    assert "X" in warnings[0]
    assert "210" in warnings[0]


def test_check_print_bed_warns_y_only() -> None:
    """A warning should be returned when the footprint exceeds bed Y only."""
    # grid_y=5 → footprint 210 mm, bed_y=200 mm
    warnings = check_print_bed(2, 5, bed_x_mm=200, bed_y_mm=200)
    assert len(warnings) == 1
    assert "Y" in warnings[0]


def test_check_print_bed_warns_both_axes() -> None:
    """Warnings should be returned for each axis when the footprint exceeds both bed dimensions."""
    warnings = check_print_bed(5, 5, bed_x_mm=200, bed_y_mm=200)
    assert len(warnings) == 2


# ---------------------------------------------------------------------------
# 5.3  Utensil-bin CLI tests
# ---------------------------------------------------------------------------


def test_utensil_bin_cli_exports_successfully(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Utensil-bin CLI should export to an explicit output path and return success."""
    monkeypatch.setattr(main, "create_utensil_bin", lambda _: object())
    monkeypatch.setattr(main, "export_bin", lambda _part, path: (path.touch(), path)[1])

    output_file = tmp_path / "sample.stl"
    exit_code = main.main(["utensil-bin", "--output", str(output_file)])

    assert exit_code == 0
    assert output_file.exists()


def test_utensil_bin_cli_default_naming_stl(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Utensil-bin default output filename should use .stl when no --format flag is given."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main, "create_utensil_bin", lambda _: object())
    monkeypatch.setattr(main, "export_bin", lambda _part, path: (path.touch(), path)[1])

    exit_code = main.main(["utensil-bin"])
    assert exit_code == 0
    assert any(p.suffix == ".stl" for p in tmp_path.iterdir())


def test_utensil_bin_cli_default_naming_3mf(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Utensil-bin default output filename should use .3mf when --format 3mf is given."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main, "create_utensil_bin", lambda _: object())
    monkeypatch.setattr(main, "export_bin", lambda _part, path: (path.touch(), path)[1])

    exit_code = main.main(["utensil-bin", "--format", "3mf"])
    assert exit_code == 0
    assert any(p.suffix == ".3mf" for p in tmp_path.iterdir())


def test_utensil_bin_cli_validation_failure_returns_non_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """Utensil-bin CLI should return non-zero with an actionable message on invalid input."""
    exit_code = main.main(["utensil-bin", "--grid-x", "0"])
    output = capsys.readouterr()

    assert exit_code == 2
    assert "grid_x" in output.out


def test_utensil_bin_cli_missing_directory_returns_non_zero(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Utensil-bin CLI should fail when the output directory does not exist."""
    output_file = tmp_path / "missing" / "out.stl"
    exit_code = main.main(["utensil-bin", "--output", str(output_file)])
    output = capsys.readouterr()

    assert exit_code == 2
    assert "Output directory does not exist" in output.out


def test_utensil_bin_cli_bed_overflow_warns_but_exits_zero(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Bed overflow should emit a warning to stderr but still export and exit zero."""
    monkeypatch.setattr(main, "create_utensil_bin", lambda _: object())
    monkeypatch.setattr(main, "export_bin", lambda _part, path: (path.touch(), path)[1])

    output_file = tmp_path / "big.stl"
    # grid-x=5 → 210 mm footprint, bed-x=200 mm → overflow
    exit_code = main.main([
        "utensil-bin",
        "--grid-x", "5",
        "--bed-x", "200",
        "--bed-y", "200",
        "--output", str(output_file),
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output_file.exists()
    assert "Warning" in captured.err
