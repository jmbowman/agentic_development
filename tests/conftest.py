"""Pytest fixtures shared by this repo's tests."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, Any

import pytest

from tests.support import (
    CHECK_WORKFLOW,
    FIXTURES,
    VERIFY_SCRIPT,
    StepRunner,
    load_workflow,
    only_job,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


@pytest.fixture
def check_job() -> dict[str, Any]:
    """The single job of the check workflow."""
    return only_job(load_workflow(CHECK_WORKFLOW))


@pytest.fixture
def fixture_runner(tmp_path: Path) -> Callable[..., StepRunner]:
    """Factory: copy a fixture into a fresh workspace and return a StepRunner for it."""

    def make(name: str, *, parent_config: str | None = None) -> StepRunner:
        workspace = tmp_path / f"workspace-{name}"
        target = workspace / "project"
        shutil.copytree(FIXTURES / name, target, symlinks=True)
        if parent_config is not None:
            (workspace / "mise.toml").write_text(parent_config)
        # Where check.yml's `script` step puts the verification script.
        fetched = workspace / ".check-workflow" / "scripts"
        fetched.mkdir(parents=True)
        shutil.copy2(VERIFY_SCRIPT, fetched)
        return StepRunner(workspace, target, only_job(load_workflow(CHECK_WORKFLOW)))

    return make
