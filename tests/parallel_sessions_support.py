"""Machines, fixtures and a runner for the tests of tools/parallel-sessions/.

Each test gets a `Machine`: a temporary home directory with `HOME` and `XDG_CONFIG_HOME` pointing
into it, a `bin` directory as the whole of `PATH`, and a working directory of its own. Python
scripts run as subprocesses through `tests/parallel_sessions_shim.py`, which replaces the
platform, the network and the process list as the test asks; the launcher runs under `sh` as is.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import stat
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import pytest

from tests.support import FIXTURES, REPO_ROOT

if TYPE_CHECKING:
    from pathlib import Path

TOOLS = REPO_ROOT / "tools" / "parallel-sessions"
LAUNCHER = TOOLS / "orca-launch"
INSTALLER = TOOLS / "orca_install.py"
CHECK = TOOLS / "orca_settings_check.py"
SETUP = TOOLS / "setup.py"
PYTHON_SCRIPTS = (INSTALLER, CHECK, SETUP)
SHIM = REPO_ROOT / "tests" / "parallel_sessions_shim.py"
SCHEMA = FIXTURES / "parallel-sessions" / "profile-state-schema.sql"

# The interpreter the project venv was made from. The scripts may use only the standard library,
# and under the venv's own interpreter a stray import of a dev dependency (PyYAML) would pass here
# and fail under `uv run --script`.
BASE_PYTHON = getattr(sys, "_base_executable", sys.executable)

# Permission bits don't stop root, so tests that make a file unreadable or a directory read-only
# can't run as root (a container, say).
requires_non_root = pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0, reason="root ignores permission bits"
)

KNOWN_VERSION = "1.4.269"
TAG = f"v{KNOWN_VERSION}"

# Platform-table rows the tests rely on, keyed by `platform.machine()`.
MANIFESTS = {"x86_64": "latest-linux.yml", "aarch64": "latest-linux-arm64.yml"}
PACKAGES = {"x86_64": "orca-linux.AppImage", "aarch64": "orca-linux-arm64.AppImage"}

# The settings the check compares, each with a value it expects (matching) and one it doesn't.
GOOD_SETTINGS: dict[str, Any] = {
    "agentPermissionDefault": "ask",
    "nativeChatPermissionMode": "ask",
    "autoRenameBranchFromWork": False,
    "updateDelayDays": 3,
    "automaticUpdates": False,
    "orchestrationCoordinatorApprovalsEnabled": False,
    "agentStatusHooksEnabled": True,
    "deleteChatHistoryWithWorkspace": False,
    "alwaysForceDeleteWorktrees": False,
    "alwaysForceDeletePreservedBranches": False,
    "skipDeleteWorktreeConfirm": False,
}

# A Claude Code version new enough for Orca 1.4.269 to hook every event below.
CLAUDE_CODE_VERSION = "2.1.328"

# Claude Code events Orca 1.4.269 installs a hook for, given a current Claude Code
# (src/main/claude/hooks/claude-managed-hook-events.ts at v1.4.269).
ORCA_EVENTS = (
    "SessionStart",
    "UserPromptSubmit",
    "Stop",
    "StopFailure",
    "SubagentStart",
    "SubagentStop",
    "TeammateIdle",
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "PermissionRequest",
    "PostCompact",
    "Elicitation",
    "ElicitationResult",
    "SessionEnd",
    "PostToolBatch",
)
MATCHED_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "PermissionRequest",
    "Elicitation",
    "ElicitationResult",
}
CLASH_ENTRY = {
    "matcher": "Write|Edit|MultiEdit",
    "hooks": [{"type": "command", "command": "clash check"}],
}


def orca_hook_command() -> str:
    """A shortened form of the command Orca writes for each event: it names `claude-hook.sh`."""
    return (
        'if [ -n "${HOME-}" ] && [ -x "${HOME-}/.orca/agent-hooks/claude-hook.sh" ]; '
        'then "${HOME-}/.orca/agent-hooks/claude-hook.sh"; fi'
    )


def orca_hooks(events: tuple[str, ...] = ORCA_EVENTS) -> dict[str, list[dict[str, Any]]]:
    """Orca's hook entries for the given events, shaped as Orca writes them."""
    hooks: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        group: dict[str, Any] = {
            "hooks": [{"type": "command", "command": orca_hook_command(), "timeout": 10}]
        }
        if event in MATCHED_EVENTS:
            group = {"matcher": "*", **group}
        hooks[event] = [group]
    return hooks


