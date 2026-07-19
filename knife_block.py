"""Parametric Gridfinity knife blade block.

A ``KnifeBladeBlock`` holds kitchen knives lying flat, edge-down, gripped by their blades rather than
their handles. Knives alternate head-to-toe so their handles fall to opposite ends; every blade passes
through a single central block of tapered, self-centring slots. Only the block is generated -- the
generic handle-rest zones at each end are out of scope, composed instead from stock
``gridfinity_build123d`` blanks. See ``openspec/changes/knife-blade-block/design.md`` for the design
decisions behind this shape.
"""

from dataclasses import dataclass

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BaseSketchObject,
    BuildLine,
    BuildPart,
    BuildSketch,
    Line,
    Mode,
    Plane,
    RotationLike,
    add,
    extrude,
    make_face,
)
from gridfinity_build123d import BaseEqual

from cutlery_bin import BASE_CORNER_RADIUS, GRIDFINITY_CLEARANCE_MM, GRIDFINITY_PITCH_MM, rounded_panel

# Defaults sized for the target 7-knife Prima set (2-3 mm spines, ~26 mm handles); see
# notebooks/knife_block.ipynb for the geometry prototype these were validated against.
DEFAULT_KNIFE_COUNT = 7
DEFAULT_HANDLE_WIDTH_MM = 26.0  # mm; measured max handle width across the target set.
DEFAULT_HANDLE_GAP_MM = 10.0  # mm; finger clearance between two same-end handles.
MIN_HANDLE_GAP_MM = 2.0  # mm; minimum printable/usable finger clearance.
DEFAULT_GRID_X = 3  # Gridfinity units wide (across lanes).
DEFAULT_GRID_Y = 2  # Gridfinity units long (along the blade axis).
DEFAULT_MAX_SPINE_MM = 3.0  # mm; thickest supported blade spine.
DEFAULT_MIN_SPINE_MM = 2.0  # mm; thinnest supported blade spine.
DEFAULT_SLOT_MOUTH_CLEARANCE_MM = 1.5  # mm added to max_spine_mm so the mouth freely admits it.
DEFAULT_SLOT_APEX_CLEARANCE_MM = 1.0  # mm subtracted from min_spine_mm so the relief stays narrower.
DEFAULT_TAPER_DEPTH_MM = 12.0  # mm; vertical extent of the sloped part of the V.
DEFAULT_RELIEF_DEPTH_MM = 3.0  # mm; constant-width channel below the taper where the edge floats.
DEFAULT_MIN_DECK_THICKNESS_MM = 3.0  # mm; solid material required below the relief for strength.
DEFAULT_LANE_MARGIN_MM = 3.0  # mm; solid margin outboard of the outermost slot's mouth, each side.


