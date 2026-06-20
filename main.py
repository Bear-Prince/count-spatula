"""CLI entry point for parametric Gridfinity kitchen bin generation."""

import argparse
import sys
from pathlib import Path

from build123d.mesher import Mesher
from build123d.topology import Shape

from chop_bin import BinParameters, create_chop_bin
from utensil_bin import UtensilBinParameters, check_print_bed, create_utensil_bin


def export_bin(part: Shape, output_path: Path) -> Path:
    """Export bin geometry to STL or 3MF, selected by the output file extension."""
    mesher = Mesher()
    mesher.add_shape(part)
    mesher.write(output_path)
    return output_path


# ---------------------------------------------------------------------------
# Chopping-board bin
# ---------------------------------------------------------------------------


def _build_chop_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the chopping-board bin command."""
    parser = argparse.ArgumentParser(
        description="Generate a Gridfinity-compatible chopping-board bin as STL or 3MF.",
    )
    defaults = BinParameters()
    parser.add_argument("--grid-length", type=int, default=defaults.grid_length_units)
    parser.add_argument("--grid-width", type=int, default=defaults.grid_width_units)
    parser.add_argument("--height-mm", type=float, default=defaults.bin_height_mm)
    parser.add_argument("--chop-length-mm", type=float, default=defaults.chop_length_mm)
    parser.add_argument("--chop-width-mm", type=float, default=defaults.chop_width_mm)
    parser.add_argument("--chop-corner-radius-mm", type=float, default=defaults.chop_corner_radius_mm)
    parser.add_argument("--base-corner-radius-mm", type=float, default=defaults.base_corner_radius_mm)
    parser.add_argument("--cutout-offset-mm", type=float, default=defaults.cutout_offset_from_edge_mm)
    parser.add_argument("--cutout-radius-mm", type=float, default=defaults.cutout_radius_mm)
    parser.add_argument(
        "--format",
        choices=["stl", "3mf"],
        default="stl",
        help="Output file format when --output is omitted. Default: stl.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path. If omitted, a deterministic filename is used in the current directory.",
    )
    return parser


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the chopping-board bin command (public alias)."""
    return _build_chop_parser()


def create_parameters(args: argparse.Namespace) -> BinParameters:
    """Build BinParameters from parsed CLI arguments (public alias)."""
    return BinParameters(
        grid_length_units=args.grid_length,
        grid_width_units=args.grid_width,
        bin_height_mm=args.height_mm,
        chop_length_mm=args.chop_length_mm,
        chop_width_mm=args.chop_width_mm,
        chop_corner_radius_mm=args.chop_corner_radius_mm,
        base_corner_radius_mm=args.base_corner_radius_mm,
        cutout_offset_from_edge_mm=args.cutout_offset_mm,
        cutout_radius_mm=args.cutout_radius_mm,
    )


def default_output_path(params: BinParameters, fmt: str = "stl") -> Path:
    """Build a deterministic default output path for the generated chop bin."""
    height_token = f"{params.bin_height_mm:g}".replace(".", "p")
    file_name = f"chop_bin_{params.grid_length_units}x{params.grid_width_units}_h{height_token}.{fmt}"
    return Path.cwd() / file_name


def _run_chop_bin(argv: list[str] | None = None) -> int:
    """Parse arguments, build, export a chop bin, and return a process exit code."""
    parser = _build_chop_parser()
    args = parser.parse_args(argv)

    try:
        params = create_parameters(args)
        params.validate()
        output_path = args.output if args.output is not None else default_output_path(params, args.format)
        if not output_path.parent.exists():
            msg = f"Output directory does not exist: {output_path.parent}"
            raise FileNotFoundError(msg)
        part = create_chop_bin(params)
        exported_file = export_bin(part, output_path)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}")
        return 2
    except OSError as exc:
        print(f"Error: Failed to write output: {exc}")
        return 2

    print(f"Exported: {exported_file}")
    return 0


# ---------------------------------------------------------------------------
# Utensil bin
# ---------------------------------------------------------------------------