def b64_sha512(data: bytes) -> str:
    """The sha512 of some bytes, base64-encoded as manifests and the install record hold it."""
    return base64.b64encode(hashlib.sha512(data).digest()).decode()


@dataclass
class Result:
    """What a script run left: its exit status, its output, and the shim's log."""

    returncode: int
    stdout: str
    stderr: str
    log: list[dict[str, Any]]

    @property
    def output(self) -> str:
        """Standard output and standard error together, for messages that may go to either."""
        return self.stdout + self.stderr

    def events(self, kind: str) -> list[dict[str, Any]]:
        """The shim's log entries of one kind: `request`, `socket`, `rename` or `sqlite`."""
        return [entry for entry in self.log if entry["event"] == kind]


@dataclass
class Machine:
    """A developer's machine in a temporary directory."""

    root: Path
    platform: tuple[str, str] = ("Linux", "x86_64")
    urls: dict[str, dict[str, Any]] = field(default_factory=dict)
    processes: list[str] | None = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Create the home, `bin` and working directories, and the base environment."""
        self.home.mkdir(parents=True, exist_ok=True)
        self.bin.mkdir(exist_ok=True)
        self.cwd.mkdir(exist_ok=True)
        self.env = {
            "HOME": str(self.home),
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "PATH": str(self.bin),
            "LANG": "C.UTF-8",
            **self.env,
        }

    @property
    def home(self) -> Path:
        """The fake home directory."""
        return self.root / "home"

    @property
    def bin(self) -> Path:
        """The only directory on `PATH`."""
        return self.root / "bin"

    @property
    def cwd(self) -> Path:
        """The working directory scripts run in."""
        return self.root / "work"

    @property
    def config_file(self) -> Path:
        """The config file under the fake `XDG_CONFIG_HOME`."""
        return self.home / ".config" / "parallel-sessions" / "config.toml"

    @property
    def install_dir(self) -> Path:
        """The default install directory."""
        return self.home / "Applications" / "orca"

    @property
    def claude_settings(self) -> Path:
        """The Claude settings file."""
        return self.home / ".claude" / "settings.json"

    @property
    def user_data(self) -> Path:
        """Orca's user-data directory."""
        return self.home / ".config" / "orca"

    @property
    def profile_db(self) -> Path:
        """The profile database of the `local-default` profile."""
        return self.user_data / "profiles" / "local-default" / "profile-state.db"

    @property
    def backups(self) -> Path:
        """The backup directory, with `XDG_STATE_HOME` unset."""
        return self.home / ".local" / "state" / "parallel-sessions" / "backups"

    def tool(self, name: str, script: str = "exit 0\n") -> Path:
        """Put an executable stand-in for a command on `PATH`."""
        path = self.bin / name
        path.write_text(f"#!/bin/sh\n{script}")
        path.chmod(0o755)
        return path

    def tools(self, *names: str) -> None:
        """Put stand-ins for several commands on `PATH`."""
        for name in names:
            self.tool(name)

    def write_config(self, text: str) -> None:
        """Write the config file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(textwrap.dedent(text))

    def run(self, script: Path, *args: str, mutate: dict[str, str] | None = None) -> Result:
        """Run a Python script through the shim, with this machine's boundaries.

        Args:
            script: The script to run.
            *args: Its arguments.
            mutate: The shim's `mutate` instruction, if any.

        Returns:
            The run's result.
        """
        plan_dir = self.root / "shim"
        plan_dir.mkdir(exist_ok=True)
        log = plan_dir / "log.jsonl"
        log.write_text("")
        plan = {
            "platform": list(self.platform),
            "urls": self.urls,
            "processes": self.processes,
            "log": str(log),
            "mutate": mutate,
        }
        plan_file = plan_dir / "plan.json"
        plan_file.write_text(json.dumps(plan))
        completed = subprocess.run(  # noqa: S603 - a fixed interpreter running repo files
            [BASE_PYTHON, "-I", str(SHIM), str(plan_file), str(script), *args],
            cwd=self.cwd,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        # A crash exits 1, which would pass for "a check failed": every failure must be reported.
        assert "Traceback (most recent call last)" not in completed.stderr, completed.stderr
        entries = [json.loads(line) for line in log.read_text().splitlines() if line]
        return Result(completed.returncode, completed.stdout, completed.stderr, entries)


def snapshot(root: Path) -> dict[str, tuple[str, int, bytes | str]]:
    """Every path under a directory, with its kind, mode and content (or link target)."""
    shot: dict[str, tuple[str, int, bytes | str]] = {}
    for path in sorted(root.rglob("*")):
        info = path.lstat()
        key = str(path.relative_to(root))
        if stat.S_ISLNK(info.st_mode):
            shot[key] = ("link", info.st_mode, str(path.readlink()))
        elif stat.S_ISDIR(info.st_mode):
            shot[key] = ("dir", info.st_mode, "")
        else:
            shot[key] = ("file", info.st_mode, path.read_bytes())
    return shot


# --- Orca's installed files ----------------------------------------------------------------


def install_package(
    machine: Machine,
    version: str = KNOWN_VERSION,
    content: bytes | None = None,
    *,
    link: bool = True,
    record: bool = True,
) -> Path:
    """Lay out an installed package as the installer leaves it.

    Args:
        machine: The machine.
        version: The package's version.
        content: The package's bytes.
        link: Whether to point `orca.AppImage` at it.
        record: Whether to record its sha512 in the install record.

    Returns:
        The versioned package's path.
    """
    content = content if content is not None else f"orca {version}\n".encode()
    machine.install_dir.mkdir(parents=True, exist_ok=True)
    package = machine.install_dir / f"orca-{version}.AppImage"
    package.write_bytes(content)
    package.chmod(0o755)
    if record:
        record_file = machine.install_dir / "install-record.json"
        entries = json.loads(record_file.read_text()) if record_file.exists() else {}
        entries[version] = b64_sha512(content)
        record_file.write_text(json.dumps(entries))
    if link:
        current = machine.install_dir / "orca.AppImage"
        current.unlink(missing_ok=True)
        current.symlink_to(package.name)
    return package


def make_profile_db(
    path: Path,
    settings: dict[str, Any] | str | None,
    *,
    parts: bool = False,
) -> None:
    """Build a profile database with Orca's schema.

    Args:
        path: Where to create it.
        settings: The `settings` document (a dict, or raw payload text), or None for no row.
        parts: Whether to also store parts for `settings` in `profile_state_document_parts`.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.executescript(SCHEMA.read_text())
        if settings is not None:
            payload = settings if isinstance(settings, str) else json.dumps(settings)
            connection.execute(
                "INSERT INTO profile_state_documents VALUES ('settings', ?, 1, 1, 0, 'hash')",
                (payload,),
            )
        if parts:
            connection.execute(
                "INSERT INTO profile_state_document_parts VALUES ('settings', 'a', 0, '{}', 'h')"
            )
        connection.commit()
    finally:
        connection.close()