@dataclass(slots=True)
class KnifeBlockParameters:
    """Input contract for building a parametric knife blade block.

    ``grid_x`` runs across the lanes and ``grid_y`` along the blade axis, matching the Gridfinity base
    convention used by ``BinParameters``. Lanes are laid out side by side across ``grid_x``; each blade
    runs the full length of the block along ``grid_y``.
    """

    knife_count: int = DEFAULT_KNIFE_COUNT
    handle_width_mm: float = DEFAULT_HANDLE_WIDTH_MM
    handle_gap_mm: float = DEFAULT_HANDLE_GAP_MM
    grid_x: int = DEFAULT_GRID_X
    grid_y: int = DEFAULT_GRID_Y
    max_spine_mm: float = DEFAULT_MAX_SPINE_MM
    min_spine_mm: float = DEFAULT_MIN_SPINE_MM
    slot_mouth_clearance_mm: float = DEFAULT_SLOT_MOUTH_CLEARANCE_MM
    slot_apex_clearance_mm: float = DEFAULT_SLOT_APEX_CLEARANCE_MM
    taper_depth_mm: float = DEFAULT_TAPER_DEPTH_MM
    relief_depth_mm: float = DEFAULT_RELIEF_DEPTH_MM
    min_deck_thickness_mm: float = DEFAULT_MIN_DECK_THICKNESS_MM
    lane_margin_mm: float = DEFAULT_LANE_MARGIN_MM
    base_corner_radius_mm: float = BASE_CORNER_RADIUS

    @property
    def lane_pitch_mm(self) -> float:
        """Return the centre-to-centre lane pitch.

        Knives alternate head-to-toe, so two same-end handles sit two lanes apart rather than one --
        halving the pitch a handle would otherwise force. See design.md Decision 1.
        """
        return (self.handle_width_mm + self.handle_gap_mm) / 2

    @property
    def footprint_width_mm(self) -> float:
        """Return the block's outer footprint width (X), following the Gridfinity clearance convention."""
        return self.grid_x * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM

    @property
    def footprint_length_mm(self) -> float:
        """Return the block's outer footprint length (Y), following the Gridfinity clearance convention."""
        return self.grid_y * GRIDFINITY_PITCH_MM - GRIDFINITY_CLEARANCE_MM

    @property
    def slot_mouth_width_mm(self) -> float:
        """Return the V-slot's width at its mouth (top), sized to admit the thickest supported spine."""
        return self.max_spine_mm + self.slot_mouth_clearance_mm

    @property
    def slot_apex_width_mm(self) -> float:
        """Return the relief channel's width, kept narrower than the thinnest supported spine."""
        return self.min_spine_mm - self.slot_apex_clearance_mm

    @property
    def slot_total_depth_mm(self) -> float:
        """Return the slot's total depth: the tapered section plus the constant-width relief channel."""
        return self.taper_depth_mm + self.relief_depth_mm

    @property
    def deck_height_mm(self) -> float:
        """Return the block's effective height above the Gridfinity floor.

        This is the one interface between the generated block and the user-supplied
        ``gridfinity_build123d`` blanks that fill the handle zones: a blank of this height keeps the
        knives resting level. See design.md Decision 4.
        """
        return self.slot_total_depth_mm + self.min_deck_thickness_mm

    @property
    def lanes_required_width_mm(self) -> float:
        """Return the physical width needed to fit every lane with its outer margins."""
        return (self.knife_count - 1) * self.lane_pitch_mm + self.slot_mouth_width_mm + 2 * self.lane_margin_mm

    def validate(self) -> None:
        """Validate parameter ranges and combinations for printable, usable geometry."""
        errors: list[str] = []

        if self.knife_count < 1:
            errors.append("knife_count must be at least 1")
        if not 1 <= self.grid_x <= 12:
            errors.append("grid_x must be between 1 and 12")
        if not 1 <= self.grid_y <= 12:
            errors.append("grid_y must be between 1 and 12")

        if self.handle_width_mm <= 0:
            errors.append("handle_width_mm must be greater than 0")
        if self.handle_gap_mm < MIN_HANDLE_GAP_MM:
            errors.append(f"handle_gap_mm must be at least {MIN_HANDLE_GAP_MM:g} mm (finger clearance)")

        if self.max_spine_mm <= 0:
            errors.append("max_spine_mm must be greater than 0")
        if self.min_spine_mm <= 0:
            errors.append("min_spine_mm must be greater than 0")
        elif self.min_spine_mm > self.max_spine_mm:
            errors.append("min_spine_mm must not exceed max_spine_mm")

        if self.slot_mouth_clearance_mm <= 0:
            errors.append("slot_mouth_clearance_mm must be greater than 0 (it admits the thickest spine)")
        if self.slot_apex_clearance_mm <= 0:
            errors.append("slot_apex_clearance_mm must be greater than 0 (it narrows the relief)")
        elif self.slot_apex_width_mm <= 0:
            errors.append("slot_apex_width_mm must be greater than 0; reduce slot_apex_clearance_mm")

        if self.taper_depth_mm <= 0:
            errors.append("taper_depth_mm must be greater than 0")
        if self.relief_depth_mm <= 0:
            errors.append("relief_depth_mm must be greater than 0")
        if self.min_deck_thickness_mm <= 0:
            errors.append("min_deck_thickness_mm must be greater than 0")
        if self.lane_margin_mm < 0:
            errors.append("lane_margin_mm must be at least 0")

        fits_ok = not errors and self.knife_count >= 1 and self.slot_mouth_width_mm > 0
        if fits_ok and self.lanes_required_width_mm > self.footprint_width_mm:
            errors.append(
                f"grid_x is too narrow for {self.knife_count} lanes at this pitch; needs "
                f"{self.lanes_required_width_mm:.1f} mm but the footprint is only "
                f"{self.footprint_width_mm:.1f} mm -- increase grid_x or reduce knife_count, "
                "handle_width_mm, or handle_gap_mm"
            )

        if errors:
            raise ValueError("Invalid knife block parameters: " + "; ".join(errors))


