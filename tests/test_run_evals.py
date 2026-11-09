"""Tests of the `eval` task, which runs `claude plugin eval` from a clean copy of the plugin."""

from __future__ import annotations

import os
import shutil
import signal
import stat
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path  # noqa: TC003 (the dataclass's annotations are evaluated)

import pytest

from tests.support import REPO_ROOT, git_repo

SCRIPT = REPO_ROOT / "scripts" / "run_evals.py"
MISE_TOML = REPO_ROOT / "mise.toml"

# A stand-in for `claude`. Each call writes one record, its working directory then each argument,
# NUL-separated, to a new file in $STUB_CALLS. With $STUB_LOCK set it also records, in
# $STUB_LOCK_STATE, whether that lock was held while it ran. The other STUB_* variables make it
# create results, delete a path, wait for a release file, end by a signal or exit with a status.
STUB_CLAUDE = """#!/usr/bin/env bash
set -u
trap 'exit 130' INT
record="$STUB_CALLS/call-$(date +%s%N)-$$"
printf '%s\\0' "$PWD" "$@" > "$record"
if [ -n "${STUB_LOCK:-}" ]; then
  if flock -n "$STUB_LOCK" true; then echo free; else echo held; fi > "$STUB_LOCK_STATE"
fi
for result in ${STUB_RESULTS:-}; do mkdir -p "$result" && echo report > "$result/report.html"; done
if [ -n "${STUB_DELETE:-}" ]; then rm -rf "$STUB_DELETE"; fi
if [ -n "${STUB_STARTED:-}" ]; then : > "$STUB_STARTED"; fi
if [ -n "${STUB_RELEASE:-}" ]; then
  for _ in $(seq 400); do [ -e "$STUB_RELEASE" ] && break; sleep 0.05; done
fi
if [ -n "${STUB_SIGNAL:-}" ]; then kill -"$STUB_SIGNAL" $$; fi
exit "${STUB_EXIT:-0}"
"""

# A wrapper for git that records, for each call, whether the eval copy's lock was held.
GIT_WRAPPER = """#!/usr/bin/env bash
if flock -n "$STUB_LOCK" true; then echo free; else echo held; fi >> "$STUB_GIT_LOG"
exec "$STUB_REAL_GIT" "$@"
"""

FIXTURE_FILES = {
    "README.md": "plugin\n",
    "skills/demo/SKILL.md": "---\nname: demo\n---\n",
    "evals/demo/case-a/scaffold.sh": "#!/usr/bin/env bash\n",
    "evals/demo/case-a/notes.txt": "private-ish\n",
    ".gitignore": "tmp/\nevals/**/results/\nresults/\n",
}
FIXTURE_LINKS = {
    ".claude/skills/demo": "../../skills/demo",
    "dangling": "does-not-exist",
}


