"""Tests of the Orca settings check, tools/parallel-sessions/orca_settings_check.py.

Each runs against a fixture profile database built with Orca's schema, an install directory laid
out as the installer leaves it, and a Claude settings file carrying Orca's hook entries.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from tests.parallel_sessions_support import (
    CHECK,
    GOOD_SETTINGS,
    ORCA_EVENTS,
    Machine,
    claude_version,
    good_check_machine,
    install_package,
    make_profile_db,
    orca_hook_command,
    orca_hooks,
    requires_non_root,
    snapshot,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


@pytest.fixture
def machine(tmp_path: Path) -> Machine:
    """A machine with no Orca process running."""
    return Machine(tmp_path, processes=[])


# --- Outcome ----------------------------------------------------------------------------------


# @spec PAR-CHECK-002
def test_check_passes_when_everything_matches(machine: Machine) -> None:
    """A machine set up as expected exits 0."""
    good_check_machine(machine)
    result = machine.run(CHECK)
    assert result.returncode == 0, result.output


# @spec PAR-CHECK-001
@pytest.mark.parametrize(
    ("overrides", "status"),
    [
        ({}, 0),
        ({"autoRenameBranchFromWork": True}, 1),
        ({"agentStatusHooksEnabled": None}, 0),
        ({"autoRenameBranchFromWork": None}, 1),
    ],
    ids=["matching", "differing", "default-matching", "default-differing"],
)
def test_check_changes_no_file(machine: Machine, overrides: dict[str, object], status: int) -> None:
    """The check leaves every file under the home directory as it found it."""
    good_check_machine(machine, **overrides)
    before = snapshot(machine.home)
    result = machine.run(CHECK)
    assert result.returncode == status, result.output
    assert snapshot(machine.home) == before


# @spec PAR-CHECK-003, PAR-ALL-002
def test_check_prints_every_difference(machine: Machine) -> None:
    """Several differences are each printed, and the check exits 1."""
    good_check_machine(machine, autoRenameBranchFromWork=True, skipDeleteWorktreeConfirm=True)
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    assert "autoRenameBranchFromWork" in result.output
    assert "skipDeleteWorktreeConfirm" in result.output


# @spec PAR-CHECK-004, PAR-ALL-001
def test_check_exits_2_when_a_comparison_is_incomplete_even_with_differences(
    machine: Machine,
) -> None:
    """A difference (1) alongside a comparison it couldn't complete (2) exits 2."""
    install_package(machine, version="9.9.9")
    settings = {**GOOD_SETTINGS, "autoRenameBranchFromWork": True}
    del settings["automaticUpdates"]
    make_profile_db(machine.profile_db, settings)
    machine.claude_settings.parent.mkdir(parents=True)
    machine.claude_settings.write_text(json.dumps({"hooks": orca_hooks()}))
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert "autoRenameBranchFromWork" in result.output


# @spec PAR-CHECK-004
def test_check_exits_2_on_a_database_it_cannot_read(machine: Machine) -> None:
    """A profile database that isn't SQLite is a check that couldn't complete."""
    good_check_machine(machine)
    machine.profile_db.write_bytes(b"not a database at all, just text" * 10)
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert re.search("database|profile-state", result.output, re.IGNORECASE)


# @spec PAR-CHECK-005
def test_check_with_orca_running_checks_files_and_not_the_database(tmp_path: Path) -> None:
    """With Orca running, file differences still print, the database stays shut, and it exits 2."""
    machine = Machine(tmp_path, processes=["bash", "orca-ide"])
    good_check_machine(machine)
    (machine.install_dir / "orca-1.4.269.AppImage").write_bytes(b"replaced in place")
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert "orca-1.4.269.AppImage" in result.output
    assert re.search("quit", result.output, re.IGNORECASE)
    assert result.events("sqlite") == []


