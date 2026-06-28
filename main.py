"""CLI entry point for parametric Gridfinity kitchen/cutlery bin generation."""

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from build123d.mesher import Mesher
from build123d.topology import Shape

from cutlery_bin import (
    BinParameters,
    check_print_bed,
    create_cutlery_bin,
    create_kitchen_bin,
    preset_names,
    preset_requires_cutouts,
    resolve_preset,
)

# Default print volume in millimetres (width x depth x height). Printers quote build volumes in mm,
# so these are plain millimetres with no unit conversion. Override per axis with --bed-x/--bed-y/--bed-z.
DEFAULT_BED_X_MM = 220.0
DEFAULT_BED_Y_MM = 220.0
DEFAULT_BED_Z_MM = 240.0


def export_bin(part: Shape, output_path: Path) -> Path:
    """Export bin geometry to STL or 3MF, selected by the output file extension."""
    mesher = Mesher()
    mesher.add_shape(part)
    mesher.write(output_path)
    return output_path


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for kitchen/cutlery bin generation."""
    parser = argparse.ArgumentParser(
        description="Generate a Gridfinity-compatible kitchen or cutlery bin as STL or 3MF.",
    )
    parser.add_argument(
        "--preset",
        default=None,
        help=f"Seed parameters from a named preset: {', '.join(preset_names())}.",
    )
    parser.add_argument("--grid-x", type=int, default=None)
    parser.add_argument("--grid-y", type=int, default=None)
    height_group = parser.add_mutually_exclusive_group()
    height_group.add_argument(
        "--height-units",
        type=int,
        default=None,
        help="Height in Gridfinity units (7 mm each). Mutually exclusive with --height-mm.",
    )
    height_group.add_argument(
        "--height-mm",
        type=float,
        default=None,
        help="Freeform height in mm. Mutually exclusive with --height-units.",
    )
    parser.add_argument("--pocket-length-mm", type=float, default=None)
    parser.add_argument("--pocket-width-mm", type=float, default=None)
    parser.add_argument("--pocket-corner-radius-mm", type=float, default=None)
    parser.add_argument("--base-corner-radius-mm", type=float, default=None)
    parser.add_argument("--cutout-offset-mm", type=float, default=None)
    parser.add_argument("--cutout-radius-mm", type=float, default=None)
    parser.add_argument(
        "--no-cutouts",
        action="store_const",
        const=False,
        default=None,
        dest="cutouts_enabled",
        help="Disable the side cutouts and leave the walls (and any dividers) solid.",
    )
    parser.add_argument(
        "--divisions",
        type=int,
        default=None,
        help="Split the pocket into this many equal columns; 2 or more produces a CutleryBin.",
    )
    parser.add_argument("--divider-thickness-mm", type=float, default=None)
    parser.add_argument("--bed-x", type=float, default=DEFAULT_BED_X_MM, help="Print bed width in mm.")
    parser.add_argument("--bed-y", type=float, default=DEFAULT_BED_Y_MM, help="Print bed depth in mm.")
    parser.add_argument("--bed-z", type=float, default=DEFAULT_BED_Z_MM, help="Maximum print height in mm.")
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


def create_parameters(args: argparse.Namespace) -> BinParameters:
    """Build BinParameters from parsed CLI arguments, layering overrides on any preset."""
    params = resolve_preset(args.preset) if args.preset else BinParameters()

    simple = {
        "grid_x": args.grid_x,
        "grid_y": args.grid_y,
        "pocket_length_mm": args.pocket_length_mm,
        "pocket_width_mm": args.pocket_width_mm,
        "pocket_corner_radius_mm": args.pocket_corner_radius_mm,
        "base_corner_radius_mm": args.base_corner_radius_mm,
        "cutout_offset_from_edge_mm": args.cutout_offset_mm,
        "cutout_radius_mm": args.cutout_radius_mm,
        "cutouts_enabled": args.cutouts_enabled,
        "divisions": args.divisions,
        "divider_thickness_mm": args.divider_thickness_mm,
    }
    overrides = {key: value for key, value in simple.items() if value is not None}

    if args.height_units is not None:
        overrides["height_in_units"] = args.height_units
        overrides["height_mm"] = None
    elif args.height_mm is not None:
        overrides["height_mm"] = args.height_mm
        overrides["height_in_units"] = None

    result = replace(params, **overrides)

    if args.preset and preset_requires_cutouts(args.preset) and not result.cutouts_enabled:
        msg = (
            f"Side cutouts cannot be disabled for the '{args.preset}' preset; "
            "without them the contents are trapped."
        )
        raise ValueError(msg)

    return result


def default_output_path(params: BinParameters, fmt: str = "stl") -> Path:
    """Build a deterministic default output path for the generated bin."""
    kind = "cutlery_bin" if params.divisions >= 2 else "kitchen_bin"
    height_token = f"{params.effective_height_mm:g}".replace(".", "p")
    file_name = f"{kind}_{params.grid_x}x{params.grid_y}_h{height_token}.{fmt}"
    return Path.cwd() / file_name


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, build, and export a bin; return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        params = create_parameters(args)
        params.validate()
        output_path = args.output if args.output is not None else default_output_path(params, args.format)
        if not output_path.parent.exists():
            msg = f"Output directory does not exist: {output_path.parent}"
            raise FileNotFoundError(msg)
        part = create_cutlery_bin(params) if params.divisions >= 2 else create_kitchen_bin(params)
        size = part.bounding_box().size
        for warning in check_print_bed(size.X, size.Y, size.Z, args.bed_x, args.bed_y, args.bed_z):
            print(f"Warning: {warning}", file=sys.stderr)
        exported_file = export_bin(part, output_path)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}")
        return 2
    except OSError as exc:
        print(f"Error: Failed to write output: {exc}")
        return 2

    print(f"Exported: {exported_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
