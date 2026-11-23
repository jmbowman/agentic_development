"""Tests of what tools/parallel-sessions/ shares: platforms, the config file and exit statuses."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from tests.parallel_sessions_support import (
    CHECK,
    INSTALLER,
    PYTHON_SCRIPTS,
    SETUP,
    TAG,
    TOOLS,
    Machine,
    good_check_machine,
    requires_non_root,
    serve_release,
    snapshot,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tests.parallel_sessions_support import Result

SCRIPT_IDS = [script.name for script in PYTHON_SCRIPTS]
# Either the name `platform.system()` reports or its usual name may name an operating system.
FRIENDLY_SYSTEMS = {"Darwin": "macOS"}


def run_ready(machine: Machine, script: Path) -> Result:
    """Run a script on a machine laid out so that it would otherwise succeed."""
    if script == INSTALLER:
        release = serve_release(machine)
        return machine.run(INSTALLER, str(release.package), "--tag", TAG)
    if script == CHECK:
        good_check_machine(machine)
        return machine.run(CHECK)
    machine.tools("git", "uv", "claude", "clash")
    return machine.run(SETUP)


# --- Platforms --------------------------------------------------------------------------------


# @spec PAR-PLAT-002
@pytest.mark.parametrize("script", PYTHON_SCRIPTS, ids=SCRIPT_IDS)
@pytest.mark.parametrize(
    "platform",
    [("Darwin", "arm64"), ("Windows", "AMD64"), ("Linux", "riscv64"), ("Linux", "armv7l")],
    ids=["macos", "windows", "riscv", "arm32"],
)
def test_scripts_stop_on_an_unsupported_platform(
    tmp_path: Path, script: Path, platform: tuple[str, str]
) -> None:
    """Each script exits 2 naming the platform, before reading the config file or writing."""
    machine = Machine(tmp_path)
    run_ready(machine, script)  # lays out the machine; the run itself is discarded
    machine.platform = platform
    machine.write_config("not = [valid toml\n")
    before = snapshot(machine.home)
    result = (
        machine.run(INSTALLER, str(machine.cwd / "orca-linux.AppImage"), "--tag", TAG)
        if script == INSTALLER
        else machine.run(script, *(["--apply"] if script == SETUP else []))
    )
    assert result.returncode == 2, result.output
    system_names = {platform[0], FRIENDLY_SYSTEMS.get(platform[0], platform[0])}
    assert any(name in result.output for name in system_names), result.output
    assert platform[1] in result.output
    assert "config.toml" not in result.output
    assert result.events("request") == []
    assert snapshot(machine.home) == before


# @spec PAR-PLAT-002
@pytest.mark.parametrize("script", PYTHON_SCRIPTS, ids=SCRIPT_IDS)
@pytest.mark.parametrize("machine_name", ["x86_64", "amd64", "aarch64", "arm64"])
def test_scripts_accept_each_name_of_a_supported_architecture(
    tmp_path: Path, script: Path, machine_name: str
) -> None:
    """Linux on any reported name of x86_64 or arm64 is supported."""
    machine = Machine(tmp_path, platform=("Linux", machine_name))
    if script == INSTALLER:
        # The fixture release is served under the canonical name's manifest.
        canonical = "aarch64" if machine_name in {"aarch64", "arm64"} else "x86_64"
        machine.platform = ("Linux", canonical)
        release = serve_release(machine)
        machine.platform = ("Linux", machine_name)
        result = machine.run(INSTALLER, str(release.package), "--tag", TAG)
    else:
        result = run_ready(machine, script)
    assert result.returncode == 0, result.output


# Values of the platform table that only the table should hold.
PLATFORM_FACTS = (
    "latest-linux.yml",
    "latest-linux-arm64.yml",
    "orca-linux.AppImage",
    "orca-linux-arm64.AppImage",
    "orca.desktop",
    "profile-state.db",
    "resources/build/icon.png",
    "orca-ide",
    "Applications/orca",
)


# @spec PAR-PLAT-001
@pytest.mark.parametrize("fact", PLATFORM_FACTS)
def test_each_platform_fact_is_held_in_one_place(fact: str) -> None:
    """Each platform-specific value appears in exactly one of the Python files under the tool."""
    holders = [path.name for path in sorted(TOOLS.glob("*.py")) if fact in path.read_text()]
    assert len(holders) == 1, f"{fact!r} appears in {holders}"


# --- Config file ----------------------------------------------------------------------------


# @spec PAR-CONF-001
def test_check_expands_a_tilde_install_directory(tmp_path: Path) -> None:
    """The settings check reads `install_dir = "~/opt/orca"` as under the home directory."""
    machine = Machine(tmp_path, processes=[])
    good_check_machine(machine)
    machine.install_dir.rename(machine.home / "orca-elsewhere")
    machine.write_config('install_dir = "~/orca-elsewhere"\n')
    result = machine.run(CHECK)
    assert result.returncode == 0, result.output


# @spec PAR-CONF-001, PAR-CHECK-006
def test_config_and_orca_data_follow_an_absolute_xdg_config_home(tmp_path: Path) -> None:
    """With `XDG_CONFIG_HOME` elsewhere, the config file and Orca's data are read from there."""
    machine = Machine(tmp_path, processes=[])
    good_check_machine(machine)
    elsewhere = tmp_path / "xdg-config"
    (machine.home / ".config").rename(elsewhere)
    machine.env["XDG_CONFIG_HOME"] = str(elsewhere)
    # A config file read from the right place makes the 3-day update delay a difference.
    (elsewhere / "parallel-sessions").mkdir()
    (elsewhere / "parallel-sessions" / "config.toml").write_text("min_release_age_days = 7\n")
    result = machine.run(CHECK)
    assert result.returncode == 1, result.output
    assert "updateDelayDays" in result.output