# @spec PAR-CHECK-005
def test_running_command_names_sees_a_real_orca_ide_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The real lookup the other tests replace finds a running process named `orca-ide`."""
    monkeypatch.syspath_prepend(str(CHECK.parent))  # as `uv run --script` would put it
    fake_orca = tmp_path / "orca-ide"
    shutil.copy2(shutil.which("sleep") or "/bin/sleep", fake_orca)
    process = subprocess.Popen([str(fake_orca), "30"])  # noqa: S603 - a copy of sleep
    try:
        spec = importlib.util.spec_from_file_location("orca_settings_check_under_test", CHECK)
        assert spec
        assert spec.loader
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, spec.name, module)  # so its dataclasses resolve
        spec.loader.exec_module(module)
        assert "orca-ide" in module.running_command_names()
    finally:
        process.kill()
        process.wait()


# @spec PAR-CHECK-005
def test_check_ignores_processes_with_other_names(tmp_path: Path) -> None:
    """Only a process named `orca-ide` counts as Orca."""
    machine = Machine(tmp_path, processes=["orca", "orca-ide-helper", "Orca"])
    good_check_machine(machine)
    result = machine.run(CHECK)
    assert result.returncode == 0, result.output


# @spec PAR-CHECK-006
def test_check_without_orca_user_data_says_to_run_orca_once(machine: Machine) -> None:
    """No user-data directory means Orca hasn't run: exit 2, saying to run it once."""
    good_check_machine(machine)
    for path in sorted(machine.user_data.rglob("*"), reverse=True):
        path.unlink() if path.is_file() else path.rmdir()
    machine.user_data.rmdir()
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert re.search(r"\b(run|start|launch|open)\b.*\borca\b", result.output, re.IGNORECASE)


# @spec PAR-CHECK-009
@pytest.mark.parametrize("profiles", [[], ["local-default", "work"]], ids=["none", "two"])
def test_check_needs_exactly_one_profile(machine: Machine, profiles: list[str]) -> None:
    """No profile directory, or several, is a check that couldn't complete, naming what it found."""
    good_check_machine(machine)
    root = machine.user_data / "profiles"
    (root / "local-default" / "profile-state.db").unlink()
    (root / "local-default").rmdir()
    for name in profiles:
        make_profile_db(root / name / "profile-state.db", GOOD_SETTINGS)
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    for name in profiles:
        assert name in result.output


# @spec PAR-CHECK-007
@pytest.mark.parametrize("problem", ["no-row", "parts"])
def test_check_needs_a_whole_settings_row(machine: Machine, problem: str) -> None:
    """A missing `settings` row, or parts stored for it, is a check that couldn't complete."""
    good_check_machine(machine)
    machine.profile_db.unlink()
    if problem == "no-row":
        make_profile_db(machine.profile_db, None)
    else:
        make_profile_db(machine.profile_db, GOOD_SETTINGS, parts=True)
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert re.search("settings", result.output, re.IGNORECASE)


# @spec PAR-CHECK-008
def test_check_opens_the_database_read_only_and_immutable(machine: Machine) -> None:
    """The database is opened as a read-only, immutable URI, leaving no file beside it."""
    good_check_machine(machine)
    beside = sorted(p.name for p in machine.profile_db.parent.iterdir())
    result = machine.run(CHECK)
    assert result.returncode == 0, result.output
    (opened,) = result.events("sqlite")
    assert opened["database"].startswith("file:")
    assert "mode=ro" in opened["database"]
    assert "immutable=1" in opened["database"]
    assert opened["kwargs"].get("uri") is True
    assert sorted(p.name for p in machine.profile_db.parent.iterdir()) == beside


# @spec PAR-CHECK-015
def test_check_refuses_a_database_with_a_write_ahead_log_left_beside_it(machine: Machine) -> None:
    """A non-empty `-wal` file means Orca didn't close cleanly: exit 2, database unopened."""
    good_check_machine(machine)
    machine.profile_db.with_name("profile-state.db-wal").write_bytes(b"\x37\x7f\x06\x82 log")
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert re.search(r"\bquit\b", result.output, re.IGNORECASE)
    assert result.events("sqlite") == []


# @spec PAR-CHECK-015
def test_check_reads_a_database_beside_an_empty_write_ahead_log(machine: Machine) -> None:
    """An empty `-wal` file holds nothing the main file lacks."""
    good_check_machine(machine)
    machine.profile_db.with_name("profile-state.db-wal").write_bytes(b"")
    result = machine.run(CHECK)
    assert result.returncode == 0, result.output


# --- Installed files ------------------------------------------------------------------------


def _plain_file(machine: Machine) -> None:
    link = machine.install_dir / "orca.AppImage"
    link.unlink()
    link.write_bytes(b"a plain file")


