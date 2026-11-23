#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Report where Orca's installed files, settings and hook entries differ from the expected state.

Run it as `uv run --script orca_settings_check.py` with Orca closed, after Orca's first launch and
after every upgrade. It changes nothing. It exits 0 when everything matches, 1 when something
differs, and 2 when it couldn't check something.
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

from parallel_sessions_common import (
    DIFFERS,
    FAILED,
    OK,
    Config,
    Platform,
    StopError,
    complain,
    config_dir,
    current_platform,
    load_config,
    prepare_output,
    say,
)

RECORD = "install-record.json"
CURRENT = "orca.AppImage"
VERSIONED = re.compile(r"orca-(?P<version>.+)\.AppImage")
CLAUDE_CODE_VERSION = re.compile(
    r"\b((\d+)\.(\d+)\.(\d+)(-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)[ \t]+\(Claude Code\)",
    re.IGNORECASE,
)
CLAUDE_TIMEOUT_SECONDS = 15
HELP = frozenset({"-h", "--help"})
PRERELEASE = 0
RELEASE = 1

# Major, minor, patch, then RELEASE or PRERELEASE: a prerelease ranks below its release, as Orca's
# hasReachedAppVersion ranks it. Floors are releases, so prereleases needn't rank among themselves.
Version = tuple[int, int, int, int]


def parse_version(text: str) -> Version:
    """A release's `x.y.z`, for comparing versions."""
    major, minor, patch = (int(part) for part in text.split("."))
    return major, minor, patch, RELEASE


@dataclass(frozen=True)
class OrcaVersion:
    """What one Orca version's source says about its defaults and its Claude Code hooks."""

    defaults: dict[str, object]
    hook_script: str
    managed_scripts: tuple[str, ...]
    event_first_versions: dict[str, str]
    event_install_floors: dict[str, str]

    def expected_events(self, claude: Version) -> set[str]:
        """The events this Orca version hooks for a Claude Code version."""
        return {
            event
            for event, first in self.event_first_versions.items()
            if claude >= parse_version(first)
            and claude >= parse_version(self.event_install_floors.get(event, first))
        }


# Read from Orca's source at v1.4.269. Defaults: src/shared/settings/default-global-settings.ts
# and host-owned-settings.ts; an unset updateDelayDays normalizes to 0
# (src/shared/updater/update-delay.ts), and automaticUpdates counts only when true. Hook scripts:
# src/main/claude/hooks/hook-settings.ts. Events: claude-managed-hook-events.ts, each from the
# Claude Code version in src/main/claude/cli-capabilities/claude-hook-event-versions.ts.
_SCRIPT_BASES = (
    "claude-hook",
    "openclaude-hook",
    "qoder-hook",
    "qoder-cn-hook",
    "qwen-code-hook",
    "codebuddy-hook",
)
KNOWN_VERSIONS = {
    "1.4.269": OrcaVersion(
        defaults={
            "agentPermissionDefault": "full-access",
            "nativeChatPermissionMode": "full-access",
            "autoRenameBranchFromWork": True,
            "updateDelayDays": 0,
            "automaticUpdates": False,
            "orchestrationCoordinatorApprovalsEnabled": False,
            "agentStatusHooksEnabled": True,
            "deleteChatHistoryWithWorkspace": False,
            "alwaysForceDeleteWorktrees": False,
            "alwaysForceDeletePreservedBranches": False,
            "skipDeleteWorktreeConfirm": False,
        },
        hook_script="claude-hook.sh",
        managed_scripts=tuple(f"{base}.{ext}" for base in _SCRIPT_BASES for ext in ("sh", "cmd")),
        event_first_versions={
            "PreToolUse": "1.0.23",
            "PostToolUse": "1.0.23",
            "Stop": "1.0.31",
            "SubagentStop": "1.0.41",
            "UserPromptSubmit": "1.0.53",
            "SessionStart": "1.0.62",
            "SessionEnd": "1.0.85",
            "SubagentStart": "2.0.43",
            "PermissionRequest": "2.0.45",
            "PostToolUseFailure": "2.0.56",
            "TeammateIdle": "2.1.33",
            "Elicitation": "2.1.63",
            "ElicitationResult": "2.1.63",
            "PostCompact": "2.1.76",
            "StopFailure": "2.1.78",
            "PostToolBatch": "2.1.118",
        },
        event_install_floors={"SessionEnd": "2.1.261"},
    ),
}


