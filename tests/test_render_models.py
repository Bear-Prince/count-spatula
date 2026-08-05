import re
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

import render_models
from cutlery_bin import BinParameters


@pytest.mark.scenario("model-rendering", "The knife blade block is part of the set")
def test_render_manifest_covers_the_uat_set_and_wave_divider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The manifest covers the UAT.md cases, a wave-divider bin, and the knife block, all named uniquely."""
    calls: list[tuple[str, tuple, dict]] = []

    def record(kind: str) -> object:
        def factory(params: BinParameters | None = None) -> object:
            calls.append((kind, params))
            return object()

        return factory

    monkeypatch.setattr(render_models, "create_kitchen_bin", record("kitchen"))
    monkeypatch.setattr(render_models, "create_cutlery_bin", record("cutlery"))
    monkeypatch.setattr(render_models, "create_knife_blade_block", record("knife_block"))
    monkeypatch.setattr(render_models, "create_blanking_plate", record("blanking_plate"))
    monkeypatch.setattr(render_models, "resolve_preset", lambda _name: BinParameters(pocket_length_mm=220))

    manifest = render_models.render_manifest()
    names = [name for name, _ in manifest]

    assert len(names) == len(set(names)), "manifest entry names must be unique"
    assert {
        "kitchen_bin", "chop_board", "cutlery_bin", "wave_divider_bin", "knife_block", "blanking_plate"
    } <= set(names)

    wave_call = next(params for kind, params in calls if kind == "cutlery" and params.divider_profile == "wave")
    assert wave_call.divider_amplitude_mm == 4.0
    assert wave_call.divisions >= 2


def test_find_openscad_locates_binary_on_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """find_openscad returns whatever shutil.which reports, including None when absent."""
    monkeypatch.setattr(
        render_models.shutil, "which", lambda name: "/usr/bin/openscad" if name == "openscad" else None
    )
    assert render_models.find_openscad() == "/usr/bin/openscad"

    monkeypatch.setattr(render_models.shutil, "which", lambda _name: None)
    assert render_models.find_openscad() is None


def test_find_imagemagick_prefers_magick_then_falls_back_to_convert(monkeypatch: pytest.MonkeyPatch) -> None:
    """IM7's 'magick' is preferred; IM6's 'convert' is used only when 'magick' is absent."""
    monkeypatch.setattr(
        render_models.shutil, "which", lambda name: "/usr/bin/magick" if name == "magick" else None
    )
    assert render_models.find_imagemagick() == "/usr/bin/magick"

    monkeypatch.setattr(
        render_models.shutil, "which", lambda name: "/usr/bin/convert" if name == "convert" else None
    )
    assert render_models.find_imagemagick() == "/usr/bin/convert"

    monkeypatch.setattr(render_models.shutil, "which", lambda _name: None)
    assert render_models.find_imagemagick() is None


class _FakeMesher:
    """Stand-in for build123d's Mesher: writes a placeholder file instead of real geometry."""

    def add_shape(self, part: object) -> None:
        self.part = part

    def write(self, path: Path) -> None:
        Path(path).write_text("stub stl")