def good_check_machine(machine: Machine, **overrides: object) -> None:
    """Lay out a machine the settings check finds nothing wrong with, then apply overrides.

    An override whose value is `None` removes that setting from Orca's settings.
    """
    install_package(machine)
    settings = {**GOOD_SETTINGS, "unrelatedSetting": "kept"}
    for key, value in overrides.items():
        if value is None:
            settings.pop(key, None)
        else:
            settings[key] = value
    make_profile_db(machine.profile_db, settings)
    machine.claude_settings.parent.mkdir(parents=True, exist_ok=True)
    machine.claude_settings.write_text(json.dumps({"hooks": orca_hooks()}, indent=2))
    claude_version(machine)


def claude_version(machine: Machine, version: str = CLAUDE_CODE_VERSION) -> None:
    """Put a `claude` on `PATH` whose `--version` prints a version as Claude Code does."""
    machine.tool("claude", f'echo "{version} (Claude Code)"\n')


# --- Releases --------------------------------------------------------------------------------


def api_url(tag: str = TAG) -> str:
    """GitHub's releases API URL for a tag of Orca."""
    return f"https://api.github.com/repos/stablyai/orca/releases/tags/{tag}"


def download_url(name: str, tag: str = TAG) -> str:
    """The download URL of a file attached to a release of Orca."""
    return f"https://github.com/stablyai/orca/releases/download/{tag}/{name}"


