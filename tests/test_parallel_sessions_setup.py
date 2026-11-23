"""Tests of machine setup, tools/parallel-sessions/setup.py, and the Clash entry it adds."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from tests.parallel_sessions_support import (
    CLASH_ENTRY,
    LAUNCHER,
    SETUP,
    Machine,
    orca_hooks,
    requires_non_root,
    snapshot,
)

STAMP = re.compile(r"(\d{8}T\d{6}\.\d{6}Z)")


def installed_launcher(machine: Machine) -> Path:
    """Where setup installs the launcher."""
    return machine.home / ".local" / "bin" / "orca-launch"


def desktop_entry(machine: Machine) -> Path:
    """Where setup writes the desktop entry."""
    return machine.home / ".local" / "share" / "applications" / "orca.desktop"


def ready(machine: Machine, *, clash: bool = True, settings: dict[str, Any] | None = None) -> None:
    """Put the prerequisites on `PATH`, and write a Claude settings file holding Orca's hooks."""
    machine.tools("git", "uv", "claude")
    if clash:
        machine.tool("clash")
    machine.claude_settings.parent.mkdir(parents=True, exist_ok=True)
    content = settings if settings is not None else {"model": "opus", "hooks": orca_hooks()}
    machine.claude_settings.write_text(json.dumps(content, indent=2) + "\n")


def settings_json(machine: Machine) -> dict[str, Any]:
    """The Claude settings file, parsed."""
    return json.loads(machine.claude_settings.read_text())


def diff_lines(output: str) -> list[str]:
    """The unified-diff lines in some output: headers, hunk markers and changed lines."""
    return [
        line
        for line in output.splitlines()
        if line.startswith(("--- ", "+++ ", "@@")) or re.match(r"^[+-](?![+-]{2} )", line)
    ]


def is_subsequence(part: list[str], whole: list[str]) -> bool:
    """Whether `part` appears in `whole` in order, not necessarily together."""
    remaining = iter(whole)
    return all(line in remaining for line in part)


def desktop_keys(path: Path) -> dict[str, str]:
    """The keys of a desktop entry's `[Desktop Entry]` group."""
    lines = [
        line for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")
    ]
    assert lines[0] == "[Desktop Entry]"
    keys: dict[str, str] = {}
    for line in lines[1:]:
        if line.startswith("#"):
            continue
        assert not line.startswith("["), "only the [Desktop Entry] group is expected"
        key, _, value = line.partition("=")
        keys[key] = value
    return keys


@pytest.fixture
def machine(tmp_path: Path) -> Machine:
    """A machine with every prerequisite and Clash on `PATH`."""
    machine = Machine(tmp_path)
    ready(machine)
    return machine


# --- Showing and applying -------------------------------------------------------------------


# @spec PAR-SETUP-001
def test_setup_without_apply_shows_diffs_and_changes_nothing(machine: Machine) -> None:
    """By default setup prints a unified diff for each target and writes nothing."""
    before = snapshot(machine.home)
    result = machine.run(SETUP)
    assert result.returncode == 0, result.output
    assert snapshot(machine.home) == before
    for target in ("orca-launch", "orca.desktop", "settings.json"):
        assert target in result.stdout, target
    assert result.stdout.count("@@") >= 2 * 3  # a hunk header, at least, for each target
    assert "clash check" in result.stdout


# @spec PAR-SETUP-001, PAR-SETUP-009
def test_setup_shows_a_change_of_permissions(machine: Machine) -> None:
    """A launcher with the right content but not executable needs a change, shown as a line."""
    machine.run(SETUP, "--apply")
    installed_launcher(machine).chmod(0o644)
    result = machine.run(SETUP)
    assert result.returncode == 0, result.output
    lines = [line for line in result.stdout.splitlines() if "orca-launch" in line]
    assert any(re.search(r"mode|permission|chmod|644|755|x", line) for line in lines), lines
    assert "@@" not in result.stdout


