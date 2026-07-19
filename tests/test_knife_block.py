import pytest
from build123d import Box, BuildPart, Location, Mode, add

from cutlery_bin import GRIDFINITY_CLEARANCE_MM, GRIDFINITY_PITCH_MM
from knife_block import (
    MIN_HANDLE_GAP_MM,
    KnifeBlockParameters,
    check_drawer_clearance,
    create_knife_blade_block,
)


def _region_volume(solid: object, center: tuple, size: tuple) -> float:
    """Return the volume of `solid` inside an axis-aligned probe box (mirrors the cutlery_bin helper)."""
    with BuildPart() as probe:
        with BuildPart(Location(center)):
            Box(*size)
        add(solid, mode=Mode.INTERSECT)
    return probe.part.volume if probe.part else 0.0


def _wedge_depth_for_thickness(params: KnifeBlockParameters, thickness: float) -> float:
    """Return the depth at which a blade of this thickness should wedge in the taper.

    Independent re-derivation of the taper geometry (not a call into production code), used as an
    oracle the way ``_start_grid_line_overshoot`` re-derives the cutout offset in test_cutlery_bin.py.
    """
    mouth, apex = params.slot_mouth_width_mm, params.slot_apex_width_mm
    fraction = (mouth - thickness) / (mouth - apex)
    return fraction * params.taper_depth_mm


# Default-block geometry, computed from KnifeBlockParameters() and confirmed by direct inspection:
# floor_z ~= 0, top_z == deck_height_mm == 18.0, lane centres at -54/-36/-18/0/18/36/54 (18 mm pitch).
_TOP_Z = 18.0
_LANE0_X = -54.0
_MID_BETWEEN_LANES_X = -45.0  # halfway between lane 0 (-54) and lane 1 (-36)
_NEAR_MOUTH_Z = _TOP_Z - 1.0
_RELIEF_MID_Z = _TOP_Z - (12.0 + 3.0 / 2)  # taper_depth_mm + relief_depth_mm / 2
_DECK_MID_Z = 3.0 / 2  # min_deck_thickness_mm / 2, measured from floor_z ~= 0


@pytest.fixture(scope="module")
def knife_blocks() -> dict:
    """Build the reference knife blocks once for the whole module (geometry builds are slow)."""
    return {
        "default": create_knife_blade_block(),
        "custom": create_knife_blade_block(KnifeBlockParameters(knife_count=3, grid_x=2)),
    }


@pytest.mark.scenario("knife-blade-block", "Pitch derives from handle width and gap")
def test_default_lane_pitch_is_eighteen_mm() -> None:
    """The default handle width and gap give an 18 mm lane pitch."""
    params = KnifeBlockParameters()
    assert params.lane_pitch_mm == pytest.approx(18.0)


@pytest.mark.scenario("knife-blade-block", "Seven-lane default spans three units")
def test_default_seven_lanes_span_three_gridfinity_units() -> None:
    """Seven lanes at the default 18 mm pitch nominally span 126 mm -- three Gridfinity units."""
    params = KnifeBlockParameters()
    assert params.knife_count * params.lane_pitch_mm == pytest.approx(3 * GRIDFINITY_PITCH_MM)
    assert params.grid_x == 3


@pytest.mark.scenario("knife-blade-block", "Deck height is exposed for blank matching")
def test_deck_height_is_taper_plus_relief_plus_min_deck() -> None:
    """The exposed deck height sums the taper, relief, and minimum solid deck below it."""
    params = KnifeBlockParameters()
    assert params.deck_height_mm == pytest.approx(
        params.taper_depth_mm + params.relief_depth_mm + params.min_deck_thickness_mm
    )


def test_default_footprint_matches_gridfinity_convention() -> None:
    """The default footprint follows the Gridfinity N*42 - 0.5 convention."""
    params = KnifeBlockParameters()
    assert params.footprint_width_mm == pytest.approx(3 * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM)
    assert params.footprint_length_mm == pytest.approx(2 * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM)


def test_default_parameters_validate_cleanly() -> None:
    """The default parameter set is valid as-is."""
    KnifeBlockParameters().validate()


@pytest.mark.scenario("knife-blade-block", "Reject an invalid lane count")
def test_validation_rejects_zero_knife_count() -> None:
    """A lane count below one is rejected."""
    with pytest.raises(ValueError, match="knife_count must be at least 1"):
        KnifeBlockParameters(knife_count=0).validate()


@pytest.mark.scenario("knife-blade-block", "Reject a pitch that cannot clear the handles")
def test_validation_rejects_handle_gap_below_minimum() -> None:
    """A handle gap below the minimum finger clearance is rejected."""
    with pytest.raises(ValueError, match="handle_gap_mm must be at least"):
        KnifeBlockParameters(handle_gap_mm=MIN_HANDLE_GAP_MM / 2).validate()


def test_validation_rejects_out_of_range_grid() -> None:
    """Grid dimensions outside 1-12 are rejected."""
    with pytest.raises(ValueError, match="grid_x"):
        KnifeBlockParameters(grid_x=0).validate()
    with pytest.raises(ValueError, match="grid_y"):
        KnifeBlockParameters(grid_y=13).validate()


