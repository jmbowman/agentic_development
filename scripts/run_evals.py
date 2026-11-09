"""Run `claude plugin eval` from a clean copy of this repo's plugin files.

The repo root is the plugin, and `claude plugin eval` counts every entry under it, gitignored
scratch included, against a 20,000-entry cap. This script copies only what git lists as the
plugin's files into a fixed cache directory, runs the runner there with the given arguments,
and copies the new results back.

Design: docs/intent/repo-setup/repo-setup-design.md (Running the evals)
"""

from __future__ import annotations

import contextlib
import fcntl
import os
import shutil
import signal
import stat
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Sequence
    from types import FrameType

RUNNER_NOT_STARTED = 127


class ListingError(Exception):
    """git couldn't list the plugin's files; the message is git's error output."""


class CopyError(Exception):
    """One of the plugin's files couldn't be copied into the eval copy."""

    def __init__(self, name: str, copy: Path, error: OSError) -> None:
        """Name the file, the eval copy and the underlying error."""
        super().__init__(f"couldn't copy {name} into {copy}: {error}")


def cache_directory() -> Path:
    """The directory that holds the eval copy and its lock, under the user's cache directory.

    As the XDG Base Directory spec says, a relative `XDG_CACHE_HOME` is ignored, so the copy can
    never land inside the repo the script was started in.
    """
    base = Path(os.environ.get("XDG_CACHE_HOME", ""))
    return (base if base.is_absolute() else Path.home() / ".cache") / "agentic-development"


def _git(*args: str, cwd: Path) -> bytes:
    completed = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=cwd,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ListingError(completed.stderr.decode(errors="replace").strip())
    return completed.stdout


def plugin_files(start: Path) -> tuple[Path, list[str]]:
    """The repo root above `start`, and the paths git lists as tracked or untracked, not ignored."""
    root = Path(os.fsdecode(_git("rev-parse", "--show-toplevel", cwd=start)).strip())
    listed = _git("ls-files", "-z", "--cached", "--others", "--exclude-standard", cwd=root)
    names = [os.fsdecode(name) for name in listed.split(b"\0") if name]
    return root, list(dict.fromkeys(names))


def _make_writable_and_retry(
    function: Callable[[str], object], path: str, _error: BaseException
) -> None:
    """For `shutil.rmtree`: make `path` and its parent writable by the owner, then retry."""
    for target in (Path(path).parent, Path(path)):
        if not target.is_symlink():
            target.chmod(target.stat().st_mode | stat.S_IWUSR | stat.S_IXUSR)
    function(path)


def clear_copy(copy: Path) -> None:
    """Delete `copy`, even where a previous run left it read-only, and create it empty."""
    if copy.is_symlink() or copy.is_file():
        copy.unlink()
    elif copy.exists():
        shutil.rmtree(copy, onexc=_make_writable_and_retry)
    copy.mkdir(parents=True)


def copy_plugin(root: Path, names: Sequence[str], copy: Path) -> None:
    """Copy into the empty `copy` each listed file that exists, keeping links and modes."""
    for name in names:
        source = root / name
        if not source.is_symlink() and not source.exists():
            continue
        target = copy / name
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_symlink():
                target.symlink_to(source.readlink())
            elif source.is_dir():
                target.mkdir(exist_ok=True)
            else:
                shutil.copy2(source, target)
        except OSError as error:
            raise CopyError(name, copy, error) from error


def results_entries(copy: Path, failures: list[str] | None = None) -> set[Path]:
    """Each entry of a `results` directory below the copy's `evals/`, relative to the copy.

    A results directory that can't be read is added to `failures`, when given, and skipped.
    """
    evals = copy / "evals"
    found: set[Path] = set()
    if not evals.is_dir():
        return found
    for directory, subdirectories, _ in os.walk(evals):
        path = Path(directory)
        if path.name == "results":
            try:
                found.update(entry.relative_to(copy) for entry in path.iterdir())
            except OSError as error:
                if failures is not None:
                    failures.append(f"couldn't read {path.relative_to(copy)}: {error}")
            subdirectories.clear()
    return found