# @spec PAR-SETUP-002
def test_setup_apply_prints_and_makes_the_shown_changes(machine: Machine) -> None:
    """`--apply` prints the same diffs as a plain run, then makes them."""
    shown = machine.run(SETUP)
    applied = machine.run(SETUP, "--apply")
    assert applied.returncode == 0, applied.output
    assert diff_lines(shown.stdout)
    assert is_subsequence(diff_lines(shown.stdout), applied.stdout.splitlines())
    assert installed_launcher(machine).is_file()
    assert desktop_entry(machine).is_file()
    assert CLASH_ENTRY in settings_json(machine)["hooks"]["PreToolUse"]


# @spec PAR-SETUP-002, PAR-SETUP-007
def test_setup_a_second_time_changes_nothing_and_backs_up_nothing(machine: Machine) -> None:
    """Once applied, setup finds nothing to change, writes nothing and makes no backup."""
    machine.run(SETUP, "--apply")
    before = snapshot(machine.home)
    shown = machine.run(SETUP)
    applied = machine.run(SETUP, "--apply")
    assert (shown.returncode, applied.returncode) == (0, 0), applied.output
    assert diff_lines(shown.stdout) == []
    assert diff_lines(applied.stdout) == []
    assert snapshot(machine.home) == before
    assert applied.events("rename") == []


# @spec PAR-SETUP-003
def test_setup_writes_each_target_through_a_rename_in_its_directory(machine: Machine) -> None:
    """Every target arrives by renaming a file from its own directory."""
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    renames = {entry["dst"]: entry["src"] for entry in result.events("rename")}
    for target in (installed_launcher(machine), desktop_entry(machine), machine.claude_settings):
        assert str(target) in renames, f"{target} wasn't renamed into place"
        assert Path(renames[str(target)]).parent == target.parent


# @spec PAR-SETUP-004
def test_setup_leaves_a_target_changed_underneath(machine: Machine) -> None:
    """A settings file changed while setup prepares its write keeps the other program's content."""
    theirs = json.dumps({"written": "by another program"})
    result = machine.run(
        SETUP, "--apply", mutate={"target": str(machine.claude_settings), "content": theirs}
    )
    assert result.returncode == 1, result.output
    assert machine.claude_settings.read_text() == theirs
    assert re.search("changed", result.output, re.IGNORECASE)
    assert re.search("incomplete", result.output, re.IGNORECASE)
    assert installed_launcher(machine).is_file()
    assert desktop_entry(machine).is_file()


