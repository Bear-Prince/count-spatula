"""Shared pytest configuration for the test suite."""

import pytest

_REAL_GEOMETRY_FIXTURES = ("bins", "knife_blocks", "lip_bins")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark every test that builds real geometry as slow.

    The module-scoped ``bins`` fixture in ``test_cutlery_bin.py`` and the ``knife_blocks`` fixture in
    ``test_knife_block.py`` each build a set of real parts, which dominates the suite's runtime. Marking
    their consumers automatically keeps the fast/slow split accurate without every test needing a manual
    marker; run the quick suite with ``-m "not slow"``.
    """
    for item in items:
        if any(name in getattr(item, "fixturenames", ()) for name in _REAL_GEOMETRY_FIXTURES):
            item.add_marker(pytest.mark.slow)