def _link_outside(machine: Machine) -> None:
    outside = machine.root / "elsewhere" / "orca-1.4.269.AppImage"
    outside.parent.mkdir()
    outside.write_bytes(b"x")
    link = machine.install_dir / "orca.AppImage"
    link.unlink()
    link.symlink_to(outside)


def _link_to_other_file(machine: Machine) -> None:
    (machine.install_dir / "notes.txt").write_text("x")
    link = machine.install_dir / "orca.AppImage"
    link.unlink()
    link.symlink_to("notes.txt")


# @spec PAR-CHECK-010
@pytest.mark.parametrize(
    "breakage", [_plain_file, _link_outside, _link_to_other_file], ids=["file", "outside", "other"]
)
def test_check_reports_orca_appimage_that_is_not_a_link_to_a_versioned_package(
    machine: Machine, breakage: Callable[[Machine], None]
) -> None:
    """`orca.AppImage` must link to a versioned package in the install directory."""
    good_check_machine(machine)
    breakage(machine)
    result = machine.run(CHECK)
    assert result.returncode in {1, 2}, result.output
    assert "orca.AppImage" in result.output


# @spec PAR-CHECK-011
@pytest.mark.parametrize("problem", ["replaced", "no-entry", "no-record"])
def test_check_reports_a_versioned_package_its_record_does_not_vouch_for(
    machine: Machine, problem: str
) -> None:
    """A versioned package whose sha512 isn't the one recorded, or none is, is a difference."""
    good_check_machine(machine)
    install_package(machine, version="1.4.268", content=b"earlier build", link=False)
    record = machine.install_dir / "install-record.json"
    if problem == "replaced":
        (machine.install_dir / "orca-1.4.268.AppImage").write_bytes(b"updated in place")
    elif problem == "no-entry":
        entries = json.loads(record.read_text())
        del entries["1.4.268"]
        record.write_text(json.dumps(entries))
    else:
        record.unlink()
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    assert "orca-1.4.268.AppImage" in result.output


# @spec PAR-CHECK-012, PAR-CHECK-028
def test_check_takes_the_installed_version_from_the_link(machine: Machine) -> None:
    """With the link on 1.4.269 and an unknown version also present, 1.4.269's defaults apply."""
    good_check_machine(machine, automaticUpdates=None)
    install_package(machine, version="9.9.9", link=False)
    result = machine.run(CHECK)
    assert result.returncode == 0, result.output


# @spec PAR-CHECK-013
def test_check_exits_2_on_an_install_record_that_is_not_a_json_object(machine: Machine) -> None:
    """An install record that isn't a JSON object means the installed files couldn't be checked."""
    good_check_machine(machine)
    (machine.install_dir / "install-record.json").write_text('["not", "an", "object"]')
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert re.search("record", result.output, re.IGNORECASE)


# @spec PAR-CHECK-014
def test_check_exits_2_without_an_installed_version(machine: Machine) -> None:
    """With no `orca.AppImage`, defaults and hook entries can't be checked: exit 2."""
    good_check_machine(machine)
    (machine.install_dir / "orca.AppImage").unlink()
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert re.search("hook", result.output, re.IGNORECASE)


# --- Orca's settings ------------------------------------------------------------------------


# @spec PAR-CHECK-020, PAR-CHECK-021, PAR-CHECK-022, PAR-CHECK-023
# @spec PAR-CHECK-024, PAR-CHECK-025, PAR-CHECK-026, PAR-CHECK-027
@pytest.mark.parametrize(
    ("key", "value", "differs"),
    [
        ("agentPermissionDefault", "full-access", True),
        ("agentPermissionDefault", "own", False),
        ("nativeChatPermissionMode", "full-access", True),
        ("nativeChatPermissionMode", "accept-edits", False),
        ("autoRenameBranchFromWork", True, True),
        ("autoRenameBranchFromWork", False, False),
        ("updateDelayDays", 2, True),
        ("updateDelayDays", 3, False),
        ("updateDelayDays", 7, False),
        ("automaticUpdates", True, True),
        ("automaticUpdates", False, False),
        ("orchestrationCoordinatorApprovalsEnabled", True, True),
        ("orchestrationCoordinatorApprovalsEnabled", False, False),
        ("agentStatusHooksEnabled", False, True),
        ("agentStatusHooksEnabled", True, False),
        ("deleteChatHistoryWithWorkspace", True, True),
        ("deleteChatHistoryWithWorkspace", False, False),
        ("alwaysForceDeleteWorktrees", True, True),
        ("alwaysForceDeleteWorktrees", False, False),
        ("alwaysForceDeletePreservedBranches", True, True),
        ("alwaysForceDeletePreservedBranches", False, False),
        ("skipDeleteWorktreeConfirm", True, True),
        ("skipDeleteWorktreeConfirm", False, False),
    ],
)
def test_check_compares_each_setting(
    machine: Machine,
    key: str,
    value: object,
    differs: bool,  # noqa: FBT001 - a parametrized case, not a flag
) -> None:
    """Each setting is a difference exactly when it holds a value the table rules out."""
    good_check_machine(machine, **{key: value})
    result = machine.run(CHECK)
    assert result.returncode == (1 if differs else 0), result.output
    if differs:
        assert key in result.output


