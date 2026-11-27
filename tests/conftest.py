"""Pytest configuration for the pbg_chaste package tests.

The engine-driving test modules below invoke the real Chaste engine, which runs
in the ``chaste/pychaste`` Docker image (not a pip dependency). On a host without
the daemon + image — vanilla CI, most dev machines — those tests are skipped as a
whole module here, so the package test suite stays green without the native
engine. (Individual tests also carry ``@chaste_required`` markers; this module
guard is the belt-and-suspenders that also covers any engine test that predates
or misses the marker.)

Set ``CHASTE_FORCE_ENGINE_TESTS=1`` to force-collect them (e.g. in an environment
that really does have the image).
"""
from __future__ import annotations

import os

import pytest

# Test modules whose tests construct/run the Chaste engine.
_ENGINE_MODULES = {"test_cell_sorting", "test_processes"}


def _engine_ready() -> bool:
    if os.environ.get("CHASTE_FORCE_ENGINE_TESTS") == "1":
        return True
    try:
        from pbg_chaste import runtime

        return bool(runtime.chaste_ready())
    except Exception:
        # Any failure probing for the engine (no docker CLI, daemon down, import
        # error) means it is not runnable here -> skip the engine tests.
        return False


def pytest_collection_modifyitems(config, items):
    if _engine_ready():
        return
    skip = pytest.mark.skip(
        reason="Chaste engine (chaste/pychaste Docker image) not available; "
        "set CHASTE_FORCE_ENGINE_TESTS=1 to force."
    )
    for item in items:
        if item.module.__name__.split(".")[-1] in _ENGINE_MODULES:
            item.add_marker(skip)
