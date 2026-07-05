from dataclasses import replace

import pytest
from build123d import Box, BuildPart, Location, Mode, add
from gridfinity_build123d import BaseEqual

from cutlery_bin import (
    GRIDFINITY_CLEARANCE_MM,
    GRIDFINITY_PITCH_MM,
    BinParameters,
    KitchenBin,
    check_print_bed,
    create_cutlery_bin,
    create_kitchen_bin,
    preset_names,
    resolve_preset,
)


def _base_footprint(grid_x: int, grid_y: int) -> tuple:
    """Return the (X, Y) footprint of a bare Gridfinity BaseEqual of the given grid."""
    with BuildPart() as base:
        add(BaseEqual(grid_x=grid_x, grid_y=grid_y, mode=Mode.ADD))
    bbox = base.part.bounding_box()
    return bbox.size.X, bbox.size.Y


def _region_volume(solid: object, center: tuple, size: tuple) -> float:
    """Return the volume of `solid` inside an axis-aligned probe box."""
    with BuildPart() as probe:
        with BuildPart(Location(center)):
            Box(*size)
        add(solid, mode=Mode.INTERSECT)
    return probe.part.volume if probe.part else 0.0


# Probe boxes for the chop-board frame (4 (X) x 6 (Y)): base slab, the upper half of each long wall
# (at X = +/-84), a band below the inner floor, and the central/end of a div=2 divider (at X = 0).
_BASE_BOX = ((0.0, 0.0, -2.0), (180.0, 260.0, 4.0))
_LEFT_WALL_BOX = ((-79.0, 0.0, 40.0), (12.0, 260.0, 30.0))
_RIGHT_WALL_BOX = ((79.0, 0.0, 40.0), (12.0, 260.0, 30.0))
_BELOW_FLOOR_BOX = ((0.0, 0.0, 1.5), (180.0, 260.0, 4.0))
_DIVIDER_MID_BOX = ((0.0, 0.0, 40.0), (8.0, 40.0, 30.0))
_DIVIDER_END_BOX = ((0.0, 100.0, 40.0), (8.0, 30.0, 30.0))

# Probe boxes for wave dividers on the default 2x4 grid (pocket 79.5 (X) x 163.5 (Y); div=3 puts the
# two divider centrelines at X = -/+13.25 with column pitch 26.5). The sine swings fully at Y = -L/4
# (= -40.875): with amplitude 4 mm the two dividers move to X = -9.25 and +9.25 (both toward centre),
# and away from X = -17.25 / +17.25. Near the ends the offset returns to ~0, so the dividers sit on
# their nominal centrelines.
_W_END_LEFT_BOX = ((-13.25, 78.0, 40.0), (4.0, 6.0, 30.0))
_W_END_RIGHT_BOX = ((13.25, 78.0, 40.0), (4.0, 6.0, 30.0))
_W_SWING_INNER_L_BOX = ((-9.25, -40.875, 40.0), (2.0, 6.0, 30.0))
_W_SWING_INNER_R_BOX = ((9.25, -40.875, 40.0), (2.0, 6.0, 30.0))
_W_SWING_OUTER_L_BOX = ((-17.25, -40.875, 40.0), (2.0, 6.0, 30.0))
_W_SWING_OUTER_R_BOX = ((17.25, -40.875, 40.0), (2.0, 6.0, 30.0))
_W_CUT_MID_BOX = ((-13.25, 0.0, 40.0), (6.0, 30.0, 30.0))
# A sub-floor probe at a divider centreline (floor_z ~ 3.9, base bottom ~ -3.9): spans Z -3.5..3.5,
# inside the base where the Gridfinity grooves live. A correctly-placed divider adds nothing here.
_W_SUBFLOOR_BOX = ((-13.25, 0.0, 0.0), (4.0, 40.0, 7.0))