def _build_utensil_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the utensil-bin sub-command."""
    parser = argparse.ArgumentParser(
        description="Generate a Gridfinity-compatible open-top utensil bin as STL or 3MF.",
    )
    defaults = UtensilBinParameters()
    parser.add_argument("--grid-x", type=int, default=defaults.grid_x)
    parser.add_argument("--grid-y", type=int, default=defaults.grid_y)
    height_group = parser.add_mutually_exclusive_group()
    height_group.add_argument(
        "--height-units",
        type=int,
        default=defaults.height_in_units,
        help="Height in Gridfinity units (multiples of 7 mm). Default: 7.",
    )
    height_group.add_argument(
        "--height-mm",
        type=float,
        default=None,
        help="Freeform height in mm. Mutually exclusive with --height-units.",
    )
    parser.add_argument("--div-x", type=int, default=defaults.div_x)
    parser.add_argument("--div-y", type=int, default=defaults.div_y)
    parser.add_argument("--wall-thickness-mm", type=float, default=defaults.wall_thickness_mm)
    parser.add_argument("--bed-x", type=float, default=None, help="Print bed X dimension in mm.")
    parser.add_argument("--bed-y", type=float, default=None, help="Print bed Y dimension in mm.")
    parser.add_argument(
        "--format",
        choices=["stl", "3mf"],
        default="stl",
        help="Output file format when --output is omitted. Default: stl.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path. If omitted, a deterministic filename is used in the current directory.",
    )
    return parser


def _utensil_params_from_args(args: argparse.Namespace) -> UtensilBinParameters:
    """Build UtensilBinParameters from parsed utensil-bin CLI arguments."""
    if args.height_mm is not None:
        return UtensilBinParameters(
            grid_x=args.grid_x,
            grid_y=args.grid_y,
            height_in_units=None,
            height_mm=args.height_mm,
            div_x=args.div_x,
            div_y=args.div_y,
            wall_thickness_mm=args.wall_thickness_mm,
        )
    return UtensilBinParameters(
        grid_x=args.grid_x,
        grid_y=args.grid_y,
        height_in_units=args.height_units,
        height_mm=None,
        div_x=args.div_x,
        div_y=args.div_y,
        wall_thickness_mm=args.wall_thickness_mm,
    )


def default_utensil_output_path(params: UtensilBinParameters, fmt: str = "stl") -> Path:
    """Build a deterministic default output path for the generated utensil bin."""
    height_token = f"{params.effective_height_mm:g}".replace(".", "p")
    file_name = f"utensil_bin_{params.grid_x}x{params.grid_y}_h{height_token}.{fmt}"
    return Path.cwd() / file_name


def _run_utensil_bin(argv: list[str] | None = None) -> int:
    """Parse arguments, build, export a utensil bin, and return a process exit code."""
    parser = _build_utensil_parser()
    args = parser.parse_args(argv)

    try:
        params = _utensil_params_from_args(args)
        params.validate()
        output_path = args.output if args.output is not None else default_utensil_output_path(params, args.format)
        if not output_path.parent.exists():
            msg = f"Output directory does not exist: {output_path.parent}"
            raise FileNotFoundError(msg)
        if args.bed_x is not None and args.bed_y is not None:
            warnings = check_print_bed(params.grid_x, params.grid_y, args.bed_x, args.bed_y)
            for warning in warnings:
                print(f"Warning: {warning}", file=sys.stderr)
        part = create_utensil_bin(params)
        exported_file = export_bin(part, output_path)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}")
        return 2
    except OSError as exc:
        print(f"Error: Failed to write output: {exc}")
        return 2

    print(f"Exported: {exported_file}")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Route to the chop-bin or utensil-bin handler and return a process exit code."""
    args_list: list[str] = argv if argv is not None else sys.argv[1:]
    if args_list and args_list[0] == "utensil-bin":
        return _run_utensil_bin(args_list[1:])
    return _run_chop_bin(args_list)


if __name__ == "__main__":
    raise SystemExit(main())
