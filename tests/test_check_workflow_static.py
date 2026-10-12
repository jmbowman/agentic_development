"""Static tests of the shared check workflow and of this repo's own CI workflow."""

from __future__ import annotations

import re
from typing import Any

from tests.support import (
    CHECK_WORKFLOW,
    SELF_CI,
    load_workflow,
    only_job,
    step_by_id,
    step_index,
)

WORKING_DIRECTORY_EXPR = "${{ inputs.working-directory }}"
SHA_PIN = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
VERSION_COMMENT = re.compile(r"#\s*v\S+\s*$")


# @spec CHECK-001
def test_triggered_only_by_workflow_call() -> None:
    """The workflow has `workflow_call` as its only trigger."""
    triggers = load_workflow(CHECK_WORKFLOW)["on"]
    assert list(triggers) == ["workflow_call"]


# @spec CHECK-002
def test_single_optional_working_directory_input() -> None:
    """The only input is an optional string `working-directory` defaulting to `.`."""
    inputs = load_workflow(CHECK_WORKFLOW)["on"]["workflow_call"]["inputs"]
    assert list(inputs) == ["working-directory"]
    spec = inputs["working-directory"]
    assert spec.get("required", False) is False
    assert spec["type"] == "string"
    assert spec["default"] == "."


# @spec CHECK-003
def test_working_directory_reaches_mise_action_and_run_steps(check_job: dict[str, Any]) -> None:
    """The mise-action step and every `run` step use the `working-directory` input."""
    mise_step = step_by_id(check_job, "mise")
    assert mise_step["with"]["working_directory"] == WORKING_DIRECTORY_EXPR
    default = check_job.get("defaults", {}).get("run", {}).get("working-directory")
    run_steps = [step for step in check_job["steps"] if "run" in step]
    assert run_steps
    for step in run_steps:
        assert step.get("working-directory", default) == WORKING_DIRECTORY_EXPR, step


# @spec CHECK-004
def test_only_contents_read_permission(check_job: dict[str, Any]) -> None:
    """The workflow asks for read access to contents and nothing else."""
    workflow = load_workflow(CHECK_WORKFLOW)
    levels = [workflow.get("permissions"), check_job.get("permissions")]
    granted = [level for level in levels if level is not None]
    assert granted
    assert all(level == {"contents": "read"} for level in granted)


# @spec CHECK-005
def test_trusts_the_workspace_at_job_level(check_job: dict[str, Any]) -> None:
    """Mise trusts every config under the workspace, for every step."""
    assert check_job["env"]["MISE_TRUSTED_CONFIG_PATHS"] == "${{ github.workspace }}"


# @spec CHECK-006
def test_runs_on_a_versioned_x86_ubuntu_image(check_job: dict[str, Any]) -> None:
    """The runner image names an explicit Ubuntu version and no ARM suffix."""
    assert re.fullmatch(r"ubuntu-\d{2}\.\d{2}", check_job["runs-on"])


# @spec CHECK-007
def test_mise_action_pins_an_exact_mise_version(check_job: dict[str, Any]) -> None:
    """mise-action installs an exact, calendar-versioned mise release."""
    mise_step = step_by_id(check_job, "mise")
    assert mise_step["uses"].startswith("jdx/mise-action@")
    assert re.fullmatch(r"\d{4}\.\d+\.\d+", str(mise_step["with"]["version"]))


# @spec CHECK-008
def test_every_action_is_pinned_by_sha_with_a_version_comment() -> None:
    """Each `uses:` line names a 40-character SHA followed by `# v<version>`."""
    uses_lines = [
        line.strip()
        for line in CHECK_WORKFLOW.read_text().splitlines()
        if line.strip().removeprefix("- ").startswith("uses:")
    ]
    assert uses_lines
    for line in uses_lines:
        value = line.removeprefix("- ").removeprefix("uses:").split("#")[0].strip()
        assert SHA_PIN.fullmatch(value), line
        assert VERSION_COMMENT.search(line), line


