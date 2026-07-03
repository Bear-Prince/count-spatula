"""Repo-level licensing artefacts and preset licensing metadata.

These verify the mechanically checkable parts of the licensing-and-attribution spec: the license
texts exist where the spec says they live, and presets carry provenance/license metadata. The
policy-level requirements (e.g. code staying Apache-only) are review concerns, not runtime checks.
"""

from pathlib import Path

import pytest

from cutlery_bin import PRESETS, Provenance

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.scenario("licensing-and-attribution", "Apache license present at repository root")
def test_apache_license_at_repo_root() -> None:
    """The code license lives at LICENSE and is Apache 2.0."""
    license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Apache License" in license_text
    assert "Version 2.0" in license_text


@pytest.mark.scenario("licensing-and-attribution", "License text available for models")
def test_model_license_text_available() -> None:
    """The CC BY-SA 4.0 text for generated models is available under LICENSES/."""
    cc_text = (REPO_ROOT / "LICENSES" / "CC-BY-SA-4.0.txt").read_text(encoding="utf-8")
    assert "Attribution-ShareAlike 4.0" in cc_text


@pytest.mark.scenario("licensing-and-attribution", "Lineage documented")
def test_lineage_documented_in_credits() -> None:
    """CREDITS.md exists and is non-trivial."""
    credits = (REPO_ROOT / "CREDITS.md").read_text(encoding="utf-8")
    assert len(credits.strip()) > 0


@pytest.mark.scenario("licensing-and-attribution", "Dependency notices present")
def test_dependency_notices_present() -> None:
    """The NOTICE file carries dependency notices."""
    notice = (REPO_ROOT / "NOTICE").read_text(encoding="utf-8")
    assert "gridfinity" in notice.lower()


@pytest.mark.scenario("licensing-and-attribution", "Preset carries provenance and license metadata")
def test_every_preset_carries_provenance_and_license() -> None:
    """Each preset declares provenance and a model license; derived presets name their upstream."""
    for name, preset in PRESETS.items():
        assert isinstance(preset.provenance, Provenance), f"preset {name} lacks provenance"
        assert preset.model_license, f"preset {name} lacks a model license"
        if preset.provenance is Provenance.DERIVED:
            assert preset.derived_from, f"derived preset {name} must name its upstream design"
