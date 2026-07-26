"""Tests for the opt-in Gridfinity stacking lip."""

from dataclasses import replace

import pytest
from build123d import Align, Box, BuildPart, Location, Mode, add
from gridfinity_build123d import BaseEqual

from cutlery_bin import (
    STACKING_LIP_SEAT_MM,
    BinParameters,
    check_print_bed,
    create_cutlery_bin,
    create_kitchen_bin,
    resolve_preset,
)

# The measured lip height for the pinned gridfinity_build123d: the standard's nominal 4.4 mm less the
# 0.2 mm apex fillet the library applies. Asserted with a tolerance so a pin bump reports a shift rather
# than an exact-equality failure.
EXPECTED_LIP_HEIGHT_MM = 4.117
LIP_HEIGHT_TOLERANCE_MM = 0.15


def _volume_in(
    part: object,
    x_range: tuple[float, float],
    y_range: tuple[float, float],
    z_range: tuple[float, float],
) -> float:
    """Return the volume of ``part`` inside an axis-aligned box, in mm^3."""
    probe = Box(
        x_range[1] - x_range[0],
        y_range[1] - y_range[0],
        z_range[1] - z_range[0],
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).locate(Location((x_range[0], y_range[0], z_range[0])))
    return (part & probe).volume


@pytest.fixture(scope="module")
def lip_bins() -> dict:
    """Build the reference lipped and unlipped bins once for the module (geometry builds are slow)."""
    small = BinParameters(grid_x=2, grid_y=4, height_in_units=4)
    chop = resolve_preset("chop-board")
    # The inner floor is the top of the Gridfinity base, so measure it rather than assuming z = 0.
    with BuildPart() as base:
        add(BaseEqual(grid_x=2, grid_y=4, mode=Mode.ADD))
    return {
        "params_small": small,
        "floor_z": base.part.bounding_box().max.Z,
        "cut_plain": create_kitchen_bin(small),
        "cut_lip": create_kitchen_bin(replace(small, stacking_lip=True)),
        "solid_plain": create_kitchen_bin(replace(small, cutouts_enabled=False)),
        "solid_lip": create_kitchen_bin(replace(small, cutouts_enabled=False, stacking_lip=True)),
        "cutlery_lip": create_cutlery_bin(replace(small, divisions=3, stacking_lip=True)),
        "params_chop": chop,
        "chop_lip": create_kitchen_bin(replace(chop, stacking_lip=True)),
    }


@pytest.mark.scenario("stacking-lip", "Lip is absent by default")
def test_lip_is_absent_by_default(lip_bins: dict) -> None:
    """The parameter defaults to disabled, and a bin built from defaults carries no lip material."""
    assert BinParameters().stacking_lip is False
    plain, lipped = lip_bins["cut_plain"], lip_bins["cut_lip"]
    # `params_small` leaves stacking_lip at its default, so this bin is the "unchanged" geometry.
    assert plain.volume < lipped.volume
    assert plain.bounding_box().max.Z < lipped.bounding_box().max.Z


@pytest.mark.scenario("stacking-lip", "Add a lip to a plain bin")
def test_lip_added_to_plain_bin(lip_bins: dict) -> None:
    """A lipped KitchenBin carries lip material above the wall top."""
    plain, lipped = lip_bins["solid_plain"], lip_bins["solid_lip"]
    wall_top = plain.bounding_box().max.Z
    assert wall_top < lipped.bounding_box().max.Z
    # Material exists all the way round the rim above the wall top.
    band = (wall_top + 1.0, wall_top + 3.0)
    assert _volume_in(lipped, (38.0, 42.0), (-10.0, 10.0), band) > 0
    assert _volume_in(lipped, (-10.0, 10.0), (80.0, 84.0), band) > 0


@pytest.mark.scenario("stacking-lip", "Add a lip to a bin with dividers")
def test_lip_on_divided_bin_leaves_divider_tops_untouched(lip_bins: dict) -> None:
    """The lip follows the outer rim only; divider tops get no lip."""
    lipped = lip_bins["cutlery_lip"]
    wall_top = lip_bins["solid_plain"].bounding_box().max.Z
    band = (wall_top + 0.5, wall_top + 3.0)
    # With three divisions the dividers sit at x = +/-13.25; probe directly over one of them.
    assert _volume_in(lipped, (-14.0, -12.5), (-20.0, 20.0), band) == pytest.approx(0.0, abs=1e-6)
    # The outer rim at the same height does carry the lip.
    assert _volume_in(lipped, (-10.0, 10.0), (80.0, 84.0), band) > 0