# @spec PAR-CHECK-023
def test_check_compares_update_delay_with_the_configured_minimum(machine: Machine) -> None:
    """With a minimum release age of 7 days, an update delay of 3 is a difference."""
    machine.write_config("min_release_age_days = 7\n")
    good_check_machine(machine)
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    assert "updateDelayDays" in result.output


# @spec PAR-CHECK-028
@pytest.mark.parametrize(
    ("key", "differs"),
    [
        ("agentPermissionDefault", True),
        ("nativeChatPermissionMode", True),
        ("autoRenameBranchFromWork", True),
        ("updateDelayDays", True),
        ("automaticUpdates", False),
        ("orchestrationCoordinatorApprovalsEnabled", False),
        ("agentStatusHooksEnabled", False),
        ("deleteChatHistoryWithWorkspace", False),
        ("alwaysForceDeleteWorktrees", False),
        ("alwaysForceDeletePreservedBranches", False),
        ("skipDeleteWorktreeConfirm", False),
    ],
)
def test_check_judges_a_missing_setting_by_the_known_version_default(
    machine: Machine,
    key: str,
    differs: bool,  # noqa: FBT001
) -> None:
    """A setting missing on 1.4.269 takes 1.4.269's default (from Orca's source at that tag)."""
    good_check_machine(machine, **{key: None})
    result = machine.run(CHECK)
    assert result.returncode == (1 if differs else 0), result.output
    if differs:
        assert key in result.output


# @spec PAR-CHECK-029
def test_check_cannot_judge_a_missing_setting_on_an_unknown_version(machine: Machine) -> None:
    """A setting missing on an unknown version is "unset, default unknown": exit 2."""
    good_check_machine(machine, automaticUpdates=None)
    install_package(machine, version="9.9.9")
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert "automaticUpdates" in result.output
    assert "unset, default unknown" in result.output


# @spec PAR-CHECK-032
@pytest.mark.parametrize(
    ("key", "value", "shown"),
    [
        ("autoRenameBranchFromWork", "false", ('"false"', "'false'")),
        ("updateDelayDays", "7", ('"7"', "'7'")),
        ("agentStatusHooksEnabled", 1, ("1",)),
        ("agentPermissionDefault", 5, ("5",)),
        ("skipDeleteWorktreeConfirm", None, ("null", "None")),
    ],
)
def test_check_reports_a_setting_of_the_wrong_type(
    machine: Machine, key: str, value: object, shown: tuple[str, ...]
) -> None:
    """A value of a type Orca doesn't store for the setting is a difference, showing the value.

    A string is shown quoted, as JSON or Python writes it, so it can't be taken for a boolean.
    """
    good_check_machine(machine)
    machine.profile_db.unlink()
    make_profile_db(machine.profile_db, {**GOOD_SETTINGS, key: value})
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    line = next(line for line in result.output.splitlines() if key in line)
    assert any(form in line for form in shown), line


# --- Orca's hook entries ------------------------------------------------------------------


# @spec PAR-CHECK-030
@pytest.mark.parametrize("missing", ["Stop", "PreToolUse", "SessionStart"])
def test_check_reports_an_event_without_orca_hook(machine: Machine, missing: str) -> None:
    """An event Orca hooks, with no entry running its script, is reported."""
    good_check_machine(machine)
    hooks = orca_hooks(tuple(e for e in ORCA_EVENTS if e != missing))
    machine.claude_settings.write_text(json.dumps({"hooks": hooks}))
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    assert re.search(rf"\b{missing}\b", result.output)


