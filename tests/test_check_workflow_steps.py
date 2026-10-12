"""Behavioral tests: run the check workflow's own steps against fixture repos."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from tests.support import StepRunner

if TYPE_CHECKING:
    from pathlib import Path

RunnerFactory = Callable[..., StepRunner]


def run_steps(runner: StepRunner, *step_ids: str) -> dict[str, Any]:
    """Run the check workflow's steps by id; the ceiling step must always succeed."""
    results = {step_id: runner.run(step_id) for step_id in step_ids}
    if "ceiling" in results:
        assert results["ceiling"].returncode == 0, results["ceiling"].output
    return results


# @spec CHECK-RUN-002
def test_check_defined_in_repo_config_is_rejected(fixture_runner: RunnerFactory) -> None:
    """Verification fails and names the repo-owned file that redefines `check`."""
    runner = fixture_runner("override-check")
    results = run_steps(runner, "ceiling", "verify")
    assert results["ceiling"].returncode == 0, results["ceiling"].output
    assert results["verify"].returncode != 0
    absolute = runner.working_directory.resolve() / ".config/mise/config.toml"
    assert str(absolute) in results["verify"].output


# @spec CHECK-RUN-003
def test_symlinked_conf_d_entry_is_accepted(fixture_runner: RunnerFactory) -> None:
    """A `check` task from a conf.d symlink into another directory passes verification."""
    results = run_steps(fixture_runner("symlinked"), "ceiling", "verify", "check")
    assert results["verify"].returncode == 0, results["verify"].output
    assert results["check"].returncode == 0, results["check"].output
    assert "symlinked-ok" in results["check"].output


# @spec CHECK-RUN-004, CHECK-010
def test_missing_check_task_fails_despite_a_parent_check(fixture_runner: RunnerFactory) -> None:
    """With no `check` task, verification fails; a parent directory's `check` is not seen."""
    runner = fixture_runner("no-check", parent_config='[tasks.check]\nrun = "echo parent-check"\n')
    results = run_steps(runner, "ceiling", "verify")
    assert results["verify"].returncode != 0
    assert 'no "check" task' in results["verify"].output


# @spec CHECK-RUN-005
def test_a_failing_dependency_does_not_abort_the_others(fixture_runner: RunnerFactory) -> None:
    """The checks step fails, but a slower passing dependency still finishes."""
    results = run_steps(fixture_runner("failing"), "ceiling", "verify", "check")
    assert results["verify"].returncode == 0, results["verify"].output
    assert results["check"].returncode != 0
    assert "MARKER-slow-ok" in results["check"].output


# @spec CHECK-RUN-007
def test_redefined_dependency_of_check_is_rejected(fixture_runner: RunnerFactory) -> None:
    """Verification fails and names the task and file when a repo redefines `test`."""
    for fixture in ("override-test", "override-closure", "override-structured"):
        runner = fixture_runner(fixture)
        results = run_steps(runner, "ceiling", "verify")
        assert results["verify"].returncode != 0, fixture
        source = runner.working_directory.resolve() / ".config/mise/config.toml"
        expected = f'task "test" is defined in {source}'
        assert expected in results["verify"].output, (fixture, results["verify"].output)


# @spec CHECK-RUN-007
def test_redefined_extra_task_is_allowed(fixture_runner: RunnerFactory) -> None:
    """A repo may redefine a `-extra` task without failing verification."""
    results = run_steps(fixture_runner("override-extra"), "ceiling", "verify", "check")
    assert results["verify"].returncode == 0, results["verify"].output
    assert "repo-extra" in results["check"].output


def test_passing_fixture_passes(fixture_runner: RunnerFactory) -> None:
    """Baseline: a well-formed fixture passes verification and its checks."""
    results = run_steps(fixture_runner("passing"), "ceiling", "verify", "check")
    assert results["verify"].returncode == 0, results["verify"].output
    assert results["check"].returncode == 0, results["check"].output


# @spec CHECK-RUN-008
def test_glob_dependency_is_rejected(fixture_runner: RunnerFactory) -> None:
    """A pattern dependency fails verification, since mise reports only its first match."""
    results = run_steps(fixture_runner("glob-dependency"), "ceiling", "verify")
    assert results["verify"].returncode != 0
    assert 'dependency "lint:*" uses a pattern' in results["verify"].output


# @spec CHECK-RUN-010
def test_missing_dependency_is_rejected(fixture_runner: RunnerFactory) -> None:
    """A dependency mise can't find fails verification and is named."""
    results = run_steps(fixture_runner("missing-dependency"), "ceiling", "verify")
    assert results["verify"].returncode != 0
    assert 'dependency "gone" was not found' in results["verify"].output


# @spec CHECK-012
def test_verification_leaves_nothing_in_the_workspace(fixture_runner: RunnerFactory) -> None:
    """The fetched script runs from $RUNNER_TEMP and is gone from the workspace."""
    runner = fixture_runner("passing")
    workspace = runner.working_directory.parent
    results = run_steps(runner, "ceiling", "verify")
    assert results["verify"].returncode == 0, results["verify"].output
    assert not (workspace / ".check-workflow").exists()
    assert (workspace / "runner_temp" / "check-workflow" / "scripts" / "verify_check.py").is_file()


# @spec CHECK-012
def test_callers_python_path_cannot_shadow_the_standard_library(
    fixture_runner: RunnerFactory, tmp_path: Path
) -> None:
    """A caller's PYTHONPATH (as mise-action exports it) doesn't reach the script."""
    shadow = tmp_path / "shadow"
    shadow.mkdir()
    (shadow / "json.py").write_text('raise SystemExit("shadowed json imported")\n')
    runner = fixture_runner("passing")
    runner.env["PYTHONPATH"] = str(shadow)
    results = run_steps(runner, "ceiling", "verify")
    assert results["verify"].returncode == 0, results["verify"].output


# @spec CHECK-RUN-008
def test_alias_dependency_is_accepted(fixture_runner: RunnerFactory) -> None:
    """A dependency named by a task's alias passes verification."""
    results = run_steps(fixture_runner("alias-dependency"), "ceiling", "verify", "check")
    assert results["verify"].returncode == 0, results["verify"].output
    assert "alias-ok" in results["check"].output


# @spec CHECK-RUN-007
def test_redefined_task_run_by_check_is_rejected(fixture_runner: RunnerFactory) -> None:
    """A task `check` starts from its `run` list is checked like a dependency."""
    runner = fixture_runner("override-run")
    results = run_steps(runner, "ceiling", "verify")
    assert results["verify"].returncode != 0
    source = runner.working_directory.resolve() / ".config/mise/config.toml"
    assert f'task "lint" is defined in {source}' in results["verify"].output


# @spec CHECK-RUN-008
def test_monorepo_root_is_accepted(fixture_runner: RunnerFactory) -> None:
    """A repo in mise's monorepo mode, whose tasks are named `//:<name>`, passes verification."""
    results = run_steps(fixture_runner("monorepo"), "ceiling", "verify", "check")
    assert results["verify"].returncode == 0, results["verify"].output
    assert "monorepo-lint-ok" in results["check"].output
    assert "monorepo-fmt-ok" in results["check"].output
