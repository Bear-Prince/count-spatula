"""Render the example bin set to PNGs and a looping GIF for the README.

Uses headless OpenSCAD to render each model (via a one-line .scad file that imports an exported
STL) and ImageMagick to stitch the renders into a looping GIF. Neither tool is a Python dependency;
both are looked up on PATH so a missing tool fails fast with an actionable message instead of a
partial set of images.

OpenSCAD's image export still opens an OpenGL context even though nothing is shown on screen, so it
needs a display. Without one (headless CI, most containers, Codespaces) it dies with a bare SIGSEGV
instead of a readable error -- run this script under ``xvfb-run -a`` in that case (install ``xvfb``).
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from build123d.mesher import Mesher
from build123d.topology import Shape

from cutlery_bin import BinParameters, create_blanking_plate, create_cutlery_bin, create_kitchen_bin, resolve_preset
from knife_block import KnifeBlockParameters, create_knife_blade_block

ASSETS_DIR = Path(__file__).parent / "docs" / "assets"
GIF_PATH = ASSETS_DIR / "models.gif"

# A single fixed camera position (translate x,y,z, rotate x,y,z, distance) so every render is
# framed consistently; --viewall recomputes the distance to fit the model, so 0 is left as auto.
CAMERA_POSITION = "0,0,0,55,0,25,0"
IMAGE_SIZE = 720
GIF_DELAY_CENTISECONDS = 75


def render_manifest() -> list[tuple[str, Shape]]:
    """Build the example model set: the UAT.md bin cases, a wave-divider bin, the knife block, and a plate."""
    return [
        ("kitchen_bin", create_kitchen_bin(BinParameters())),
        ("chop_board", create_kitchen_bin(resolve_preset("chop-board"))),
        ("cutlery_bin", create_cutlery_bin(BinParameters(divisions=3))),
        ("wave_divider_bin", create_cutlery_bin(
            BinParameters(divisions=3, divider_profile="wave", divider_amplitude_mm=4.0)
        )),
        ("solid_bin_2x4", create_kitchen_bin(BinParameters(cutouts_enabled=False))),
        ("solid_bin_3x3", create_kitchen_bin(BinParameters(grid_x=3, grid_y=3, cutouts_enabled=False))),
        ("knife_block", create_knife_blade_block(KnifeBlockParameters())),
        ("blanking_plate", create_blanking_plate()),
    ]


def find_openscad() -> str | None:
    """Locate the headless OpenSCAD binary on PATH."""
    return shutil.which("openscad")


def find_imagemagick() -> str | None:
    """Locate ImageMagick's convert tool: 'magick' (v7) or 'convert' (v6)."""
    return shutil.which("magick") or shutil.which("convert")


def render_png(part: Shape, output_path: Path, openscad_bin: str) -> None:
    """Render one part to a PNG via a temporary STL and a one-line OpenSCAD import."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        stl_path = Path(tmp_dir) / "model.stl"
        scad_path = Path(tmp_dir) / "model.scad"
        mesher = Mesher()
        mesher.add_shape(part)
        mesher.write(stl_path)
        scad_path.write_text(f'import("{stl_path}");\n')
        subprocess.check_call([
            openscad_bin,
            "--autocenter",
            "--viewall",
            "--camera",
            CAMERA_POSITION,
            "-o",
            str(output_path),
            f"--imgsize={IMAGE_SIZE},{IMAGE_SIZE}",
            str(scad_path),
        ])


def build_gif(png_paths: list[Path], output_path: Path, magick_bin: str) -> None:
    """Stitch a sequence of PNGs into a single looping GIF.

    IM7's ``magick`` and IM6's ``convert`` accept the same arguments for this operation, so
    ``magick_bin`` (whichever was found on PATH) is invoked identically either way.
    """
    subprocess.check_call([
        magick_bin,
        "-delay",
        str(GIF_DELAY_CENTISECONDS),
        "-loop",
        "0",
        *(str(path) for path in png_paths),
        str(output_path),
    ])


def main() -> int:
    """Render every example model to a PNG and stitch them into a looping GIF."""
    openscad_bin = find_openscad()
    if openscad_bin is None:
        print(
            "Error: openscad not found on PATH. Install it (e.g. 'apt install openscad') to render models.",
            file=sys.stderr,
        )
        return 1

    magick_bin = find_imagemagick()
    if magick_bin is None:
        print(
            "Error: ImageMagick not found on PATH. Install it (e.g. 'apt install imagemagick') "
            "to build the model GIF.",
            file=sys.stderr,
        )
        return 1

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    png_paths: list[Path] = []
    for name, part in render_manifest():
        output_path = ASSETS_DIR / f"{name}.png"
        render_png(part, output_path, openscad_bin)
        png_paths.append(output_path)
        print(f"Rendered: {output_path}")

    build_gif(png_paths, GIF_PATH, magick_bin)
    print(f"Rendered: {GIF_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
