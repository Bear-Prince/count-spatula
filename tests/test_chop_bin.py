from chop_bin import BASE_LENGTH, BASE_WIDTH, GRIDFINITY_PITCH_MM, BinParameters, create_chop_bin


def test_chop_bin_creation() -> None:
    """Test that ChopBin can be instantiated via the public factory and has valid geometry."""
    bin_obj = create_chop_bin()

    assert bin_obj is not None
    assert bin_obj.volume > 0

    bbox = bin_obj.bounding_box()
    defaults = BinParameters()

    assert abs(bbox.size.X - BASE_WIDTH * GRIDFINITY_PITCH_MM) < 1.0, f"Width {bbox.size.X} mismatch"
    assert abs(bbox.size.Y - BASE_LENGTH * GRIDFINITY_PITCH_MM) < 1.0, f"Length {bbox.size.Y} mismatch"
    assert abs(bbox.size.Z - defaults.bin_height_mm) < 5.0, f"Height {bbox.size.Z} mismatch"


def test_create_chop_bin_uses_default_parameters() -> None:
    """Default helper path should produce a valid part."""
    part = create_chop_bin()
    assert part.volume > 0


def test_create_chop_bin_with_explicit_parameters() -> None:
    """Explicitly provided parameters should create geometry at the requested scale."""
    params = BinParameters(
        grid_length_units=5,
        grid_width_units=3,
        bin_height_mm=50,
        chop_length_mm=190,
        chop_width_mm=110,
    )
    part = create_chop_bin(params)
    bbox = part.bounding_box()

    assert abs(bbox.size.X - (3 * GRIDFINITY_PITCH_MM)) < 1.0
    assert abs(bbox.size.Y - (5 * GRIDFINITY_PITCH_MM)) < 1.0