# @spec PAR-SETUP-005
def test_setup_backs_up_an_existing_target_named_for_the_run(machine: Machine) -> None:
    """The settings file's earlier content is backed up, named with the run's UTC start time."""
    original = machine.claude_settings.read_bytes()
    start = datetime.now(UTC)
    result = machine.run(SETUP, "--apply")
    end = datetime.now(UTC)
    assert result.returncode == 0, result.output
    (backup,) = [p for p in machine.backups.iterdir() if "settings.json" in p.name]
    assert backup.read_bytes() == original
    match = STAMP.search(backup.name)
    assert match, backup.name
    stamp = datetime.strptime(match.group(1), "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=UTC)
    assert start <= stamp <= end


# @spec PAR-SETUP-005
def test_setup_backs_up_only_targets_that_existed(machine: Machine) -> None:
    """New targets (the launcher and the desktop entry, here) get no backup."""
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    names = [p.name for p in machine.backups.iterdir()]
    assert len(names) == 1
    assert "settings.json" in names[0]


# @spec PAR-SETUP-005
def test_setup_puts_backups_under_xdg_state_home(tmp_path: Path) -> None:
    """With `XDG_STATE_HOME` set to an absolute path, backups go under it."""
    state = tmp_path / "state"
    machine = Machine(tmp_path, env={"XDG_STATE_HOME": str(state)})
    ready(machine)
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert list((state / "parallel-sessions" / "backups").iterdir())
    assert not machine.backups.exists()


# @spec PAR-SETUP-016
def test_setup_backups_are_private_and_not_executable(machine: Machine) -> None:
    """Only the user can read or write the backups, and no copy is executable, even a launcher's."""
    launcher = installed_launcher(machine)
    launcher.parent.mkdir(parents=True)
    launcher.write_text("#!/bin/sh\necho old launcher\n")
    launcher.chmod(0o755)
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    directory_mode = stat.S_IMODE(machine.backups.stat().st_mode)
    assert directory_mode & 0o077 == 0, oct(directory_mode)
    assert directory_mode & 0o600 == 0o600, oct(directory_mode)
    copies = list(machine.backups.iterdir())
    for target in ("orca-launch", "settings.json"):
        assert any(p.name.startswith(target) for p in copies), target
    for copy in copies:
        assert stat.S_IMODE(copy.stat().st_mode) == 0o600, copy.name


# @spec PAR-SETUP-006
def test_setup_writes_through_a_symlinked_target(machine: Machine) -> None:
    """A settings file that is a link is written where it points, and stays a link."""
    real = machine.root / "dotfiles" / "claude-settings.json"
    real.parent.mkdir()
    real.write_text(machine.claude_settings.read_text())
    machine.claude_settings.unlink()
    machine.claude_settings.symlink_to(real)
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert machine.claude_settings.is_symlink()
    assert machine.claude_settings.readlink() == real
    assert CLASH_ENTRY in json.loads(real.read_text())["hooks"]["PreToolUse"]
    renames = {entry["dst"]: entry["src"] for entry in result.events("rename")}
    assert str(real) in renames
    assert Path(renames[str(real)]).parent == real.parent


# @spec PAR-SETUP-017
@pytest.mark.parametrize("target", ["launcher", "desktop"])
def test_setup_replaces_a_linked_launcher_or_desktop_entry(machine: Machine, target: str) -> None:
    """A launcher or desktop entry that links elsewhere becomes a file; what it linked to stays."""
    path = installed_launcher(machine) if target == "launcher" else desktop_entry(machine)
    elsewhere = machine.root / "checkout" / path.name
    elsewhere.parent.mkdir()
    elsewhere.write_text("#!/bin/sh\necho the source file\n")
    path.parent.mkdir(parents=True)
    path.symlink_to(elsewhere)
    shown = machine.run(SETUP)
    assert re.search(r"replac", shown.stdout, re.IGNORECASE), shown.stdout
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert not path.is_symlink()
    assert path.is_file()
    assert elsewhere.read_text() == "#!/bin/sh\necho the source file\n"
    renames = {entry["dst"]: entry["src"] for entry in result.events("rename")}
    assert Path(renames[str(path)]).parent == path.parent


# @spec PAR-SETUP-009
def test_setup_judges_the_settings_file_on_parsed_json(machine: Machine) -> None:
    """A settings file with the Clash entry, formatted differently, needs no change."""
    content = {"model": "opus", "hooks": {**orca_hooks()}}
    content["hooks"]["PreToolUse"] = [*content["hooks"]["PreToolUse"], CLASH_ENTRY]
    machine.claude_settings.write_text(json.dumps(content, indent=4, separators=(",", " : ")))
    before = machine.claude_settings.read_bytes()
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert machine.claude_settings.read_bytes() == before
    assert not any("settings.json" in line for line in diff_lines(result.stdout))


# @spec PAR-SETUP-008
def test_setup_keeps_every_other_key_and_entry(machine: Machine) -> None:
    """Unrelated keys, their order and Orca's entries survive; the file is 2-space JSON."""
    original = {
        "zeta": 1,
        "hooks": {
            **orca_hooks(),
            "Notification": [{"hooks": [{"type": "command", "command": "n"}]}],
        },
        "alpha": {"nested": [1, 2, {"deep": True}]},
        "statusLine": {"type": "command", "command": "~/.claude/statusline.sh"},
    }
    ready(machine, settings=original)
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    expected = json.loads(json.dumps(original))
    expected["hooks"]["PreToolUse"].append(CLASH_ENTRY)
    written = machine.claude_settings.read_text()
    assert json.loads(written) == expected
    assert list(json.loads(written)) == list(original)
    assert list(json.loads(written)["hooks"]) == list(original["hooks"])
    assert written.strip() == json.dumps(expected, indent=2)


# @spec PAR-SETUP-015
def test_setup_creates_a_missing_settings_file(tmp_path: Path) -> None:
    """With no Claude settings file and a Clash entry to add, setup creates the file."""
    machine = Machine(tmp_path)
    machine.tools("git", "uv", "claude", "clash")
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert settings_json(machine) == {"hooks": {"PreToolUse": [CLASH_ENTRY]}}


# @spec PAR-SETUP-025
@requires_non_root
def test_setup_carries_on_after_a_failed_write(machine: Machine) -> None:
    """A target that can't be written is reported, the others are written, and setup exits 2."""
    applications = desktop_entry(machine).parent
    applications.mkdir(parents=True)
    applications.chmod(0o555)
    try:
        result = machine.run(SETUP, "--apply")
    finally:
        applications.chmod(0o755)
    assert result.returncode == 2, result.output
    reported = [
        line
        for line in result.output.splitlines()
        if "orca.desktop" in line and line not in diff_lines(result.output)
    ]
    failed = re.compile("fail|error|could not|couldn't|denied", re.IGNORECASE)
    assert any(failed.search(line) for line in reported), result.output
    assert not desktop_entry(machine).exists()
    assert installed_launcher(machine).is_file()
    assert CLASH_ENTRY in settings_json(machine)["hooks"]["PreToolUse"]


# --- What setup writes ----------------------------------------------------------------------


# @spec PAR-SETUP-010
@pytest.mark.parametrize(
    ("configured", "directory"),
    [(None, "Applications/orca"), ("~/My Apps/orca $x", "My Apps/orca $x")],
    ids=["default", "configured"],
)
def test_setup_installs_the_launcher_with_the_install_directory(
    tmp_path: Path, configured: str | None, directory: str
) -> None:
    """The installed launcher is executable, quotes the install directory, and runs Orca there."""
    machine = Machine(tmp_path)
    ready(machine)
    if configured is not None:
        machine.write_config(f'install_dir = "{configured}"\n')
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    launcher = installed_launcher(machine)
    assert os.access(launcher, os.X_OK)
    install_dir = machine.home / directory
    escaped = str(install_dir).replace("$", "\\$")
    quoted = (f"'{install_dir}'", f'"{escaped}"')
    assert any(form in launcher.read_text() for form in quoted), launcher.read_text()
    package = install_dir / "orca.AppImage"
    package.parent.mkdir(parents=True)
    package.write_text('#!/bin/sh\necho "started $1"\n')
    package.chmod(0o755)
    ran = subprocess.run(  # noqa: S603 - the launcher setup just installed
        [str(launcher), "arg"],
        env={"HOME": str(machine.root / "other-home"), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    assert ran.stdout == "started arg\n"


# @spec PAR-SETUP-010
def test_installed_launcher_is_the_repo_launcher_apart_from_the_directory(machine: Machine) -> None:
    """The installed launcher keeps the repo's lines, changing only ones that name the directory."""
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    repo = LAUNCHER.read_text().splitlines()
    installed = installed_launcher(machine).read_text().splitlines()
    kept = [line for line in repo if "Applications/orca" not in line]
    assert is_subsequence(kept, installed)
    added = [line for line in installed if line not in repo]
    assert added
    assert all(str(machine.install_dir) in line for line in added), added


# @spec PAR-SETUP-011, PAR-SETUP-013
@pytest.mark.parametrize("icon", [False, True], ids=["no-icon", "icon"])
def test_setup_writes_the_desktop_entry(machine: Machine, *, icon: bool) -> None:
    """The desktop entry holds exactly the expected keys, with `Icon` only when the icon exists."""
    if icon:
        machine.install_dir.mkdir(parents=True)
        (machine.install_dir / "icon.png").write_bytes(b"png")
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    expected = {
        "Type": "Application",
        "Name": "Orca",
        "Exec": str(installed_launcher(machine)),
        "Categories": "Development;",
        "StartupWMClass": "orca",
    }
    if icon:
        expected["Icon"] = str(machine.install_dir / "icon.png")
    assert desktop_keys(desktop_entry(machine)) == expected


# @spec PAR-SETUP-013
def test_setup_adds_the_icon_once_the_installer_has_saved_it(machine: Machine) -> None:
    """Re-running setup after the icon appears changes the desktop entry to add it."""
    machine.run(SETUP, "--apply")
    machine.install_dir.mkdir(parents=True)
    (machine.install_dir / "icon.png").write_bytes(b"png")
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert desktop_keys(desktop_entry(machine))["Icon"] == str(machine.install_dir / "icon.png")


# --- Prerequisites and outcome --------------------------------------------------------------


# @spec PAR-SETUP-020, PAR-SETUP-021
@pytest.mark.parametrize(
    "present",
    [("uv", "claude"), ("git", "claude"), ("git", "uv"), ()],
    ids=["git", "uv", "claude", "all"],
)
def test_setup_stops_when_a_prerequisite_is_missing(
    tmp_path: Path, present: tuple[str, ...]
) -> None:
    """Setup names each missing prerequisite, exits 2, and prints and changes nothing."""
    machine = Machine(tmp_path)
    machine.tools(*present, "clash")
    machine.claude_settings.parent.mkdir(parents=True)
    machine.claude_settings.write_text("{}")
    before = snapshot(machine.home)
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 2, result.output
    for name in {"git", "uv", "claude"} - set(present):
        assert re.search(rf"\b{name}\b", result.output), name
    assert diff_lines(result.stdout) == []
    assert snapshot(machine.home) == before


# @spec PAR-SETUP-022
def test_setup_exits_0_when_complete(machine: Machine) -> None:
    """With every change made, setup exits 0 and doesn't call the setup incomplete."""
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert not re.search("incomplete", result.output, re.IGNORECASE)


# @spec PAR-SETUP-024
def test_setup_exits_2_on_an_unreadable_settings_file(machine: Machine) -> None:
    """A Claude settings file that isn't valid JSON is a failure: exit 2, and it's left alone."""
    machine.claude_settings.write_text("{not json")
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 2, result.output
    assert machine.claude_settings.read_text() == "{not json"


# --- Clash's entry --------------------------------------------------------------------------


# @spec PAR-CLASH-001
def test_setup_appends_the_clash_entry(machine: Machine) -> None:
    """With `clash` on `PATH` and no equivalent entry, the Clash entry is appended after Orca's."""
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    groups = settings_json(machine)["hooks"]["PreToolUse"]
    assert groups[-1] == CLASH_ENTRY
    assert groups[:-1] == orca_hooks()["PreToolUse"]


# @spec PAR-CLASH-001
def test_setup_adds_the_clash_entry_when_the_plugin_is_disabled(machine: Machine) -> None:
    """A Clash plugin set to `false` doesn't count as enabled."""
    ready(machine, settings={"enabledPlugins": {"clash@clash-sh": False}})
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert settings_json(machine)["hooks"]["PreToolUse"] == [CLASH_ENTRY]


def _equivalent(matcher: str, command: str = "clash check") -> dict[str, Any]:
    return {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": matcher,
                    "hooks": [
                        {"type": "command", "command": "other"},
                        {"type": "command", "command": command},
                    ],
                }
            ]
        }
    }