@pytest.mark.scenario("model-rendering", "Render the set to PNGs")
def test_render_png_invokes_openscad_with_fixed_camera_and_size(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """render_png writes a one-line .scad import and calls OpenSCAD with a fixed camera and image size."""
    monkeypatch.setattr(render_models, "Mesher", _FakeMesher)
    recorded_scad_content: list[str] = []

    def fake_check_call(cmd: list[str]) -> int:
        recorded_scad_content.append(Path(cmd[-1]).read_text())
        return 0

    monkeypatch.setattr(subprocess, "check_call", fake_check_call)

    output_path = tmp_path / "kitchen_bin.png"
    render_models.render_png(object(), output_path, "/usr/bin/openscad")

    assert len(recorded_scad_content) == 1
    assert 'import("' in recorded_scad_content[0]


def test_render_png_command_shape(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The OpenSCAD command includes the fixed camera position, image size, and output path."""
    monkeypatch.setattr(render_models, "Mesher", _FakeMesher)
    captured_cmd: list[str] = []

    def fake_check_call(cmd: list[str]) -> int:
        captured_cmd.extend(cmd)
        return 0

    monkeypatch.setattr(subprocess, "check_call", fake_check_call)

    output_path = tmp_path / "kitchen_bin.png"
    render_models.render_png(object(), output_path, "/usr/bin/openscad")

    assert captured_cmd[0] == "/usr/bin/openscad"
    assert "--camera" in captured_cmd
    assert captured_cmd[captured_cmd.index("--camera") + 1] == render_models.CAMERA_POSITION
    assert "-o" in captured_cmd
    assert captured_cmd[captured_cmd.index("-o") + 1] == str(output_path)
    assert f"--imgsize={render_models.IMAGE_SIZE},{render_models.IMAGE_SIZE}" in captured_cmd


@pytest.mark.scenario("model-rendering", "GIF cycles the example models")
def test_build_gif_stitches_frames_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """build_gif calls ImageMagick with the frames in order, a loop flag, and the output path last."""
    captured_cmd: list[str] = []
    monkeypatch.setattr(subprocess, "check_call", lambda cmd: captured_cmd.extend(cmd))

    png_paths = [Path("a.png"), Path("b.png"), Path("c.png")]
    output_path = Path("models.gif")
    render_models.build_gif(png_paths, output_path, "/usr/bin/magick")

    assert captured_cmd[0] == "/usr/bin/magick"
    assert "-loop" in captured_cmd
    assert captured_cmd[captured_cmd.index("-loop") + 1] == "0"
    assert captured_cmd[-4:] == ["a.png", "b.png", "c.png", "models.gif"]


def test_build_gif_works_identically_with_im6_convert(monkeypatch: pytest.MonkeyPatch) -> None:
    """build_gif invokes IM6's 'convert' the same way as IM7's 'magick'."""
    captured_cmd: list[str] = []
    monkeypatch.setattr(subprocess, "check_call", lambda cmd: captured_cmd.extend(cmd))

    render_models.build_gif([Path("a.png")], Path("out.gif"), "/usr/bin/convert")

    assert captured_cmd[0] == "/usr/bin/convert"
    assert captured_cmd[-2:] == ["a.png", "out.gif"]


@pytest.mark.scenario("model-rendering", "Missing render tool fails with an actionable error")
def test_main_fails_fast_when_openscad_is_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """main exits non-zero naming openscad and does no work when it is absent."""
    monkeypatch.setattr(render_models, "find_openscad", lambda: None)
    monkeypatch.setattr(render_models, "find_imagemagick", lambda: "/usr/bin/magick")
    manifest_spy = Mock(wraps=render_models.render_manifest)
    monkeypatch.setattr(render_models, "render_manifest", manifest_spy)

    exit_code = render_models.main()

    assert exit_code == 1
    assert "openscad" in capsys.readouterr().err
    manifest_spy.assert_not_called()


def test_main_fails_fast_when_imagemagick_is_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """main exits non-zero naming ImageMagick and does no work when it is absent, writing no partial output."""
    monkeypatch.setattr(render_models, "find_openscad", lambda: "/usr/bin/openscad")
    monkeypatch.setattr(render_models, "find_imagemagick", lambda: None)
    manifest_spy = Mock(wraps=render_models.render_manifest)
    monkeypatch.setattr(render_models, "render_manifest", manifest_spy)

    exit_code = render_models.main()

    assert exit_code == 1
    assert "ImageMagick" in capsys.readouterr().err
    manifest_spy.assert_not_called()


def test_main_renders_every_manifest_entry_and_builds_one_gif(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """main renders one PNG per manifest entry, then stitches all of them into a single GIF."""
    assets_dir = tmp_path / "assets"
    monkeypatch.setattr(render_models, "ASSETS_DIR", assets_dir)
    monkeypatch.setattr(render_models, "GIF_PATH", assets_dir / "models.gif")
    monkeypatch.setattr(render_models, "find_openscad", lambda: "/usr/bin/openscad")
    monkeypatch.setattr(render_models, "find_imagemagick", lambda: "/usr/bin/magick")
    monkeypatch.setattr(
        render_models, "render_manifest", lambda: [("alpha", object()), ("beta", object())]
    )

    render_png_calls: list[tuple[object, Path, str]] = []
    monkeypatch.setattr(
        render_models,
        "render_png",
        lambda part, output_path, openscad_bin: render_png_calls.append((part, output_path, openscad_bin)),
    )
    build_gif_calls: list[tuple[list[Path], Path, str]] = []
    monkeypatch.setattr(
        render_models,
        "build_gif",
        lambda png_paths, output_path, magick_bin: build_gif_calls.append((png_paths, output_path, magick_bin)),
    )

    exit_code = render_models.main()

    assert exit_code == 0
    assert [output_path for _, output_path, _ in render_png_calls] == [
        assets_dir / "alpha.png",
        assets_dir / "beta.png",
    ]
    assert len(build_gif_calls) == 1
    png_paths, gif_output_path, magick_bin = build_gif_calls[0]
    assert png_paths == [assets_dir / "alpha.png", assets_dir / "beta.png"]
    assert gif_output_path == assets_dir / "models.gif"
    assert magick_bin == "/usr/bin/magick"


@pytest.mark.scenario("model-rendering", "README references existing committed images")
def test_readme_image_references_exist_with_licence_caption() -> None:
    """Every docs/assets image the README links to exists, and the CC BY-SA caption follows it."""
    repo_root = Path(__file__).resolve().parent.parent
    readme_text = (repo_root / "README.md").read_text()

    image_refs = re.findall(r"!\[[^\]]*\]\((docs/assets/[^)]+)\)", readme_text)
    assert image_refs, "README should embed at least one docs/assets image"

    for ref in image_refs:
        assert (repo_root / ref).exists(), f"README references missing file: {ref}"
        caption_window = readme_text[readme_text.index(ref) : readme_text.index(ref) + 400]
        assert "CC BY-SA" in caption_window, f"no CC BY-SA caption found near {ref}"