@dataclass(frozen=True)
class Setting:
    """A setting the check compares: the type Orca stores, and what's expected of it."""

    key: str
    kind: str  # "string", "boolean" or "number"
    expectation: str

    def has_kind(self, value: object) -> bool:
        """Whether a value is of the type Orca stores for this setting."""
        if self.kind == "boolean":
            return isinstance(value, bool)
        if self.kind == "number":
            return isinstance(value, int | float) and not isinstance(value, bool)
        return isinstance(value, str)


SETTINGS = (
    Setting("agentPermissionDefault", "string", 'not "full-access"'),
    Setting("nativeChatPermissionMode", "string", 'not "full-access"'),
    Setting("autoRenameBranchFromWork", "boolean", "false"),
    Setting("updateDelayDays", "number", "at least the minimum release age"),
    Setting("automaticUpdates", "boolean", "not true"),
    Setting("orchestrationCoordinatorApprovalsEnabled", "boolean", "not true"),
    Setting("agentStatusHooksEnabled", "boolean", "true"),
    Setting("deleteChatHistoryWithWorkspace", "boolean", "not true"),
    Setting("alwaysForceDeleteWorktrees", "boolean", "not true"),
    Setting("alwaysForceDeletePreservedBranches", "boolean", "not true"),
    Setting("skipDeleteWorktreeConfirm", "boolean", "not true"),
)


def matches(key: str, value: object, config: Config) -> bool:
    """Whether a setting's value, already of the right type, is what's expected."""
    if key in {"agentPermissionDefault", "nativeChatPermissionMode"}:
        return value != "full-access"
    if key == "autoRenameBranchFromWork":
        return value is False
    if key == "updateDelayDays":
        return isinstance(value, int | float) and value >= config.min_release_age_days
    if key == "agentStatusHooksEnabled":
        return value is True
    return value is not True


@dataclass
class Report:
    """Differences, and comparisons that couldn't be completed, in the order found."""

    differences: list[str] = field(default_factory=list)
    incomplete: list[str] = field(default_factory=list)

    def status(self) -> int:
        """The exit status: 2 over 1 over 0 (PAR-ALL-001)."""
        if self.incomplete:
            return FAILED
        return DIFFERS if self.differences else OK


def running_command_names() -> set[str]:
    """The command names of the running processes, from `/proc/<pid>/comm`."""
    names: set[str] = set()
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            with contextlib.suppress(OSError):
                names.add((entry / "comm").read_text(encoding="utf-8", errors="replace").strip())
    return names


def _sha512_b64(path: Path) -> str:
    with path.open("rb") as stream:
        return base64.b64encode(hashlib.file_digest(stream, "sha512").digest()).decode()


def read_install_record(install_dir: Path, report: Report) -> dict[str, object] | None:
    """The install record; None when there's none, or when it isn't a JSON object (reported)."""
    path = install_dir / RECORD
    if not path.exists():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        loaded = None
    if not isinstance(loaded, dict) or not all(isinstance(v, str) for v in loaded.values()):
        report.incomplete.append(
            f"couldn't check the installed files: the install record {path} "
            "isn't a valid JSON object of sha512s"
        )
        return None
    return {str(key): value for key, value in loaded.items()}


