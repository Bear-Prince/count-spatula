from pathlib import Path

import yaml


def test_openspec_config_parses_and_has_expected_sections() -> None:
    """Validate OpenSpec config YAML syntax and required top-level sections."""
    config_path = Path("openspec/config.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    assert isinstance(config, dict)
    assert config.get("schema") == "spec-driven"
    assert "context" in config
    assert "rules" in config