# @spec PAR-CONF-001
def test_a_relative_xdg_config_home_is_ignored(tmp_path: Path) -> None:
    """A relative `XDG_CONFIG_HOME` falls back to `~/.config` for the config file."""
    machine = Machine(tmp_path)
    machine.tools("git", "uv", "claude", "clash")
    machine.write_config('install_dir = "~/from-home-config"\n')
    machine.env["XDG_CONFIG_HOME"] = "relative-config"
    relative = machine.cwd / "relative-config" / "parallel-sessions"
    relative.mkdir(parents=True)
    (relative / "config.toml").write_text('install_dir = "~/from-relative-config"\n')
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    text = (machine.home / ".local" / "bin" / "orca-launch").read_text()
    assert "from-home-config" in text
    assert "from-relative-config" not in text


# @spec PAR-CONF-002
@pytest.mark.parametrize("script", PYTHON_SCRIPTS, ids=SCRIPT_IDS)
@pytest.mark.parametrize(
    "problem", ["invalid-toml", pytest.param("unreadable", marks=requires_non_root)]
)
def test_scripts_stop_on_a_config_file_they_cannot_read(
    tmp_path: Path, script: Path, problem: str
) -> None:
    """An unreadable or malformed config file stops each script with status 2, naming it."""
    machine = Machine(tmp_path, processes=[])
    if problem == "invalid-toml":
        machine.write_config("install_dir = \n")
    else:
        machine.write_config('install_dir = "~/x"\n')
        machine.config_file.chmod(0)
    result = run_ready(machine, script)
    assert result.returncode == 2, result.output
    assert "config.toml" in result.output


# @spec PAR-CONF-003
@pytest.mark.parametrize("script", PYTHON_SCRIPTS, ids=SCRIPT_IDS)
def test_scripts_stop_on_an_unknown_key(tmp_path: Path, script: Path) -> None:
    """A key other than the two known ones stops each script, naming the key."""
    machine = Machine(tmp_path, processes=[])
    machine.write_config("install_directory = '/opt/orca'\n")
    result = run_ready(machine, script)
    assert result.returncode == 2, result.output
    assert "install_directory" in result.output