# @spec PAR-CHECK-010, PAR-CHECK-011, PAR-CHECK-012, PAR-CHECK-013, PAR-CHECK-014
def check_installed_files(install_dir: Path, report: Report) -> str | None:
    """Compare the versioned packages with the install record, and read the installed version.

    Returns:
        The version `orca.AppImage` links to, or None when it can't be taken.
    """
    unreadable = len(report.incomplete)
    record = read_install_record(install_dir, report)
    record_ok = len(report.incomplete) == unreadable
    packages = sorted(
        path
        for path in install_dir.glob("orca-*.AppImage")
        if path.is_file() and not path.is_symlink()
    )
    for package in packages if record_ok else ():
        found = VERSIONED.fullmatch(package.name)
        recorded = record.get(found["version"]) if record is not None and found else None
        if recorded is None:
            why = "there's no install record" if record is None else "the install record has none"
            report.differences.append(f"{package.name}: no sha512 recorded for it ({why})")
            continue
        try:
            actual = _sha512_b64(package)
        except OSError as error:
            report.incomplete.append(f"couldn't check {package.name}: {error}")
            continue
        if actual != recorded:
            report.differences.append(
                f"{package.name}: its sha512 isn't the one recorded at install, so it was "
                "replaced afterwards (Orca's in-app Update does this; upgrade with the installer)"
            )
    return installed_version(install_dir, report)


def installed_version(install_dir: Path, report: Report) -> str | None:
    """The version of the versioned package `orca.AppImage` links to."""
    current = install_dir / CURRENT
    if not current.is_symlink():
        state = "isn't a symbolic link" if current.exists() else "is missing"
        report.differences.append(f"{current} {state}; it should link to a versioned package")
        return None
    target = (install_dir / current.readlink()).resolve(strict=False)
    found = VERSIONED.fullmatch(target.name)
    if target.parent != install_dir.resolve() or found is None or not target.is_file():
        report.differences.append(
            f"{current} links to {target}, which isn't a versioned package in {install_dir}"
        )
        return None
    return str(found["version"])


# @spec PAR-CHECK-006, PAR-CHECK-009, PAR-CHECK-015
def profile_database(row: Platform, report: Report) -> Path | None:
    """The one profile's database, unless Orca left a write-ahead log beside it."""
    user_data = config_dir() / row.user_data
    if not user_data.is_dir():
        report.incomplete.append(
            f"Orca's user-data directory {user_data} doesn't exist: run Orca once first"
        )
        return None
    profiles = user_data / "profiles"
    found = sorted(p.name for p in profiles.iterdir() if p.is_dir()) if profiles.is_dir() else []
    if len(found) != 1:
        names = ", ".join(found) or "none"
        report.incomplete.append(
            f"couldn't choose a profile: {profiles} holds {len(found)} profile directories "
            f"({names})"
        )
        return None
    database = profiles / found[0] / row.profile_database
    log = database.with_name(f"{database.name}-wal")
    if log.exists() and log.stat().st_size > 0:
        report.incomplete.append(
            f"Orca didn't close its profile database cleanly ({log.name} is left beside it), so "
            "the settings may be stale: start Orca, quit it, and run the check again"
        )
        return None
    if not database.is_file():
        report.incomplete.append(f"couldn't find Orca's profile database at {database}")
        return None
    return database


def _settings_row(connection: sqlite3.Connection) -> tuple[object, int]:
    """The `settings` payload (or None), and how many parts are stored for `settings`."""
    row = connection.execute(
        "SELECT payload FROM profile_state_documents WHERE domain = 'settings'"
    ).fetchone()
    has_parts = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'profile_state_document_parts'"
    ).fetchone()
    parts = 0
    if has_parts is not None:
        counted = connection.execute(
            "SELECT count(*) FROM profile_state_document_parts WHERE domain = 'settings'"
        ).fetchone()
        parts = int(counted[0])
    return (None if row is None else row[0]), parts


