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
from knife_block import KnifeBlockParameters, check_drawer_clearance, create_knife_blade_block

# Default print volume in millimetres (width x depth x height). Printers quote build volumes in mm,
# so these are plain millimetres with no unit conversion. Override per axis with --bed-x/--bed-y/--bed-z.
DEFAULT_BED_X_MM = 220.0
DEFAULT_BED_Y_MM = 220.0
DEFAULT_BED_Z_MM = 240.0

# Defaults for the --knife-block drawer-clearance check. The height matches the target drawer this
# feature was designed for; the blade depth is a conservative typical chef's-knife spine-to-edge
# figure -- override with --max-blade-depth-mm for a taller knife (e.g. a cleaver).
DEFAULT_DRAWER_HEIGHT_MM = 78.0
DEFAULT_MAX_BLADE_DEPTH_MM = 40.0
DEFAULT_DRAWER_CLEARANCE_MM = 5.0


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
    parser.add_argument(
        "--cutout-offset-units",
        type=int,
        nargs="+",
        default=None,
        metavar="UNITS",
        help=(
            "Whole Gridfinity units of solid wall reserved at each cutout end. One value applies "
            "to both ends; two values set the start and end independently (e.g. '1 2')."
        ),
    )
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
        "--stacking-lip",
        action="store_const",
        const=True,
        default=None,
        dest="stacking_lip",
        help=(
            "Add a Gridfinity stacking lip to the outer top rim so another bin can sit on top. "
            "The lip is added above the requested height, so the model ends up about 4.12 mm taller."
        ),
    )
    parser.add_argument(
        "--divisions",
        type=int,
        default=None,
        help="Split the pocket into this many equal columns; 2 or more produces a CutleryBin.",
    )
    parser.add_argument("--divider-thickness-mm", type=float, default=None)
    parser.add_argument(
        "--divider-profile",
        choices=["straight", "wave"],
        default=None,
        help="Divider shape: 'straight' (flat, default) or 'wave' (S-curve for nesting cutlery).",
    )
    parser.add_argument(
        "--divider-amplitude-mm",
        type=float,
        default=None,
        help="Sideways swing of a wave divider in mm; required when --divider-profile is 'wave'.",
    )
    parser.add_argument(
        "--knife-block",
        action="store_true",
        help="Build a KnifeBladeBlock instead of a bin. --grid-x/--grid-y apply to the block's own "
        "footprint; bin-only flags (pocket, cutout, divider options) are ignored.",
    )
    parser.add_argument("--knife-count", type=int, default=None, help="Number of knife lanes.")
    parser.add_argument("--handle-width-mm", type=float, default=None, help="Widest supported knife handle.")
    parser.add_argument(
        "--handle-gap-mm",
        type=float,
        default=None,
        help="Finger clearance between two same-end handles.",
    )
    parser.add_argument(
        "--drawer-height-mm",
        type=float,
        default=DEFAULT_DRAWER_HEIGHT_MM,
        help="Drawer internal height in mm, for the --knife-block drawer-clearance check.",
    )
    parser.add_argument(
        "--max-blade-depth-mm",
        type=float,
        default=DEFAULT_MAX_BLADE_DEPTH_MM,
        help="Tallest supported knife's spine-to-edge depth in mm, for the drawer-clearance check.",
    )
    parser.add_argument(
        "--drawer-clearance-mm",
        type=float,
        default=DEFAULT_DRAWER_CLEARANCE_MM,
        help="Extra safety margin in mm added on top of the deck height and blade depth.",
    )
    parser.add_argument("--bed-x", type=float, default=DEFAULT_BED_X_MM, help="Print bed width in mm.")
    parser.add_argument("--bed-y", type=float, default=DEFAULT_BED_Y_MM, help="Print bed depth in mm.")
    parser.add_argument("--bed-z", type=float, default=DEFAULT_BED_Z_MM, help="Maximum print height in mm.")
    parser.add_argument(
        "--format",
        choices=["stl", "3mf"],
        default=None,
        help="Output file format when --output is omitted. Default: stl. Conflicts with an --output "
        "extension that names a different format.",
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
        "cutout_radius_mm": args.cutout_radius_mm,
        "cutouts_enabled": args.cutouts_enabled,
        "stacking_lip": args.stacking_lip,
        "divisions": args.divisions,
        "divider_thickness_mm": args.divider_thickness_mm,
        "divider_profile": args.divider_profile,
        "divider_amplitude_mm": args.divider_amplitude_mm,
    }
    overrides = {key: value for key, value in simple.items() if value is not None}

    if args.height_units is not None:
        overrides["height_in_units"] = args.height_units
        overrides["height_mm"] = None
    elif args.height_mm is not None:
        overrides["height_mm"] = args.height_mm
        overrides["height_in_units"] = None

    if args.cutout_offset_units is not None:
        if len(args.cutout_offset_units) == 1:
            start_units = end_units = args.cutout_offset_units[0]
        elif len(args.cutout_offset_units) == 2:
            start_units, end_units = args.cutout_offset_units
        else:
            msg = "--cutout-offset-units takes 1 or 2 values"
            raise ValueError(msg)
        overrides["cutout_offset_start_units"] = start_units
        overrides["cutout_offset_end_units"] = end_units

    result = replace(params, **overrides)

    if args.preset and preset_requires_cutouts(args.preset) and not result.cutouts_enabled:
        msg = (
            f"Side cutouts cannot be disabled for the '{args.preset}' preset; "
            "without them the contents are trapped."
        )
        raise ValueError(msg)

    return result


