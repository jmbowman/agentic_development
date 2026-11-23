"""Tests of Orca's launcher, tools/parallel-sessions/orca-launch, run with a stand-in package."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

import pytest

from tests.parallel_sessions_support import LAUNCHER, Machine

if TYPE_CHECKING:
    from pathlib import Path

# A stand-in package: records its PID, arguments and telemetry variables, then exits with 7.
STAND_IN = """\
#!/bin/sh
{
  printf '{"pid": %s, "dnt": "%s", "otd": "%s", "args": [' "$$" "${DO_NOT_TRACK-unset}" \
"${ORCA_TELEMETRY_DISABLED-unset}"
  sep=''
  for arg in "$@"; do printf '%s"%s"' "$sep" "$arg"; sep=', '; done
  printf ']}\\n'
} > "$RECORD"
exit 7
"""


def stand_in(path: Path) -> Path:
    """Write the stand-in package at a path, executable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(STAND_IN)
    path.chmod(0o755)
    return path


def launch(
    machine: Machine, *args: str, env: dict[str, str] | None = None
) -> tuple[subprocess.CompletedProcess[str], int, Path]:
    """Run the launcher under `sh`, returning the result, the launcher's PID and the record path."""
    record = machine.root / "record.json"
    full_env = {**machine.env, "RECORD": str(record), **(env or {})}
    process = subprocess.Popen(  # noqa: S603 - sh running the repo's launcher
        ["/bin/sh", str(LAUNCHER), *args],
        cwd=machine.cwd,
        env=full_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        raise
    completed = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
    return completed, process.pid, record


# @spec PAR-LAUNCH-001
@pytest.mark.parametrize(
    "inherited",
    [{}, {"DO_NOT_TRACK": "0", "ORCA_TELEMETRY_DISABLED": "false"}],
    ids=["unset", "set-otherwise"],
)
def test_launcher_sets_both_telemetry_variables_to_1(
    tmp_path: Path, inherited: dict[str, str]
) -> None:
    """Both variables reach the package as `1`, whatever the environment held."""
    machine = Machine(tmp_path)
    package = stand_in(tmp_path / "pkg" / "orca.AppImage")
    result, _, record = launch(machine, env={"ORCA_APPIMAGE": str(package), **inherited})
    assert result.returncode == 7, result.stderr
    recorded = json.loads(record.read_text())
    assert (recorded["dnt"], recorded["otd"]) == ("1", "1")


# @spec PAR-LAUNCH-002
def test_launcher_execs_the_package_with_its_arguments(tmp_path: Path) -> None:
    """The package replaces the launcher's process, gets its arguments, and sets its status."""
    machine = Machine(tmp_path)
    package = stand_in(tmp_path / "pkg" / "orca.AppImage")
    args = ("--flag", "two words", "")
    result, pid, record = launch(machine, *args, env={"ORCA_APPIMAGE": str(package)})
    assert result.returncode == 7, result.stderr
    recorded = json.loads(record.read_text())
    assert recorded["pid"] == pid
    assert recorded["args"] == list(args)


# @spec PAR-LAUNCH-002
@pytest.mark.parametrize("orca_appimage", [None, ""], ids=["unset", "empty"])
def test_launcher_defaults_to_the_repo_install_directory(
    tmp_path: Path, orca_appimage: str | None
) -> None:
    """Without `$ORCA_APPIMAGE`, the repo's launcher runs the package in `~/Applications/orca`."""
    machine = Machine(tmp_path)
    stand_in(machine.install_dir / "orca.AppImage")
    env = {} if orca_appimage is None else {"ORCA_APPIMAGE": orca_appimage}
    result, _, record = launch(machine, env=env)
    assert result.returncode == 7, result.stderr
    assert record.exists()


# @spec PAR-LAUNCH-003
@pytest.mark.parametrize("problem", ["missing", "not-executable", "directory"])
def test_launcher_refuses_a_package_it_cannot_run(tmp_path: Path, problem: str) -> None:
    """A missing, non-executable or non-regular package stops the launcher with status 1."""
    machine = Machine(tmp_path)
    package = tmp_path / "pkg" / "orca.AppImage"
    if problem == "not-executable":
        stand_in(package).chmod(0o644)
    elif problem == "directory":
        package.mkdir(parents=True)
        (package / "AppRun").write_text("#!/bin/sh\n")
    result, _, record = launch(machine, env={"ORCA_APPIMAGE": str(package)})
    assert result.returncode == 1
    assert str(package) in result.stderr
    assert not record.exists()


# @spec PAR-LAUNCH-004
def test_launcher_is_a_posix_sh_script_needing_no_commands_on_path(tmp_path: Path) -> None:
    """The launcher starts with `#!/bin/sh` and runs with nothing on `PATH`: built-ins only."""
    assert LAUNCHER.read_text().splitlines()[0] == "#!/bin/sh"
    machine = Machine(tmp_path)  # PATH is an empty directory
    package = stand_in(tmp_path / "pkg" / "orca.AppImage")
    result, _, record = launch(machine, "x", env={"ORCA_APPIMAGE": str(package)})
    assert result.returncode == 7, result.stderr
    assert json.loads(record.read_text())["args"] == ["x"]
