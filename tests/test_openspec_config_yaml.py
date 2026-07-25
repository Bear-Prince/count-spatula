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


def test_openspec_rules_are_lists_of_strings() -> None:
    """Every artifact's rules must be a list of plain strings.

    An unquoted "key: value" rule parses as a mapping rather than a string, which makes OpenSpec discard
    that artifact's entire rule list with only a warning -- so the rules silently stop being applied.
    """
    config_path = Path("openspec/config.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    for artifact, rules in config["rules"].items():
        assert isinstance(rules, list), f"rules for {artifact!r} must be a list"
        offenders = [rule for rule in rules if not isinstance(rule, str)]
        assert not offenders, (
            f"rules for {artifact!r} contain non-string items {offenders}; "
            "quote any rule containing a colon followed by a space"
        )