# @spec PAR-CHECK-030
def test_check_needs_the_hook_under_the_event_itself(machine: Machine) -> None:
    """An Orca entry under another event doesn't count for `Stop`."""
    good_check_machine(machine)
    hooks = orca_hooks()
    hooks["Stop"] = [{"hooks": [{"type": "command", "command": "echo unrelated"}]}]
    machine.claude_settings.write_text(json.dumps({"hooks": hooks}))
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    assert re.search(r"\bStop\b", result.output)


# @spec PAR-CHECK-030
def test_check_accepts_orca_hooks_alongside_other_entries(machine: Machine) -> None:
    """Other entries under the same events don't hide Orca's."""
    good_check_machine(machine)
    hooks = orca_hooks()
    hooks["PreToolUse"].insert(
        0, {"matcher": "Bash", "hooks": [{"type": "command", "command": "x"}]}
    )
    machine.claude_settings.write_text(json.dumps({"hooks": hooks, "model": "opus"}))
    result = machine.run(CHECK)
    assert result.returncode == 0, result.output


# @spec PAR-CHECK-030
def test_check_does_not_count_openclaude_script_as_claude(machine: Machine) -> None:
    """`openclaude-hook.sh` under `Stop` isn't Orca's Claude hook script, `claude-hook.sh`."""
    good_check_machine(machine)
    hooks = orca_hooks()
    command = orca_hook_command().replace("claude-hook.sh", "openclaude-hook.sh")
    hooks["Stop"] = [{"hooks": [{"type": "command", "command": command, "timeout": 10}]}]
    machine.claude_settings.write_text(json.dumps({"hooks": hooks}))
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    assert re.search(r"\bStop\b", result.output)


# Events Orca 1.4.269 hooks only from a Claude Code version on
# (src/main/claude/cli-capabilities/claude-hook-event-versions.ts, and SessionEnd's own
# 2.1.261 floor in claude-managed-hook-events.ts).
NOT_BEFORE_2_1_76 = ("PostCompact", "StopFailure", "PostToolBatch", "SessionEnd")


# @spec PAR-CHECK-030
@pytest.mark.parametrize(
    ("claude", "absent"),
    [
        ("2.1.70", NOT_BEFORE_2_1_76),
        ("2.1.200", ("SessionEnd",)),
        ("2.1.261", ()),
        ("2.1.261-beta.1", ("SessionEnd",)),
        ("2.1.261+build.5", ()),
    ],
)
def test_check_expects_the_events_orca_hooks_for_the_claude_code_version(
    machine: Machine, claude: str, absent: tuple[str, ...]
) -> None:
    """Without the events an older Claude Code doesn't get, the hook entries match."""
    good_check_machine(machine)
    claude_version(machine, claude)
    hooks = orca_hooks(tuple(e for e in ORCA_EVENTS if e not in absent))
    machine.claude_settings.write_text(json.dumps({"hooks": hooks}))
    result = machine.run(CHECK)
    assert result.returncode == 0, result.output


# @spec PAR-CHECK-034
def test_check_reports_orca_entries_an_older_claude_code_would_not_get(machine: Machine) -> None:
    """With Claude Code 2.1.70, Orca entries under the later events are unexpected."""
    good_check_machine(machine)
    claude_version(machine, "2.1.70")
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    for event in NOT_BEFORE_2_1_76:
        assert re.search(rf"\b{event}\b", result.output), event


# @spec PAR-CHECK-034
def test_check_reports_an_orca_entry_under_an_event_orca_does_not_hook(machine: Machine) -> None:
    """An Orca entry under `Notification`, an event Orca never hooks, is reported."""
    good_check_machine(machine)
    hooks = orca_hooks()
    hooks["Notification"] = orca_hooks(("Stop",))["Stop"]
    machine.claude_settings.write_text(json.dumps({"hooks": hooks}))
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    assert "Notification" in result.output