def test_validation_rejects_non_positive_handle_width() -> None:
    """A non-positive handle width is rejected."""
    with pytest.raises(ValueError, match="handle_width_mm must be greater than 0"):
        KnifeBlockParameters(handle_width_mm=0.0).validate()


def test_validation_rejects_non_positive_spines() -> None:
    """A non-positive max or min spine thickness is rejected, independent of the min-vs-max check."""
    with pytest.raises(ValueError, match="max_spine_mm must be greater than 0"):
        KnifeBlockParameters(max_spine_mm=0.0).validate()
    with pytest.raises(ValueError, match="min_spine_mm must be greater than 0"):
        KnifeBlockParameters(min_spine_mm=0.0).validate()


def test_validation_rejects_min_spine_above_max_spine() -> None:
    """min_spine_mm greater than max_spine_mm is a contradictory range and is rejected."""
    with pytest.raises(ValueError, match="min_spine_mm must not exceed max_spine_mm"):
        KnifeBlockParameters(min_spine_mm=5.0, max_spine_mm=3.0).validate()


def test_validation_rejects_non_positive_apex_clearance() -> None:
    """An apex clearance that does not exceed zero is rejected directly, before the width check."""
    with pytest.raises(ValueError, match="slot_apex_clearance_mm must be greater than 0"):
        KnifeBlockParameters(slot_apex_clearance_mm=0.0).validate()


@pytest.mark.scenario("knife-blade-block", "Reject a slot too narrow for the blade spine")
def test_validation_rejects_non_positive_mouth_clearance() -> None:
    """A slot mouth clearance that does not exceed zero cannot admit the thickest supported spine."""
    with pytest.raises(ValueError, match="slot_mouth_clearance_mm must be greater than 0"):
        KnifeBlockParameters(slot_mouth_clearance_mm=0.0).validate()


@pytest.mark.scenario("knife-blade-block", "Reject a slot too narrow for the blade spine")
def test_validation_rejects_apex_clearance_that_closes_the_relief() -> None:
    """An apex clearance that leaves a non-positive relief width is rejected."""
    with pytest.raises(ValueError, match="slot_apex_width_mm must be greater than 0"):
        KnifeBlockParameters(min_spine_mm=1.0, slot_apex_clearance_mm=2.0).validate()


def test_validation_rejects_non_positive_taper_and_relief_depths() -> None:
    """Non-positive taper or relief depths are rejected."""
    with pytest.raises(ValueError, match="taper_depth_mm must be greater than 0"):
        KnifeBlockParameters(taper_depth_mm=0.0).validate()
    with pytest.raises(ValueError, match="relief_depth_mm must be greater than 0"):
        KnifeBlockParameters(relief_depth_mm=0.0).validate()


def test_validation_rejects_non_positive_min_deck_thickness() -> None:
    """A non-positive minimum deck thickness is rejected."""
    with pytest.raises(ValueError, match="min_deck_thickness_mm must be greater than 0"):
        KnifeBlockParameters(min_deck_thickness_mm=0.0).validate()


def test_validation_rejects_negative_lane_margin() -> None:
    """A negative lane margin is rejected."""
    with pytest.raises(ValueError, match="lane_margin_mm must be at least 0"):
        KnifeBlockParameters(lane_margin_mm=-1.0).validate()


def test_validation_rejects_too_many_lanes_for_the_footprint() -> None:
    """Too many lanes for the chosen grid_x width is rejected with an actionable message."""
    with pytest.raises(ValueError, match="too narrow for 7 lanes"):
        KnifeBlockParameters(grid_x=1).validate()


@pytest.mark.scenario("knife-blade-block", "Generate a block from valid parameters")
def test_default_block_is_a_valid_watertight_solid(knife_blocks: dict) -> None:
    """A default KnifeBladeBlock is a single valid solid."""
    assert knife_blocks["default"].is_valid()


def test_custom_params_produce_a_smaller_valid_block(knife_blocks: dict) -> None:
    """Passing explicit KnifeBlockParameters (not the None-default) builds a correctly sized block."""
    custom = knife_blocks["custom"]
    assert custom.is_valid()
    bbox = custom.bounding_box()
    assert abs(bbox.size.X - (2 * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM)) < 0.1


@pytest.mark.scenario("knife-blade-block", "Base is a standard Gridfinity footprint")
@pytest.mark.scenario("knife-blade-block", "Only the block is produced")
def test_default_block_footprint_matches_gridfinity_convention(knife_blocks: dict) -> None:
    """The block's outer footprint follows the Gridfinity clearance convention.

    Also claims "Only the block is produced": the bounding box matching the block's own footprint
    exactly, with no extra length, confirms nothing beyond the slotted block itself is generated (no
    handle-zone deck).
    """
    bbox = knife_blocks["default"].bounding_box()
    params = KnifeBlockParameters()
    assert abs(bbox.size.X - params.footprint_width_mm) < 0.1
    assert abs(bbox.size.Y - params.footprint_length_mm) < 0.1


