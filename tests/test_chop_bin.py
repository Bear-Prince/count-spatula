import pytest
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Location,
    Mode,
    RectangleRounded,
    add,
    extrude,
)
from gridfinity_build123d import BaseEqual

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


def _region_volume(solid: object, center: tuple, size: tuple) -> float:
    """Return the volume of `solid` inside an axis-aligned probe box."""
    with BuildPart() as probe:
        with BuildPart(Location(center)):
            Box(*size)
        add(solid, mode=Mode.INTERSECT)
    return probe.part.volume if probe.part else 0.0


def _build_uncut_ring(params: BinParameters) -> object:
    """Build the bin base and pocket walls without the side cutouts, as a reference."""
    with BuildPart() as ring:
        add(BaseEqual(grid_x=params.grid_width_units, grid_y=params.grid_length_units, mode=Mode.ADD))
        with BuildSketch(ring.faces().sort_by(Axis.Z)[-1]) as sketch:
            RectangleRounded(
                height=params.grid_length_units * GRIDFINITY_PITCH_MM,
                width=params.grid_width_units * GRIDFINITY_PITCH_MM,
                radius=params.base_corner_radius_mm,
                align=(Align.CENTER, Align.CENTER),
            )
            RectangleRounded(
                height=params.chop_length_mm,
                width=params.chop_width_mm,
                radius=params.chop_corner_radius_mm,
                mode=Mode.SUBTRACT,
                align=(Align.CENTER, Align.CENTER),
            )
        extrude(to_extrude=sketch.face(), amount=params.bin_height_mm)
    return ring.part


@pytest.fixture(scope="module")
def default_cut_and_reference() -> tuple:
    """Build the default cut bin and an equivalent uncut ring once for the cutout tests."""
    params = BinParameters()
    return create_chop_bin(params), _build_uncut_ring(params)


# Probe boxes for the default 4 (X) x 6 (Y) bin: the base slab and the upper half of each
# long wall (which sit at X = +/-84). These pin down where the side cutout removes material.
_BASE_BOX = ((0.0, 0.0, -2.0), (180.0, 260.0, 4.0))
_LEFT_WALL_BOX = ((-79.0, 0.0, 40.0), (12.0, 260.0, 30.0))
_RIGHT_WALL_BOX = ((79.0, 0.0, 40.0), (12.0, 260.0, 30.0))


def test_side_cutout_leaves_base_intact(default_cut_and_reference: tuple) -> None:
    """The side cutout must not remove any material from the Gridfinity base slab."""
    cut, uncut = default_cut_and_reference
    assert abs(_region_volume(cut, *_BASE_BOX) - _region_volume(uncut, *_BASE_BOX)) < 1.0


def test_side_cutout_removes_material_from_walls(default_cut_and_reference: tuple) -> None:
    """The side cutout must remove material from the side walls, not leave them solid."""
    cut, uncut = default_cut_and_reference
    removed = _region_volume(uncut, *_LEFT_WALL_BOX) - _region_volume(cut, *_LEFT_WALL_BOX)
    assert removed > 1000.0, f"Expected the side wall to be slotted, only {removed:.1f} mm^3 removed"


def test_side_cutout_is_symmetric(default_cut_and_reference: tuple) -> None:
    """Both long walls must receive an identical cutout (no per-face orientation flip)."""
    cut, _ = default_cut_and_reference
    left = _region_volume(cut, *_LEFT_WALL_BOX)
    right = _region_volume(cut, *_RIGHT_WALL_BOX)
    assert abs(left - right) < 1.0, f"Cutout asymmetric: left {left:.1f} vs right {right:.1f}"