@pytest.fixture(scope="module")
def bins() -> dict:
    """Build the reference bins once for the whole module (geometry builds are slow)."""
    chop = resolve_preset("chop-board")
    return {
        "default": create_kitchen_bin(),
        "default_solid": create_kitchen_bin(BinParameters(cutouts_enabled=False)),
        "cutlery_default1": create_cutlery_bin(BinParameters(divisions=1)),
        "cutlery_default3": create_cutlery_bin(BinParameters(divisions=3)),
        "cutlery_straight3": create_cutlery_bin(BinParameters(divisions=3, divider_profile="straight")),
        "cutlery_wave3_solid": create_cutlery_bin(
            BinParameters(divisions=3, divider_profile="wave", divider_amplitude_mm=4.0, cutouts_enabled=False)
        ),
        "cutlery_wave3_cut": create_cutlery_bin(
            BinParameters(divisions=3, divider_profile="wave", divider_amplitude_mm=4.0)
        ),
        "chop": create_kitchen_bin(chop),
        "chop_solid": create_kitchen_bin(replace(chop, cutouts_enabled=False)),
        "cutlery_chop2": create_cutlery_bin(replace(chop, divisions=2)),
        "cutlery_chop2_solid": create_cutlery_bin(replace(chop, divisions=2, cutouts_enabled=False)),
    }


@pytest.mark.scenario("gridfinity-utensil-bin", "Default pocket derived from wall thickness")
def test_default_is_a_2x4_thin_walled_bin() -> None:
    """The default bin is a 2x4 with 2 mm walls -- not the chop dimensions (parameter-level)."""
    params = BinParameters()
    assert (params.grid_x, params.grid_y) == (2, 4)
    assert params.height_in_units == 8
    # Pocket = the clearanced outer footprint (N*42 - 0.5) inset by 2 mm walls on each side.
    assert params.effective_pocket_width_mm == pytest.approx(2 * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM - 4)
    assert params.effective_pocket_length_mm == pytest.approx(4 * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM - 4)


@pytest.mark.scenario("gridfinity-utensil-bin", "Generate geometry from defaults")
@pytest.mark.scenario("gridfinity-utensil-bin", "Footprint applies the GridFinity clearance")
def test_default_kitchen_footprint(bins: dict) -> None:
    """A default KitchenBin has the 2x4 outer footprint with the GridFinity 0.5 mm clearance."""
    bbox = bins["default"].bounding_box()
    assert abs(bbox.size.X - (2 * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM)) < 0.1
    assert abs(bbox.size.Y - (4 * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM)) < 0.1


@pytest.mark.scenario("gridfinity-utensil-bin", "Walls sit flush on the base")
def test_wall_outline_matches_base_footprint(bins: dict) -> None:
    """The bin's outer footprint matches the Gridfinity base it sits on (no overhang)."""
    base_x, base_y = _base_footprint(2, 4)
    bbox = bins["default"].bounding_box()
    assert abs(bbox.size.X - base_x) < 0.2
    assert abs(bbox.size.Y - base_y) < 0.2


def test_kitchen_bin_mode_subtract_combines_into_enclosing_part() -> None:
    """Building a KitchenBin with mode=Mode.SUBTRACT inside an enclosing part combines correctly.

    `mode` controls how the finished bin combines into an enclosing BuildPart context; it must not
    also be forwarded to the bin's own internal BuildPart, or the internal Gridfinity base ends up
    being added into an otherwise-empty internal part with nothing left to subtract from.
    """
    with BuildPart() as enclosing:
        Box(200, 200, 200)
        KitchenBin(BinParameters(), mode=Mode.SUBTRACT)
    assert 0 < enclosing.part.volume < 200**3


@pytest.mark.scenario("gridfinity-utensil-bin", "Generate a KitchenBin from explicit valid parameters")
@pytest.mark.scenario("gridfinity-utensil-bin", "Explicit pocket with non-uniform walls")
@pytest.mark.scenario("bin-presets", "Generate a bin from a preset")
def test_chop_board_preset_reproduces_chop_bin(bins: dict) -> None:
    """The chop-board preset is the 4x6 chop bin, distinct from the default."""
    chop_bbox = bins["chop"].bounding_box()
    assert abs(chop_bbox.size.X - (4 * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM)) < 0.1
    assert abs(chop_bbox.size.Y - (6 * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM)) < 0.1
    assert bins["chop"].volume != pytest.approx(bins["default"].volume)
    chop = resolve_preset("chop-board")
    assert (chop.pocket_width_mm, chop.pocket_length_mm) == (160, 220)


@pytest.mark.scenario("gridfinity-utensil-bin", "A single division is a plain KitchenBin pocket")
def test_cutlery_with_one_division_matches_kitchen(bins: dict) -> None:
    """A CutleryBin with a single division is geometrically a plain KitchenBin."""
    assert abs(bins["cutlery_default1"].volume - bins["default"].volume) < 1.0