@pytest.mark.scenario("knife-blade-block", "Default block fits a typical bed")
def test_default_block_prints_without_splitting(knife_blocks: dict) -> None:
    """The default block's footprint fits within a typical 220x220 mm bed with no splitting."""
    bbox = knife_blocks["default"].bounding_box()
    assert bbox.size.X < 220.0
    assert bbox.size.Y < 220.0


def test_lane_mouth_is_open_and_between_lanes_is_solid(knife_blocks: dict) -> None:
    """Near the top, a lane's mouth is open while the material between two lanes is solid."""
    block = knife_blocks["default"]
    open_at_lane = _region_volume(block, (_LANE0_X, 0, _NEAR_MOUTH_Z), (2.0, 5.0, 0.5))
    solid_between = _region_volume(block, (_MID_BETWEEN_LANES_X, 0, _NEAR_MOUTH_Z), (2.0, 5.0, 0.5))
    assert open_at_lane < 0.01, f"expected the lane mouth to be open, found {open_at_lane:.4f} mm^3"
    assert solid_between > 4.0, f"expected solid material between lanes, found {solid_between:.4f} mm^3"


def test_deck_below_relief_is_solid(knife_blocks: dict) -> None:
    """The minimum deck thickness below the relief channel remains solid, for structural strength."""
    vol = _region_volume(knife_blocks["default"], (_LANE0_X, 0, _DECK_MID_Z), (2.0, 5.0, 0.5))
    assert vol > 4.0, f"expected the deck below the relief to be solid, found {vol:.4f} mm^3"


@pytest.mark.scenario("knife-blade-block", "Cutting edge does not bottom out")
def test_relief_channel_is_open(knife_blocks: dict) -> None:
    """The relief channel is fully open, so a blade's cutting edge floats clear of the block."""
    params = KnifeBlockParameters()
    vol = _region_volume(
        knife_blocks["default"],
        (_LANE0_X, 0, _RELIEF_MID_Z),
        (params.slot_apex_width_mm * 0.9, 5.0, params.relief_depth_mm * 0.8),
    )
    assert vol < 0.01, f"expected the relief channel to be fully open, found {vol:.4f} mm^3"


@pytest.mark.scenario("knife-blade-block", "Thick and thin blades both centre")
def test_thick_and_thin_blade_proxies_fit_without_collision(knife_blocks: dict) -> None:
    """A blade proxy at the thickness-appropriate wedge depth sits in pure void, for both extremes."""
    block = knife_blocks["default"]
    params = KnifeBlockParameters()
    for thickness in (params.max_spine_mm, params.min_spine_mm):
        depth = _wedge_depth_for_thickness(params, thickness)
        z = _TOP_Z - depth
        vol = _region_volume(block, (_LANE0_X, 0, z), (thickness * 0.98, 5.0, 0.05))
        assert vol < 0.01, f"{thickness} mm blade proxy unexpectedly collides with solid ({vol:.4f} mm^3)"


@pytest.mark.scenario("knife-blade-block", "Each lane accepts a blade facing either direction")
def test_lane_mouth_is_symmetric_along_the_length(knife_blocks: dict) -> None:
    """A lane's mouth is equally open near both ends, so a blade can face either direction."""
    block = knife_blocks["default"]
    params = KnifeBlockParameters()
    y_offset = params.footprint_length_mm / 2 - 5.0
    near_positive_end = _region_volume(block, (_LANE0_X, y_offset, _NEAR_MOUTH_Z), (2.0, 2.0, 0.5))
    near_negative_end = _region_volume(block, (_LANE0_X, -y_offset, _NEAR_MOUTH_Z), (2.0, 2.0, 0.5))
    assert near_positive_end < 0.01
    assert near_negative_end < 0.01


@pytest.mark.scenario("knife-blade-block", "One block spans all lanes")
def test_default_block_has_seven_open_lanes(knife_blocks: dict) -> None:
    """All seven default lanes are open at the mouth within the same single block."""
    block = knife_blocks["default"]
    params = KnifeBlockParameters()
    lane_span = (params.knife_count - 1) * params.lane_pitch_mm
    lane_start = -lane_span / 2
    for index in range(params.knife_count):
        lane_x = lane_start + index * params.lane_pitch_mm
        vol = _region_volume(block, (lane_x, 0, _NEAR_MOUTH_Z), (2.0, 5.0, 0.5))
        assert vol < 0.01, f"lane {index} at x={lane_x} is not open ({vol:.4f} mm^3)"


@pytest.mark.scenario("knife-blade-block", "No warning when everything clears")
def test_check_drawer_clearance_fits() -> None:
    """An occupied height within the drawer's internal height yields no warning."""
    assert check_drawer_clearance(18.0, 65.0, 8.0, 100.0) == []


@pytest.mark.scenario("knife-blade-block", "Warn when the tallest knife will not clear the drawer")
def test_check_drawer_clearance_warns_when_too_tall() -> None:
    """An occupied height exceeding the drawer's internal height warns, naming the overage."""
    warnings = check_drawer_clearance(18.0, 65.0, 8.0, 78.0)
    assert len(warnings) == 1
    assert "78.0" in warnings[0]
    assert "13.0" in warnings[0]