# @spec PAR-CHECK-007, PAR-CHECK-008
def read_orca_settings(database: Path, report: Report) -> dict[str, object] | None:
    """Read Orca's settings from its profile database, opened read-only and immutable."""
    uri = f"file:{urllib.parse.quote(str(database))}?mode=ro&immutable=1"
    try:
        with contextlib.closing(sqlite3.connect(uri, uri=True)) as connection:
            payload, parts = _settings_row(connection)
    except sqlite3.Error as error:
        report.incomplete.append(f"couldn't read Orca's profile database {database}: {error}")
        return None
    if parts:
        report.incomplete.append(
            "couldn't check Orca's settings: the settings document is split into parts"
        )
        return None
    if payload is None:
        report.incomplete.append("couldn't check Orca's settings: the database has no settings row")
        return None
    try:
        settings = json.loads(str(payload))
    except ValueError:
        settings = None
    if not isinstance(settings, dict):
        report.incomplete.append(
            "couldn't check Orca's settings: the settings row isn't a JSON object"
        )
        return None
    return {str(key): value for key, value in settings.items()}


# @spec PAR-CHECK-020, PAR-CHECK-021, PAR-CHECK-022, PAR-CHECK-023, PAR-CHECK-024
# @spec PAR-CHECK-025, PAR-CHECK-026, PAR-CHECK-027, PAR-CHECK-028, PAR-CHECK-029, PAR-CHECK-032
def compare_settings(
    settings: dict[str, object],
    known: OrcaVersion | None,
    version: str | None,
    config: Config,
    report: Report,
) -> None:
    """Compare each setting with what's expected, using the version's default for a missing one."""
    for setting in SETTINGS:
        if setting.key in settings:
            value = settings[setting.key]
            if not setting.has_kind(value):
                report.differences.append(
                    f"{setting.key}: {json.dumps(value)} isn't a {setting.kind}, "
                    "the type Orca stores for it"
                )
                continue
            source = ""
        elif known is not None:
            value = known.defaults[setting.key]
            source = f" (unset; Orca {version}'s default)"
        else:
            report.incomplete.append(
                f"{setting.key}: unset, default unknown for Orca {version or '(version unknown)'}"
            )
            continue
        if not matches(setting.key, value, config):
            minimum = (
                f" of {config.min_release_age_days}" if setting.key == "updateDelayDays" else ""
            )
            report.differences.append(
                f"{setting.key}: {json.dumps(value)}{source}, "
                f"expected {setting.expectation}{minimum}"
            )


