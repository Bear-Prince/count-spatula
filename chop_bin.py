"""Parametric Gridfinity-compatible chopping-board bin geometry."""

from dataclasses import dataclass

from build123d import (
    MM,
    Align,
    Axis,
    BasePartObject,
    BaseSketchObject,
    BuildLine,
    BuildPart,
    BuildSketch,
    FilletPolyline,
    Line,
    Mode,
    Plane,
    RectangleRounded,
    RotationLike,
    add,
    extrude,
    make_face,
    mirror,
)
from gridfinity_build123d import BaseEqual
from ocp_vscode import show

BASE_LENGTH = 6  # Units
BASE_WIDTH = 4  # Units
BASE_CORNER_RADIUS = 7.5 / 2 * MM  # mm
HEIGHT = 63 * MM  # mm

CHOP_LENGTH = 220 * MM  # mm
CHOP_WIDTH = 160 * MM  # mm
CHOP_CORNER_RADIUS = 35 * MM  # mm
CHOP_HEIGHT = (HEIGHT - 7) * MM  # mm

SIDE_DOUBLE_LENGTH = 75 * MM  # mm from outside edge of bin wall to edge of cutout.
SIDE_HALF_LENGTH = (BASE_LENGTH * 42 * MM) / 2  # mm from centerline to outside edge of bin wall.
CUTOUT_LENGTH = SIDE_HALF_LENGTH - SIDE_DOUBLE_LENGTH  # mm from centerline to edge of cutout.
CUTOUT_RADIUS = 12.5 * MM  # mm radius of side cutout arc
CUTOUT_ARC = CUTOUT_LENGTH + CUTOUT_RADIUS + 0.1 * MM  # mm from centerline to edge of cutout arc.


@dataclass(slots=True)
class BinParameters:
    """Input contract for building a parametric chopping-board bin."""

    grid_length_units: int = BASE_LENGTH
    grid_width_units: int = BASE_WIDTH
    bin_height_mm: float = CHOP_HEIGHT
    chop_length_mm: float = CHOP_LENGTH
    chop_width_mm: float = CHOP_WIDTH
    chop_corner_radius_mm: float = CHOP_CORNER_RADIUS
    base_corner_radius_mm: float = BASE_CORNER_RADIUS
    cutout_offset_from_edge_mm: float = SIDE_DOUBLE_LENGTH
    cutout_radius_mm: float = CUTOUT_RADIUS
    cutout_depth_mm: float = 20.0

    @property
    def side_half_length_mm(self) -> float:
        """Return the half-length of the bin side from centerline to outside edge."""
        return (self.grid_length_units * 42 * MM) / 2

    @property
    def cutout_length_mm(self) -> float:
        """Return the length of the cutout."""
        return self.side_half_length_mm - self.cutout_offset_from_edge_mm

    @property
    def cutout_arc_mm(self) -> float:
        """Return the arc length of the cutout."""
        return self.cutout_length_mm + self.cutout_radius_mm + (0.1 * MM)

    def validate(self) -> None:
        """Validate parameter ranges and combinations for printable geometry."""
        errors: list[str] = []

        if not 1 <= self.grid_length_units <= 12:
            errors.append("grid_length_units must be between 1 and 12")
        if not 1 <= self.grid_width_units <= 12:
            errors.append("grid_width_units must be between 1 and 12")

        if not 7.0 < self.bin_height_mm <= 200.0:
            errors.append("bin_height_mm must be greater than 7 and at most 200")

        if self.chop_length_mm <= 0:
            errors.append("chop_length_mm must be greater than 0")
        if self.chop_width_mm <= 0:
            errors.append("chop_width_mm must be greater than 0")

        max_outer_length = self.grid_length_units * 42 * MM
        max_outer_width = self.grid_width_units * 42 * MM
        if self.chop_length_mm >= max_outer_length:
            errors.append("chop_length_mm must be smaller than the outer bin length")
        if self.chop_width_mm >= max_outer_width:
            errors.append("chop_width_mm must be smaller than the outer bin width")

        max_corner = min(self.chop_length_mm, self.chop_width_mm) / 2
        if not 0 <= self.chop_corner_radius_mm <= max_corner:
            errors.append(
                "chop_corner_radius_mm must be between 0 and half of the smaller chop dimension"
            )

        if not 0 <= self.base_corner_radius_mm <= (min(max_outer_length, max_outer_width) / 2):
            errors.append(
                "base_corner_radius_mm must be between 0 and half of the smaller outer bin dimension"
            )

        if self.cutout_offset_from_edge_mm <= 0:
            errors.append("cutout_offset_from_edge_mm must be greater than 0")
        if self.cutout_radius_mm <= 0:
            errors.append("cutout_radius_mm must be greater than 0")
        if self.cutout_depth_mm <= 0:
            errors.append("cutout_depth_mm must be greater than 0")

        if self.cutout_length_mm <= 0:
            errors.append(
                "cutout_offset_from_edge_mm is too large for grid_length_units; it must leave room for a cutout"
            )

        if (self.cutout_length_mm + self.cutout_radius_mm) >= self.side_half_length_mm:
            errors.append(
                "cutout_offset_from_edge_mm and cutout_radius_mm are incompatible "
                "for this grid_length_units"
            )

        if errors:
            raise ValueError("Invalid bin parameters: " + "; ".join(errors))


