"""Static tests of the shared lock-refresh workflow."""

from __future__ import annotations

import json
import re
from typing import Any

import pytest

from tests.support import (
    CHECK_WORKFLOW,
    LOCK_REFRESH,
    PRESET,
    load_workflow,
    only_job,
    step_by_id,
)

SHA_PIN = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
VERSION_COMMENT = re.compile(r"#\s*v\S+\s*$")
AUTHOR_EMAIL = "lock-refresh@agentic-development.invalid"


@pytest.fixture
def job() -> dict[str, Any]:
    """The single job of the lock-refresh workflow."""
    return only_job(load_workflow(LOCK_REFRESH))


# @spec LOCK-001
def test_triggered_only_by_workflow_call() -> None:
    """The workflow is reusable and has no other trigger."""
    assert list(load_workflow(LOCK_REFRESH)["on"]) == ["workflow_call"]


# @spec LOCK-002
def test_one_required_input_and_one_required_secret() -> None:
    """Callers pass the App's client ID and its private key, and nothing else."""
    call = load_workflow(LOCK_REFRESH)["on"]["workflow_call"]
    assert list(call["inputs"]) == ["client-id"]
    assert call["inputs"]["client-id"]["type"] == "string"
    assert call["inputs"]["client-id"]["required"] is True
    assert list(call["secrets"]) == ["app-private-key"]
    assert call["secrets"]["app-private-key"]["required"] is True


# @spec LOCK-003
def test_only_contents_read_permission(job: dict[str, Any]) -> None:
    """The job's own token can only read."""
    workflow = load_workflow(LOCK_REFRESH)
    granted = [level for level in (workflow.get("permissions"), job.get("permissions")) if level]
    assert granted
    assert all(level == {"contents": "read"} for level in granted)


# @spec LOCK-004
def test_safe_mode_for_the_whole_job(job: dict[str, Any]) -> None:
    """Every mise command in the job runs in safe mode."""
    assert str(job["env"]["MISE_SAFE"]) == "1"


# @spec LOCK-005
def test_runs_only_for_renovate_pull_requests_from_the_same_repo(job: dict[str, Any]) -> None:
    """The job condition requires a same-repo pull request opened by Renovate."""
    condition = " ".join(job["if"].split())
    assert "github.event_name == 'pull_request'" in condition
    assert "github.event.pull_request.user.login == 'renovate[bot]'" in condition
    assert "github.event.pull_request.head.repo.full_name == github.repository" in condition
    assert "||" not in condition


# @spec LOCK-006
def test_one_run_per_pull_request(job: dict[str, Any]) -> None:
    """A newer run for the same PR cancels an older one."""
    assert job["concurrency"] == {
        "group": "lock-refresh-${{ github.event.pull_request.number }}",
        "cancel-in-progress": True,
    }


# @spec LOCK-007
def test_same_runner_as_the_check_workflow(job: dict[str, Any]) -> None:
    """Renovate's runner bumps keep both workflows on one image."""
    assert job["runs-on"] == only_job(load_workflow(CHECK_WORKFLOW))["runs-on"]


# @spec LOCK-008
def test_thirty_minute_timeout(job: dict[str, Any]) -> None:
    """Provenance downloads can be slow, but a hung run still ends."""
    assert job["timeout-minutes"] == 30


# @spec LOCK-009
def test_every_action_is_pinned_by_sha_with_a_version_comment() -> None:
    """Each `uses:` line names a 40-character SHA followed by `# v<version>`."""
    uses_lines = [
        line.strip()
        for line in LOCK_REFRESH.read_text().splitlines()
        if line.strip().removeprefix("- ").startswith("uses:")
    ]
    assert uses_lines
    for line in uses_lines:
        value = line.removeprefix("- ").removeprefix("uses:").split("#")[0].strip()
        assert SHA_PIN.fullmatch(value), line
        assert VERSION_COMMENT.search(line), line