@pytest.mark.scenario("stacking-lip", "Add a lip to a preset bin")
def test_lip_on_preset_bin(lip_bins: dict) -> None:
    """The chop-board preset accepts a lip and stays a valid solid."""
    chop_lip = lip_bins["chop_lip"]
    assert chop_lip.is_valid()
    assert lip_bins["params_chop"].effective_height_mm < chop_lip.bounding_box().size.Z


@pytest.mark.scenario("stacking-lip", "Lip preserves the bin footprint")
def test_lip_preserves_footprint(lip_bins: dict) -> None:
    """Adding a lip changes nothing in X or Y."""
    plain = lip_bins["cut_plain"].bounding_box()
    lipped = lip_bins["cut_lip"].bounding_box()
    assert pytest.approx(plain.size.X, abs=0.001) == lipped.size.X
    assert pytest.approx(plain.size.Y, abs=0.001) == lipped.size.Y


@pytest.mark.scenario("stacking-lip", "Lip adds the standard profile height")
def test_lip_adds_standard_height(lip_bins: dict) -> None:
    """The lip adds the measured profile height, asserted with a tolerance."""
    grown = lip_bins["cut_lip"].bounding_box().size.Z - lip_bins["cut_plain"].bounding_box().size.Z
    assert grown == pytest.approx(EXPECTED_LIP_HEIGHT_MM, abs=LIP_HEIGHT_TOLERANCE_MM)


@pytest.mark.scenario("stacking-lip", "Lipped bin is a valid solid")
def test_lipped_bin_is_valid_solid(lip_bins: dict) -> None:
    """Every lipped variant is a valid solid suitable for export."""
    for key in ("cut_lip", "solid_lip", "cutlery_lip"):
        assert lip_bins[key].is_valid(), f"{key} is not a valid solid"


@pytest.mark.scenario("stacking-lip", "Lip is interrupted by the handle slot")
def test_lip_is_interrupted_by_handle_slot(lip_bins: dict) -> None:
    """No lip material spans either handle slot opening."""
    lipped = lip_bins["cut_lip"]
    params = lip_bins["params_small"]
    wall_top = lip_bins["cut_plain"].bounding_box().max.Z
    inner = (-(params.cutout_arc_start_mm - 0.5), params.cutout_arc_end_mm - 0.5)
    band = (wall_top + 1.0, wall_top + 3.0)
    assert _volume_in(lipped, (38.0, 42.0), inner, band) == pytest.approx(0.0, abs=1e-6)
    assert _volume_in(lipped, (-42.0, -38.0), inner, band) == pytest.approx(0.0, abs=1e-6)


@pytest.mark.scenario("stacking-lip", "Lip is continuous when cutouts are disabled")
def test_lip_is_continuous_without_cutouts(lip_bins: dict) -> None:
    """With no cutouts the lip runs unbroken around the rim."""
    lipped = lip_bins["solid_lip"]
    wall_top = lip_bins["solid_plain"].bounding_box().max.Z
    band = (wall_top + 1.0, wall_top + 3.0)
    # Sample the rim where the handle slot would otherwise have removed it, plus the other three sides.
    for x_range, y_range in (
        ((38.0, 42.0), (-10.0, 10.0)),
        ((-42.0, -38.0), (-10.0, 10.0)),
        ((-10.0, 10.0), (80.0, 84.0)),
        ((-10.0, 10.0), (-84.0, -80.0)),
    ):
        assert _volume_in(lipped, x_range, y_range, band) > 0, f"lip missing at {x_range}, {y_range}"


@pytest.mark.scenario("stacking-lip", "Handle slot remains open to the full wall height")
def test_handle_slot_open_past_the_lip(lip_bins: dict) -> None:
    """The slot stays clear from the inner floor to above the top of the lip."""
    lipped = lip_bins["cut_lip"]
    params = lip_bins["params_small"]
    box = lipped.bounding_box()
    wall_top = lip_bins["cut_plain"].bounding_box().max.Z
    inner = (-(params.cutout_arc_start_mm - 0.5), params.cutout_arc_end_mm - 0.5)
    # A column through the slot, from just above the inner floor to the very top of the lip.
    floor_z = lip_bins["floor_z"]
    narrow = (-5.0, 5.0)
    assert _volume_in(lipped, (38.0, 42.0), narrow, (floor_z + 1.0, box.max.Z)) == pytest.approx(0.0, abs=1e-6)
    assert _volume_in(lipped, (38.0, 42.0), inner, (wall_top + 0.2, box.max.Z)) == pytest.approx(0.0, abs=1e-6)


