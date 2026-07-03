"""Traceability guard between OpenSpec scenarios and the test suite.

Every ``#### Scenario:`` in ``openspec/specs/<capability>/spec.md`` must be claimed by at least one
test via ``@pytest.mark.scenario("<capability>", "<scenario>")``, or be explicitly listed in
``UNTESTED_SCENARIOS`` with a reason. Markers must in turn point at scenarios that really exist, so
the linkage cannot silently rot from either side when specs are archived or tests are renamed.
"""

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO_ROOT / "openspec" / "specs"
TESTS_DIR = Path(__file__).resolve().parent

_SCENARIO_HEADING = re.compile(r"^#### Scenario: (?P<name>.+?)\s*$", re.MULTILINE)

# Scenarios we knowingly do not verify with a test, each with the reason. Removing an entry here is
# how a new test "claims" one of these; the stale-entry check below forces the removal.
UNTESTED_SCENARIOS: dict[tuple[str, str], str] = {
    ("licensing-and-attribution", "Generic geometry code stays Apache-only"): "review policy, not runtime-checkable",
    ("licensing-and-attribution", "Derived model license is not altered"): "review policy, not runtime-checkable",
    ("licensing-and-attribution", "Reproducing a third-party profile forces derived status"): "review policy",
    ("licensing-and-attribution", "Attribution block is complete"): "no attribution generator exists yet",
    ("licensing-and-attribution", "Incompatible platform is rejected"): "enforced by uv required-environments",
    ("licensing-and-attribution", "Compatible platform is permitted"): "enforced by uv required-environments",
    ("multi-format-export", "Export to STL"): "needs a real Mesher export; candidate for a future slow test",
    ("multi-format-export", "Export to 3MF"): "needs a real Mesher export; candidate for a future slow test",
    ("multi-format-export", "Chopping board bin exported via Mesher"): "needs a real Mesher export",
    ("print-bed-validation", "A model is not rotated to fit"): "implicit in check_print_bed taking raw dimensions",
}


def _spec_scenarios() -> set[tuple[str, str]]:
    """Return every (capability, scenario) pair declared in the main specs."""
    pairs: set[tuple[str, str]] = set()
    for spec_file in sorted(SPECS_DIR.glob("*/spec.md")):
        capability = spec_file.parent.name
        for match in _SCENARIO_HEADING.finditer(spec_file.read_text(encoding="utf-8")):
            pairs.add((capability, match.group("name")))
    return pairs


def _claimed_scenarios() -> set[tuple[str, str]]:
    """Return every (capability, scenario) pair claimed by a scenario marker in the test files."""
    pairs: set[tuple[str, str]] = set()
    for test_file in sorted(TESTS_DIR.glob("test_*.py")):
        tree = ast.parse(test_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr == "scenario"
                    and len(decorator.args) == 2
                    and all(isinstance(arg, ast.Constant) for arg in decorator.args)
                ):
                    pairs.add((decorator.args[0].value, decorator.args[1].value))
    return pairs


def test_every_spec_scenario_has_a_test() -> None:
    """Each spec scenario is claimed by a scenario marker or explicitly allowlisted with a reason."""
    unclaimed = _spec_scenarios() - _claimed_scenarios() - set(UNTESTED_SCENARIOS)
    listing = "\n".join(f"  {capability}: {scenario}" for capability, scenario in sorted(unclaimed))
    assert not unclaimed, (
        "Spec scenarios with no test claiming them (add a @pytest.mark.scenario marker "
        f"or an UNTESTED_SCENARIOS entry with a reason):\n{listing}"
    )


def test_every_scenario_marker_matches_the_specs() -> None:
    """Each scenario marker points at a scenario that exists in the main specs."""
    dangling = _claimed_scenarios() - _spec_scenarios()
    listing = "\n".join(f"  {capability}: {scenario}" for capability, scenario in sorted(dangling))
    assert not dangling, (
        f"Scenario markers referencing scenarios that do not exist in openspec/specs:\n{listing}"
    )


def test_untested_allowlist_is_not_stale() -> None:
    """Allowlist entries must still exist in the specs and must not also be claimed by a test."""
    scenarios = _spec_scenarios()
    vanished = set(UNTESTED_SCENARIOS) - scenarios
    now_tested = set(UNTESTED_SCENARIOS) & _claimed_scenarios()
    problems = [f"  no longer in the specs: {pair}" for pair in sorted(vanished)]
    problems += [f"  now covered by a test, remove from the allowlist: {pair}" for pair in sorted(now_tested)]
    assert not problems, "Stale UNTESTED_SCENARIOS entries:\n" + "\n".join(problems)