# @spec LOCK-010
def test_steps_in_order(job: dict[str, Any]) -> None:
    """The token is minted only after `mise lock` and the staging step."""
    ids = [step.get("id") for step in job["steps"]]
    assert ids == ["checkout", "tracked", "mise", "lock", "changes", "token", "push"]


# @spec LOCK-011
def test_checks_out_the_pr_head_without_credentials(job: dict[str, Any]) -> None:
    """The checkout is the PR's head commit, and leaves no token in git config."""
    step = step_by_id(job, "checkout")
    assert step["uses"].startswith("actions/checkout@")
    assert step["with"] == {
        "ref": "${{ github.event.pull_request.head.sha }}",
        "persist-credentials": False,
    }


# @spec LOCK-012
def test_mise_action_sees_no_project_config(job: dict[str, Any]) -> None:
    """mise-action runs in an empty directory, installs nothing and exports nothing."""
    step = step_by_id(job, "mise")
    check_mise = step_by_id(only_job(load_workflow(CHECK_WORKFLOW)), "mise")
    assert step["uses"] == check_mise["uses"]
    assert step["with"] == {
        "version": check_mise["with"]["version"],
        "install": False,
        "env": False,
        "cache": False,
        "working_directory": "${{ runner.temp }}/lock-refresh-empty",
    }


# @spec LOCK-013
def test_token_only_when_something_is_staged(job: dict[str, Any]) -> None:
    """The App token can write contents in this repo only, and exists only to push."""
    step = step_by_id(job, "token")
    assert step["uses"].startswith("actions/create-github-app-token@")
    assert step["if"] == "steps.changes.outputs.staged == 'true'"
    assert step["with"] == {
        "client-id": "${{ inputs.client-id }}",
        "private-key": "${{ secrets.app-private-key }}",
        "repositories": "${{ github.event.repository.name }}",
        "permission-contents": "write",
    }


# @spec LOCK-RUN-001, LOCK-RUN-005
def test_later_steps_depend_on_earlier_outputs(job: dict[str, Any]) -> None:
    """Without a tracked lock, nothing after `tracked` runs; without changes, nothing pushes."""
    for step_id in ("mise", "lock", "changes"):
        assert step_by_id(job, step_id)["if"] == "steps.tracked.outputs.found == 'true'", step_id
    assert step_by_id(job, "push")["if"] == "steps.changes.outputs.staged == 'true'"


# @spec LOCK-014
def test_run_steps_use_bash_without_expressions(job: dict[str, Any]) -> None:
    """Values reach scripts through `env:`, so the same text runs in this repo's tests."""
    run_steps = [step for step in job["steps"] if "run" in step]
    assert {step["id"] for step in run_steps} == {"tracked", "lock", "changes", "push"}
    for step in run_steps:
        assert step.get("shell") == "bash", step["id"]
        assert "${{" not in step["run"], step["id"]


# @spec LOCK-016
def test_lock_step_has_a_read_only_github_token(job: dict[str, Any]) -> None:
    """The GitHub API calls `mise lock` makes use the job's own read-only token."""
    step = step_by_id(job, "lock")
    assert step["env"]["GITHUB_TOKEN"] == "${{ github.token }}"  # noqa: S105
    assert re.search(r"(^|\s)mise lock(\s|$)", step["run"])


# @spec LOCK-RUN-006, PRESET-LOCK-001
def test_commit_author_is_the_one_the_preset_ignores(job: dict[str, Any]) -> None:
    """Renovate keeps maintaining PRs the workflow commits to."""
    assert AUTHOR_EMAIL in step_by_id(job, "push")["run"]
    assert json.loads(PRESET.read_text())["gitIgnoredAuthors"] == [AUTHOR_EMAIL]


# @spec LOCK-RUN-010
def test_token_header_is_scoped_to_github(job: dict[str, Any]) -> None:
    """The authorization header applies to https://github.com/ and is set through the env."""
    script = step_by_id(job, "push")["run"]
    assert "GIT_CONFIG_KEY_0=http.https://github.com/.extraheader" in script
    assert "GIT_CONFIG_COUNT=1" in script
