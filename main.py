from build123d import export_stl
from ocp_vscode import show_all
from gridfinity_build123d import (
    BaseEqual,
    Bin,
    Compartment,
    CompartmentsEqual,
)

part = Bin(
    BaseEqual(grid_x=6, grid_y=4),
    height=63,
    compartments=CompartmentsEqual(compartment_list=[Compartment()]),
)
show_all()
export_stl(part, "chopping_blocks_6x4.stl")
