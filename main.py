import build123d
from gridfinity_build123d import (
    BaseEqual,
    Bin,
    Compartment,
    CompartmentsEqual,
)

part = Bin(
    BaseEqual(grid_x=2, grid_y=1),
    height_in_units=3,
    compartments=CompartmentsEqual(compartment_list=[Compartment()]),
)

build123d.export_stl(part, "bin_2x1x3.stl")
