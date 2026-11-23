"""What the parallel-sessions scripts share: the platform table, the config file, exit statuses.

Every platform-specific value lives in `PLATFORMS`, so supporting another platform adds a row
rather than changing the scripts. Each script imports this module from its own directory, where
`uv run --script` puts it on the import path.
"""

# @spec PAR-PLAT-001, PAR-PLAT-002, PAR-CONF-001, PAR-CONF-002, PAR-CONF-003, PAR-CONF-004
# @spec PAR-CONF-005, PAR-CONF-006, PAR-CONF-007

from __future__ import annotations

import os
import platform
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

# Exit statuses, in rising order of seriousness (PAR-ALL-001).
OK = 0
DIFFERS = 1
FAILED = 2

DEFAULT_MIN_RELEASE_AGE_DAYS = 3
CONFIG_KEYS = ("install_dir", "min_release_age_days")


def prepare_output() -> None:
    """Let output carry any text: a character the terminal's encoding lacks is escaped."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(errors="backslashreplace")


def say(text: str) -> None:
    """Print a line on standard output."""
    sys.stdout.write(f"{text}\n")


def complain(text: str) -> None:
    """Print a line on standard error."""
    sys.stderr.write(f"{text}\n")


class StopError(Exception):
    """A problem that ends a script at once, with its exit status."""

    def __init__(self, message: str, status: int = FAILED) -> None:
        """Hold the message to print and the status to exit with."""
        super().__init__(message)
        self.message = message
        self.status = status


@dataclass(frozen=True)
class Platform:
    """One supported platform's facts. Paths under the home directory are relative to it."""

    name: str
    manifest: str
    package: str
    default_install_dir: str
    launcher: str
    desktop_entry: str
    user_data: str
    profile_database: str
    icon_path: str
    process_name: str


_LINUX = {
    "default_install_dir": "Applications/orca",
    "launcher": ".local/bin/orca-launch",
    "desktop_entry": ".local/share/applications/orca.desktop",
    "user_data": "orca",  # under $XDG_CONFIG_HOME, default ~/.config
    "profile_database": "profile-state.db",
    "icon_path": "resources/build/icon.png",
    "process_name": "orca-ide",
}

PLATFORMS = {
    ("Linux", "x86_64"): Platform(
        name="Linux x86_64",
        manifest="latest-linux.yml",
        package="orca-linux.AppImage",
        **_LINUX,
    ),
    ("Linux", "arm64"): Platform(
        name="Linux arm64",
        manifest="latest-linux-arm64.yml",
        package="orca-linux-arm64.AppImage",
        **_LINUX,
    ),
}

# The names `platform.machine()` reports for each supported architecture.
ARCHITECTURES = {"x86_64": "x86_64", "amd64": "x86_64", "aarch64": "arm64", "arm64": "arm64"}


def current_platform() -> Platform:
    """Return this machine's row of the platform table.

    Raises:
        StopError: On a platform the table has no row for.
    """
    system = platform.system()
    machine = platform.machine()
    row = PLATFORMS.get((system, ARCHITECTURES.get(machine.lower(), "")))
    if row is None:
        supported = ", ".join(known.name for known in PLATFORMS.values())
        message = f"unsupported platform: {system} on {machine} (supported: {supported})"
        raise StopError(message)
    return row


def xdg_dir(variable: str, default: str) -> Path:
    """An XDG base directory: the variable when it holds an absolute path, else the default.

    Args:
        variable: The environment variable, such as `XDG_CONFIG_HOME`.
        default: The default, relative to the home directory.
    """
    value = os.environ.get(variable, "")
    if value and Path(value).is_absolute():
        return Path(value)
    return Path.home() / default


def config_dir() -> Path:
    """`$XDG_CONFIG_HOME`, or `~/.config`."""
    return xdg_dir("XDG_CONFIG_HOME", ".config")


@dataclass(frozen=True)
class Config:
    """The machine-level settings, with defaults for anything the config file doesn't set."""

    install_dir: Path
    min_release_age_days: int


def config_path() -> Path:
    """Where the config file is."""
    return config_dir() / "parallel-sessions" / "config.toml"


def _expand_install_dir(value: object, problems: list[str]) -> Path | None:
    if not isinstance(value, str):
        problems.append(f"install_dir: {value!r} isn't a string")
        return None
    if value == "~" or value.startswith("~/"):
        path = Path.home() / value[2:]
    elif value.startswith("~"):
        problems.append(f"install_dir: {value!r} names another user's home, which isn't supported")
        return None
    else:
        path = Path(value)
    if not path.is_absolute():
        problems.append(f"install_dir: {value!r} isn't an absolute path")
        return None
    return path


def load_config(row: Platform) -> Config:
    """Read the config file, never writing it.

    Args:
        row: The platform, for the default install directory.

    Raises:
        StopError: When the file can't be read or parsed, or has bad keys or values.
    """
    path = config_path()
    install_dir = Path.home() / row.default_install_dir
    min_age = DEFAULT_MIN_RELEASE_AGE_DAYS
    if not path.exists():
        return Config(install_dir, min_age)
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        message = f"can't read the config file {path}: {error}"
        raise StopError(message) from error
    except tomllib.TOMLDecodeError as error:
        message = f"the config file {path} isn't valid TOML: {error}"
        raise StopError(message) from error
    problems = [f"unknown key {key!r}" for key in data if key not in CONFIG_KEYS]
    if "install_dir" in data:
        install_dir = _expand_install_dir(data["install_dir"], problems) or install_dir
    if "min_release_age_days" in data:
        value = data["min_release_age_days"]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            problems.append(f"min_release_age_days: {value!r} isn't a non-negative integer")
        else:
            min_age = value
    if problems:
        listed = "\n".join(f"  * {problem}" for problem in problems)
        message = f"the config file {path} has problems:\n{listed}"
        raise StopError(message)
    return Config(install_dir, min_age)
