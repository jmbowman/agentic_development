"""Paths, loaders and step-running helpers shared by this repo's tests."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures"
CHECK_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "check.yml"
SELF_CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"
PRESET = REPO_ROOT / "renovate" / "default.json"
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify_check.py"

# How GitHub runs a step's script on Linux: `shell: bash`, or no `shell` at all.
SHELLS = {
    "bash": ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c"],
    None: ["bash", "-e", "-c"],
}


def load_workflow(path: Path) -> dict[str, Any]:
    """Load a GitHub Actions workflow, normalizing YAML 1.1's `on: -> True` quirk.

    Args:
        path: The workflow file to read.

    Returns:
        The parsed workflow, with its trigger mapping under the `"on"` key.
    """
    data = yaml.safe_load(path.read_text())
    if True in data:
        data["on"] = data.pop(True)
    return data


def only_job(workflow: dict[str, Any]) -> dict[str, Any]:
    """Return the single job of a workflow, failing if it has more than one.

    Args:
        workflow: A parsed workflow.

    Returns:
        The workflow's only job.
    """
    jobs = list(workflow["jobs"].values())
    assert len(jobs) == 1, f"expected exactly one job, found {len(jobs)}"
    return jobs[0]


def step_by_id(job: dict[str, Any], step_id: str) -> dict[str, Any]:
    """Return the step with the given `id` in a job.

    Args:
        job: A parsed job.
        step_id: The step's `id`.

    Returns:
        The matching step.
    """
    for step in job["steps"]:
        if step.get("id") == step_id:
            return step
    pytest.fail(f"no step with id {step_id!r}")


def step_index(job: dict[str, Any], step_id: str) -> int:
    """Return the position of the step with the given `id` in a job.

    Args:
        job: A parsed job.
        step_id: The step's `id`.

    Returns:
        The step's zero-based index.
    """
    steps: list[dict[str, Any]] = job["steps"]
    return steps.index(step_by_id(job, step_id))


def parse_github_env(text: str) -> dict[str, str]:
    """Parse `NAME=value` lines from `$GITHUB_ENV`; the multiline `NAME<<EOF` form is unsupported.

    Args:
        text: The file's content.

    Returns:
        The exported variables.
    """
    exported: dict[str, str] = {}
    for line in text.splitlines():
        if line:
            name, separator, value = line.partition("=")
            assert separator, f"unsupported $GITHUB_ENV line: {line!r}"
            exported[name] = value
    return exported


@dataclass
class StepResult:
    """The outcome of running one workflow step locally."""

    returncode: int
    output: str


class StepRunner:
    """Runs `run` steps from the check workflow the way a GitHub runner would.

    Each step's script runs in the working directory with the shell GitHub would use,
    the job's and step's `env`, and the variables earlier steps appended to
    `$GITHUB_ENV`. mise sees only the workspace's config: global and system configs
    point at empty files, and inherited `MISE_*` variables are removed.
    """

    def __init__(self, workspace: Path, working_directory: Path, job: dict[str, Any]) -> None:
        """Prepare a runner.

        Args:
            workspace: Stands in for `${{ github.workspace }}`.
            working_directory: The directory the steps run in.
            job: The parsed job whose steps will run.
        """
        self.working_directory = working_directory
        self.job = job
        self.github_env = workspace / "github_env"
        self.github_env.write_text("")
        runner_temp = workspace / "runner_temp"
        runner_temp.mkdir()
        empty_config = workspace / "empty-mise.toml"
        empty_config.write_text("")
        inherited = {key: value for key, value in os.environ.items() if not key.startswith("MISE_")}
        self.expressions = {
            "${{ github.workspace }}": str(workspace),
            "${{ inputs.working-directory }}": str(working_directory.relative_to(workspace)),
        }
        job_env = self._expand(job.get("env", {}))
        self.env = {
            **inherited,
            "CI": "true",
            "GITHUB_ACTIONS": "true",
            "GITHUB_ENV": str(self.github_env),
            "GITHUB_WORKSPACE": str(workspace),
            "RUNNER_TEMP": str(runner_temp),
            "MISE_GLOBAL_CONFIG_FILE": str(empty_config),
            "MISE_SYSTEM_CONFIG_FILE": str(empty_config),
            **job_env,
        }

    def _expand(self, env: dict[str, Any]) -> dict[str, str]:
        """Substitute the expressions this runner knows; fail on any other."""
        expanded = {}
        for key, value in env.items():
            text = str(value)
            for expression, replacement in self.expressions.items():
                text = text.replace(expression, replacement)
            assert "${{" not in text, f"unsupported expression in env {key}: {value}"
            expanded[key] = text
        return expanded

    def run(self, step_id: str) -> StepResult:
        """Run one step's script and absorb what it exported.

        Args:
            step_id: The `id` of a `run` step in the job.

        Returns:
            The step's exit code and combined output.
        """
        step = step_by_id(self.job, step_id)
        script = step["run"]
        assert "${{" not in script, f"step {step_id!r} uses an expression in its run text"
        shell = step.get("shell", self.job.get("defaults", {}).get("run", {}).get("shell"))
        assert shell in SHELLS, f"unsupported shell {shell!r}"
        step_env = self._expand(step.get("env", {}))
        completed = subprocess.run(  # noqa: S603
            [*SHELLS[shell], script],
            cwd=self.working_directory,
            env={**self.env, **step_env},
            capture_output=True,
            text=True,
            check=False,
        )
        self.env.update(parse_github_env(self.github_env.read_text()))
        return StepResult(completed.returncode, completed.stdout + completed.stderr)


def require_tool(name: str) -> str:
    """Return the path of a pinned tool, failing the test if it isn't on PATH.

    Args:
        name: The executable name.

    Returns:
        The executable's absolute path.
    """
    path = shutil.which(name)
    if path is None:
        pytest.fail(f"{name} is not on PATH; run the tests through `mise run test`")
    return path