class ChopProfile(BaseSketchObject):
    def __init__(
        self,
        *,
        cutout_length: float,
        chop_height: float,
        cutout_arc: float,
        cutout_radius: float,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        """Build the side cutout profile used on both long faces."""
        with BuildSketch() as chop_profile:
            with BuildLine():
                FilletPolyline(
                    (0, 0),
                    (cutout_length, 0),
                    (cutout_length, chop_height),
                    (cutout_arc, chop_height),
                    radius=cutout_radius,
                )
                Line(
                    (0, chop_height),
                    (cutout_arc, chop_height),
                )
                mirror(about=Plane.YZ)
            make_face()
        super().__init__(chop_profile.face(), rotation, align, mode)


class ChopBin(BasePartObject):
    """Gridfinity Bin object with compartment for storing chopping boards."""

    def __init__(
        self,
        params: BinParameters | None = None,
        height: float = 0,
        height_in_units: int = 0,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        """Construct a custom bin object."""
        if params is not None and (height or height_in_units):
            msg = "params cannot be combined with height or height_in_units"
            raise ValueError(msg)

        if height and height_in_units:
            msg = "height or height_in_units can be defined, not both"
            raise ValueError(msg)

        if params is None:
            bin_height = height_in_units * 7 if height_in_units else height
            params = BinParameters(bin_height_mm=bin_height)

        params.validate()

        with BuildPart() as build:
            add(
                BaseEqual(
                    grid_x=params.grid_width_units,
                    grid_y=params.grid_length_units,
                    rotation=rotation,
                    align=align,
                    mode=mode,
                )
            )

            with BuildSketch(build.faces().sort_by(Axis.Z)[-1]) as chop_sketch:
                RectangleRounded(
                    height=params.grid_length_units * 42 * MM,
                    width=params.grid_width_units * 42 * MM,
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

            extrude(to_extrude=chop_sketch.face(), amount=params.bin_height_mm)

            side_faces = [
                build.faces().sort_by(Axis.X)[0],
                build.faces().sort_by(Axis.X)[-1],
            ]
            with BuildSketch(side_faces) as side_sketch:
                ChopProfile(
                    cutout_length=params.cutout_length_mm,
                    chop_height=params.bin_height_mm,
                    cutout_arc=params.cutout_arc_mm,
                    cutout_radius=params.cutout_radius_mm,
                    align=(Align.CENTER, Align.MIN),
                )

            extrude(
                to_extrude=side_sketch.faces(),
                amount=-params.cutout_depth_mm,
                mode=Mode.SUBTRACT,
            )

        super().__init__(build.part, rotation, align, mode)

    @property
    def top(self) -> object:
        """Return the highest face of the bin."""
        return self.faces().sort_by(Axis.Z)[-1]

    @property
    def bottom(self) -> object:
        """Return the lowest face of the bin."""
        return self.faces().sort_by(Axis.Z)[0]

    @property
    def front(self) -> object:
        """Return the front face of the bin (minimum Y)."""
        return self.faces().sort_by(Axis.Y)[0]

    @property
    def back(self) -> object:
        """Return the back face of the bin (maximum Y)."""
        return self.faces().sort_by(Axis.Y)[-1]

    @property
    def left(self) -> object:
        """Return the left face of the bin (minimum X)."""
        return self.faces().sort_by(Axis.X)[0]

    @property
    def right(self) -> object:
        """Return the right face of the bin (maximum X)."""
        return self.faces().sort_by(Axis.X)[-1]


def create_chop_bin(params: BinParameters | None = None) -> ChopBin:
    """Create a chopping-board bin from validated parameters."""
    return ChopBin(params=params or BinParameters())


if __name__ == "__main__":
    chop_block = create_chop_bin()
    show(chop_block)
    # export_stl(chop_block, "chop_block.stl")