# @spec PAR-CLASH-002
@pytest.mark.parametrize(
    "settings",
    [
        _equivalent("Write|Edit|MultiEdit"),
        _equivalent("MultiEdit|Bash|Edit|Write"),
        _equivalent("*"),
        _equivalent(".*"),
        _equivalent(""),
        _equivalent("Write|Edit|MultiEdit", "  clash check \n"),
        {"enabledPlugins": {"clash@clash-sh": True}},
    ],
    ids=["same", "superset", "star", "dot-star", "empty", "padded", "plugin"],
)
def test_setup_adds_no_clash_entry_when_one_is_covered(
    machine: Machine, settings: dict[str, Any]
) -> None:
    """An equivalent entry, or Clash's enabled plugin, means no entry is added."""
    ready(machine, settings=settings)
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert settings_json(machine) == settings


# @spec PAR-CLASH-001
@pytest.mark.parametrize(
    "settings",
    [_equivalent("Write|Edit"), _equivalent("Write|Edit|MultiEdit", "clash check --strict")],
    ids=["partial-matcher", "other-command"],
)
def test_setup_adds_the_entry_beside_a_near_miss(
    machine: Machine, settings: dict[str, Any]
) -> None:
    """An entry that isn't equivalent leaves the Clash entry still to add."""
    ready(machine, settings=settings)
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert settings_json(machine)["hooks"]["PreToolUse"][-1] == CLASH_ENTRY