@pytest.mark.scenario("gridfinity-utensil-bin", "Split the pocket into equal columns")
def test_cutlery_with_three_divisions_adds_material(bins: dict) -> None:
    """Adding dividers adds material relative to an undivided bin."""
    assert bins["cutlery_default3"].volume > bins["default"].volume


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutouts disabled")
def test_disabling_cutouts_leaves_more_material(bins: dict) -> None:
    """A bin without cutouts uses more material but keeps the same footprint."""
    cut, solid = bins["default"], bins["default_solid"]
    assert solid.volume > cut.volume
    assert abs(solid.bounding_box().size.X - cut.bounding_box().size.X) < 1.0


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutouts are symmetric and leave the base intact")
def test_side_cutout_leaves_base_intact(bins: dict) -> None:
    """The side cutout removes no material from the Gridfinity base slab."""
    cut, solid = bins["chop"], bins["chop_solid"]
    assert abs(_region_volume(cut, *_BASE_BOX) - _region_volume(solid, *_BASE_BOX)) < 1.0


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutouts are symmetric and leave the base intact")
def test_side_cutout_starts_at_inner_floor(bins: dict) -> None:
    """The side cutout begins at the inner floor and does not cut the base below it."""
    cut, solid = bins["chop"], bins["chop_solid"]
    assert abs(_region_volume(cut, *_BELOW_FLOOR_BOX) - _region_volume(solid, *_BELOW_FLOOR_BOX)) < 1.0


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutouts enabled by default")
def test_side_cutout_removes_material_from_walls(bins: dict) -> None:
    """The side cutout removes material from the side walls."""
    cut, solid = bins["chop"], bins["chop_solid"]
    removed = _region_volume(solid, *_LEFT_WALL_BOX) - _region_volume(cut, *_LEFT_WALL_BOX)
    assert removed > 1000.0, f"Expected the side wall to be slotted, only {removed:.1f} mm^3 removed"


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutouts are symmetric and leave the base intact")
def test_side_cutout_is_symmetric(bins: dict) -> None:
    """Both long walls receive an identical cutout."""
    cut = bins["chop"]
    left = _region_volume(cut, *_LEFT_WALL_BOX)
    right = _region_volume(cut, *_RIGHT_WALL_BOX)
    assert abs(left - right) < 1.0, f"Cutout asymmetric: left {left:.1f} vs right {right:.1f}"


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutout passes through dividers")
def test_cutout_passes_through_divider(bins: dict) -> None:
    """With cutouts on, the slot removes material from the divider's central band."""
    cut, solid = bins["cutlery_chop2"], bins["cutlery_chop2_solid"]
    removed = _region_volume(solid, *_DIVIDER_MID_BOX) - _region_volume(cut, *_DIVIDER_MID_BOX)
    assert removed > 100.0, f"Expected the slot to pass through the divider, only {removed:.1f} mm^3 removed"


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutout passes through dividers")
def test_divider_stays_attached_at_ends(bins: dict) -> None:
    """The divider ends (outside the cutout band) remain present with cutouts on."""
    assert _region_volume(bins["cutlery_chop2"], *_DIVIDER_END_BOX) > 100.0


@pytest.mark.scenario("gridfinity-utensil-bin", "Default profile preserves straight geometry")
def test_default_profile_matches_straight(bins: dict) -> None:
    """Omitting the divider profile produces the same geometry as the explicit straight profile."""
    assert abs(bins["cutlery_default3"].volume - bins["cutlery_straight3"].volume) < 1.0


@pytest.mark.scenario("gridfinity-utensil-bin", "Wave profile bends the dividers")
def test_wave_profile_adds_dividers_without_changing_footprint(bins: dict) -> None:
    """A wave CutleryBin adds divider material to an undivided bin and keeps the 2x4 footprint."""
    wave, plain = bins["cutlery_wave3_solid"], bins["default_solid"]
    assert wave.volume > plain.volume
    assert abs(wave.bounding_box().size.X - plain.bounding_box().size.X) < 0.5
    assert abs(wave.bounding_box().size.Y - plain.bounding_box().size.Y) < 0.5


@pytest.mark.scenario("gridfinity-utensil-bin", "Wave profile bends the dividers")
def test_wave_dividers_meet_end_walls(bins: dict) -> None:
    """Near the pocket ends a wave divider returns to its nominal centreline and meets both walls."""
    wave = bins["cutlery_wave3_solid"]
    assert _region_volume(wave, *_W_END_LEFT_BOX) > 100.0
    assert _region_volume(wave, *_W_END_RIGHT_BOX) > 100.0