def icon_urls(tag: str = TAG) -> list[str]:
    """The URLs Orca's icon can be fetched from at a tag."""
    path = "resources/build/icon.png"
    return [
        f"https://raw.githubusercontent.com/stablyai/orca/{tag}/{path}",
        f"https://github.com/stablyai/orca/raw/{tag}/{path}",
    ]


def body(data: bytes | str) -> dict[str, Any]:
    """A 200 response carrying some bytes."""
    raw = data.encode() if isinstance(data, str) else data
    return {"body": base64.b64encode(raw).decode()}


def manifest_text(
    package: str, digest: str, size: int, version: str = KNOWN_VERSION, *, entry: bool = True
) -> str:
    """A release manifest in electron-builder's format, as Orca's releases carry it."""
    files = (
        f"  - url: {package}\n    sha512: {digest}\n    size: {size}\n    blockMapSize: 292354\n"
        if entry
        else ""
    )
    return (
        f"version: {version}\nfiles:\n{files}"
        f"  - url: orca-ide_{version}_amd64.deb\n    sha512: AAAA\n    size: 10\n"
        f"path: {package}\nsha512: {digest}\nreleaseDate: '2026-11-21T17:45:39.349Z'\n"
    )


@dataclass
class Release:
    """A downloaded package and the release it claims to come from."""

    package: Path
    content: bytes
    tag: str = TAG


def serve_release(  # noqa: PLR0913 - each argument varies one fact of the release
    machine: Machine,
    *,
    content: bytes = b"#!/bin/sh\necho orca\n",
    age: timedelta = timedelta(days=10),
    prerelease: bool = False,
    manifest_version: str = KNOWN_VERSION,
    manifest_digest: str | None = None,
    manifest_size: int | None = None,
    manifest: str | None = None,
    icon: bool = True,
    tag: str = TAG,
) -> Release:
    """Write a downloaded package into the working directory and serve its release.

    Args:
        machine: The machine whose URLs to set.
        content: The package's bytes.
        age: How long ago the release was published (negative for the future).
        prerelease: Whether the release is a prerelease.
        manifest_version: The manifest's `version`.
        manifest_digest: The manifest's sha512, if not the package's.
        manifest_size: The manifest's size, if not the package's.
        manifest: The manifest's whole text, overriding the above.
        icon: Whether the icon can be fetched.
        tag: The release's tag.

    Returns:
        The downloaded package.
    """
    arch = machine.platform[1]
    package_name = PACKAGES[arch]
    manifest_name = MANIFESTS[arch]
    downloaded = machine.cwd / package_name
    downloaded.write_bytes(content)
    published = (datetime.now(UTC) - age).strftime("%Y-%m-%dT%H:%M:%SZ")
    release = {
        "tag_name": tag,
        "draft": False,
        "prerelease": prerelease,
        "published_at": published,
        "assets": [
            {"name": name, "browser_download_url": download_url(name, tag)}
            for name in (manifest_name, package_name)
        ],
    }
    text = (
        manifest
        if manifest is not None
        else manifest_text(
            package_name,
            manifest_digest or b64_sha512(content),
            len(content) if manifest_size is None else manifest_size,
            manifest_version,
        )
    )
    machine.urls[api_url(tag)] = body(json.dumps(release))
    machine.urls[download_url(manifest_name, tag)] = body(text)
    for url in icon_urls(tag):
        machine.urls[url] = body(b"\x89PNG fake icon") if icon else {"status": 404}
    return Release(downloaded, content, tag)


def files_outside_work(machine: Machine) -> dict[str, tuple[str, int, bytes | str]]:
    """A snapshot of the fake home, where no failed install may write."""
    return snapshot(machine.home)
