"""Shared pytest configuration for the test suite."""

import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark every test that builds real geometry as slow.

    The module-scoped ``bins`` fixture in ``test_cutlery_bin.py`` builds a set of real bins, which
    dominates the suite's runtime. Marking its consumers automatically keeps the fast/slow split
    accurate without every test needing a manual marker; run the quick suite with ``-m "not slow"``.
    """
    for item in items:
        if "bins" in getattr(item, "fixturenames", ()):
            item.add_marker(pytest.mark.slow)