# @spec CHECK-009
def test_first_step_checks_out_the_triggering_commit(check_job: dict[str, Any]) -> None:
    """The first step is actions/checkout with no ref override."""
    first = check_job["steps"][0]
    assert first["uses"].startswith("actions/checkout@")
    assert not {"ref", "repository"} & set(first.get("with", {}))


# @spec CHECK-010
def test_ceiling_is_set_before_any_mise_step(check_job: dict[str, Any]) -> None:
    """The config-ceiling step runs before mise-action and the verify and check steps."""
    ceiling = step_index(check_job, "ceiling")
    for later in ("mise", "verify", "check"):
        assert ceiling < step_index(check_job, later), later
    assert "MISE_CEILING_PATHS" in step_by_id(check_job, "ceiling")["run"]


# @spec CHECK-011
def test_script_step_fetches_only_the_verifier_from_the_workflows_commit(
    check_job: dict[str, Any],
) -> None:
    """A second checkout fetches the verification script from the workflow's own repo and commit."""
    step = step_by_id(check_job, "script")
    assert step["uses"].startswith("actions/checkout@")
    assert step["with"] == {
        "repository": "${{ job.workflow_repository }}",
        "ref": "${{ job.workflow_sha }}",
        "path": ".check-workflow",
        "persist-credentials": False,
        "sparse-checkout": "scripts/verify_check.py",
        "sparse-checkout-cone-mode": False,
    }
    assert step_index(check_job, "mise") < step_index(check_job, "script")
    assert step_index(check_job, "script") + 1 == step_index(check_job, "verify")


# @spec CHECK-012
def test_verify_moves_the_script_out_and_runs_it_isolated(check_job: dict[str, Any]) -> None:
    """The verify step moves the script to $RUNNER_TEMP, then runs it with the image's Python."""
    lines = [line.strip() for line in step_by_id(check_job, "verify")["run"].splitlines()]
    move = 'mv -T "$GITHUB_WORKSPACE/.check-workflow" "$RUNNER_TEMP/check-workflow"'
    run = '/usr/bin/python3 -I "$RUNNER_TEMP/check-workflow/scripts/verify_check.py"'
    assert move in lines
    assert run in lines
    assert lines.index(move) < lines.index(run)


# @spec CHECK-RUN-001
def test_verification_precedes_checks(check_job: dict[str, Any]) -> None:
    """The task-location verification runs before the checks."""
    assert step_index(check_job, "verify") < step_index(check_job, "check")


# @spec CHECK-RUN-005
def test_checks_run_with_continue_on_error(check_job: dict[str, Any]) -> None:
    """The checks step runs every dependency of `check` even after one fails."""
    script = step_by_id(check_job, "check")["run"]
    assert re.search(r"mise run --continue-on-error check(\s|$)", script)


# @spec CHECK-RUN-006
def test_failing_verification_or_checks_fail_the_job(check_job: dict[str, Any]) -> None:
    """The script checkout, verification and checks steps don't tolerate failure."""
    for step_id in ("script", "verify", "check"):
        assert "continue-on-error" not in step_by_id(check_job, step_id)


def test_run_steps_use_bash_without_expressions(check_job: dict[str, Any]) -> None:
    """Every `run` step declares `shell: bash` and has no `${{ }}` in its script (design)."""
    for step in check_job["steps"]:
        if "run" in step:
            assert step.get("shell") == "bash", step.get("id")
            assert "${{" not in step["run"], step.get("id")


def _self_ci_jobs() -> dict[str, dict[str, Any]]:
    workflow = load_workflow(SELF_CI)
    assert "push" in workflow["on"]
    return workflow["jobs"]


def _reusable_call_dirs() -> set[str]:
    return {
        job["with"]["working-directory"]
        for job in _self_ci_jobs().values()
        if job.get("uses") == "./.github/workflows/check.yml"
    }


# @spec CHECK-TEST-001
def test_self_ci_calls_the_workflow_on_the_passing_fixture() -> None:
    """This repo's CI calls the workflow on the passing fixture on every push."""
    assert "tests/fixtures/passing" in _reusable_call_dirs()


# @spec CHECK-TEST-002
def test_self_ci_calls_the_workflow_on_the_fragment_fixture() -> None:
    """This repo's CI calls the workflow on a fixture whose tool is pinned only in a fragment."""
    assert "tests/fixtures/fragment" in _reusable_call_dirs()


