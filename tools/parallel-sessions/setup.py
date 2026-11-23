#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Show, then apply, the machine setup for Orca: the launcher, its menu entry, and Clash's hook.

Run it as `uv run --script setup.py` to see each change as a diff, and with `--apply` to make
them. Each changed file is backed up first, and a file another program changed while setup ran is
left alone.
"""

from __future__ import annotations

import argparse
import contextlib
import difflib
import json
import os
import shutil
import stat
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from parallel_sessions_common import (
    DIFFERS,
    FAILED,
    OK,
    Config,
    Platform,
    StopError,
    complain,
    current_platform,
    load_config,
    prepare_output,
    say,
    xdg_dir,
)

LAUNCHER_SOURCE = Path(__file__).resolve().parent / "orca-launch"
INSTALL_DIR_LINE = "install_dir="
PREREQUISITES = ("git", "uv", "claude")
CLASH_COMMAND = "clash check"
CLASH_MATCHER = "Write|Edit|MultiEdit"
CLASH_TOOLS = {"Write", "Edit", "MultiEdit"}
# The Clash release these scripts were written against, pinned per machine in mise's global config.
CLASH_INSTALL = "mise use -g github:clash-sh/clash@0.2.0"
EXECUTABLE = 0o755
READABLE = 0o644
PRIVATE_FILE = 0o600
PRIVATE_DIR = 0o700
# Characters that make a desktop entry's Exec argument need quoting (Desktop Entry spec, Exec key).
DESKTOP_RESERVED = frozenset(" \t\n\"'\\><~|&;$*?#()`")


class ChangedUnderneathError(Exception):
    """Another program changed a target between setup reading it and writing it."""


@dataclass
class Change:
    """One target's change: what setup read, and what it would write."""

    target: Path
    old: bytes | None
    new: bytes
    old_mode: int | None
    new_mode: int
    through_link: bool = False

    @property
    def linked_to(self) -> Path | None:
        """The file the target links to, when it's a symbolic link."""
        return Path(os.path.realpath(self.target)) if self.target.is_symlink() else None

    # @spec PAR-SETUP-006, PAR-SETUP-017
    @property
    def real(self) -> Path:
        """The path written: through a link for the settings file, else the target itself."""
        linked = self.linked_to
        return linked if self.through_link and linked is not None else self.target

    @property
    def replaces_link(self) -> bool:
        """Whether writing the target replaces a symbolic link with a regular file."""
        return not self.through_link and self.linked_to is not None

    # @spec PAR-SETUP-009
    def needed(self) -> bool:
        """Whether the content or the permissions differ, or a link is to be replaced."""
        return self.old != self.new or self.old_mode != self.new_mode or self.replaces_link


@dataclass
class Outcome:
    """What setup couldn't do: incomplete items (exit 1) and failures (exit 2)."""

    incomplete: list[str]
    failures: list[str]

    def status(self) -> int:
        """The exit status: 2 over 1 over 0 (PAR-ALL-001)."""
        if self.failures:
            return FAILED
        return DIFFERS if self.incomplete else OK


def read_target(target: Path) -> tuple[bytes | None, int | None]:
    """A target's content and permission bits, or None for each when it doesn't exist."""
    try:
        return target.read_bytes(), stat.S_IMODE(target.stat().st_mode)
    except FileNotFoundError:
        return None, None


def shell_quote(text: str) -> str:
    """Quote text for POSIX `sh` in single quotes."""
    return "'" + text.replace("'", "'\\''") + "'"


# @spec PAR-SETUP-010
def launcher_change(row: Platform, config: Config) -> Change:
    """The installed launcher: the repo's, with the install directory written in."""
    lines = LAUNCHER_SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)
    written = [
        f"{INSTALL_DIR_LINE}{shell_quote(str(config.install_dir))}\n"
        if line.startswith(INSTALL_DIR_LINE)
        else line
        for line in lines
    ]
    target = Path.home() / row.launcher
    old, mode = read_target(target)
    return Change(target, old, "".join(written).encode(), mode, EXECUTABLE)


def desktop_string(text: str) -> str:
    """Escape a desktop entry's string value as the Desktop Entry spec's string type asks."""
    escaped = text.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t")
    return "\\s" + escaped[1:] if escaped.startswith(" ") else escaped


def desktop_exec(path: Path) -> str:
    """A path as a desktop entry's `Exec` holds it: quoted when needed, `%` doubled.

    The quoting rule applies to the value after the string escapes are undone, so a backslash
    escaped for the quoting is escaped again for the string.
    """
    text = str(path).replace("%", "%%")
    if any(char in DESKTOP_RESERVED for char in text):
        quoted = (
            text.replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$")
        )
        text = f'"{quoted}"'
    return desktop_string(text)