# @spec PAR-CLASH-003, PAR-SETUP-023
def test_setup_reports_a_stale_clash_entry(tmp_path: Path) -> None:
    """With `clash` gone, an existing entry is reported stale, kept, and makes setup incomplete."""
    machine = Machine(tmp_path)
    settings = _equivalent("Write|Edit|MultiEdit")
    ready(machine, clash=False, settings=settings)
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 1, result.output
    assert re.search("stale", result.output, re.IGNORECASE)
    assert re.search("incomplete", result.output, re.IGNORECASE)
    assert settings_json(machine) == settings


# @spec PAR-CLASH-004, PAR-SETUP-023
def test_setup_skips_clash_when_it_is_not_installed(tmp_path: Path) -> None:
    """With no `clash`, no entry is added, the mise command is printed, and setup is incomplete."""
    machine = Machine(tmp_path)
    ready(machine, clash=False)
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 1, result.output
    assert "clash check" not in machine.claude_settings.read_text()
    assert re.search(r"mise use -g \S*clash\S*@\d", result.output)
    assert re.search("incomplete", result.output, re.IGNORECASE)
    assert re.search("skip", result.output, re.IGNORECASE)
    assert installed_launcher(machine).is_file()


# @spec PAR-CLASH-005, PAR-SETUP-023
def test_setup_reports_clash_plugin_without_clash(tmp_path: Path) -> None:
    """Clash's plugin enabled with no `clash` on `PATH`: reported, no entry added, incomplete."""
    machine = Machine(tmp_path)
    settings = {"enabledPlugins": {"clash@clash-sh": True}}
    ready(machine, clash=False, settings=settings)
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 1, result.output
    assert settings_json(machine) == settings
    assert re.search("plugin", result.output, re.IGNORECASE)
    assert re.search(r"mise use -g \S*clash\S*@\d", result.output)
    assert re.search("incomplete", result.output, re.IGNORECASE)


