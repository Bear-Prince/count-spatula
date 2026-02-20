from build123d import (
    Align,
    Axis,
    BuildPart,
    BasePartObject,
    BuildLine,
    BuildSketch,
    BaseSketchObject,
    FilletPolyline,
    Line,
    MM,
    Mode,
    Plane,
    RectangleRounded,
    RotationLike,
    add,
    extrude,
    export_stl,
    make_face,
    mirror,
)
from ocp_vscode import show
from gridfinity_build123d import BaseEqual

BASE_LENGTH = 6 # Units
BASE_WIDTH = 4 # Units
BASE_CORNER_RADIUS = 7.5 / 2 * MM # mm
HEIGHT = 63 * MM # mm

CHOP_LENGTH = 220 * MM # mm
CHOP_WIDTH  = 160 * MM # mm
CHOP_CORNER_RADIUS = 35 * MM # mm
CHOP_HEIGHT = (HEIGHT - 7) * MM # mm

SIDE_DOUBLE_LENGTH = 75 * MM # mm from outside edge of bin wall to edge of cutout
SIDE_HALF_LENGTH = (BASE_LENGTH * 42 * MM) / 2 # mm from centerline to outside edge of bin wall
CUTOUT_LENGTH = SIDE_HALF_LENGTH - SIDE_DOUBLE_LENGTH # mm from centerline to edge of cutout 
CUTOUT_RADIUS = 12.5 * MM # mm radius of side cutout arc
CUTOUT_ARC = CUTOUT_LENGTH + CUTOUT_RADIUS + 0.1 * MM # mm from centerline to edge of cutout arc

class ChopProfile(BaseSketchObject):
    def __init__(self, rotation: RotationLike = (0, 0, 0), align: Align | tuple[Align, Align] | None = None, mode: Mode = Mode.ADD):
        with BuildSketch() as chop_profile:
            with BuildLine():
                FilletPolyline(
                    (0, 0),
                    (CUTOUT_LENGTH, 0),
                    (CUTOUT_LENGTH, CHOP_HEIGHT),
                    (CUTOUT_ARC, CHOP_HEIGHT),
                    radius=CUTOUT_RADIUS,
                )
                Line(
                    (0, CHOP_HEIGHT),
                    (CUTOUT_ARC, CHOP_HEIGHT),
                )
                mirror(about=Plane.YZ)
            make_face()
        super().__init__(chop_profile.face(), rotation, align, mode)

class ChopBin(BasePartObject):
    """Gridfinity Bin object with quirky compartment for storing IKEA chopping boards."""

    def __init__(
        self,
        height: float = 0,
        height_in_units: int = 0,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct a custom bin object.

        Args:
            base (Part): Base object on which the bin is constructed.
            height (float, optional): Height of the bin in mm. Can't be used when height_in_units is
                defined.Defaults to 0.
            height_in_units (int, optional): Heigth defined by gridfinity units. Can't be used when
                height is defined. Defaults to 0.
            compartment (Compartment | None): Custom compartment of the bin, Defaults to None.
            rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
            of object. Defaults to None.
            mode (Mode, optional): combination mode. Defaults to Mode.ADD.
        """
        if height and height_in_units:
            msg = "height or height_in_units can be defined, not both"
            raise ValueError(msg)
        if height_in_units:
            bin_height = height_in_units * 7
        else:
            bin_height = height

        with BuildPart() as bin:
            # Add the base
            add(
                BaseEqual(
                    grid_x=BASE_WIDTH, 
                    grid_y=BASE_LENGTH,
                    rotation=rotation,
                    align=align,
                    mode=mode
                )
            )
            # Add a sketch on top for the chop compartment
            with BuildSketch(bin.faces().sort_by(Axis.Z)[-1]) as chop_sketch:

                RectangleRounded(
                    height=BASE_LENGTH * 42 * MM, 
                    width=BASE_WIDTH * 42 * MM,
                    radius=BASE_CORNER_RADIUS * MM,
                    align=(Align.CENTER, Align.CENTER)
                )
                RectangleRounded(
                    height=CHOP_LENGTH * MM, 
                    width=CHOP_WIDTH * MM,
                    radius=CHOP_CORNER_RADIUS * MM,
                    mode=Mode.SUBTRACT,
                    align=(Align.CENTER, Align.CENTER)
                )
            # Extrude the bin to the specified height
            extrude(to_extrude=chop_sketch.face(), amount=bin_height)
            # Add the cutout on the side for the chopping boards
            side_faces = [
                bin.faces().sort_by(Axis.X)[0],
                bin.faces().sort_by(Axis.X)[-1],
            ]
            with BuildSketch(side_faces) as side_sketch:
                ChopProfile(align=(Align.CENTER, Align.MIN))

            # Extrude the cutout from long side of bin
            extrude(to_extrude=side_sketch.faces(), amount=-20, mode=Mode.SUBTRACT)

        super().__init__(bin.part, rotation, align, mode)

    @property
    def top(self):
        return self.faces().sort_by(Axis.Z)[-1]

    @property
    def bottom(self):
        return self.faces().sort_by(Axis.Z)[0]

    @property
    def front(self):
        return self.faces().sort_by(Axis.Y)[0]

    @property
    def back(self):
        return self.faces().sort_by(Axis.Y)[-1]

    @property
    def left(self):
        return self.faces().sort_by(Axis.X)[0]

    @property
    def right(self):
        return self.faces().sort_by(Axis.X)[-1]

if __name__ == "__main__":
    chop_block = ChopBin(
        height=CHOP_HEIGHT
    )
    show(chop_block)
    # export_stl(chop_block, "chop_block.stl")