class KnifeSlotProfile(BaseSketchObject):
    """The tapered, self-centring knife slot profile.

    A V from the mouth (wide, at local Y=0) narrowing to a constant-width relief channel (local Y from
    ``taper_depth`` to ``taper_depth + relief_depth``), symmetric about local X=0. A blade wedges at the
    depth where the taper's width equals its own spine thickness -- a thicker blade wedges shallower, a
    thinner one sinks deeper -- and the relief channel, narrower than any supported spine, keeps the
    cutting edge floating clear of the block material. See design.md Decision 3.
    """

    def __init__(
        self,
        *,
        mouth_width: float,
        apex_width: float,
        taper_depth: float,
        relief_depth: float,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        """Build the knife slot profile."""
        relief_bottom = taper_depth + relief_depth
        with BuildSketch() as profile:
            with BuildLine():
                Line((-mouth_width / 2, 0), (mouth_width / 2, 0))
                Line((mouth_width / 2, 0), (apex_width / 2, taper_depth))
                Line((apex_width / 2, taper_depth), (apex_width / 2, relief_bottom))
                Line((apex_width / 2, relief_bottom), (-apex_width / 2, relief_bottom))
                Line((-apex_width / 2, relief_bottom), (-apex_width / 2, taper_depth))
                Line((-apex_width / 2, taper_depth), (-mouth_width / 2, 0))
            make_face()
        super().__init__(profile.sketch, rotation, align, mode)


class KnifeBladeBlock(BasePartObject):
    """A Gridfinity module that holds knives by their blades in tapered, self-centring slots.

    Only the block is generated; the generic handle-rest zones at each end are out of scope and are
    composed from stock ``gridfinity_build123d`` blanks matched to ``deck_height_mm``. Every lane's slot
    is identical and symmetric along its length, so alternating knife handles between adjacent lanes is a
    loading pattern, not a feature encoded in the block's own geometry. See design.md.
    """

    def __init__(
        self,
        params: KnifeBlockParameters | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        """Construct the block from validated parameters."""
        if params is None:
            params = KnifeBlockParameters()
        params.validate()

        with BuildPart() as build:
            # This inner Mode.ADD is independent of the `mode` parameter, which controls how the
            # finished block combines into an enclosing build context (see super().__init__ below).
            add(BaseEqual(grid_x=params.grid_x, grid_y=params.grid_y, mode=Mode.ADD))

            base_top = build.faces().sort_by(Axis.Z)[-1]

            with BuildSketch(base_top) as block_sketch:
                rounded_panel(params.footprint_width_mm, params.footprint_length_mm, params.base_corner_radius_mm)
            extrude(to_extrude=block_sketch.face(), amount=params.deck_height_mm)
            top_z = build.part.bounding_box().max.Z

            # Lane centrelines are evenly spaced across X, symmetric about the block's own centre.
            lane_span = (params.knife_count - 1) * params.lane_pitch_mm
            lane_start = -lane_span / 2
            half_length = params.footprint_length_mm / 2
            for index in range(params.knife_count):
                lane_x = lane_start + index * params.lane_pitch_mm
                # build123d's y_dir = cross(z_dir, x_dir): with x_dir=world X and z_dir=world Y, the
                # sketch's local Y maps to world -Z, so local (u, v) is (blade-thickness, depth-downward)
                # with the origin at this lane's slot mouth on the block's top surface.
                cut_plane = Plane(origin=(lane_x, 0, top_z), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
                with BuildSketch(cut_plane) as slot_sketch:
                    KnifeSlotProfile(
                        mouth_width=params.slot_mouth_width_mm,
                        apex_width=params.slot_apex_width_mm,
                        taper_depth=params.taper_depth_mm,
                        relief_depth=params.relief_depth_mm,
                    )
                extrude(
                    to_extrude=slot_sketch.sketch.faces(),
                    amount=half_length + 1,
                    both=True,
                    mode=Mode.SUBTRACT,
                )

        super().__init__(build.part, rotation, align, mode)


def create_knife_blade_block(params: KnifeBlockParameters | None = None) -> KnifeBladeBlock:
    """Create a knife blade block from validated parameters."""
    return KnifeBladeBlock(params=params)


def check_drawer_clearance(
    deck_height_mm: float,
    max_blade_depth_mm: float,
    clearance_mm: float,
    drawer_height_mm: float,
) -> list[str]:
    """Return a warning if the occupied height would not clear a drawer's internal height.

    Mirrors ``check_print_bed``: the module is evaluated upright, as generated (no rotation). The
    occupied height is ``deck_height_mm + max_blade_depth_mm + clearance_mm`` -- the block's own height
    plus how far the tallest supported blade reaches above it, plus a safety margin. Returns an empty
    list when the occupied height is within the drawer's internal height.
    """
    occupied_mm = deck_height_mm + max_blade_depth_mm + clearance_mm
    if occupied_mm > drawer_height_mm:
        return [
            f"Occupied height ({occupied_mm:.1f} mm) exceeds the drawer's internal height "
            f"({drawer_height_mm:.1f} mm) by {occupied_mm - drawer_height_mm:.1f} mm."
        ]
    return []