# @spec PAR-CHECK-035
@pytest.mark.parametrize(
    "claude",
    [None, "exit 1\n", 'echo "1.2.3"\n', 'echo "claude is a launcher"\n'],
    ids=["missing", "fails", "launcher-version", "no-version"],
)
def test_check_cannot_check_hooks_without_the_claude_code_version(
    machine: Machine, claude: str | None
) -> None:
    """With no readable Claude Code version, hook entries can't be checked: exit 2."""
    good_check_machine(machine)
    (machine.bin / "claude").unlink()
    if claude is not None:
        machine.tool("claude", claude)
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert re.search("hook", result.output, re.IGNORECASE)
    assert re.search("claude", result.output, re.IGNORECASE)


# @spec PAR-CHECK-031
def test_check_cannot_check_hooks_on_an_unknown_version(machine: Machine) -> None:
    """On an unknown version, hook entries can't be checked: exit 2."""
    good_check_machine(machine)
    install_package(machine, version="9.9.9")
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert re.search("hook", result.output, re.IGNORECASE)


# @spec PAR-CHECK-033
@pytest.mark.parametrize(
    ("problem", "content"),
    [
        ("missing", None),
        ("invalid", "{not json"),
        ("not-object", "[]"),
        ("hooks-not-object", '{"hooks": ["Stop"]}'),
    ],
    ids=["missing", "invalid", "not-object", "hooks-not-object"],
)
def test_check_cannot_check_hooks_without_a_readable_claude_settings_file(
    machine: Machine, problem: str, content: str | None
) -> None:
    """A settings file that's missing or not an object of hooks means they can't be checked."""
    good_check_machine(machine)
    if problem == "missing":
        machine.claude_settings.unlink()
    else:
        machine.claude_settings.write_text(content or "")
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert re.search("hook", result.output, re.IGNORECASE)


# @spec PAR-ALL-003
def test_check_makes_no_network_request(machine: Machine) -> None:
    """The settings check makes no request and opens no socket."""
    good_check_machine(machine)
    result = machine.run(CHECK)
    assert result.returncode == 0, result.output
    assert result.events("request") == []
    assert result.events("socket") == []


# @spec PAR-CHECK-030
@pytest.mark.parametrize("suffix", [".bak", "x", "-old"])
def test_check_needs_the_script_name_to_end_there(machine: Machine, suffix: str) -> None:
    """`/claude-hook.sh.bak` under `Stop` doesn't run Orca's `claude-hook.sh`."""
    good_check_machine(machine)
    hooks = orca_hooks()
    command = orca_hook_command().replace("claude-hook.sh", f"claude-hook.sh{suffix}")
    hooks["Stop"] = [{"hooks": [{"type": "command", "command": command, "timeout": 10}]}]
    machine.claude_settings.write_text(json.dumps({"hooks": hooks}))
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    assert re.search(r"\bStop\b", result.output)


# @spec PAR-CHECK-004, PAR-CHECK-035
def test_check_reads_a_claude_version_beside_bytes_that_are_not_utf8(machine: Machine) -> None:
    """Stray non-UTF-8 bytes in `claude --version` don't crash the check."""
    good_check_machine(machine)
    machine.tool("claude", "printf '2.1.328 (Claude Code) \\377\\n'\n")
    result = machine.run(CHECK)
    assert result.returncode == 0, result.output


# @spec PAR-CHECK-013
def test_check_exits_2_on_an_install_record_holding_something_other_than_sha512s(
    machine: Machine,
) -> None:
    """A record entry that isn't a string means the installed files couldn't be checked."""
    good_check_machine(machine)
    (machine.install_dir / "install-record.json").write_text('{"1.4.269": 5}')
    result = machine.run(CHECK)
    assert result.returncode == 2, result.output
    assert re.search("record", result.output, re.IGNORECASE)


# @spec PAR-ALL-002, PAR-CHECK-004
@requires_non_root
def test_check_carries_on_past_a_package_it_cannot_read(machine: Machine) -> None:
    """An unreadable versioned package is reported, and the settings are still compared."""
    good_check_machine(machine, autoRenameBranchFromWork=True)
    package = machine.install_dir / "orca-1.4.269.AppImage"
    package.chmod(0)
    try:
        result = machine.run(CHECK)
    finally:
        package.chmod(0o755)
    assert result.returncode == 2, result.output
    assert "orca-1.4.269.AppImage" in result.output
    assert "autoRenameBranchFromWork" in result.output