@pytest.mark.scenario("gridfinity-utensil-bin", "Adjacent wave dividers alternate orientation")
def test_adjacent_wave_dividers_alternate(bins: dict) -> None:
    """At full swing the two dividers are phase-mirrored, both pulled toward the centre."""
    wave = bins["cutlery_wave3_solid"]
    # Material is where the mirrored dividers swing inward, and absent where they swing away from.
    assert _region_volume(wave, *_W_SWING_INNER_L_BOX) > 100.0
    assert _region_volume(wave, *_W_SWING_INNER_R_BOX) > 100.0
    assert _region_volume(wave, *_W_SWING_OUTER_L_BOX) < 30.0
    assert _region_volume(wave, *_W_SWING_OUTER_R_BOX) < 30.0


def test_wave_dividers_do_not_intrude_into_base(bins: dict) -> None:
    """Wave dividers rise from the inner floor, adding no material below it (into the base grooves)."""
    wave, plain = bins["cutlery_wave3_solid"], bins["default_solid"]
    below_floor = abs(_region_volume(wave, *_W_SUBFLOOR_BOX) - _region_volume(plain, *_W_SUBFLOOR_BOX))
    assert below_floor < 30.0, f"Wave divider intrudes {below_floor:.1f} mm^3 into the base below the floor"


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutout passes through dividers")
def test_cutout_passes_through_wave_divider(bins: dict) -> None:
    """The side cutout slot still removes material from a wave divider's central band."""
    cut, solid = bins["cutlery_wave3_cut"], bins["cutlery_wave3_solid"]
    removed = _region_volume(solid, *_W_CUT_MID_BOX) - _region_volume(cut, *_W_CUT_MID_BOX)
    assert removed > 100.0, f"Expected the slot to pass through the wave divider, only {removed:.1f} mm^3 removed"


@pytest.mark.scenario("gridfinity-utensil-bin", "Cutout passes through dividers")
def test_wave_divider_stays_attached_at_ends_with_cutout(bins: dict) -> None:
    """With cutouts on, the wave divider's ends (outside the slot band) remain attached."""
    assert _region_volume(bins["cutlery_wave3_cut"], *_W_END_LEFT_BOX) > 100.0


@pytest.mark.scenario("gridfinity-utensil-bin", "Reject out-of-range grid size")
def test_validation_rejects_out_of_range_grid() -> None:
    """Validation reports an out-of-range grid size."""
    with pytest.raises(ValueError, match="grid_x"):
        BinParameters(grid_x=0).validate()


@pytest.mark.scenario("gridfinity-utensil-bin", "Reject a pocket that does not fit")
def test_validation_rejects_oversized_pocket() -> None:
    """Validation rejects an explicit pocket that does not fit the footprint."""
    with pytest.raises(ValueError, match="pocket width must be smaller"):
        BinParameters(pocket_width_mm=10_000).validate()


@pytest.mark.scenario("gridfinity-utensil-bin", "Reject invalid divider count")
def test_validation_rejects_invalid_divisions() -> None:
    """Validation rejects a division count below 1."""
    with pytest.raises(ValueError, match="divisions"):
        BinParameters(divisions=0).validate()


def test_validation_rejects_overlapping_straight_dividers() -> None:
    """A straight divider count too high for the pocket width to leave a printable gap is rejected."""
    with pytest.raises(ValueError, match="divider_thickness_mm is too large"):
        BinParameters(divisions=50).validate()


@pytest.mark.scenario("gridfinity-utensil-bin", "Default profile preserves straight geometry")
def test_divider_profile_defaults_to_straight() -> None:
    """The divider profile defaults to straight with no amplitude, preserving existing behaviour."""
    params = BinParameters()
    assert params.divider_profile == "straight"
    assert params.divider_amplitude_mm == 0.0


def test_validation_rejects_unknown_divider_profile() -> None:
    """Validation rejects a divider profile that is neither straight nor wave."""
    with pytest.raises(ValueError, match="divider_profile"):
        BinParameters(divider_profile="zigzag").validate()


@pytest.mark.scenario("gridfinity-utensil-bin", "Reject a non-positive wave amplitude")
def test_validation_rejects_non_positive_wave_amplitude() -> None:
    """The wave profile requires a positive amplitude."""
    with pytest.raises(ValueError, match="divider_amplitude_mm must be greater than 0"):
        BinParameters(divisions=2, divider_profile="wave", divider_amplitude_mm=0.0).validate()


