"""Paths, loaders and step-running helpers shared by this repo's tests."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
import yaml

if TYPE_CHECKING:
    from collections.abc import Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures"
CHECK_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "check.yml"
SELF_CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"
LOCK_REFRESH = REPO_ROOT / ".github" / "workflows" / "lock-refresh.yml"
PRESET = REPO_ROOT / "renovate" / "default.json"
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify_check.py"
SKILLS = REPO_ROOT / "skills"
EVALS = REPO_ROOT / "evals"

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
    """Runs a workflow job's `run` steps the way a GitHub runner would.

    Each step's script runs in the working directory with the shell GitHub would use,
    the job's and step's `env`, and the variables earlier steps appended to
    `$GITHUB_ENV`. What a step writes to `$GITHUB_OUTPUT` becomes available to later
    steps' `env` as `${{ steps.<id>.outputs.<name> }}`. mise sees only the workspace's
    config: global and system configs point at empty files, and inherited `MISE_*`
    variables are removed.
    """

    def __init__(
        self,
        workspace: Path,
        working_directory: Path,
        job: dict[str, Any],
        expressions: dict[str, str] | None = None,
    ) -> None:
        """Prepare a runner.

        Args:
            workspace: Stands in for `${{ github.workspace }}`.
            working_directory: The directory the steps run in.
            job: The parsed job whose steps will run.
            expressions: Further `${{ }}` expressions and the values to substitute for them.
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
            "${{ runner.temp }}": str(runner_temp),
            **(expressions if expressions is not None else {}),
        }
        self.github_output = workspace / "github_output"
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

    def install_like_mise_action(self) -> StepResult:
        """Install the tools as mise-action does when it finds a `mise.lock` above the directory.

        mise-action searches every ancestor of its working directory for a lock file, ignoring
        mise's config ceiling, and then runs `mise install --locked`. In this repo's CI it always
        finds the root `mise.lock`.

        Returns:
            The install's exit code and combined output.
        """
        completed = subprocess.run(
            ["mise", "install", "--locked"],  # noqa: S607
            cwd=self.working_directory,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        return StepResult(completed.returncode, completed.stdout + completed.stderr)

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
        self.github_output.write_text("")
        completed = subprocess.run(  # noqa: S603
            [*SHELLS[shell], script],
            cwd=self.working_directory,
            env={**self.env, **step_env, "GITHUB_OUTPUT": str(self.github_output)},
            capture_output=True,
            text=True,
            check=False,
        )
        self.env.update(parse_github_env(self.github_env.read_text()))
        for name, value in parse_github_env(self.github_output.read_text()).items():
            self.expressions[f"${{{{ steps.{step_id}.outputs.{name} }}}}"] = value
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


def git_repo(root: Path, files: dict[str, str], links: dict[str, str] | None = None) -> Path:
    """Create a committed git repo with the given files and symlinks.

    Args:
        root: The directory to create the repo in; it must not exist yet.
        files: File contents, keyed by path relative to `root`.
        links: Symlink targets, keyed by link path relative to `root`.

    Returns:
        `root`.
    """
    root.mkdir(parents=True)
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    for name, target in (links or {}).items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run([*git, "init", "-q"], cwd=root, check=True)  # noqa: S603
    subprocess.run([*git, "add", "-A"], cwd=root, check=True)  # noqa: S603
    subprocess.run([*git, "commit", "-qm", "fixture"], cwd=root, check=True)  # noqa: S603
    return root


def renovate_log(
    repo: Path, dry_run: str, config: dict[str, Any] | None = None
) -> Iterator[dict[str, Any]]:
    """Run Renovate's local platform in `repo`, and yield its JSON log records.

    The config goes in the repo's own `renovate.json`, as consumers use the preset, so its
    keys override those of the presets it extends. (As a global config file, the preset's
    `ignorePaths` would instead be replaced by `config:best-practices`'s.)

    Args:
        repo: A git repo, as `git_repo` makes.
        dry_run: Renovate's `--dry-run` mode, such as `extract`.
        config: The repo config to commit as `renovate.json`; the preset if omitted.

    Yields:
        Each JSON record Renovate logs.
    """
    renovate = require_tool("renovate")
    if config is None:
        shutil.copy2(PRESET, repo / "renovate.json")
    else:
        (repo / "renovate.json").write_text(json.dumps(config))
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run([*git, "add", "renovate.json"], cwd=repo, check=True)  # noqa: S603
    subprocess.run([*git, "commit", "-qm", "renovate config"], cwd=repo, check=True)  # noqa: S603
    env = {**os.environ, "LOG_LEVEL": "debug", "LOG_FORMAT": "json"}
    completed = subprocess.run(  # noqa: S603
        [
            renovate,
            "--platform=local",
            f"--dry-run={dry_run}",
            "--print-config",
            "--onboarding=false",
            "--require-config=required",
        ],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    records = []
    for line in completed.stdout.splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    fatal = [record.get("msg", "") for record in records if record.get("level", 0) >= 50]
    assert completed.returncode == 0, fatal or completed.stderr[-2000:]
    # Renovate exits 0 on an invalid repo config, after logging it and skipping the run.
    invalid = [
        record.get("err", {}).get("validationMessage")
        for record in records
        if record.get("msg") == "Repository has invalid config"
    ]
    assert not invalid, invalid
    yield from records


def frontmatter(path: Path) -> dict[str, Any]:
    """The YAML frontmatter of a Markdown file.

    Args:
        path: The Markdown file to read.

    Returns:
        The frontmatter's mapping.
    """
    match = re.match(r"---\n(.*?)\n---\n", path.read_text(), flags=re.DOTALL)
    assert match, f"{path} has no frontmatter"
    meta = yaml.safe_load(match.group(1))
    assert isinstance(meta, dict), f"{path}'s frontmatter isn't a mapping"
    return meta


def eval_cases(root: Path = EVALS) -> list[Path]:
    """Every eval case directory under a root: one that holds a `prompt.md` or a `case.yaml`.

    Args:
        root: The directory to search: all of `evals/`, or one skill's suite.

    Returns:
        The case directories, sorted.
    """
    return sorted(
        {p.parent for p in root.rglob("prompt.md")} | {p.parent for p in root.rglob("case.yaml")}
    )


def cited_by_evals(root: Path) -> dict[str, list[str]]:
    """Each spec ID cited in a `case.yaml` under a root, with the cases that cite it.

    Args:
        root: One skill's eval suite, such as `evals/prior-art-search`.

    Returns:
        A mapping from spec ID to the names of the cases that cite it.
    """
    cited: dict[str, list[str]] = {}
    for case in eval_cases(root):
        text = (case / "case.yaml").read_text() if (case / "case.yaml").exists() else ""
        for line in re.findall(r"^#\s*@spec\s+(.+)$", text, flags=re.MULTILINE):
            for spec in re.split(r",\s*", line.strip()):
                cited.setdefault(spec, []).append(case.name)
    return cited
