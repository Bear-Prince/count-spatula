import pytest
from build123d import Box, BuildPart, Location, Mode, add

from cutlery_bin import (
    GRIDFINITY_PITCH_MM,
    BinParameters,
    create_cutlery_bin,
    create_kitchen_bin,
    preset_names,
    resolve_preset,
)


def _region_volume(solid: object, center: tuple, size: tuple) -> float:
    """Return the volume of `solid` inside an axis-aligned probe box."""
    with BuildPart() as probe:
        with BuildPart(Location(center)):
            Box(*size)
        add(solid, mode=Mode.INTERSECT)
    return probe.part.volume if probe.part else 0.0


# Probe boxes for the default 4 (X) x 6 (Y) bin: base slab, the upper half of each long wall (at
# X = +/-84), a band below the inner floor, and the central/end of a div=2 divider (at X = 0).
_BASE_BOX = ((0.0, 0.0, -2.0), (180.0, 260.0, 4.0))
_LEFT_WALL_BOX = ((-79.0, 0.0, 40.0), (12.0, 260.0, 30.0))
_RIGHT_WALL_BOX = ((79.0, 0.0, 40.0), (12.0, 260.0, 30.0))
_BELOW_FLOOR_BOX = ((0.0, 0.0, 1.5), (180.0, 260.0, 4.0))
_DIVIDER_MID_BOX = ((0.0, 0.0, 40.0), (8.0, 40.0, 30.0))
_DIVIDER_END_BOX = ((0.0, 100.0, 40.0), (8.0, 30.0, 30.0))


@pytest.fixture(scope="module")
def bins() -> dict:
    """Build the reference bins once for the whole module (geometry builds are slow)."""
    return {
        "kitchen": create_kitchen_bin(),
        "kitchen_solid": create_kitchen_bin(BinParameters(cutouts_enabled=False)),
        "chop_preset": create_kitchen_bin(resolve_preset("chop-board")),
        "cutlery1": create_cutlery_bin(BinParameters(divisions=1)),
        "cutlery3": create_cutlery_bin(BinParameters(divisions=3)),
        "cutlery2": create_cutlery_bin(BinParameters(divisions=2)),
        "cutlery2_solid": create_cutlery_bin(BinParameters(divisions=2, cutouts_enabled=False)),
    }


def test_kitchen_bin_builds_with_expected_footprint(bins: dict) -> None:
    """A default KitchenBin has positive volume and the expected outer footprint."""
    kb = bins["kitchen"]
    assert kb.volume > 0
    bbox = kb.bounding_box()
    assert abs(bbox.size.X - 4 * GRIDFINITY_PITCH_MM) < 1.0
    assert abs(bbox.size.Y - 6 * GRIDFINITY_PITCH_MM) < 1.0


def test_chop_board_preset_matches_default(bins: dict) -> None:
    """The chop-board preset reproduces the default KitchenBin geometry."""
    assert abs(bins["chop_preset"].volume - bins["kitchen"].volume) < 1e-6


def test_cutlery_with_one_division_matches_kitchen(bins: dict) -> None:
    """A CutleryBin with a single division is geometrically a plain KitchenBin."""
    assert abs(bins["cutlery1"].volume - bins["kitchen"].volume) < 1.0


def test_cutlery_with_three_divisions_adds_material(bins: dict) -> None:
    """Adding dividers adds material relative to an undivided bin."""
    assert bins["cutlery3"].volume > bins["kitchen"].volume


def test_disabling_cutouts_leaves_more_material(bins: dict) -> None:
    """A bin without cutouts uses more material but keeps the same footprint."""
    kb, solid = bins["kitchen"], bins["kitchen_solid"]
    assert solid.volume > kb.volume
    assert abs(solid.bounding_box().size.X - kb.bounding_box().size.X) < 1.0


def test_side_cutout_leaves_base_intact(bins: dict) -> None:
    """The side cutout removes no material from the Gridfinity base slab."""
    cut, solid = bins["kitchen"], bins["kitchen_solid"]
    assert abs(_region_volume(cut, *_BASE_BOX) - _region_volume(solid, *_BASE_BOX)) < 1.0


def test_side_cutout_starts_at_inner_floor(bins: dict) -> None:
    """The side cutout begins at the inner floor and does not cut the base below it."""
    cut, solid = bins["kitchen"], bins["kitchen_solid"]
    assert abs(_region_volume(cut, *_BELOW_FLOOR_BOX) - _region_volume(solid, *_BELOW_FLOOR_BOX)) < 1.0


def test_side_cutout_removes_material_from_walls(bins: dict) -> None:
    """The side cutout removes material from the side walls."""
    cut, solid = bins["kitchen"], bins["kitchen_solid"]
    removed = _region_volume(solid, *_LEFT_WALL_BOX) - _region_volume(cut, *_LEFT_WALL_BOX)
    assert removed > 1000.0, f"Expected the side wall to be slotted, only {removed:.1f} mm^3 removed"


def test_side_cutout_is_symmetric(bins: dict) -> None:
    """Both long walls receive an identical cutout."""
    cut = bins["kitchen"]
    left = _region_volume(cut, *_LEFT_WALL_BOX)
    right = _region_volume(cut, *_RIGHT_WALL_BOX)
    assert abs(left - right) < 1.0, f"Cutout asymmetric: left {left:.1f} vs right {right:.1f}"


def test_cutout_passes_through_divider(bins: dict) -> None:
    """With cutouts on, the slot removes material from the divider's central band."""
    cut, solid = bins["cutlery2"], bins["cutlery2_solid"]
    removed = _region_volume(solid, *_DIVIDER_MID_BOX) - _region_volume(cut, *_DIVIDER_MID_BOX)
    assert removed > 100.0, f"Expected the slot to pass through the divider, only {removed:.1f} mm^3 removed"


def test_divider_stays_attached_at_ends(bins: dict) -> None:
    """The divider ends (outside the cutout band) remain present with cutouts on."""
    cut = bins["cutlery2"]
    assert _region_volume(cut, *_DIVIDER_END_BOX) > 100.0


def test_validation_rejects_out_of_range_grid() -> None:
    """Validation reports an out-of-range grid size."""
    with pytest.raises(ValueError, match="grid_x"):
        BinParameters(grid_x=0).validate()


def test_validation_rejects_oversized_pocket() -> None:
    """Validation rejects a pocket that does not fit the footprint."""
    with pytest.raises(ValueError, match="pocket_width_mm must be smaller"):
        BinParameters(pocket_width_mm=10_000).validate()


def test_validation_rejects_invalid_divisions() -> None:
    """Validation rejects a division count below 1."""
    with pytest.raises(ValueError, match="divisions"):
        BinParameters(divisions=0).validate()


def test_validation_skips_cutout_checks_when_disabled() -> None:
    """Cutout-fit checks are skipped when cutouts are disabled."""
    BinParameters(cutout_offset_from_edge_mm=1, cutout_radius_mm=600, cutouts_enabled=False).validate()


def test_resolve_unknown_preset_raises() -> None:
    """An unknown preset name raises with the available names listed."""
    assert "chop-board" in preset_names()
    with pytest.raises(ValueError, match="Unknown preset"):
        resolve_preset("does-not-exist")