def claude_code_version() -> tuple[Version | None, str]:
    """The Claude Code version `claude --version` reports, or None and why not.

    The text after the None is the version as printed when there is one.
    """
    claude = shutil.which("claude")
    if claude is None:
        return None, "claude isn't on PATH"
    try:
        result = subprocess.run(  # noqa: S603 - the developer's own claude
            [claude, "--version"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=CLAUDE_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, f"`claude --version` failed ({error})"
    if result.returncode != 0:
        return None, f"`claude --version` exited with status {result.returncode}"
    found = CLAUDE_CODE_VERSION.search(f"{result.stdout}\n{result.stderr}")
    if found is None:
        return None, "`claude --version` printed no Claude Code version"
    rank = PRERELEASE if found[5] else RELEASE
    return (int(found[2]), int(found[3]), int(found[4]), rank), str(found[1])


def hook_commands(groups: object) -> list[str]:
    """The commands of a list of hook groups, skipping anything not shaped like one."""
    commands: list[str] = []
    for group in groups if isinstance(groups, list) else []:
        hooks = group.get("hooks") if isinstance(group, dict) else None
        commands.extend(
            str(hook["command"])
            for hook in (hooks if isinstance(hooks, list) else [])
            if isinstance(hook, dict) and isinstance(hook.get("command"), str)
        )
    return commands


def runs_script(command: str, scripts: tuple[str, ...]) -> bool:
    """Whether a command names one of the scripts as a whole file name, right after a `/`.

    The name must end there too, so `/claude-hook.sh.bak` isn't `/claude-hook.sh`.
    """
    return any(
        re.search(rf"/{re.escape(script)}(?![\w.-])", command) is not None for script in scripts
    )


def read_claude_hooks(report: Report) -> dict[str, object] | None:
    """The Claude settings file's `hooks`, or None when the file can't be read (reported)."""
    path = Path.home() / ".claude" / "settings.json"
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as error:
        report.incomplete.append(f"couldn't check Orca's hook entries: can't read {path} ({error})")
        return None
    hooks = settings.get("hooks", {}) if isinstance(settings, dict) else None
    if not isinstance(hooks, dict):
        what = "isn't a JSON object" if not isinstance(settings, dict) else "has hooks that aren't"
        report.incomplete.append(
            f"couldn't check Orca's hook entries: {path} {what} shaped as Claude Code reads them"
        )
        return None
    return {str(key): value for key, value in hooks.items()}


# @spec PAR-CHECK-030, PAR-CHECK-031, PAR-CHECK-033, PAR-CHECK-034, PAR-CHECK-035
def check_hook_entries(known: OrcaVersion | None, version: str | None, report: Report) -> None:
    """Compare Orca's entries in the Claude settings file with those Orca would install."""
    if version is None:
        return  # run_checks has already said why
    if known is None:
        report.incomplete.append(
            f"couldn't check Orca's hook entries: Orca {version} isn't a version whose hooks "
            f"are known (known: {', '.join(KNOWN_VERSIONS)})"
        )
        return
    hooks = read_claude_hooks(report)
    if hooks is None:
        return
    claude, printed = claude_code_version()
    if claude is None:
        why = printed
        report.incomplete.append(
            f"couldn't check Orca's hook entries: the Claude Code version is unknown ({why})"
        )
        return
    expected = known.expected_events(claude)
    shown = printed
    for event in sorted(expected):
        if not any(runs_script(c, (known.hook_script,)) for c in hook_commands(hooks.get(event))):
            report.differences.append(
                f"hook entries: {event} has no Orca entry running {known.hook_script}"
            )
    for event, groups in hooks.items():
        if event not in expected and any(
            runs_script(c, known.managed_scripts) for c in hook_commands(groups)
        ):
            report.differences.append(
                f"hook entries: {event} has an Orca entry, but Orca {version} doesn't hook "
                f"{event} for Claude Code {shown}"
            )


# @spec PAR-CHECK-001, PAR-CHECK-002, PAR-CHECK-003, PAR-CHECK-004, PAR-CHECK-005, PAR-ALL-002
def run_checks(row: Platform, config: Config) -> Report:
    """Make every comparison it can, and collect what it found."""
    report = Report()
    version = check_installed_files(config.install_dir, report)
    known = KNOWN_VERSIONS.get(version) if version is not None else None
    if version is None:
        report.incomplete.append(
            "couldn't take the installed version from orca.AppImage, so couldn't check Orca's "
            "settings defaults and hook entries"
        )
    check_hook_entries(known, version, report)
    if row.process_name in running_command_names():
        report.incomplete.append("Orca is running: quit Orca to check its settings")
        return report
    try:
        database = profile_database(row, report)
    except OSError as error:
        report.incomplete.append(f"couldn't find Orca's profile database: {error}")
        return report
    settings = read_orca_settings(database, report) if database is not None else None
    if settings is not None:
        compare_settings(settings, known, version, config, report)
    return report


def main(argv: list[str] | None = None) -> int:
    """Run the check; returns the exit status."""
    prepare_output()
    arguments = sys.argv[1:] if argv is None else argv
    if HELP & set(arguments):
        say(__doc__ or "")
        return OK
    if arguments:
        complain(f"orca_settings_check.py takes no arguments; got {' '.join(arguments)}")
        return FAILED
    try:
        row = current_platform()
        config = load_config(row)
        report = run_checks(row, config)
    except StopError as error:
        complain(error.message)
        return error.status
    except OSError as error:
        complain(f"couldn't complete the check: {error}")
        return FAILED
    except Exception as error:  # noqa: BLE001 - fail closed: never exit 1 or 0 on a surprise
        complain(f"couldn't complete the check: {type(error).__name__}: {error}")
        return FAILED
    for line in report.differences:
        say(f"differs: {line}")
    for line in report.incomplete:
        say(f"couldn't check: {line}")
    if not report.differences and not report.incomplete:
        say("Everything matches.")
    return report.status()


if __name__ == "__main__":
    sys.exit(main())