# @spec PAR-SETUP-011, PAR-SETUP-013
def desktop_change(row: Platform, config: Config) -> Change:
    """The desktop entry, starting Orca through the installed launcher."""
    lines = [
        "[Desktop Entry]",
        "Type=Application",
        "Name=Orca",
        f"Exec={desktop_exec(Path.home() / row.launcher)}",
        "Categories=Development;",
        "StartupWMClass=orca",
    ]
    icon = config.install_dir / "icon.png"
    if icon.is_file():
        lines.append(f"Icon={desktop_string(str(icon))}")
    target = Path.home() / row.desktop_entry
    old, mode = read_target(target)
    return Change(target, old, ("\n".join(lines) + "\n").encode(), mode, READABLE)


def is_equivalent(group: object) -> bool:
    """Whether a `PreToolUse` group already runs `clash check` on the edit tools."""
    if not isinstance(group, dict):
        return False
    matcher = group.get("matcher") or ""
    if not isinstance(matcher, str):
        return False
    covers = matcher in {"", "*", ".*"} or set(matcher.split("|")) >= CLASH_TOOLS
    hooks = group.get("hooks")
    runs = isinstance(hooks, list) and any(
        isinstance(hook, dict)
        and isinstance(hook.get("command"), str)
        and hook["command"].strip() == CLASH_COMMAND
        for hook in hooks
    )
    return covers and runs


def clash_plugin_enabled(settings: dict[str, object]) -> bool:
    """Whether Clash's own Claude Code plugin is enabled."""
    plugins = settings.get("enabledPlugins")
    return isinstance(plugins, dict) and any(
        str(name).split("@")[0] == "clash" and value is True for name, value in plugins.items()
    )


# @spec PAR-CLASH-001, PAR-CLASH-002, PAR-CLASH-003, PAR-CLASH-004, PAR-CLASH-005
# @spec PAR-SETUP-008, PAR-SETUP-015
def settings_change(outcome: Outcome) -> Change | None:
    """The Claude settings file with Clash's entry appended, when one is to be added."""
    target = Path.home() / ".claude" / "settings.json"
    old, mode = read_target(target)
    try:
        settings = json.loads(old) if old is not None else {}
    except (UnicodeDecodeError, ValueError) as error:
        outcome.failures.append(f"couldn't read {target} as JSON ({error}); left it alone")
        return None
    if not isinstance(settings, dict):
        outcome.failures.append(f"{target} isn't a JSON object; left it alone")
        return None
    hooks = settings.get("hooks")
    groups = hooks.get("PreToolUse") if isinstance(hooks, dict) else None
    equivalent = isinstance(groups, list) and any(is_equivalent(group) for group in groups)
    on_path = shutil.which("clash") is not None
    if not on_path:
        if equivalent:
            outcome.incomplete.append(
                f"stale Clash entry: {target} runs `clash check`, but clash isn't on PATH "
                f"(left in place; install it with `{CLASH_INSTALL}`)"
            )
        elif clash_plugin_enabled(settings):
            outcome.incomplete.append(
                f"Clash's plugin is enabled in {target}, but clash isn't on PATH, so the plugin's "
                f"hook can't run; install it with `{CLASH_INSTALL}`"
            )
        else:
            outcome.incomplete.append(
                f"skipped Clash's entry: clash isn't on PATH; install it with `{CLASH_INSTALL}` "
                "and run setup again"
            )
        return None
    if equivalent or clash_plugin_enabled(settings):
        return None
    if hooks is None:
        hooks = settings["hooks"] = {}
    if not isinstance(hooks, dict) or not isinstance(hooks.setdefault("PreToolUse", []), list):
        outcome.failures.append(
            f"{target}'s hooks aren't shaped as Claude Code expects; left it alone"
        )
        return None
    hooks["PreToolUse"].append(
        {"matcher": CLASH_MATCHER, "hooks": [{"type": "command", "command": CLASH_COMMAND}]}
    )
    new = (json.dumps(settings, indent=2, ensure_ascii=False) + "\n").encode()
    new_mode = mode if mode is not None else PRIVATE_FILE
    return Change(target, old, new, mode, new_mode, through_link=True)


# @spec PAR-SETUP-001
def show(change: Change) -> None:
    """Print a change: a unified diff for content, and a line for permissions."""
    if change.old != change.new:
        old = (
            change.old.decode(errors="replace").splitlines(keepends=True)
            if change.old is not None
            else []
        )
        new = change.new.decode().splitlines(keepends=True)
        # Name the file a link points to, and whether setup writes through the link.
        shown = str(change.target)
        if change.replaces_link:
            shown = f"{change.target} (now a link to {change.linked_to}, to be replaced)"
        elif change.linked_to is not None:
            shown = f"{change.target} -> {change.linked_to}"
        before = shown if change.old is not None else f"{shown} (new file)"
        diff = difflib.unified_diff(old, new, fromfile=before, tofile=shown)
        for line in diff:
            sys.stdout.write(line if line.endswith("\n") else line + "\n")
    if change.old_mode is not None and change.old_mode != change.new_mode:
        say(f"{change.target}: permissions {change.old_mode:o} -> {change.new_mode:o}")
    if change.replaces_link and change.old == change.new:
        say(f"{change.target}: replaces the link to {change.linked_to} with a regular file")


