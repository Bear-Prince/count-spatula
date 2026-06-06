import argparse
from pathlib import Path

from build123d import export_stl

from chop_bin import BinParameters, create_chop_bin


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for parametric chopping bin generation."""
    parser = argparse.ArgumentParser(
        description="Generate Gridfinity-compatible kitchen utensil bins as STL files.",
    )
    parser.add_argument("--grid-length", type=int, default=BinParameters().grid_length_units)
    parser.add_argument("--grid-width", type=int, default=BinParameters().grid_width_units)
    parser.add_argument("--height-mm", type=float, default=BinParameters().bin_height_mm)
    parser.add_argument("--chop-length-mm", type=float, default=BinParameters().chop_length_mm)
    parser.add_argument("--chop-width-mm", type=float, default=BinParameters().chop_width_mm)
    parser.add_argument("--chop-corner-radius-mm", type=float, default=BinParameters().chop_corner_radius_mm)
    parser.add_argument("--base-corner-radius-mm", type=float, default=BinParameters().base_corner_radius_mm)
    parser.add_argument("--cutout-offset-mm", type=float, default=BinParameters().cutout_offset_from_edge_mm)
    parser.add_argument("--cutout-radius-mm", type=float, default=BinParameters().cutout_radius_mm)
    parser.add_argument("--cutout-depth-mm", type=float, default=BinParameters().cutout_depth_mm)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output STL path. If omitted, a deterministic filename is used in the current directory.",
    )
    return parser


def create_parameters(args: argparse.Namespace) -> BinParameters:
    """Create a parameter object from CLI arguments."""
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
        cutout_depth_mm=args.cutout_depth_mm,
    )


def default_output_path(params: BinParameters) -> Path:
    """Build a deterministic default output path for the generated STL."""
    height_token = f"{params.bin_height_mm:g}".replace(".", "p")
    file_name = f"chop_bin_{params.grid_length_units}x{params.grid_width_units}_h{height_token}.stl"
    return Path.cwd() / file_name


def export_bin(params: BinParameters, output_path: Path) -> Path:
    """Generate and export a chopping bin as STL."""
    params.validate()
    output_parent = output_path.parent
    if not output_parent.exists():
        msg = f"Output directory does not exist: {output_parent}"
        raise FileNotFoundError(msg)

    part = create_chop_bin(params)
    export_stl(part, str(output_path))
    return output_path


def main(argv: list[str] | None = None) -> int:
    """Run CLI and return process-compatible exit status."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        params = create_parameters(args)
        output_path = args.output if args.output is not None else default_output_path(params)
        exported_file = export_bin(params, output_path)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}")
        return 2
    except OSError as exc:
        print(f"Error: Failed to write STL output: {exc}")
        return 2

    print(f"Exported STL: {exported_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