# @spec PAR-ALL-003
def test_setup_makes_no_network_request(machine: Machine) -> None:
    """Setup makes no request and opens no socket."""
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    assert result.events("request") == []
    assert result.events("socket") == []


# @spec PAR-SETUP-011
@pytest.mark.parametrize(
    ("path", "written"),
    [
        ("/home/a/.local/bin/orca-launch", "/home/a/.local/bin/orca-launch"),
        ("/home/a%u/.local/bin/orca-launch", "/home/a%%u/.local/bin/orca-launch"),
        ("/home/a b/.local/bin/orca-launch", '"/home/a b/.local/bin/orca-launch"'),
        ("/home/a\\b/orca-launch", '"/home/a\\\\\\\\b/orca-launch"'),
    ],
    ids=["plain", "percent", "space", "backslash"],
)
def test_desktop_exec_holds_the_path_with_no_field_codes(
    monkeypatch: pytest.MonkeyPatch, path: str, written: str
) -> None:
    """`%` is doubled, and a path needing quotes is quoted, then string-escaped."""
    monkeypatch.syspath_prepend(str(SETUP.parent))
    spec = importlib.util.spec_from_file_location("setup_under_test", SETUP)
    assert spec
    assert spec.loader
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    assert module.desktop_exec(Path(path)) == written