def create_knife_block_parameters(args: argparse.Namespace) -> KnifeBlockParameters:
    """Build KnifeBlockParameters from parsed CLI arguments."""
    simple = {
        "knife_count": args.knife_count,
        "handle_width_mm": args.handle_width_mm,
        "handle_gap_mm": args.handle_gap_mm,
        "grid_x": args.grid_x,
        "grid_y": args.grid_y,
    }
    overrides = {key: value for key, value in simple.items() if value is not None}
    return replace(KnifeBlockParameters(), **overrides)


def default_output_path(params: BinParameters | KnifeBlockParameters, fmt: str = "stl") -> Path:
    """Build a deterministic default output path for the generated bin or knife block."""
    if isinstance(params, KnifeBlockParameters):
        file_name = f"knife_block_{params.knife_count}knives_{params.grid_x}x{params.grid_y}.{fmt}"
        return Path.cwd() / file_name
    kind = "cutlery_bin" if params.divisions >= 2 else "kitchen_bin"
    height_token = f"{params.effective_height_mm:g}".replace(".", "p")
    file_name = f"{kind}_{params.grid_x}x{params.grid_y}_h{height_token}.{fmt}"
    return Path.cwd() / file_name


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, build, and export a bin; return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        params = create_knife_block_parameters(args) if args.knife_block else create_parameters(args)
        params.validate()
        fmt = args.format if args.format is not None else "stl"
        if args.output is not None and args.format is not None:
            output_ext = args.output.suffix.lstrip(".").lower()
            if output_ext != args.format:
                msg = (
                    f"--format {args.format} conflicts with --output's extension "
                    f"({args.output.suffix or '<none>'}); use matching values or drop one of them"
                )
                raise ValueError(msg)
        output_path = args.output if args.output is not None else default_output_path(params, fmt)
        if not output_path.parent.exists():
            msg = f"Output directory does not exist: {output_path.parent}"
            raise FileNotFoundError(msg)
        if args.knife_block:
            part = create_knife_blade_block(params)
        else:
            part = create_cutlery_bin(params) if params.divisions >= 2 else create_kitchen_bin(params)
        size = part.bounding_box().size
        for warning in check_print_bed(size.X, size.Y, size.Z, args.bed_x, args.bed_y, args.bed_z):
            print(f"Warning: {warning}", file=sys.stderr)
        if args.knife_block:
            drawer_warnings = check_drawer_clearance(
                params.deck_height_mm, args.max_blade_depth_mm, args.drawer_clearance_mm, args.drawer_height_mm
            )
            for warning in drawer_warnings:
                print(f"Warning: {warning}", file=sys.stderr)
        exported_file = export_bin(part, output_path)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Error: Failed to write output: {exc}", file=sys.stderr)
        return 2

    print(f"Exported: {exported_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
