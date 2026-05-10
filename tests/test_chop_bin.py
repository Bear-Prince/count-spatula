from build123d import Axis
from chop_bin import ChopBin, CHOP_HEIGHT, BASE_LENGTH, BASE_WIDTH

def test_chop_bin_creation():
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