# @spec PAR-SETUP-005, PAR-SETUP-016
def back_up(change: Change, backups: Path, stamp: str) -> None:
    """Copy a target's earlier content into the backup directory, private and not executable."""
    backups.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR)
    backups.chmod(PRIVATE_DIR)
    copy = backups / f"{change.target.name}.{stamp}"
    descriptor = os.open(copy, os.O_WRONLY | os.O_CREAT | os.O_EXCL, PRIVATE_FILE)
    with os.fdopen(descriptor, "wb") as stream:
        os.fchmod(stream.fileno(), PRIVATE_FILE)
        stream.write(change.old or b"")


# @spec PAR-SETUP-003, PAR-SETUP-004, PAR-SETUP-006, PAR-SETUP-017
def write(change: Change, backups: Path, stamp: str) -> None:
    """Write one target through a temporary file beside the file written, renamed into place.

    Raises:
        ChangedUnderneathError: When the file changed since setup read it.
    """
    real = change.real
    if read_target(real)[0] != change.old:
        raise ChangedUnderneathError
    if change.old is not None:
        back_up(change, backups, stamp)
    real.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(dir=real.parent, prefix=f".{real.name}.", suffix=".tmp")
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(change.new)
            os.fchmod(stream.fileno(), change.new_mode)
        unchanged = read_target(real)[0] == change.old
    except BaseException:
        _remove(temporary)
        raise
    if not unchanged:
        _remove(temporary)
        raise ChangedUnderneathError
    try:
        temporary.replace(real)
    except BaseException:
        _remove(temporary)
        raise


def _remove(path: Path) -> None:
    with contextlib.suppress(FileNotFoundError):
        path.unlink()


# @spec PAR-SETUP-002, PAR-SETUP-007, PAR-SETUP-025
def apply(changes: list[Change], outcome: Outcome) -> None:
    """Make each change, carrying on past a failed one."""
    backups = xdg_dir("XDG_STATE_HOME", ".local/state") / "parallel-sessions" / "backups"
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    for change in changes:
        try:
            write(change, backups, stamp)
        except ChangedUnderneathError:
            outcome.incomplete.append(
                f"{change.target} changed underneath setup while it ran; left it as it is"
            )
        except OSError as error:
            outcome.failures.append(f"couldn't write {change.target}: {error}")
        else:
            say(f"Wrote {change.target}.")


def summarize(outcome: Outcome, *, applied: bool, changed: bool) -> None:
    """Print what wasn't done, or that everything was."""
    if outcome.failures:
        say("Setup failed:")
        for line in outcome.failures:
            say(f"  * {line}")
    if outcome.incomplete:
        say("Setup is incomplete:")
        for line in outcome.incomplete:
            say(f"  * {line}")
    if not changed:
        say("Nothing to change.")
    elif not applied:
        say("Run again with --apply to make these changes.")


def check_prerequisites() -> None:
    """Stop when a tool setup needs isn't on `PATH`.

    Raises:
        StopError: Naming each missing tool.
    """
    missing = [tool for tool in PREREQUISITES if shutil.which(tool) is None]
    if missing:
        message = f"setup needs these on PATH: {', '.join(missing)}"
        raise StopError(message)


# @spec PAR-SETUP-020, PAR-SETUP-021, PAR-SETUP-022, PAR-SETUP-023, PAR-SETUP-024
def main(argv: list[str] | None = None) -> int:
    """Show or apply the setup; returns the exit status."""
    prepare_output()
    try:
        row = current_platform()
        parser = argparse.ArgumentParser(prog="setup.py", description=__doc__.splitlines()[0])
        parser.add_argument("--apply", action="store_true", help="make the changes shown")
        args = parser.parse_args(sys.argv[1:] if argv is None else argv)
        config = load_config(row)
        check_prerequisites()
        outcome = Outcome([], [])
        candidates = [launcher_change(row, config), desktop_change(row, config)]
        candidates.append(settings_change(outcome))
        changes = [change for change in candidates if change is not None and change.needed()]
        for change in changes:
            show(change)
        if args.apply:
            apply(changes, outcome)
        summarize(outcome, applied=args.apply, changed=bool(changes))
    except StopError as error:
        complain(error.message)
        return error.status
    except OSError as error:
        complain(f"setup failed: {error}")
        return FAILED
    except Exception as error:  # noqa: BLE001 - fail closed: never exit 1 or 0 on a surprise
        complain(f"setup failed unexpectedly: {type(error).__name__}: {error}")
        return FAILED
    return outcome.status()


if __name__ == "__main__":
    sys.exit(main())
