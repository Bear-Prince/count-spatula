"""Parametric Gridfinity-compatible kitchen bin geometry.

A ``KitchenBin`` is a Gridfinity base with open-top walls around a single explicitly-sized rounded
pocket and optional full-height side cutouts. A ``CutleryBin`` is a ``KitchenBin`` with straight,
single-axis dividers that split the pocket into equal columns; the side cutout runs through the
dividers. Generic equal-compartment grids are out of scope here -- use ``gridfinity_build123d``
directly for those.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from build123d import (
    MM,
    Align,
    Axis,
    BasePartObject,
    BaseSketchObject,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Line,
    Locations,
    Mode,
    Plane,
    Polyline,
    Rectangle,
    RectangleRounded,
    RotationLike,
    add,
    extrude,
    make_face,
)
from gridfinity_build123d import BaseEqual

GRIDFINITY_PITCH_MM = 42 * MM  # Standard Gridfinity grid pitch in mm per unit.
GRIDFINITY_HEIGHT_UNIT_MM = 7 * MM  # Millimetres per Gridfinity height unit.
BASE_CORNER_RADIUS = 7.5 / 2 * MM  # mm
GRIDFINITY_CLEARANCE_MM = 0.5 * MM  # Total per-axis footprint clearance (bin = N*42 - 0.5, per the GridFinity spec).

# Generic defaults: a 2x4, 8-unit bin with uniform 2 mm walls (a plain kitchen bin, not the chop bin).
DEFAULT_WALL_THICKNESS = 2 * MM  # mm; uniform wall thickness used to derive the default pocket.
DEFAULT_CUTOUT_OFFSET_UNITS = 1  # Whole Gridfinity units of solid wall reserved at each end by default.
DEFAULT_CUTOUT_RADIUS = 10 * MM  # mm radius of the cutout's rim fillet (the floor corner stays sharp).
# The reserved solid wall at each end is this much shorter than a whole number of grid units, so the
# cutout's sharp floor edge reaches this far past its target internal grid line -- the line sits just
# inside the open cutout, and the wall is solid only from this margin further out.
CUTOUT_GRID_ALLOWANCE_MM = 1 * MM

# Divider profiles. A "straight" divider is a flat slab; a "wave" divider follows a single S-curve
# (one sine period) along the pocket length so that tapered cutlery can nest in alternating channels.
DIVIDER_STRAIGHT = "straight"
DIVIDER_WAVE = "wave"
DIVIDER_PROFILES = (DIVIDER_STRAIGHT, DIVIDER_WAVE)
MIN_CHANNEL_GAP = 2.0 * MM  # mm; minimum printable gap a wave divider must leave to its neighbour or wall.
WAVE_SAMPLE_COUNT = 64  # Number of segments used to approximate a wave divider's sine curve.

# The chop-board preset reproduces the original chopping-board bin: an explicit, non-uniform-wall pocket.
CHOP_GRID_X = 4
CHOP_GRID_Y = 6
CHOP_HEIGHT_UNITS = 8
CHOP_POCKET_LENGTH = 220 * MM
CHOP_POCKET_WIDTH = 160 * MM
CHOP_POCKET_CORNER_RADIUS = 35 * MM
CHOP_CUTOUT_OFFSET_UNITS = 2  # Grid-aligned; splittable on the chop bin's +/-42 mm internal grid lines.


@dataclass(slots=True)
class BinParameters:
    """Input contract for building a parametric kitchen bin.

    ``grid_x`` runs along X and ``grid_y`` along Y, matching ``BaseEqual``. The pocket length runs
    along Y and its width along X. Side cutouts are cut through the two walls perpendicular to X and
    span the Y axis, so their fit is constrained by ``grid_y``.
    """

    grid_x: int = 2
    grid_y: int = 4
    height_in_units: int | None = 8
    height_mm: float | None = None
    base_corner_radius_mm: float = BASE_CORNER_RADIUS
    wall_thickness_mm: float = DEFAULT_WALL_THICKNESS
    pocket_length_mm: float | None = None
    pocket_width_mm: float | None = None
    pocket_corner_radius_mm: float = 0.0
    cutout_offset_start_units: int = DEFAULT_CUTOUT_OFFSET_UNITS
    cutout_offset_end_units: int = DEFAULT_CUTOUT_OFFSET_UNITS
    cutout_radius_mm: float = DEFAULT_CUTOUT_RADIUS
    cutouts_enabled: bool = True
    divisions: int = 1
    divider_thickness_mm: float = 2.0
    divider_profile: str = DIVIDER_STRAIGHT
    divider_amplitude_mm: float = 0.0

    @property
    def effective_height_mm(self) -> float:
        """Resolve the active bin height in millimetres."""
        if self.height_mm is not None:
            return self.height_mm
        return (self.height_in_units or 0) * GRIDFINITY_HEIGHT_UNIT_MM

    @property
    def effective_pocket_length_mm(self) -> float:
        """Pocket length along Y; derived from the wall thickness when not given explicitly."""
        if self.pocket_length_mm is not None:
            return self.pocket_length_mm
        return self.grid_y * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM - 2 * self.wall_thickness_mm

    @property
    def effective_pocket_width_mm(self) -> float:
        """Pocket width along X; derived from the wall thickness when not given explicitly."""
        if self.pocket_width_mm is not None:
            return self.pocket_width_mm
        return self.grid_x * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM - 2 * self.wall_thickness_mm

    @property
    def side_half_length_mm(self) -> float:
        """Return the half-length of the cut side (centreline to outer edge), along Y."""
        return (self.grid_y * GRIDFINITY_PITCH_MM) / 2

    @property
    def cutout_offset_start_from_edge_mm(self) -> float:
        """Return the start-end cutout offset in millimetres, derived from whole grid units.

        The reserved solid wall is ``CUTOUT_GRID_ALLOWANCE_MM`` shorter than a whole number of grid
        units, so the cutout's sharp floor edge reaches 1 mm past the target internal grid line --
        i.e. the line itself sits just inside the open cutout, not the solid wall. Unlike the
        cutout's rim, the floor has a sharp (unfilleted) corner, so its position does not depend on
        ``cutout_radius_mm``.
        """
        return self.cutout_offset_start_units * GRIDFINITY_PITCH_MM - CUTOUT_GRID_ALLOWANCE_MM

    @property
    def cutout_offset_end_from_edge_mm(self) -> float:
        """Return the end-end cutout offset in millimetres; see ``cutout_offset_start_from_edge_mm``."""
        return self.cutout_offset_end_units * GRIDFINITY_PITCH_MM - CUTOUT_GRID_ALLOWANCE_MM

    @property
    def cutout_length_start_mm(self) -> float:
        """Return the straight floor length of the cutout on the start (-Y) side."""
        return self.side_half_length_mm - self.cutout_offset_start_from_edge_mm

    @property
    def cutout_length_end_mm(self) -> float:
        """Return the straight floor length of the cutout on the end (+Y) side."""
        return self.side_half_length_mm - self.cutout_offset_end_from_edge_mm

    @property
    def cutout_arc_start_mm(self) -> float:
        """Return the rim reach of the cutout on the start (-Y) side."""
        return self.cutout_length_start_mm + self.cutout_radius_mm + (0.1 * MM)

    @property
    def cutout_arc_end_mm(self) -> float:
        """Return the rim reach of the cutout on the end (+Y) side."""
        return self.cutout_length_end_mm + self.cutout_radius_mm + (0.1 * MM)

    def validate(self) -> None:
        """Validate parameter ranges and combinations for printable geometry."""
        errors: list[str] = []

        if not 1 <= self.grid_x <= 12:
            errors.append("grid_x must be between 1 and 12")
        if not 1 <= self.grid_y <= 12:
            errors.append("grid_y must be between 1 and 12")

        if self.height_in_units is not None and self.height_mm is not None:
            errors.append("height_in_units and height_mm are mutually exclusive; specify only one")
        elif self.height_in_units is None and self.height_mm is None:
            errors.append("one of height_in_units or height_mm must be set")
        elif not GRIDFINITY_HEIGHT_UNIT_MM < self.effective_height_mm <= 200.0:
            errors.append(
                "effective height (the wall height above the inner floor, not the bin's total height) "
                f"must be greater than {GRIDFINITY_HEIGHT_UNIT_MM:g} mm (one Gridfinity height unit) "
                "and at most 200 mm"
            )

        if self.wall_thickness_mm <= 0:
            errors.append("wall_thickness_mm must be greater than 0")

        pocket_length = self.effective_pocket_length_mm
        pocket_width = self.effective_pocket_width_mm
        if pocket_length <= 0:
            errors.append("pocket length must be greater than 0 (check grid_y and wall_thickness_mm)")
        if pocket_width <= 0:
            errors.append("pocket width must be greater than 0 (check grid_x and wall_thickness_mm)")

        max_outer_length = self.grid_y * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM
        max_outer_width = self.grid_x * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM
        if pocket_length >= max_outer_length:
            errors.append("pocket length must be smaller than the outer bin length")
        if pocket_width >= max_outer_width:
            errors.append("pocket width must be smaller than the outer bin width")

        max_pocket_corner = min(pocket_length, pocket_width) / 2
        if not 0 <= self.pocket_corner_radius_mm <= max_pocket_corner:
            errors.append("pocket_corner_radius_mm must be between 0 and half of the smaller pocket dimension")

        if not 0 <= self.base_corner_radius_mm <= (min(max_outer_length, max_outer_width) / 2):
            errors.append("base_corner_radius_mm must be between 0 and half of the smaller outer bin dimension")

        if self.divisions < 1:
            errors.append("divisions must be at least 1")
        if self.divider_thickness_mm <= 0:
            errors.append("divider_thickness_mm must be greater than 0")
        elif self.divisions >= 2:
            # This applies to every profile: a straight divider is exactly as wide as the wave
            # divider's centreline band, so it needs the same minimum printable gap to its neighbour.
            column_pitch = self.effective_pocket_width_mm / self.divisions
            if column_pitch - self.divider_thickness_mm < MIN_CHANNEL_GAP:
                errors.append(
                    "divider_thickness_mm is too large for this divider spacing; columns are "
                    f"{column_pitch:.2f} mm apart and must leave a {MIN_CHANNEL_GAP:.1f} mm printable gap"
                )

        if self.divider_profile not in DIVIDER_PROFILES:
            allowed = ", ".join(DIVIDER_PROFILES)
            errors.append(f"divider_profile must be one of: {allowed}")
        elif self.divider_profile == DIVIDER_WAVE:
            # A wave divider needs a positive amplitude, and that amplitude must leave a printable gap
            # between a divider and its phase-mirrored neighbour (the tightest constraint, which also
            # keeps the outermost divider clear of the pocket wall).
            if self.divider_amplitude_mm <= 0:
                errors.append(
                    "divider_amplitude_mm must be greater than 0 for the wave profile; "
                    "use the straight profile for flat dividers"
                )
            elif self.divisions >= 2:
                column_pitch = self.effective_pocket_width_mm / self.divisions
                max_amplitude = (column_pitch - self.divider_thickness_mm - MIN_CHANNEL_GAP) / 2
                if self.divider_amplitude_mm > max_amplitude:
                    errors.append(
                        "divider_amplitude_mm is too large for this divider spacing; "
                        f"it must be at most {max_amplitude:.2f} mm to leave a printable gap"
                    )

        # The cutout-fit checks only constrain geometry that is actually built, so they are skipped
        # when cutouts are disabled and the cutout dimensions are inert.
        if self.cutouts_enabled:
            if self.cutout_radius_mm <= 0:
                errors.append("cutout_radius_mm must be greater than 0")
            if self.cutout_offset_start_units < 1:
                errors.append("cutout_offset_start_units must be at least 1")
            if self.cutout_offset_end_units < 1:
                errors.append("cutout_offset_end_units must be at least 1")
            # At least one whole grid unit of clean gap between the two reserved margins, so "no
            # cutouts below 3 units deep" (for a symmetric bin) is an explicit, structural rule.
            if self.grid_y - self.cutout_offset_start_units - self.cutout_offset_end_units < 1:
                errors.append(
                    "cutout_offset_start_units and cutout_offset_end_units leave less than one "
                    "whole grid unit of gap for grid_y; reduce one of them or increase grid_y"
                )
            elif self.cutout_length_start_mm <= 0 or self.cutout_length_end_mm <= 0:
                errors.append("cutout_offset_start_units or cutout_offset_end_units is too large for grid_y")
            elif self.cutout_arc_start_mm + self.cutout_arc_end_mm >= self.grid_y * GRIDFINITY_PITCH_MM:
                errors.append(
                    "cutout_radius_mm is too large for this grid_y and cutout offset combination"
                )
            if self.cutout_radius_mm >= self.effective_height_mm:
                errors.append("cutout_radius_mm must be less than the effective bin height")

        if errors:
            raise ValueError("Invalid bin parameters: " + "; ".join(errors))


class SideCutoutProfile(BaseSketchObject):
    """The side cutout profile: a sharp-cornered floor with an independently filleted rim on each end.

    The two ends need not be symmetric (``cutout_length_start`` / ``cutout_length_end`` may differ),
    so the shape is built directly rather than by mirroring a single half. The floor corners stay
    sharp (unfilleted) so a base split at the target grid line always cuts through flat, uninterrupted
    floor; only the rim -- where the wall flares out to its widest point -- is rounded.
    """

    def __init__(
        self,
        *,
        cutout_length_start: float,
        cutout_length_end: float,
        cutout_height: float,
        cutout_arc_start: float,
        cutout_arc_end: float,
        cutout_radius: float,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        """Build the side cutout profile."""
        # The fillet trims into the patch horizontally (by `radius`, into the arc_start/arc_end
        # margin below) and vertically (by `radius`, down into the wall) from the corner at the
        # patch's own bottom -- neither trim depends on the patch's height, so it only needs to be
        # a small, non-degenerate sliver. Keeping it independent of `radius` (rather than sized to
        # it) means the fillet's arc reaches almost all the way to the flat top, leaving only this
        # negligible straight remnant above it, instead of a full extra `radius` of straight wall.
        patch_height = 0.1 * MM

        with BuildSketch() as profile:
            # The sharp-cornered core: flat floor, both walls square. Building the two rim flares as
            # separate patches (rather than one continuous polyline reaching to each rim) avoids the
            # two ends' straight top edges retracing each other, which otherwise collapses the flare.
            with BuildLine():
                Line((-cutout_length_start, 0), (cutout_length_end, 0))
                Line((cutout_length_end, 0), (cutout_length_end, cutout_height))
                Line((cutout_length_end, cutout_height), (-cutout_length_start, cutout_height))
                Line((-cutout_length_start, cutout_height), (-cutout_length_start, 0))
            make_face()

            with BuildLine():
                Line(
                    (cutout_length_end, cutout_height - patch_height),
                    (cutout_arc_end, cutout_height - patch_height),
                )
                Line((cutout_arc_end, cutout_height - patch_height), (cutout_arc_end, cutout_height))
                Line((cutout_arc_end, cutout_height), (cutout_length_end, cutout_height))
                Line(
                    (cutout_length_end, cutout_height),
                    (cutout_length_end, cutout_height - patch_height),
                )
            make_face()

            with BuildLine():
                Line(
                    (-cutout_arc_start, cutout_height - patch_height),
                    (-cutout_length_start, cutout_height - patch_height),
                )
                Line(
                    (-cutout_length_start, cutout_height - patch_height),
                    (-cutout_length_start, cutout_height),
                )
                Line((-cutout_length_start, cutout_height), (-cutout_arc_start, cutout_height))
                Line(
                    (-cutout_arc_start, cutout_height),
                    (-cutout_arc_start, cutout_height - patch_height),
                )
            make_face()

            # Fillet only the two corners where each wall meets its rim flare (at the step height),
            # leaving the floor corners (at height 0) and the outer rim corners untouched.
            step_y = cutout_height - patch_height
            combined_face = profile.sketch.faces()[0]
            rim_corners = [
                v
                for v in combined_face.vertices()
                if abs(v.Y - step_y) < 1e-6
                and (abs(v.X - cutout_length_end) < 1e-6 or abs(v.X - (-cutout_length_start)) < 1e-6)
            ]
            filleted_face = combined_face.fillet_2d(cutout_radius, rim_corners)
        super().__init__(filleted_face, rotation, align, mode)


def rounded_panel(
    width: float,
    height: float,
    radius: float,
    *,
    mode: Mode = Mode.ADD,
    align: tuple[Align, Align] = (Align.CENTER, Align.CENTER),
) -> None:
    """Add a rectangle to the active sketch, rounded when radius > 0 and sharp when it is 0."""
    if radius > 0:
        RectangleRounded(width=width, height=height, radius=radius, mode=mode, align=align)
    else:
        Rectangle(width=width, height=height, mode=mode, align=align)


class KitchenBin(BasePartObject):
    """A Gridfinity bin with an explicitly-sized rounded pocket and optional side cutouts."""

    def __init__(
        self,
        params: BinParameters | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        """Construct the bin from validated parameters."""
        if params is None:
            params = BinParameters()
        params.validate()
        height = params.effective_height_mm

        with BuildPart() as build:
            # This inner Mode.ADD is independent of the `mode` parameter, which controls how the
            # finished bin combines into an enclosing build context (see super().__init__ below).
            add(BaseEqual(grid_x=params.grid_x, grid_y=params.grid_y, mode=Mode.ADD))

            # The top face of the Gridfinity base is the inner floor of the bin.
            base_top = build.faces().sort_by(Axis.Z)[-1]
            floor_z = base_top.center().Z

            with BuildSketch(base_top) as wall_sketch:
                rounded_panel(
                    params.grid_x * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM,
                    params.grid_y * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM,
                    params.base_corner_radius_mm,
                )
                rounded_panel(
                    params.effective_pocket_width_mm,
                    params.effective_pocket_length_mm,
                    params.pocket_corner_radius_mm,
                    mode=Mode.SUBTRACT,
                )

            extrude(to_extrude=wall_sketch.face(), amount=height)
            top_z = build.part.bounding_box().max.Z

            # Subclasses add interior dividers here, before the cutout, so the slot passes through them.
            self._add_interior(params, floor_z, top_z)

            if params.cutouts_enabled:
                # Cut the side handle slots straight through both walls perpendicular to X (and any
                # dividers), sketched once on a YZ-oriented plane at the inner floor and extruded
                # through the full width in both directions.
                half_width = params.grid_x * GRIDFINITY_PITCH_MM / 2
                cut_plane = Plane(origin=(0, 0, floor_z), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
                with BuildSketch(cut_plane) as side_sketch:
                    # No align: the profile is built with its own origin at the wall's centre (local
                    # X=0) and floor (local Y=0), matching this plane's origin exactly. The two ends
                    # may differ, so re-centering the bounding box (Align.CENTER) would misplace it.
                    SideCutoutProfile(
                        cutout_length_start=params.cutout_length_start_mm,
                        cutout_length_end=params.cutout_length_end_mm,
                        cutout_height=top_z - floor_z,
                        cutout_arc_start=params.cutout_arc_start_mm,
                        cutout_arc_end=params.cutout_arc_end_mm,
                        cutout_radius=params.cutout_radius_mm,
                    )
                extrude(
                    to_extrude=side_sketch.sketch.faces(),
                    amount=half_width + 1,
                    both=True,
                    mode=Mode.SUBTRACT,
                )

        super().__init__(build.part, rotation, align, mode)

    def _add_interior(self, params: BinParameters, floor_z: float, top_z: float) -> None:
        """Hook for subclasses to add interior structure before the cutout. No-op for a plain bin."""


class CutleryBin(KitchenBin):
    """A ``KitchenBin`` whose pocket is split into equal columns by straight single-axis dividers."""

    def _add_interior(self, params: BinParameters, floor_z: float, top_z: float) -> None:
        """Add dividers parallel to the cut walls, splitting the pocket into equal columns.

        Dividers are straight slabs by default. With the wave profile each divider follows a single
        S-curve along the pocket length and adjacent dividers are phase-mirrored, so the channels
        between them alternate orientation and tapered cutlery can nest head-to-tail.
        """
        if params.divisions < 2:
            return
        pocket_width = params.effective_pocket_width_mm
        pocket_length = params.effective_pocket_length_mm
        column_pitch = pocket_width / params.divisions
        height = top_z - floor_z
        # Dividers sit at evenly spaced X centrelines inside the pocket, span the full pocket length
        # (attaching to both un-cut walls), and rise from the inner floor to the top.
        for counter, index in enumerate(range(1, params.divisions)):
            centreline_x = -pocket_width / 2 + index * column_pitch
            if params.divider_profile == DIVIDER_WAVE:
                # Negate the amplitude on alternate dividers to phase-mirror neighbouring channels.
                amplitude = params.divider_amplitude_mm * (-1) ** counter
                self._add_wave_divider(centreline_x, amplitude, params.divider_thickness_mm, floor_z, height,
                                       pocket_length)
            else:
                with Locations((centreline_x, 0, floor_z)):
                    Box(
                        params.divider_thickness_mm,
                        pocket_length,
                        height,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )

    @staticmethod
    def _add_wave_divider(
        centreline_x: float,
        amplitude: float,
        thickness: float,
        floor_z: float,
        height: float,
        pocket_length: float,
    ) -> None:
        """Add one S-curve divider as a vertical prism extruded from a sampled wavy band.

        The centreline is displaced in X by ``amplitude * sin(2*pi*t)`` for ``t`` in ``[0, 1]`` along
        the pocket length, so it is zero at both ends and meets the un-cut walls at the nominal
        spacing. The band is the region between the centreline offset by plus/minus half the divider
        thickness, sampled as a polyline and extruded from the inner floor to the wall top.
        """
        half_thickness = thickness / 2
        right_edge: list[tuple[float, float]] = []
        left_edge: list[tuple[float, float]] = []
        for sample in range(WAVE_SAMPLE_COUNT + 1):
            t = sample / WAVE_SAMPLE_COUNT
            y = -pocket_length / 2 + t * pocket_length
            offset = amplitude * math.sin(2 * math.pi * t)
            right_edge.append((centreline_x + offset + half_thickness, y))
            left_edge.append((centreline_x + offset - half_thickness, y))
        # Trace up the right edge, then back down the left edge, to form a simple closed ribbon.
        outline = right_edge + list(reversed(left_edge))
        # Extrude via sketch.faces() to keep the floor_z placement: sketch.face() resets the face
        # location to the origin, dropping the offset and pushing the divider down into the base.
        with BuildSketch(Plane.XY.offset(floor_z)) as band:
            with BuildLine():
                Polyline(*outline, close=True)
            make_face()
        extrude(to_extrude=band.sketch.faces(), amount=height)


def create_kitchen_bin(params: BinParameters | None = None) -> KitchenBin:
    """Create a plain kitchen bin (single pocket) from validated parameters."""
    return KitchenBin(params=params)


def create_cutlery_bin(params: BinParameters | None = None) -> CutleryBin:
    """Create a cutlery bin (pocket split into columns) from validated parameters."""
    return CutleryBin(params=params)


def check_print_bed(
    model_x_mm: float,
    model_y_mm: float,
    model_z_mm: float,
    bed_x_mm: float,
    bed_y_mm: float,
    bed_z_mm: float,
) -> list[str]:
    """Return a warning for each model dimension that exceeds the print volume.

    All dimensions are in millimetres. The model is evaluated in its as-generated orientation (no
    rotation). Returns an empty list when the model fits within the build volume on every axis.
    """
    warnings: list[str] = []
    for label, model, limit in (
        ("width", model_x_mm, bed_x_mm),
        ("depth", model_y_mm, bed_y_mm),
        ("height", model_z_mm, bed_z_mm),
    ):
        if model > limit:
            warnings.append(
                f"Model {label} ({model:.1f} mm) exceeds the print volume {label} "
                f"({limit:.1f} mm) by {model - limit:.1f} mm."
            )
    return warnings


# Named presets: each returns a fully-populated BinParameters.
def _chop_board_preset() -> BinParameters:
    """Reproduce the original chopping-board bin as a KitchenBin (explicit, non-uniform-wall pocket)."""
    return BinParameters(
        grid_x=CHOP_GRID_X,
        grid_y=CHOP_GRID_Y,
        height_in_units=CHOP_HEIGHT_UNITS,
        pocket_length_mm=CHOP_POCKET_LENGTH,
        pocket_width_mm=CHOP_POCKET_WIDTH,
        pocket_corner_radius_mm=CHOP_POCKET_CORNER_RADIUS,
        cutout_offset_start_units=CHOP_CUTOUT_OFFSET_UNITS,
        cutout_offset_end_units=CHOP_CUTOUT_OFFSET_UNITS,
    )


class Provenance(Enum):
    """Where a preset's design comes from, which determines its generated model's license obligations.

    An ``ORIGINAL`` bin (our own measurements and our own profiles) carries whatever model license we
    choose; a ``DERIVED`` bin reproduces a third party's protected design and inherits that design's
    license. Provenance must reflect real independence -- dimensions must never be nudged cosmetically
    to disguise derivative status. See CREDITS.md for the lineage and attribution rules.
    """

    ORIGINAL = "original"
    DERIVED = "derived"


@dataclass(frozen=True)
class Preset:
    """A named preset: a parameter factory plus its cutout rule and licensing provenance."""

    factory: Callable[[], BinParameters]
    cutouts_required: bool = False
    provenance: Provenance = Provenance.ORIGINAL
    # SPDX identifier for the generated model. Every model is CC BY-SA 4.0 today: derived bins by the
    # ShareAlike obligation, original bins by the project's deliberate choice (revisitable per bin).
    model_license: str = "CC-BY-SA-4.0"
    # For a derived preset, a human-readable reference to the upstream design it reproduces, used for
    # attribution. ``None`` for original presets.
    derived_from: str | None = None


# The chop-board preset requires cutouts: without them the chopping board is trapped in the pocket.
# It is an original design (our own IKEA chopping-board measurements and profiles), not derived.
PRESETS: dict[str, Preset] = {
    "chop-board": Preset(
        _chop_board_preset,
        cutouts_required=True,
        provenance=Provenance.ORIGINAL,
    ),
}


def preset_names() -> list[str]:
    """Return the available preset names."""
    return sorted(PRESETS)


def _get_preset(name: str) -> Preset:
    try:
        return PRESETS[name]
    except KeyError:
        available = ", ".join(preset_names())
        msg = f"Unknown preset '{name}'. Available presets: {available}"
        raise ValueError(msg) from None


def resolve_preset(name: str) -> BinParameters:
    """Return the parameters for a named preset, or raise with the available names."""
    return _get_preset(name).factory()


def preset_requires_cutouts(name: str) -> bool:
    """Return whether the named preset forbids disabling its side cutouts."""
    return _get_preset(name).cutouts_required