def copy_results_back(copy: Path, root: Path, before: set[Path]) -> list[str]:
    """Copy each results entry the run created, and that the repo lacks, back into the repo."""
    failures: list[str] = []
    for relative in sorted(results_entries(copy, failures) - before):
        source, destination = copy / relative, root / relative
        if destination.exists() or destination.is_symlink():
            continue
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir() and not source.is_symlink():
                shutil.copytree(source, destination, symlinks=True)
            else:
                shutil.copy2(source, destination, follow_symlinks=False)
        except OSError as error:
            failures.append(f"couldn't copy {relative} back to {root}: {error}")
    return failures


def _ignore_interrupt(_signum: int, _frame: FrameType | None) -> None:
    """Let Ctrl-C reach the runner without ending this script before the copy-back."""


@contextlib.contextmanager
def _interrupts_deferred() -> Generator[None]:
    """Ignore SIGINT for the block, through a handler rather than SIG_IGN.

    A handler resets to the default in a child process, so the runner still stops on Ctrl-C;
    SIG_IGN would be inherited, and the runner would ignore it too.
    """
    previous = signal.signal(signal.SIGINT, _ignore_interrupt)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, previous)


def run_runner(copy: Path, arguments: Sequence[str]) -> int:
    """Run `claude plugin eval .` in the copy; return its status, 128 + n for signal n."""
    claude = shutil.which("claude")
    if claude is None:
        sys.stderr.write("eval: couldn't start the runner: `claude` isn't on PATH\n")
        return RUNNER_NOT_STARTED
    try:
        process = subprocess.Popen([claude, "plugin", "eval", ".", *arguments], cwd=copy)  # noqa: S603
    except OSError as error:
        sys.stderr.write(f"eval: couldn't start the runner: {error}\n")
        return RUNNER_NOT_STARTED
    status = process.wait()
    return 128 - status if status < 0 else status


@contextlib.contextmanager
def _locked(lock_path: Path) -> Generator[bool]:
    """Hold an advisory lock on `lock_path` for the block; yield whether it was free."""
    with lock_path.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        yield True


def main(arguments: Sequence[str]) -> int:
    """Copy the plugin, run the evals in the copy, bring the results back, return the status."""
    # @spec SETUP-EVAL-002, SETUP-EVAL-003, SETUP-EVAL-004, SETUP-EVAL-005, SETUP-EVAL-006
    # @spec SETUP-EVAL-007, SETUP-EVAL-008, SETUP-EVAL-009, SETUP-EVAL-010, SETUP-EVAL-011
    # @spec SETUP-EVAL-012, SETUP-EVAL-013, SETUP-EVAL-014
    cache = cache_directory()
    copy = cache / "eval-plugin"
    lock_path = cache / "eval-plugin.lock"
    try:
        cache.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        sys.stderr.write(f"eval: couldn't create {cache}: {error}\n")
        return 1
    with _locked(lock_path) as acquired:
        if not acquired:
            sys.stderr.write(f"eval: another eval run holds {lock_path}; try again when it ends\n")
            return 1
        try:
            root, names = plugin_files(Path.cwd())
        except ListingError as error:
            sys.stderr.write(f"eval: couldn't list the plugin's files: {error}\n")
            return 1
        try:
            clear_copy(copy)
        except OSError as error:
            sys.stderr.write(f"eval: couldn't clear {copy} for a new copy: {error}\n")
            return 1
        try:
            copy_plugin(root, names, copy)
        except CopyError as error:
            sys.stderr.write(f"eval: {error}\n")
            return 1
        before = results_entries(copy)
        with _interrupts_deferred():
            status = run_runner(copy, arguments)
            for failure in copy_results_back(copy, root, before):
                sys.stderr.write(f"eval: {failure}\n")
        return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