# @spec CHECK-TEST-003
def test_self_ci_calls_the_workflow_on_the_symlinked_fixture() -> None:
    """This repo's CI calls the workflow on a fixture whose conf.d entry is a symlink."""
    assert "tests/fixtures/symlinked" in _reusable_call_dirs()


def _negative_job(fixture: str) -> dict[str, Any]:
    for job in _self_ci_jobs().values():
        for step in job.get("steps", []):
            if step.get("working-directory") == f"tests/fixtures/{fixture}":
                return job
    msg = f"no CI job runs steps in tests/fixtures/{fixture}"
    raise AssertionError(msg)


def _assert_env(job: dict[str, Any]) -> dict[str, str]:
    """The assert step's env, where each expected step outcome becomes `true` or `false`."""
    step = step_by_id(job, "assert")
    assert step.get("if") == "always()"
    return {str(key): str(value) for key, value in step["env"].items()}


def _assert_negative_job(fixture: str, tolerated: tuple[str, ...]) -> dict[str, Any]:
    job = _negative_job(fixture)
    for step_id in tolerated:
        assert step_by_id(job, step_id).get("continue-on-error") is True
    assert step_index(job, "assert") > max(step_index(job, step_id) for step_id in tolerated)
    return job


# @spec CHECK-TEST-004
def test_self_ci_asserts_failures_do_not_stop_other_checks() -> None:
    """A CI job proves a failing dependency doesn't abort a slower passing one."""
    job = _assert_negative_job("failing", ("verify", "check"))
    env = _assert_env(job)
    assert env["VERIFY_PASSED"] == "${{ steps.verify.outcome == 'success' }}"
    assert env["CHECK_FAILED"] == "${{ steps.check.outcome == 'failure' }}"
    assert "MARKER-slow-ok" in step_by_id(job, "assert")["run"]
    assert "tee" in step_by_id(job, "check")["run"]


# @spec CHECK-TEST-005
def test_self_ci_asserts_an_overridden_check_is_rejected() -> None:
    """A CI job proves verification fails when a repo redefines `check`."""
    job = _assert_negative_job("override-check", ("verify",))
    assert _assert_env(job)["VERIFY_FAILED"] == "${{ steps.verify.outcome == 'failure' }}"


# @spec CHECK-TEST-007
def test_self_ci_asserts_an_overridden_dependency_is_rejected() -> None:
    """A CI job proves verification fails when a repo redefines a dependency of `check`."""
    job = _assert_negative_job("override-test", ("verify",))
    assert _assert_env(job)["VERIFY_FAILED"] == "${{ steps.verify.outcome == 'failure' }}"


# @spec CHECK-TEST-006
def test_repeated_steps_match_the_check_workflow(check_job: dict[str, Any]) -> None:
    """The negative CI jobs repeat check.yml's steps, in order, with the same content."""
    repeated = ("ceiling", "mise", "script", "verify", "check")
    for fixture in ("failing", "override-check", "override-test"):
        job = _negative_job(fixture)
        ids = [step.get("id") for step in job["steps"] if step.get("id") in repeated]
        assert ids[:4] == ["ceiling", "mise", "script", "verify"], (fixture, ids)
        assert ids in (ids[:4], [*ids[:4], "check"]), (fixture, ids)
        for step_id in ids:
            step = step_by_id(job, step_id)
            expected = step_by_id(check_job, step_id)
            assert step.get("uses") == expected.get("uses"), (fixture, step_id)
            assert step.get("run") == expected.get("run"), (fixture, step_id)
            with_ = dict(step.get("with", {}))
            expected_with = dict(expected.get("with", {}))
            if step_id == "mise":
                assert with_.pop("working_directory") == f"tests/fixtures/{fixture}", fixture
                expected_with.pop("working_directory")
            assert with_ == expected_with, (fixture, step_id)


def test_check_workflow_has_one_job() -> None:
    """The check workflow defines a single job (assumed by the other tests)."""
    only_job(load_workflow(CHECK_WORKFLOW))
