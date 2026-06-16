"""Parametric Gridfinity-compatible open-top utensil bin geometry."""

from dataclasses import dataclass

from build123d import Align, BasePartObject, Mode, RotationLike
from gridfinity_build123d import BaseEqual, Bin, CompartmentsEqual

GRIDFINITY_UNIT_MM: int = 42  # Millimetres per Gridfinity grid unit.
GRIDFINITY_HEIGHT_UNIT_MM: int = 7  # Millimetres per Gridfinity height unit.


@dataclass(slots=True)
class UtensilBinParameters:
    """Input contract for building a parametric open-top utensil bin."""

    grid_x: int = 2
    grid_y: int = 4
    height_in_units: int | None = 7
    height_mm: float | None = None
    div_x: int = 1
    div_y: int = 1
    wall_thickness_mm: float = 2.0

    @property
    def effective_height_mm(self) -> float:
        """Resolve the active bin height in millimetres."""
        if self.height_mm is not None:
            return self.height_mm
        return (self.height_in_units or 0) * GRIDFINITY_HEIGHT_UNIT_MM

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

        if self.height_in_units is not None and self.height_in_units < 1:
            errors.append("height_in_units must be at least 1")
        if self.height_mm is not None and self.height_mm <= 0:
            errors.append("height_mm must be greater than 0")

        if self.div_x < 1:
            errors.append("div_x must be at least 1")
        if self.div_y < 1:
            errors.append("div_y must be at least 1")

        if self.wall_thickness_mm <= 0:
            errors.append("wall_thickness_mm must be greater than 0")

        if errors:
            raise ValueError("Invalid utensil bin parameters: " + "; ".join(errors))


class UtensilBin(BasePartObject):
    """Gridfinity open-top utensil bin with configurable compartments and wall thickness."""

    def __init__(
        self,
        params: "UtensilBinParameters | None" = None,
        rotation: RotationLike = (0, 0, 0),
        align: "Align | tuple[Align, Align, Align] | None" = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        """Construct an open-top utensil bin from validated parameters."""
        if params is None:
            params = UtensilBinParameters()
        params.validate()

        base = BaseEqual(grid_x=params.grid_x, grid_y=params.grid_y, mode=Mode.PRIVATE)
        compartments = CompartmentsEqual(
            div_x=params.div_x,
            div_y=params.div_y,
            outer_wall=params.wall_thickness_mm,
            inner_wall=params.wall_thickness_mm,
        )

        if params.height_mm is not None:
            bin_part = Bin(base=base, height=params.height_mm, compartments=compartments, mode=Mode.PRIVATE)
        else:
            bin_part = Bin(
                base=base,
                height_in_units=params.height_in_units,
                compartments=compartments,
                mode=Mode.PRIVATE,
            )

        super().__init__(bin_part, rotation, align, mode)


def create_utensil_bin(params: "UtensilBinParameters | None" = None) -> UtensilBin:
    """Create an open-top utensil bin from validated parameters."""
    return UtensilBin(params=params or UtensilBinParameters())


def check_print_bed(grid_x: int, grid_y: int, bed_x_mm: float, bed_y_mm: float) -> list[str]:
    """Return warning strings when the bin footprint exceeds the configured print bed.

    Returns an empty list when the footprint fits within the bed on both axes.
    """
    footprint_x = grid_x * GRIDFINITY_UNIT_MM
    footprint_y = grid_y * GRIDFINITY_UNIT_MM
    warnings: list[str] = []
    if footprint_x > bed_x_mm:
        warnings.append(
            f"Bin footprint X ({footprint_x} mm) exceeds bed X ({bed_x_mm} mm) "
            f"by {footprint_x - bed_x_mm:.1f} mm."
        )
    if footprint_y > bed_y_mm:
        warnings.append(
            f"Bin footprint Y ({footprint_y} mm) exceeds bed Y ({bed_y_mm} mm) "
            f"by {footprint_y - bed_y_mm:.1f} mm."
        )
    return warnings
