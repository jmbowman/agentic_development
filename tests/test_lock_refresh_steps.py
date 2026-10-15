"""Behavioral tests: run the lock-refresh workflow's own steps against scratch git repos."""

from __future__ import annotations

import base64
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from tests.support import LOCK_REFRESH, StepRunner, load_workflow, only_job

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support import StepResult

BRANCH = "renovate/template-update"
TOKEN = "test-app-token-0123456789"  # noqa: S105 (a dummy value the tests look for)
AUTHOR = "Lock Refresh <lock-refresh@agentic-development.invalid>"
SETUP_IDENTITY = ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid"]
OLD_PIN = '[tools]\n"github:sharkdp/hyperfine" = "1.19.0"\n'
NEW_PIN = '[tools]\n"github:sharkdp/hyperfine" = "2.0.0"\n'


@dataclass
class Scratch:
    """A checked-out PR head, its bare `origin`, and a runner for the workflow's job."""

    work: Path
    origin: Path
    head_sha: str
    runner: StepRunner

    def git(self, *args: str, cwd: Path | None = None) -> str:
        """Run git for test setup or inspection, with a fixed identity."""
        completed = subprocess.run(  # noqa: S603
            ["/usr/bin/git", *SETUP_IDENTITY, *args],
            cwd=cwd or self.work,
            env=self.runner.env,
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout.strip()

    def remote_head(self) -> str:
        """The commit the remote PR branch points at, or an empty string if it's gone."""
        completed = subprocess.run(  # noqa: S603
            ["/usr/bin/git", "rev-parse", "--verify", "--quiet", f"refs/heads/{BRANCH}"],
            cwd=self.origin,
            env=self.runner.env,
            capture_output=True,
            text=True,
            check=False,
        )
        return completed.stdout.strip()

    def mise(self, *args: str, safe: bool = True) -> subprocess.CompletedProcess[str]:
        """Run mise in the work tree with the runner's environment."""
        env = dict(self.runner.env)
        if not safe:
            env.pop("MISE_SAFE", None)
        return subprocess.run(  # noqa: S603
            ["mise", *args],  # noqa: S607
            cwd=self.work,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )


def make_scratch(
    tmp_path: Path, files: dict[str, str], *, update: dict[str, str] | None = None
) -> Scratch:
    """Commit `files` on a base commit, then `update` as the PR head, and push to `origin`."""
    workspace = tmp_path / "workspace"
    work = workspace / "repo"
    work.mkdir(parents=True)
    home = tmp_path / "home"
    home.mkdir()
    runner = StepRunner(
        workspace,
        work,
        only_job(load_workflow(LOCK_REFRESH)),
        expressions={
            "${{ github.event.pull_request.head.ref }}": BRANCH,
            "${{ steps.token.outputs.token }}": TOKEN,
            "${{ github.token }}": os.environ.get("GITHUB_TOKEN", ""),
        },
    )
    # The runner has no git identity: tests must not borrow the developer's.
    runner.env.update(
        {"HOME": str(home), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
    )
    for key in ("XDG_DATA_HOME", "XDG_STATE_HOME"):
        runner.env[key] = str(tmp_path / key.lower())
    origin = tmp_path / "origin.git"
    scratch = Scratch(work, origin, "", runner)
    scratch.git("init", "--quiet", "--bare", str(origin), cwd=tmp_path)
    scratch.git("init", "--quiet", "--initial-branch=main")
    write(work, files)
    scratch.git("add", "--all")
    scratch.git("commit", "--quiet", "--message", "base")
    if update is not None:
        write(work, update)
        scratch.git("add", "--all")
        scratch.git("commit", "--quiet", "--message", "template update")
    scratch.git("remote", "add", "origin", str(origin))
    scratch.git("push", "--quiet", "origin", f"HEAD:refs/heads/{BRANCH}")
    scratch.head_sha = scratch.git("rev-parse", "HEAD")
    scratch.git("checkout", "--quiet", "--detach", scratch.head_sha)
    runner.expressions["${{ github.event.pull_request.head.sha }}"] = scratch.head_sha
    return scratch


def write(root: Path, files: dict[str, str]) -> None:
    """Write files relative to `root`, creating directories."""
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def locked_scratch(tmp_path: Path, extra: dict[str, str] | None = None) -> Scratch:
    """A repo whose base commit tracks a one-platform lock, and whose PR head bumps the pin."""
    seed = make_scratch(tmp_path / "seed", {".config/mise/config.toml": OLD_PIN})
    locked = seed.mise("lock", "--platform", "linux-x64")
    assert locked.returncode == 0, locked.stderr
    lock = (seed.work / ".config/mise/mise.lock").read_text()
    files = {".config/mise/config.toml": OLD_PIN, ".config/mise/mise.lock": lock, **(extra or {})}
    return make_scratch(tmp_path / "pr", files, update={".config/mise/config.toml": NEW_PIN})


def run_steps(scratch: Scratch, *step_ids: str) -> dict[str, StepResult]:
    """Run steps in order, failing the test if any but the last one fails."""
    results: dict[str, StepResult] = {}
    for step_id in step_ids:
        results[step_id] = scratch.runner.run(step_id)
        if step_id != step_ids[-1]:
            assert results[step_id].returncode == 0, (step_id, results[step_id].output)
    return results


def outputs(scratch: Scratch, step_id: str) -> dict[str, str]:
    """The outputs a step wrote, as later steps see them."""
    prefix = f"${{{{ steps.{step_id}.outputs."
    return {
        key.removeprefix(prefix).removesuffix(" }}"): value
        for key, value in scratch.runner.expressions.items()
        if key.startswith(prefix)
    }


def committed_paths(scratch: Scratch, commit: str) -> set[str]:
    """Paths a commit changed relative to its parent, in the work tree's object store."""
    names = scratch.git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    return set(names.splitlines())


def platforms(lock_text: str) -> set[str]:
    """The platform names a mise lock file lists."""
    return set(re.findall(r'\."platforms\.([\w-]+)"\]', lock_text))


# @spec LOCK-RUN-013
def test_tracked_step_creates_the_empty_directory(tmp_path: Path) -> None:
    """mise-action's working directory exists and holds nothing."""
    scratch = make_scratch(tmp_path, {".config/mise/mise.lock": "lockfile_version = 3\n"})
    result = run_steps(scratch, "tracked")["tracked"]
    assert result.returncode == 0, result.output
    empty = scratch.runner.working_directory.parent / "runner_temp" / "lock-refresh-empty"
    assert empty.is_dir()
    assert not list(empty.iterdir())
    assert outputs(scratch, "tracked")["found"] == "true"


# @spec LOCK-RUN-001
def test_no_tracked_lock_skips_everything(tmp_path: Path) -> None:
    """A repo that doesn't commit a lock file is left alone."""
    scratch = make_scratch(tmp_path, {".config/mise/config.toml": OLD_PIN})
    result = run_steps(scratch, "tracked")["tracked"]
    assert result.returncode == 0, result.output
    assert outputs(scratch, "tracked")["found"] == "false"


# @spec LOCK-RUN-002
@pytest.mark.parametrize(
    "path", [".mise.lock", ".config/mise.lock", "mise.ci.lock", ".config/mise/mise.ci.lock"]
)
def test_unsupported_lock_layout_fails(tmp_path: Path, path: str) -> None:
    """A lock file the workflow doesn't handle fails the job, named."""
    scratch = make_scratch(tmp_path, {path: "lockfile_version = 3\n", "mise.lock": ""})
    result = run_steps(scratch, "tracked")["tracked"]
    assert result.returncode != 0
    assert path in result.output


@pytest.mark.network
# @spec LOCK-RUN-003, LOCK-RUN-004, LOCK-RUN-006, LOCK-RUN-007, LOCK-RUN-014
def test_changed_pin_gets_a_lock_only_commit(tmp_path: Path) -> None:
    """A template update's pin change is locked and pushed, touching nothing else."""
    extra = {"README.md": "unrelated\n", "mise.toml": NEW_PIN}  # root config, lock untracked
    scratch = locked_scratch(tmp_path, extra)
    before = (scratch.work / ".config/mise/mise.lock").read_text()
    write(scratch.work, {"README.md": "edited, not staged\n", "notes.txt": "untracked\n"})
    results = run_steps(scratch, "tracked", "lock", "changes", "push")
    assert results["push"].returncode == 0, results["push"].output
    assert outputs(scratch, "changes")["staged"] == "true"
    pushed = scratch.remote_head()
    assert scratch.git("rev-parse", f"{pushed}^", cwd=scratch.origin) == scratch.head_sha
    assert committed_paths(scratch, pushed) == {".config/mise/mise.lock"}
    show = "--format=%an <%ae>%n%cn <%ce>%n%s"
    assert scratch.git("show", "--no-patch", show, pushed).splitlines() == [
        AUTHOR,
        AUTHOR,
        "Refresh mise lock files",
    ]
    after = scratch.git("show", f"{pushed}:.config/mise/mise.lock")
    assert '"2.0.0"' in after
    assert platforms(after) == platforms(before) == {"linux-x64"}
    assert (scratch.work / "mise.lock").exists(), "mise lock should have created a root lock"


# @spec LOCK-RUN-003, LOCK-RUN-004
def test_pruned_sidecar_files_are_committed_as_deletions(tmp_path: Path) -> None:
    """Sidecar files `mise lock` deleted leave in the lock commit; other sidecars never enter it.

    `mise lock` prunes a stale tool's entry and deletes its sidecar files. The test makes
    those changes by hand, since only the staging is this workflow's own behavior.
    """
    sidecar = ".mise/locks/npm-cowsay/1.6.0~0000/package.json"
    files = {"mise.lock": "lockfile_version = 3\n# cowsay\n", sidecar: "{}\n"}
    scratch = make_scratch(tmp_path, files)
    shutil.rmtree(scratch.work / ".mise")
    added = ".mise/locks/npm-cowsay/1.6.1~1111/package.json"
    untracked_sidecar = ".config/mise/locks/npm-x/1.0.0~0000/package.json"
    write(
        scratch.work,
        {"mise.lock": "lockfile_version = 3\n", added: "{}\n", untracked_sidecar: "{}\n"},
    )
    results = run_steps(scratch, "tracked", "changes", "push")
    assert results["push"].returncode == 0, results["push"].output
    assert committed_paths(scratch, scratch.remote_head()) == {"mise.lock", sidecar, added}


@pytest.mark.network
# @spec LOCK-RUN-005
def test_unchanged_lock_stages_nothing(tmp_path: Path) -> None:
    """With the lock already current, nothing is staged, so no token or push follows."""
    seed = make_scratch(tmp_path / "seed", {".config/mise/config.toml": NEW_PIN})
    assert seed.mise("lock", "--platform", "linux-x64").returncode == 0
    lock = (seed.work / ".config/mise/mise.lock").read_text()
    files = {".config/mise/config.toml": NEW_PIN, ".config/mise/mise.lock": lock}
    scratch = make_scratch(tmp_path / "pr", files)
    results = run_steps(scratch, "tracked", "lock", "changes")
    assert results["changes"].returncode == 0, results["changes"].output
    assert outputs(scratch, "changes")["staged"] == "false"


@pytest.mark.network
# @spec LOCK-RUN-011
def test_project_scripts_do_not_run(tmp_path: Path) -> None:
    """Safe mode keeps a repo's `_.source` script from running during `mise lock`."""
    config = NEW_PIN + '\n[env]\n_.source = "./canary.sh"\n'
    files = {
        ".config/mise/config.toml": config,
        ".config/mise/mise.lock": "lockfile_version = 3\n",
        "canary.sh": "touch CANARY\n",
    }
    scratch = make_scratch(tmp_path, files)
    results = run_steps(scratch, "tracked", "lock")
    assert results["lock"].returncode == 0, results["lock"].output
    assert not (scratch.work / "CANARY").exists()
    # Control: without safe mode, the same config does run the script.
    scratch.runner.env["MISE_TRUSTED_CONFIG_PATHS"] = str(scratch.work)
    scratch.mise("lock", safe=False)
    assert (scratch.work / "CANARY").exists()


# @spec LOCK-RUN-012
def test_failing_lock_fails_the_step(tmp_path: Path) -> None:
    """When `mise lock` can't run, the step fails, so nothing later runs."""
    files = {
        ".config/mise/config.toml": 'min_version = "2999.1.1"\n' + NEW_PIN,
        ".config/mise/mise.lock": "lockfile_version = 3\n",
    }
    scratch = make_scratch(tmp_path, files)
    results = run_steps(scratch, "tracked", "lock")
    assert results["lock"].returncode != 0


def hand_edited_scratch(tmp_path: Path) -> Scratch:
    """A repo whose tracked lock gets a hand edit, standing in for `mise lock` output."""
    scratch = make_scratch(tmp_path, {".config/mise/mise.lock": "lockfile_version = 3\n"})
    write(scratch.work, {".config/mise/mise.lock": "lockfile_version = 3\n# refreshed\n"})
    return scratch


# @spec LOCK-RUN-008
def test_moved_branch_is_left_alone(tmp_path: Path) -> None:
    """If Renovate pushed meanwhile, the step succeeds with a notice and pushes nothing."""
    scratch = hand_edited_scratch(tmp_path)
    run_steps(scratch, "tracked", "changes")
    moved = scratch.git(
        "commit-tree", "-p", scratch.head_sha, "-m", "renovate", f"{scratch.head_sha}^{{tree}}"
    )
    scratch.git("push", "--quiet", "origin", f"{moved}:refs/heads/{BRANCH}")
    result = scratch.runner.run("push")
    assert result.returncode == 0, result.output
    assert "::notice::" in result.output
    assert scratch.remote_head() == moved


# @spec LOCK-RUN-008
def test_deleted_branch_is_not_recreated(tmp_path: Path) -> None:
    """If the PR's branch is gone, the step succeeds and doesn't bring it back."""
    scratch = hand_edited_scratch(tmp_path)
    run_steps(scratch, "tracked", "changes")
    scratch.git("push", "--quiet", "origin", f":refs/heads/{BRANCH}")
    result = scratch.runner.run("push")
    assert result.returncode == 0, result.output
    assert "::notice::" in result.output
    assert scratch.remote_head() == ""


# @spec LOCK-RUN-009
def test_other_push_failures_fail_the_step(tmp_path: Path) -> None:
    """A rejection the branch's position doesn't explain stays visible."""
    scratch = hand_edited_scratch(tmp_path)
    run_steps(scratch, "tracked", "changes")
    hook = scratch.origin / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\necho rejected by policy >&2\nexit 1\n")
    hook.chmod(0o755)
    result = scratch.runner.run("push")
    assert result.returncode != 0
    assert scratch.remote_head() == scratch.head_sha


# @spec LOCK-RUN-010
def test_token_never_in_arguments_and_masked_first(tmp_path: Path) -> None:
    """The token never reaches a git command line, and its encoded form is masked first."""
    scratch = hand_edited_scratch(tmp_path)
    run_steps(scratch, "tracked", "changes")
    scratch.runner.env["GIT_TRACE"] = "1"
    result = scratch.runner.run("push")
    assert result.returncode == 0, result.output
    encoded = base64.b64encode(f"x-access-token:{TOKEN}".encode()).decode()
    assert TOKEN not in result.output
    lines = [line for line in result.output.splitlines() if encoded in line]
    assert lines
    assert lines[0] == f"::add-mask::{encoded}"
    traced = [line for line in result.output.splitlines() if "trace: " in line]
    assert traced
    assert not [line for line in traced if encoded in line]


# @spec LOCK-015
def test_git_on_path_never_runs(tmp_path: Path) -> None:
    """The steps that stage and push call /usr/bin/git, not whatever `git` is on PATH."""
    scratch = hand_edited_scratch(tmp_path)
    run_steps(scratch, "tracked")
    shim = tmp_path / "shim"
    shim.mkdir()
    marker = tmp_path / "SHIM-RAN"
    (shim / "git").write_text(f"#!/bin/sh\ntouch {marker}\nexit 1\n")
    (shim / "git").chmod(0o755)
    scratch.runner.env["PATH"] = f"{shim}:{scratch.runner.env['PATH']}"
    results = run_steps(scratch, "changes", "push")
    assert results["push"].returncode == 0, results["push"].output
    assert not marker.exists()


# @spec LOCK-RUN-009
def test_unreadable_remote_fails_the_step(tmp_path: Path) -> None:
    """If the push fails and the branch can't be read either, the step fails."""
    scratch = hand_edited_scratch(tmp_path)
    run_steps(scratch, "tracked", "changes")
    scratch.git("remote", "set-url", "origin", str(tmp_path / "missing.git"))
    result = scratch.runner.run("push")
    assert result.returncode != 0
    assert "::notice::" not in result.output


# @spec LOCK-RUN-015
def test_ignored_sidecar_directory_fails_clearly(tmp_path: Path) -> None:
    """A tracked lock whose sidecars are gitignored can't be refreshed, and the step says why."""
    files = {".gitignore": ".mise/\n", "mise.lock": "lockfile_version = 3\n"}
    scratch = make_scratch(tmp_path, files)
    write(scratch.work, {".mise/locks/npm-x/1.0.0~0000/package.json": "{}\n"})
    result = run_steps(scratch, "tracked", "changes")["changes"]
    assert result.returncode != 0
    assert ".mise/locks" in result.output
    assert "ignored" in result.output


# @spec LOCK-RUN-002
@pytest.mark.parametrize("path", ["mise.d/x.lock", ".config/mise/mise.d/x.lock"])
def test_nested_lock_like_paths_are_not_unsupported_layouts(tmp_path: Path, path: str) -> None:
    """Only lock files directly at the root or in `.config/mise/` count."""
    scratch = make_scratch(tmp_path, {path: "", "mise.lock": "lockfile_version = 3\n"})
    result = run_steps(scratch, "tracked")["tracked"]
    assert result.returncode == 0, result.output
