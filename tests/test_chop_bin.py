from chop_bin import BASE_LENGTH, BASE_WIDTH, CHOP_HEIGHT, BinParameters, ChopBin, create_chop_bin


def test_chop_bin_creation() -> None:
    """Test that ChopBin can be instantiated and has valid geometry."""
    # Instantiate the bin
    bin_obj = ChopBin(height=CHOP_HEIGHT)

    # 1. Validity Check
    assert bin_obj is not None
    assert bin_obj.volume > 0

    # 2. Bounding Box Check
    bbox = bin_obj.bounding_box()

    # Gridfinity units are typically 42mm
    # We expect some tolerance, but roughly:
    expected_width_mm = BASE_WIDTH * 42
    expected_length_mm = BASE_LENGTH * 42
    expected_height_mm = CHOP_HEIGHT

    # Check dimensions (allowing for small float differences or fit tolerances)
    # Using a 1mm tolerance for safety, can be tightened later
    assert abs(bbox.size.X - expected_width_mm) < 1.0, f"Width {bbox.size.X} mismatch"
    assert abs(bbox.size.Y - expected_length_mm) < 1.0, f"Length {bbox.size.Y} mismatch"
    # The bin might be slightly taller/shorter due to base features, but let's check roughly
    assert abs(bbox.size.Z - expected_height_mm) < 5.0, f"Height {bbox.size.Z} mismatch"


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

    assert abs(bbox.size.X - (3 * 42)) < 1.0
    assert abs(bbox.size.Y - (5 * 42)) < 1.0