# @spec PAR-CONF-004, PAR-CONF-005
@pytest.mark.parametrize("script", PYTHON_SCRIPTS, ids=SCRIPT_IDS)
@pytest.mark.parametrize(
    ("line", "key"),
    [
        ('install_dir = "relative/orca"', "install_dir"),
        ("install_dir = 5", "install_dir"),
        ('install_dir = "~other/orca"', "install_dir"),
        ("min_release_age_days = -1", "min_release_age_days"),
        ("min_release_age_days = 1.5", "min_release_age_days"),
        ("min_release_age_days = true", "min_release_age_days"),
        ('min_release_age_days = "3"', "min_release_age_days"),
    ],
    ids=["relative", "not-string", "other-user", "negative", "float", "boolean", "string"],
)
def test_scripts_stop_on_a_value_of_the_wrong_kind(
    tmp_path: Path, script: Path, line: str, key: str
) -> None:
    """A relative or non-string `install_dir`, or a non-integer or negative age, stops a script."""
    machine = Machine(tmp_path, processes=[])
    machine.write_config(line + "\n")
    result = run_ready(machine, script)
    assert result.returncode == 2, result.output
    assert key in result.output


# @spec PAR-CONF-001, PAR-CONF-004
@pytest.mark.parametrize("value", ["~", "~/"])
def test_a_bare_tilde_install_directory_is_the_home_directory(tmp_path: Path, value: str) -> None:
    """`install_dir = "~"` (or `"~/"`) is the home directory, an absolute path."""
    machine = Machine(tmp_path)
    machine.tools("git", "uv", "claude", "clash")
    machine.write_config(f'install_dir = "{value}"\n')
    result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    text = (machine.home / ".local" / "bin" / "orca-launch").read_text()
    home = str(machine.home)
    assert any(f"{q}{home}{end}{q}" in text for q in "'\"" for end in ("", "/")), text


# @spec PAR-CONF-006, PAR-ALL-002
@pytest.mark.parametrize("script", PYTHON_SCRIPTS, ids=SCRIPT_IDS)
def test_scripts_name_every_config_problem(tmp_path: Path, script: Path) -> None:
    """Several problems in the config file are all named in one run."""
    machine = Machine(tmp_path, processes=[])
    machine.write_config(
        """\
        install_dir = "relative"
        min_release_age_days = -2
        colour = "blue"
        """
    )
    result = run_ready(machine, script)
    assert result.returncode == 2, result.output
    for key in ("install_dir", "min_release_age_days", "colour"):
        assert key in result.output, key


# @spec PAR-CONF-007
@pytest.mark.parametrize("script", PYTHON_SCRIPTS, ids=SCRIPT_IDS)
@pytest.mark.parametrize("exists", [False, True], ids=["absent", "present"])
def test_scripts_never_write_the_config_file(tmp_path: Path, script: Path, *, exists: bool) -> None:
    """No script creates the config file, or changes one that exists."""
    machine = Machine(tmp_path, processes=[])
    if exists:
        machine.write_config("min_release_age_days = 3\n")
    before = (
        (snapshot(machine.config_file.parent), machine.config_file.stat().st_mtime_ns)
        if exists
        else None
    )
    result = run_ready(machine, script)
    if script == SETUP:
        result = machine.run(SETUP, "--apply")
    assert result.returncode == 0, result.output
    if before is not None:
        after = (snapshot(machine.config_file.parent), machine.config_file.stat().st_mtime_ns)
        assert after == before
    else:
        assert not machine.config_file.parent.exists()


# --- Exit statuses --------------------------------------------------------------------------


# @spec PAR-ALL-001
@requires_non_root
def test_setup_exits_with_the_highest_status_that_applies(tmp_path: Path) -> None:
    """A skipped Clash entry (1) alongside a failed write (2) exits 2."""
    machine = Machine(tmp_path)
    machine.tools("git", "uv", "claude")
    applications = machine.home / ".local" / "share" / "applications"
    applications.mkdir(parents=True)
    applications.chmod(0o555)
    try:
        result = machine.run(SETUP, "--apply")
    finally:
        applications.chmod(0o755)
    assert result.returncode == 2, result.output
    assert re.search("mise use -g", result.output)