@pytest.mark.scenario("stacking-lip", "Lip terminates at the cutout's widest point")
def test_lip_terminates_at_the_rim(lip_bins: dict) -> None:
    """The lip ends at the cutout's widest extent, not part-way down the fillet's curve."""
    lipped = lip_bins["cut_lip"]
    params = lip_bins["params_small"]
    wall_top = lip_bins["cut_plain"].bounding_box().max.Z
    arc = params.cutout_arc_end_mm
    band = (wall_top + 1.0, wall_top + 3.0)
    # Nothing inside the arc ...
    assert _volume_in(lipped, (38.0, 42.0), (arc - 2.0, arc - 0.2), band) == pytest.approx(0.0, abs=1e-6)
    # ... and lip immediately outside it, at both the bottom and the top of the lip band, which is what
    # makes the termination a vertical face rather than a curve.
    for z_range in ((wall_top + 0.5, wall_top + 0.8), (wall_top + 3.0, wall_top + 3.5)):
        assert _volume_in(lipped, (38.0, 42.0), (arc + 0.2, arc + 3.0), z_range) > 0


@pytest.mark.scenario("stacking-lip", "Cutout does not narrow the opening at the wall top")
def test_cutout_opening_at_wall_top_is_unchanged(lip_bins: dict) -> None:
    """The rim fillet still reaches its widest at the wall top, so hand access is not reduced.

    This is the regression guard for the construction: raising ``cutout_height`` to clear the lip would
    drag the flare upward with it and narrow this opening, because the flare patches are anchored to the
    top of the cutout profile rather than to its floor.
    """
    params = lip_bins["params_small"]
    wall_top = lip_bins["cut_plain"].bounding_box().max.Z
    inner = (-(params.cutout_arc_start_mm - 0.5), params.cutout_arc_end_mm - 0.5)
    just_below = (wall_top - 0.06, wall_top - 0.01)
    plain_opening = _volume_in(lip_bins["cut_plain"], (38.0, 42.0), inner, just_below)
    lipped_opening = _volume_in(lip_bins["cut_lip"], (38.0, 42.0), inner, just_below)
    assert plain_opening == pytest.approx(0.0, abs=1e-6)
    assert lipped_opening == pytest.approx(plain_opening, abs=1e-6)


@pytest.mark.scenario("stacking-lip", "Lip height counts toward the print-bed height check")
def test_lip_height_counts_toward_print_bed(lip_bins: dict) -> None:
    """A bin that fits without a lip but not with one is warned about."""
    plain_z = lip_bins["cut_plain"].bounding_box().size.Z
    lipped_z = lip_bins["cut_lip"].bounding_box().size.Z
    bed_z = (plain_z + lipped_z) / 2
    assert check_print_bed(50.0, 100.0, plain_z, 220.0, 220.0, bed_z) == []
    warnings = check_print_bed(50.0, 100.0, lipped_z, 220.0, 220.0, bed_z)
    assert len(warnings) == 1
    assert "height" in warnings[0]


@pytest.mark.scenario("stacking-lip", "Default wall thickness is accepted")
def test_default_wall_thickness_accepts_the_lip() -> None:
    """The default 2 mm wall is thinner than the lip's 2.6 mm reach, and is still valid."""
    params = BinParameters(stacking_lip=True)
    params.validate()
    assert params.actual_wall_thickness_x_mm == pytest.approx(2.0, abs=0.001)


@pytest.mark.scenario("stacking-lip", "Reject a wall too thin to seat the lip")
def test_reject_wall_too_thin_to_seat_the_lip() -> None:
    """A wall with less than the lip's lowest step to sit on is rejected."""
    params = BinParameters(grid_x=2, grid_y=4, pocket_width_mm=83.0, stacking_lip=True)
    assert params.actual_wall_thickness_x_mm < STACKING_LIP_SEAT_MM
    with pytest.raises(ValueError, match="too thin for a stacking lip"):
        params.validate()
    # The same bin without a lip is unaffected.
    replace(params, stacking_lip=False).validate()


@pytest.mark.scenario("stacking-lip", "Thick-walled preset is unaffected")
def test_thick_walled_preset_accepts_the_lip() -> None:
    """The chop-board preset's thinnest wall clears the lip's reach outright."""
    params = replace(resolve_preset("chop-board"), stacking_lip=True)
    params.validate()
    assert params.actual_wall_thickness_x_mm == pytest.approx(3.75, abs=0.001)
    assert params.actual_wall_thickness_y_mm == pytest.approx(15.75, abs=0.001)