@pytest.mark.scenario("gridfinity-utensil-bin", "Reject a wave amplitude that would collide")
def test_validation_rejects_oversized_wave_amplitude() -> None:
    """A wave amplitude that would collide a divider with its neighbour is rejected."""
    with pytest.raises(ValueError, match="divider_amplitude_mm is too large"):
        BinParameters(divisions=2, divider_profile="wave", divider_amplitude_mm=1000.0).validate()


@pytest.mark.scenario("gridfinity-utensil-bin", "Skip cutout validation when disabled")
def test_validation_skips_cutout_checks_when_disabled() -> None:
    """Cutout-fit checks are skipped when cutouts are disabled."""
    BinParameters(cutout_offset_from_edge_mm=1, cutout_radius_mm=600, cutouts_enabled=False).validate()


@pytest.mark.scenario("gridfinity-utensil-bin", "Reject cutouts too large for the side")
def test_validation_rejects_oversized_cutout() -> None:
    """A cutout offset and radius that cannot fit the side's length is rejected."""
    with pytest.raises(ValueError, match="cutout"):
        BinParameters(cutout_offset_from_edge_mm=1, cutout_radius_mm=600).validate()


@pytest.mark.scenario("gridfinity-utensil-bin", "Generate bin with Gridfinity height units")
def test_height_in_units_converts_to_millimetres() -> None:
    """Gridfinity height units resolve at 7 mm per unit."""
    params = BinParameters(height_in_units=7)
    params.validate()
    assert params.effective_height_mm == pytest.approx(49.0)


@pytest.mark.scenario("gridfinity-utensil-bin", "Generate bin with freeform millimetre height")
def test_freeform_height_mm_is_used_directly() -> None:
    """A freeform millimetre height is used as-is when units are not given."""
    params = BinParameters(height_in_units=None, height_mm=55.0)
    params.validate()
    assert params.effective_height_mm == pytest.approx(55.0)


@pytest.mark.scenario("gridfinity-utensil-bin", "Reject combined height specification")
def test_validation_rejects_combined_heights() -> None:
    """Giving both height_in_units and height_mm is a conflict and must be rejected."""
    with pytest.raises(ValueError, match="mutually exclusive"):
        BinParameters(height_in_units=8, height_mm=56.0).validate()


@pytest.mark.scenario("bin-presets", "Reject an unknown preset")
def test_resolve_unknown_preset_raises() -> None:
    """An unknown preset name raises with the available names listed."""
    assert "chop-board" in preset_names()
    with pytest.raises(ValueError, match="Unknown preset"):
        resolve_preset("does-not-exist")


@pytest.mark.scenario("print-bed-validation", "Model fits within the build volume")
def test_check_print_bed_fits() -> None:
    """A model within the build volume on every axis yields no warnings."""
    assert check_print_bed(100.0, 150.0, 50.0, 220.0, 220.0, 240.0) == []


@pytest.mark.scenario("print-bed-validation", "Model exceeds the build volume on an axis")
@pytest.mark.scenario("print-bed-validation", "Warning message is actionable")
def test_check_print_bed_exceeds_width() -> None:
    """A model wider than bed X warns, naming the dimension and the limit."""
    warnings = check_print_bed(250.0, 100.0, 50.0, 220.0, 220.0, 240.0)
    assert len(warnings) == 1
    assert "width" in warnings[0]
    assert "250.0" in warnings[0]
    assert "220.0" in warnings[0]


@pytest.mark.scenario("print-bed-validation", "Model exceeds the build volume on an axis")
def test_check_print_bed_exceeds_depth() -> None:
    """A model deeper than bed Y warns about depth."""
    warnings = check_print_bed(100.0, 300.0, 50.0, 220.0, 220.0, 240.0)
    assert len(warnings) == 1
    assert "depth" in warnings[0]


@pytest.mark.scenario("print-bed-validation", "Model exceeds the build volume on an axis")
def test_check_print_bed_exceeds_height() -> None:
    """A model taller than the max print height warns about height."""
    warnings = check_print_bed(100.0, 100.0, 300.0, 220.0, 220.0, 240.0)
    assert len(warnings) == 1
    assert "height" in warnings[0]


@pytest.mark.scenario("print-bed-validation", "Model exceeds the build volume on an axis")
def test_check_print_bed_reports_every_exceeded_axis() -> None:
    """A model exceeding all three limits produces three warnings."""
    assert len(check_print_bed(250.0, 250.0, 250.0, 220.0, 220.0, 240.0)) == 3
