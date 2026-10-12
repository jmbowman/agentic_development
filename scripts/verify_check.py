"""Fail unless the repo's `check` task and its dependencies come from template fragments.

The shared check workflow fetches this script at its own commit and runs it with the runner
image's Python, so it uses only the standard library.
Design: docs/intent/check-workflow/check-workflow-design.md
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import deque
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    Lookup = Callable[[str], dict[str, Any]]

CONF_D = ".config/mise/conf.d/"
# Glob syntax mise accepts in a task name; it reports only the first task a pattern matches.
PATTERN_CHARACTERS = frozenset("*?[{")


class TaskLookupError(Exception):
    """mise couldn't report a task; the message is mise's error output."""


class UnreadableTaskError(Exception):
    """mise reported a task, but not in a form this script can read."""


def mise_lookup(task: str) -> dict[str, Any]:
    """Return what `mise tasks info <task> --json` reports.

    Args:
        task: The task name.

    Returns:
        The task's parsed info.

    Raises:
        TaskLookupError: mise exited with an error.
        UnreadableTaskError: mise printed something other than a JSON object.
    """
    completed = subprocess.run(  # noqa: S603
        ["mise", "tasks", "info", task, "--json"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise TaskLookupError(completed.stderr.strip())
    try:
        info = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise UnreadableTaskError(str(error)) from error
    if not isinstance(info, dict):
        msg = "it isn't a JSON object"
        raise UnreadableTaskError(msg)
    return info


def allowed_prefixes(cwd: Path, pwd: str | None) -> tuple[str, ...]:
    """Return the path prefixes a task's source may start with.

    mise may report a source by its logical or its symlink-resolved path, so both forms of
    `.config/mise/conf.d/` are accepted. `$PWD` gives the logical form, but only when it names
    the current directory.

    Args:
        cwd: The current directory, symlinks resolved.
        pwd: The value of `$PWD`, if set.

    Returns:
        The logical prefix (when known and different) followed by the physical one.
    """
    physical = f"{cwd}/{CONF_D}"
    if (
        pwd is not None
        and pwd not in {"", str(cwd)}
        and Path(pwd).is_dir()
        and Path(pwd).samefile(cwd)
    ):
        return (f"{pwd}/{CONF_D}", physical)
    return (physical,)


def root_name(name: object) -> object:
    """Remove mise's monorepo root prefix (`//:` or `:`) from a task name.

    In monorepo mode mise reports root tasks as `//:check`, and `check`, `:check` and
    `//:check` all resolve to the same task.

    Args:
        name: A task name, or any JSON value mise reported in its place.

    Returns:
        The name without the prefix; anything else unchanged.
    """
    if isinstance(name, str):
        return name.removeprefix("//:").removeprefix(":")
    return name


def nonempty_string(value: object) -> str | None:
    """Return the value if it is a non-blank string, else None.

    Args:
        value: Any JSON value.

    Returns:
        The string, or None.
    """
    return value if isinstance(value, str) and value.strip() else None


def dependency_names(entry: object) -> list[str] | None:
    """Return the task a `depends` entry names, or None for a form mise doesn't emit.

    Args:
        entry: A name, `"name args"`, `[name, args...]` or `{"task": name, "args": [...]}`.

    Returns:
        A one-item list with the task name.
    """
    if isinstance(entry, list) and entry:
        entry = entry[0]
    elif isinstance(entry, dict):
        entry = entry.get("task")
    name = nonempty_string(entry)
    return [name.split()[0]] if name is not None else None


def run_task_names(entry: object) -> list[str] | None:
    """Return the tasks a `run` entry starts, or None for a form mise doesn't emit.

    Args:
        entry: A script string, `{"task": "name args"}` or `{"tasks": ["name args", ...]}`.

    Returns:
        The task names (each string's first word), empty for a script.
    """
    if isinstance(entry, str):
        return []
    if not isinstance(entry, dict):
        return None
    if "task" in entry:
        name = nonempty_string(entry["task"])
        return [name.split()[0]] if name is not None else None
    tasks = entry.get("tasks")
    if not isinstance(tasks, list):
        return None
    names = [nonempty_string(task) for task in tasks]
    return None if None in names else [name.split()[0] for name in names if name is not None]


READERS = {"depends": dependency_names, "depends_post": dependency_names, "run": run_task_names}


def inspect_task(
    task: str, info: dict[str, Any], prefixes: tuple[str, ...]
) -> tuple[list[str], list[str]]:
    """Check one task's source and read the tasks it depends on or runs.

    Args:
        task: The task name.
        info: The task's info from mise.
        prefixes: Path prefixes an allowed source starts with.

    Returns:
        The task's violations, and the names of the tasks it reaches.
    """
    found: list[str] = []
    source = info.get("source")
    if not isinstance(source, str):
        found.append(
            f'error: mise\'s report for task "{task}" is unreadable: it has no source path.'
        )
    # mise reports `includes` paths unnormalized, so `conf.d/../../x.toml` would match the prefix.
    elif not source.startswith(prefixes) or ".." in PurePosixPath(source).parts:
        found.append(f'error: task "{task}" is defined in {source}, outside {CONF_D}.')
    names: list[str] = []
    for field, read in READERS.items():
        entries = info.get(field, [])
        if not isinstance(entries, list):
            found.append(
                f'error: task "{task}" has an unrecognized {field} value: {json.dumps(entries)}'
            )
            continue
        for entry in entries:
            reached = read(entry)
            if reached is None:
                found.append(
                    f'error: task "{task}" has an unrecognized {field} entry: {json.dumps(entry)}'
                )
            else:
                names.extend(reached)
    return found, names


# @spec CHECK-RUN-002, CHECK-RUN-003, CHECK-RUN-004, CHECK-RUN-007, CHECK-RUN-008
# @spec CHECK-RUN-009, CHECK-RUN-010, CHECK-RUN-011, CHECK-RUN-012
def find_violations(lookup: Lookup, prefixes: tuple[str, ...]) -> list[str]:
    """Walk `check`'s closure and return a message for every violation.

    Args:
        lookup: Returns a task's info, raising TaskLookupError or UnreadableTaskError if it can't.
        prefixes: Path prefixes an allowed source starts with.

    Returns:
        One error message per violation, in the order found.
    """
    found: list[str] = []
    queue: deque[str] = deque(["check"])
    seen: set[str] = set()
    while queue:
        task = queue.popleft()
        # Repos extend checks through `-extra` tasks; those and their dependencies aren't checked.
        if task in seen or task.endswith("-extra"):
            continue
        seen.add(task)
        if PATTERN_CHARACTERS & set(task):
            found.append(f'error: dependency "{task}" uses a pattern; list the tasks by name.')
            continue
        try:
            info = lookup(task)
        except TaskLookupError as error:
            if task == "check":
                return [f'error: no "check" task is defined in this repo: {error}']
            found.append(f'error: dependency "{task}" was not found: {error}')
            continue
        except UnreadableTaskError as error:
            found.append(f'error: mise\'s report for task "{task}" is unreadable: {error}')
            continue
        name = info.get("name")
        aliases = [root_name(alias) for alias in info.get("aliases") or []]
        if root_name(name) != root_name(task) and root_name(task) not in aliases:
            found.append(
                f'error: dependency "{task}" resolved to task "{name}"; list tasks by name.'
            )
            continue
        violations, names = inspect_task(task, info, prefixes)
        found.extend(violations)
        queue.extend(names)
    return found


def main() -> int:
    """Verify the current directory's repo and report every violation on stderr.

    Returns:
        The exit status: 0 if `check` and its dependencies all come from template fragments.
    """
    prefixes = allowed_prefixes(Path.cwd(), os.environ.get("PWD"))
    try:
        found = find_violations(mise_lookup, prefixes)
    except OSError as error:
        found = [f"error: couldn't run mise: {error}"]
    for message in found:
        sys.stderr.write(f"{message}\n")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