@dataclass
class Sandbox:
    """A fixture repo, a cache directory, a stub `claude` and a git wrapper for one test."""

    repo: Path
    cache: Path
    bin: Path
    calls: Path
    git_log: Path

    @property
    def copy(self) -> Path:
        """The eval copy under this sandbox's cache directory."""
        return self.cache / "agentic-development" / "eval-plugin"

    @property
    def lock(self) -> Path:
        """The eval copy's lock file."""
        return self.cache / "agentic-development" / "eval-plugin.lock"

    def env(self, **extra: str) -> dict[str, str]:
        """The run's environment: stubs first on PATH, this cache, no user git or mise config."""
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("STUB_", "GIT_", "MISE_", "XDG_CACHE_HOME"))
        }
        real_git = shutil.which("git")
        assert real_git is not None
        env |= {
            "PATH": f"{self.bin}{os.pathsep}{env.get('PATH', '')}",
            "XDG_CACHE_HOME": str(self.cache),
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "STUB_CALLS": str(self.calls),
            "STUB_GIT_LOG": str(self.git_log),
            "STUB_REAL_GIT": real_git,
            "STUB_LOCK": str(self.lock),
            "STUB_LOCK_STATE": str(self.calls.parent / "lock-state"),
        }
        env.update(extra)
        return env

    def run(
        self, *args: str, cwd: Path | None = None, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        """Run the eval script with `args`, in the fixture repo unless `cwd` says otherwise."""
        return subprocess.run(  # noqa: S603
            [sys.executable, str(SCRIPT), *args],
            cwd=cwd or self.repo,
            env=env if env is not None else self.env(),
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    def runner_calls(self) -> list[list[str]]:
        """Each call of the stub `claude`, as its working directory followed by its arguments."""
        return [
            path.read_bytes().decode().split("\0")[:-1] for path in sorted(self.calls.iterdir())
        ]

    def git_calls(self) -> list[str]:
        """For each git call the script made, whether the lock was `held` or `free` at the time."""
        return self.git_log.read_text().split() if self.git_log.exists() else []

    def lock_state_during_run(self) -> str:
        """Whether the lock was `held` or `free` while the stub `claude` ran."""
        return (self.calls.parent / "lock-state").read_text().strip()


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text)
    path.chmod(0o755)


@pytest.fixture
def sandbox(tmp_path: Path) -> Sandbox:
    """A committed fixture repo with a skill, a link, a dangling link and a scaffold script."""
    repo = git_repo(tmp_path / "repo", FIXTURE_FILES, FIXTURE_LINKS)
    (repo / "evals/demo/case-a/scaffold.sh").chmod(0o755)
    (repo / "evals/demo/case-a/notes.txt").chmod(0o640)
    # Without flock(1) the stubs would report the lock as held whatever the script did.
    assert shutil.which("flock") is not None, "the lock tests need flock(1) from util-linux"
    stub_bin = tmp_path / "bin"
    stub_bin.mkdir()
    _write_executable(stub_bin / "claude", STUB_CLAUDE)
    _write_executable(stub_bin / "git", GIT_WRAPPER)
    calls = tmp_path / "calls"
    calls.mkdir()
    return Sandbox(
        repo=repo, cache=tmp_path / "cache", bin=stub_bin, calls=calls, git_log=tmp_path / "git.log"
    )


# --- The task --------------------------------------------------------------------------------


# @spec SETUP-EVAL-001
def test_task_runs_the_script_with_uv_and_no_dependencies() -> None:
    """`mise run eval` runs the script in the locked project environment, and nothing else first."""
    task = tomllib.loads(MISE_TOML.read_text())["tasks"]["eval"]
    assert task["run"] == "uv run --locked scripts/run_evals.py"
    assert not {"depends", "depends_post", "wait_for"} & set(task)


# @spec SETUP-EVAL-001
def test_task_passes_arguments_but_not_the_separator(tmp_path: Path) -> None:
    """`mise run eval -- <args>` hands the runner exactly `<args>`, without mise's `--`."""
    stub_bin = tmp_path / "bin"
    stub_bin.mkdir()
    _write_executable(stub_bin / "claude", STUB_CLAUDE)
    calls = tmp_path / "calls"
    calls.mkdir()
    empty_config = tmp_path / "empty-mise.toml"
    empty_config.write_text("")
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("STUB_", "MISE_", "GIT_", "XDG_CACHE_HOME"))
    }
    env |= {
        "PATH": f"{stub_bin}{os.pathsep}{env.get('PATH', '')}",
        "XDG_CACHE_HOME": str(tmp_path / "cache"),
        "MISE_GLOBAL_CONFIG_FILE": str(empty_config),
        "MISE_SYSTEM_CONFIG_FILE": str(empty_config),
        "STUB_CALLS": str(calls),
    }
    completed = subprocess.run(
        ["mise", "run", "eval", "--", "--eval-dir", "evals/x", "--case", "a b"],  # noqa: S607
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    assert completed.returncode == 0, completed.stderr
    [record] = [path.read_bytes().decode().split("\0")[:-1] for path in calls.iterdir()]
    copy = tmp_path / "cache" / "agentic-development" / "eval-plugin"
    args = ["--eval-dir", "evals/x", "--case", "a b"]
    assert record == [str(copy.resolve()), "plugin", "eval", ".", *args]


# --- The lock --------------------------------------------------------------------------------


# @spec SETUP-EVAL-002
def test_lock_is_held_from_listing_through_the_run(sandbox: Sandbox) -> None:
    """The lock beside the copy is held from before the first git call and while the runner runs."""
    assert sandbox.run().returncode == 0
    assert sandbox.git_calls()
    assert set(sandbox.git_calls()) == {"held"}
    assert sandbox.lock_state_during_run() == "held"
    assert sandbox.lock.parent == sandbox.copy.parent


# @spec SETUP-EVAL-009
def test_second_run_is_refused_while_the_first_holds_the_lock(sandbox: Sandbox) -> None:
    """A second run lists nothing, changes nothing and starts no runner while the first runs."""
    started = sandbox.calls.parent / "started"
    release = sandbox.calls.parent / "release"
    first = subprocess.Popen(  # noqa: S603
        [sys.executable, str(SCRIPT)],
        cwd=sandbox.repo,
        env=sandbox.env(STUB_STARTED=str(started), STUB_RELEASE=str(release)),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(400):
            if started.exists():
                break
            time.sleep(0.05)
        assert started.exists(), "the first run never started its runner"
        git_calls_before = len(sandbox.git_calls())
        marker = sandbox.copy / "marker"
        marker.write_text("first run's copy\n")
        second = sandbox.run()
        assert second.returncode != 0
        assert second.stderr.strip()
        assert len(sandbox.git_calls()) == git_calls_before
        assert marker.read_text() == "first run's copy\n"
        assert len(sandbox.runner_calls()) == 1
    finally:
        release.write_text("")
        first.wait(timeout=30)


# --- Copying the plugin's files ----------------------------------------------------------------


# @spec SETUP-EVAL-003
def test_copy_holds_tracked_and_untracked_files_but_not_ignored_ones(sandbox: Sandbox) -> None:
    """The copy is the plugin as it would be committed: working-tree edits in, ignored files out."""
    (sandbox.repo / "README.md").write_text("edited, not committed\n")
    (sandbox.repo / "new-file.md").write_text("untracked\n")
    (sandbox.repo / "tmp").mkdir()
    (sandbox.repo / "tmp/scratch.txt").write_text("ignored\n")
    assert sandbox.run().returncode == 0
    assert (sandbox.copy / "README.md").read_text() == "edited, not committed\n"
    assert (sandbox.copy / "new-file.md").read_text() == "untracked\n"
    assert (sandbox.copy / "skills/demo/SKILL.md").is_file()
    assert not (sandbox.copy / "tmp").exists()
    assert not (sandbox.copy / ".git").exists()


# @spec SETUP-EVAL-003
def test_copy_works_from_a_subdirectory(sandbox: Sandbox) -> None:
    """Started below the repo's root, the script still copies the whole repo's plugin files."""
    assert sandbox.run(cwd=sandbox.repo / "skills").returncode == 0
    assert (sandbox.copy / "README.md").is_file()


# @spec SETUP-EVAL-003
def test_copy_skips_files_deleted_from_the_working_tree(sandbox: Sandbox) -> None:
    """A tracked file the working tree has deleted is left out, without an error."""
    (sandbox.repo / "README.md").unlink()
    completed = sandbox.run()
    assert completed.returncode == 0, completed.stderr
    assert not (sandbox.copy / "README.md").exists()


# @spec SETUP-EVAL-003
def test_copy_is_rebuilt_from_empty(sandbox: Sandbox) -> None:
    """Nothing from an earlier run survives in the copy."""
    sandbox.copy.mkdir(parents=True)
    (sandbox.copy / "stale.txt").write_text("from an earlier run\n")
    assert sandbox.run().returncode == 0
    assert not (sandbox.copy / "stale.txt").exists()


# @spec SETUP-EVAL-014
def test_read_only_leftovers_are_cleared(sandbox: Sandbox) -> None:
    """Files and directories a previous run left without write permission don't block the next."""
    if os.geteuid() == 0:
        pytest.skip("root ignores directory permissions")
    locked = sandbox.copy / "left-by-sandbox"
    locked.mkdir(parents=True)
    (locked / "file.txt").write_text("read-only\n")
    (locked / "file.txt").chmod(0o444)
    locked.chmod(0o555)
    try:
        completed = sandbox.run()
    finally:
        if locked.exists():
            locked.chmod(0o755)
    assert completed.returncode == 0, completed.stderr
    assert not locked.exists()
    assert (sandbox.copy / "README.md").is_file()


# @spec SETUP-EVAL-014
def test_copy_that_cant_be_created_is_reported(sandbox: Sandbox) -> None:
    """A cache path that can't hold the copy ends the run with the cause, before the runner."""
    sandbox.cache.mkdir()
    (sandbox.cache / "agentic-development").write_text("a file where the directory should be\n")
    completed = sandbox.run()
    assert completed.returncode != 0
    assert "agentic-development" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert sandbox.runner_calls() == []


# @spec SETUP-EVAL-003
@pytest.mark.parametrize(
    ("path", "mode"),
    [("evals/demo/case-a/scaffold.sh", 0o755), ("evals/demo/case-a/notes.txt", 0o640)],
)
def test_copy_keeps_permission_bits(sandbox: Sandbox, path: str, mode: int) -> None:
    """Each file keeps its permission bits, so a scaffold script stays executable."""
    assert sandbox.run().returncode == 0
    assert stat.S_IMODE((sandbox.copy / path).stat().st_mode) == mode


# @spec SETUP-EVAL-003
@pytest.mark.parametrize("value", [None, "", "relative-cache"])
def test_copy_location_falls_back_to_home_cache(
    sandbox: Sandbox, tmp_path: Path, value: str | None
) -> None:
    """With XDG_CACHE_HOME unset, empty or relative, the copy goes under ~/.cache, not the repo."""
    home = tmp_path / "home"
    home.mkdir()
    env = sandbox.env(HOME=str(home))
    if value is None:
        del env["XDG_CACHE_HOME"]
    else:
        env["XDG_CACHE_HOME"] = value
    assert sandbox.run(env=env).returncode == 0
    assert (home / ".cache/agentic-development/eval-plugin/README.md").is_file()
    assert not (sandbox.repo / "relative-cache").exists()


# @spec SETUP-EVAL-003, SETUP-EVAL-004
def test_links_are_copied_as_links_with_the_same_target(sandbox: Sandbox) -> None:
    """A skill link keeps its relative target, and a dangling link is still copied."""
    assert sandbox.run().returncode == 0
    for name, target in FIXTURE_LINKS.items():
        copied = sandbox.copy / name
        assert copied.is_symlink(), name
        assert str(copied.readlink()) == target
    assert (sandbox.copy / ".claude/skills/demo/SKILL.md").is_file()


# --- Running the runner ------------------------------------------------------------------------


# @spec SETUP-EVAL-005
def test_runner_starts_in_the_copy_with_the_arguments_in_order(sandbox: Sandbox) -> None:
    """The runner sees the copy as the plugin, and the script's arguments unchanged after `.`."""
    args = ["--case", "x y", "--prompt", "line one\nline two", "--runs", "1"]
    assert sandbox.run(*args).returncode == 0
    assert sandbox.runner_calls() == [[str(sandbox.copy.resolve()), "plugin", "eval", ".", *args]]


# --- Copying results back ----------------------------------------------------------------------


# @spec SETUP-EVAL-006
def test_new_results_are_copied_back(sandbox: Sandbox) -> None:
    """New runs below any `results` directory under `evals/` come back; others don't."""
    (sandbox.repo / "evals/demo/results/older").mkdir(parents=True)
    results = "evals/demo/results/run-1 evals/results/run-2 evals/demo/case-a/results/run-3"
    completed = sandbox.run(env=sandbox.env(STUB_RESULTS=f"{results} results/outside"))
    assert completed.returncode == 0, completed.stderr
    for run in results.split():
        assert (sandbox.repo / run / "report.html").read_text() == "report\n"
    assert not (sandbox.repo / "results").exists()


# @spec SETUP-EVAL-006
def test_results_already_in_the_repo_are_left_alone(sandbox: Sandbox) -> None:
    """A results directory that already exists in the repo isn't overwritten or merged into."""
    existing = sandbox.repo / "evals/demo/results/run-1"
    existing.mkdir(parents=True)
    (existing / "keep.txt").write_text("mine\n")
    completed = sandbox.run(env=sandbox.env(STUB_RESULTS="evals/demo/results/run-1"))
    assert completed.returncode == 0, completed.stderr
    assert sorted(p.name for p in existing.iterdir()) == ["keep.txt"]


# @spec SETUP-EVAL-006
def test_results_copied_in_before_the_run_are_not_copied_back(sandbox: Sandbox) -> None:
    """Only what the run created comes back, not results that were part of the plugin's files."""
    # An uncommitted .gitignore without the results rule makes `old` one of the plugin's files,
    # so it is copied in; the stub then deletes the repo's copy, which only a snapshot can tell.
    (sandbox.repo / ".gitignore").write_text("tmp/\n")
    old = sandbox.repo / "evals/demo/results/old"
    old.mkdir(parents=True)
    (old / "report.html").write_text("old\n")
    completed = sandbox.run(env=sandbox.env(STUB_DELETE=str(old)))
    assert completed.returncode == 0, completed.stderr
    assert not old.exists()


# @spec SETUP-EVAL-007, SETUP-EVAL-008
def test_failed_copy_backs_are_each_reported_and_dont_stop_the_others(sandbox: Sandbox) -> None:
    """Every results directory is tried, every failure is named, and the runner's status wins."""
    if os.geteuid() == 0:
        pytest.skip("root ignores directory permissions")
    blocked = [sandbox.repo / "evals/demo/results", sandbox.repo / "evals/other/results"]
    for directory in blocked:
        directory.mkdir(parents=True)
        directory.chmod(0o500)
    results = "evals/demo/results/run-1 evals/other/results/run-1 evals/results/run-2"
    try:
        completed = sandbox.run(env=sandbox.env(STUB_RESULTS=results, STUB_EXIT="0"))
    finally:
        for directory in blocked:
            directory.chmod(0o700)
    assert completed.returncode == 0
    assert "evals/demo/results/run-1" in completed.stderr
    assert "evals/other/results/run-1" in completed.stderr
    assert (sandbox.repo / "evals/results/run-2/report.html").is_file()


# --- Exit status -------------------------------------------------------------------------------


# @spec SETUP-EVAL-008
@pytest.mark.parametrize("status", [0, 1, 3])
def test_exit_status_is_the_runners(sandbox: Sandbox, status: int) -> None:
    """The script's status is the runner's, so callers and CI see the eval's own result."""
    assert sandbox.run(env=sandbox.env(STUB_EXIT=str(status))).returncode == status


# @spec SETUP-EVAL-006, SETUP-EVAL-008
def test_runner_ended_by_a_signal_gives_128_plus_the_signal(sandbox: Sandbox) -> None:
    """A runner killed by SIGTERM gives 143, and its results still come back."""
    completed = sandbox.run(env=sandbox.env(STUB_SIGNAL="TERM", STUB_RESULTS="evals/results/r"))
    assert completed.returncode == 128 + signal.SIGTERM
    assert (sandbox.repo / "evals/results/r/report.html").is_file()


# @spec SETUP-EVAL-013
def test_interrupt_still_copies_results_back(sandbox: Sandbox) -> None:
    """A Ctrl-C to the whole process group ends the runner, and the script still copies back."""
    started = sandbox.calls.parent / "started"
    process = subprocess.Popen(  # noqa: S603
        [sys.executable, str(SCRIPT)],
        cwd=sandbox.repo,
        env=sandbox.env(
            STUB_STARTED=str(started),
            STUB_RELEASE=str(sandbox.calls.parent / "never"),
            STUB_RESULTS="evals/results/interrupted",
        ),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    for _ in range(400):
        if started.exists():
            break
        time.sleep(0.05)
    assert started.exists(), "the runner never started"
    os.killpg(process.pid, signal.SIGINT)
    _, stderr = process.communicate(timeout=30)
    assert process.returncode == 130, stderr
    assert (sandbox.repo / "evals/results/interrupted/report.html").is_file()


# @spec SETUP-EVAL-012
def test_missing_runner_gives_127(sandbox: Sandbox, tmp_path: Path) -> None:
    """With no `claude` on PATH the script says why and exits 127."""
    git_only = tmp_path / "git-only"
    git_only.mkdir()
    real_git = shutil.which("git")
    assert real_git is not None
    (git_only / "git").symlink_to(real_git)
    env = sandbox.env()
    env["PATH"] = str(git_only)
    completed = sandbox.run(env=env)
    assert completed.returncode == 127
    assert "claude" in completed.stderr


# @spec SETUP-EVAL-012
def test_runner_that_cant_execute_gives_127(sandbox: Sandbox) -> None:
    """A `claude` on PATH that the system can't execute is reported, with status 127."""
    (sandbox.bin / "claude").write_bytes(b"\x00\x01 not a program\n")
    completed = sandbox.run()
    assert completed.returncode == 127
    assert "couldn't start the runner" in completed.stderr
    assert "Traceback" not in completed.stderr


# --- Refusals ----------------------------------------------------------------------------------


# @spec SETUP-EVAL-010
def test_listing_failure_leaves_the_copy_and_starts_no_runner(
    sandbox: Sandbox, tmp_path: Path
) -> None:
    """Outside a git work tree the script reports git's error and touches nothing."""
    sandbox.copy.mkdir(parents=True)
    (sandbox.copy / "earlier.txt").write_text("earlier run\n")
    not_a_repo = tmp_path / "not-a-repo"
    not_a_repo.mkdir()
    completed = sandbox.run(cwd=not_a_repo)
    assert completed.returncode != 0
    assert "not a git repository" in completed.stderr.lower()
    assert (sandbox.copy / "earlier.txt").exists()
    assert sandbox.runner_calls() == []


# @spec SETUP-EVAL-011
def test_unreadable_file_stops_the_run(sandbox: Sandbox) -> None:
    """A file that can't be copied is named, and the runner never starts on a partial plugin."""
    if os.geteuid() == 0:
        pytest.skip("root reads files whatever their permissions")
    unreadable = sandbox.repo / "README.md"
    unreadable.chmod(0)
    try:
        completed = sandbox.run()
    finally:
        unreadable.chmod(0o644)
    assert completed.returncode != 0
    assert "README.md" in completed.stderr
    assert sandbox.runner_calls() == []
