"""Parametric Gridfinity-compatible kitchen bin geometry.

A ``KitchenBin`` is a Gridfinity base with open-top walls around a single explicitly-sized rounded
pocket and optional full-height side cutouts. A ``CutleryBin`` is a ``KitchenBin`` with straight,
single-axis dividers that split the pocket into equal columns; the side cutout runs through the
dividers. Generic equal-compartment grids are out of scope here -- use ``gridfinity_build123d``
directly for those.
"""

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
    Face,
    FilletPolyline,
    Line,
    Locations,
    Mode,
    Plane,
    Rectangle,
    RectangleRounded,
    RotationLike,
    add,
    extrude,
    make_face,
    mirror,
)
from gridfinity_build123d import BaseEqual

GRIDFINITY_PITCH_MM = 42 * MM  # Standard Gridfinity grid pitch in mm per unit.
GRIDFINITY_HEIGHT_UNIT_MM = 7 * MM  # Millimetres per Gridfinity height unit.
BASE_CORNER_RADIUS = 7.5 / 2 * MM  # mm
GRIDFINITY_CLEARANCE_MM = 0.5 * MM  # Total per-axis footprint clearance (bin = N*42 - 0.5, per the GridFinity spec).

# Generic defaults: a 2x4, 8-unit bin with uniform 2 mm walls (a plain kitchen bin, not the chop bin).
DEFAULT_WALL_THICKNESS = 2 * MM  # mm; uniform wall thickness used to derive the default pocket.
DEFAULT_CUTOUT_OFFSET = 40 * MM  # mm from the outer Y edge to the edge of the cutout (tunable starting point).
DEFAULT_CUTOUT_RADIUS = 12.5 * MM  # mm radius of the side cutout arc.

# The chop-board preset reproduces the original chopping-board bin: an explicit, non-uniform-wall pocket.
CHOP_GRID_X = 4
CHOP_GRID_Y = 6
CHOP_HEIGHT_UNITS = 8
CHOP_POCKET_LENGTH = 220 * MM
CHOP_POCKET_WIDTH = 160 * MM
CHOP_POCKET_CORNER_RADIUS = 35 * MM
CHOP_CUTOUT_OFFSET = 75 * MM


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
    cutout_offset_from_edge_mm: float = DEFAULT_CUTOUT_OFFSET
    cutout_radius_mm: float = DEFAULT_CUTOUT_RADIUS
    cutouts_enabled: bool = True
    divisions: int = 1
    divider_thickness_mm: float = 2.0

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
    def cutout_length_mm(self) -> float:
        """Return the straight length of the cutout, along Y."""
        return self.side_half_length_mm - self.cutout_offset_from_edge_mm

    @property
    def cutout_arc_mm(self) -> float:
        """Return the arc reach of the cutout, along Y."""
        return self.cutout_length_mm + self.cutout_radius_mm + (0.1 * MM)

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
        elif not 7.0 < self.effective_height_mm <= 200.0:
            errors.append("effective height must be greater than 7 mm and at most 200 mm")

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

        # The cutout-fit checks only constrain geometry that is actually built, so they are skipped
        # when cutouts are disabled and the cutout dimensions are inert.
        if self.cutouts_enabled:
            if self.cutout_offset_from_edge_mm <= 0:
                errors.append("cutout_offset_from_edge_mm must be greater than 0")
            if self.cutout_radius_mm <= 0:
                errors.append("cutout_radius_mm must be greater than 0")
            if self.cutout_length_mm <= 0:
                errors.append(
                    "cutout_offset_from_edge_mm is too large for grid_y; it must leave room for a cutout"
                )
            if self.cutout_arc_mm >= self.side_half_length_mm:
                errors.append(
                    "cutout_offset_from_edge_mm and cutout_radius_mm are incompatible for this grid_y"
                )

        if errors:
            raise ValueError("Invalid bin parameters: " + "; ".join(errors))


class SideCutoutProfile(BaseSketchObject):
    """The side cutout profile (a mirrored fillet polyline), used on both cut walls."""

    def __init__(
        self,
        *,
        cutout_length: float,
        cutout_height: float,
        cutout_arc: float,
        cutout_radius: float,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        """Build the side cutout profile."""
        with BuildSketch() as profile:
            with BuildLine():
                FilletPolyline(
                    (0, 0),
                    (cutout_length, 0),
                    (cutout_length, cutout_height),
                    (cutout_arc, cutout_height),
                    radius=cutout_radius,
                )
                Line(
                    (0, cutout_height),
                    (cutout_arc, cutout_height),
                )
                mirror(about=Plane.YZ)
            make_face()
        super().__init__(profile.face(), rotation, align, mode)


def _rounded_panel(
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
            add(BaseEqual(grid_x=params.grid_x, grid_y=params.grid_y, mode=mode))

            # The top face of the Gridfinity base is the inner floor of the bin.
            base_top = build.faces().sort_by(Axis.Z)[-1]
            floor_z = base_top.center().Z

            with BuildSketch(base_top) as wall_sketch:
                _rounded_panel(
                    params.grid_x * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM,
                    params.grid_y * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM,
                    params.base_corner_radius_mm,
                )
                _rounded_panel(
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
                    SideCutoutProfile(
                        cutout_length=params.cutout_length_mm,
                        cutout_height=top_z - floor_z,
                        cutout_arc=params.cutout_arc_mm,
                        cutout_radius=params.cutout_radius_mm,
                        align=(Align.CENTER, Align.MIN),
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
        """Add straight dividers parallel to the cut walls, splitting the pocket into equal columns."""
        if params.divisions < 2:
            return
        pocket_width = params.effective_pocket_width_mm
        pocket_length = params.effective_pocket_length_mm
        column_pitch = pocket_width / params.divisions
        height = top_z - floor_z
        # Dividers sit at evenly spaced X positions inside the pocket, span the full pocket length
        # (attaching to both un-cut walls), and rise from the inner floor to the top.
        for index in range(1, params.divisions):
            x = -pocket_width / 2 + index * column_pitch
            with Locations((x, 0, floor_z)):
                Box(
                    params.divider_thickness_mm,
                    pocket_length,
                    height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

    @property
    def top(self) -> Face:
        """Return the highest face of the bin."""
        return self.faces().sort_by(Axis.Z)[-1]


def create_kitchen_bin(params: BinParameters | None = None) -> KitchenBin:
    """Create a plain kitchen bin (single pocket) from validated parameters."""
    return KitchenBin(params=params)


def create_cutlery_bin(params: BinParameters | None = None) -> CutleryBin:
    """Create a cutlery bin (pocket split into columns) from validated parameters."""
    return CutleryBin(params=params)


def check_print_bed(grid_x: int, grid_y: int, bed_x_mm: float, bed_y_mm: float) -> list[str]:
    """Return warning strings when the bin footprint exceeds the configured print bed.

    Returns an empty list when the footprint fits within the bed on both axes.
    """
    footprint_x = grid_x * GRIDFINITY_PITCH_MM
    footprint_y = grid_y * GRIDFINITY_PITCH_MM
    warnings: list[str] = []
    if footprint_x > bed_x_mm:
        warnings.append(
            f"Bin footprint X ({footprint_x} mm) exceeds bed X ({bed_x_mm} mm) by {footprint_x - bed_x_mm:.1f} mm."
        )
    if footprint_y > bed_y_mm:
        warnings.append(
            f"Bin footprint Y ({footprint_y} mm) exceeds bed Y ({bed_y_mm} mm) by {footprint_y - bed_y_mm:.1f} mm."
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
        cutout_offset_from_edge_mm=CHOP_CUTOUT_OFFSET,
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
