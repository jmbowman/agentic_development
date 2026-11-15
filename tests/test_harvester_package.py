"""Structure tests of the harvester's packaging: its pins, lock file, Renovate manager and docs."""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from typing import TYPE_CHECKING, Any

import pytest

from tests.harvester_support import HARVEST
from tests.support import REPO_ROOT, SKILLS

if TYPE_CHECKING:
    from pathlib import Path

SKILL = SKILLS / "prior-art-search"
LOCK = HARVEST.with_name("harvest.py.lock")
HARVESTER_MD = SKILL / "references" / "harvester.md"
RENOVATE = REPO_ROOT / ".github" / "renovate.json"
FORK = "https://github.com/jmbowman/paper-search-mcp"
PIN = re.compile(r"paper-search-mcp\s*@\s*git\+" + re.escape(FORK) + r"@([0-9a-f]{40})")


def script_metadata(path: Path) -> dict[str, Any]:
    """The PEP 723 `script` block of a file, parsed as TOML.

    Args:
        path: The script.

    Returns:
        The block's settings.
    """
    text = path.read_text()
    match = re.search(r"^# /// script$\s(?P<body>(?:^#(?:| .*)$\s)+)^# ///$", text, re.MULTILINE)
    assert match, f"no PEP 723 block in {path}"
    body = "".join(
        line[2:] if line.startswith("# ") else line[1:]
        for line in match["body"].splitlines(keepends=True)
    )
    return tomllib.loads(body)


def fork_pins(dependencies: object) -> list[str]:
    """The fork commits pinned in a list of dependency specifiers.

    Args:
        dependencies: The specifiers.

    Returns:
        Each pinned commit SHA.
    """
    assert isinstance(dependencies, list)
    return [m[1] for d in dependencies if (m := PIN.fullmatch(str(d).strip()))]


def header_pin() -> str:
    """The fork commit that the harvester's header pins.

    Returns:
        The commit SHA.
    """
    pins = fork_pins(script_metadata(HARVEST)["dependencies"])
    assert len(pins) == 1, pins
    return pins[0]


# @spec PRIOR-SCR-001
def test_script_header_and_lock() -> None:
    """The header needs Python 3.11 and pins one fork commit; the lock file sits beside it."""
    assert script_metadata(HARVEST)["requires-python"] == ">=3.11"
    assert re.fullmatch(r"[0-9a-f]{40}", header_pin())
    assert LOCK.is_file()


# @spec PRIOR-SCR-002
def test_dev_group_pins_the_same_fork_commit() -> None:
    """This repo's dev dependencies test the same fork commit the script runs."""
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    assert fork_pins(pyproject["dependency-groups"]["dev"]) == [header_pin()]


@pytest.mark.network
# @spec PRIOR-SCR-003
def test_script_lock_is_current(tmp_path: Path) -> None:
    """`uv lock --script --check` passes, so CI fails on a stale lock."""
    result = subprocess.run(  # noqa: S603
        ["uv", "lock", "--script", str(HARVEST), "--check"],  # noqa: S607
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def _js_regex(pattern: str) -> re.Pattern[str]:
    """A Renovate regex (JavaScript syntax, slashes optional) as a Python pattern."""
    if pattern.startswith("/") and pattern.endswith("/"):
        pattern = pattern[1:-1]
    python = pattern.replace("(?<", "(?P<").replace("(?P<=", "(?<=").replace("(?P<!", "(?<!")
    return re.compile(python)


# @spec PRIOR-SCR-004
@pytest.mark.parametrize("target", ["skills/prior-art-search/scripts/harvest.py", "pyproject.toml"])
def test_renovate_bumps_the_fork_commit(target: str) -> None:
    """One git-refs manager on the fork's integration branch finds the pin in both files."""
    config = json.loads(RENOVATE.read_text())
    managers = [
        m
        for m in config.get("customManagers", [])
        if m.get("datasourceTemplate") == "git-refs"
        and FORK in m.get("packageNameTemplate", "") + m.get("depNameTemplate", "")
    ]
    assert len(managers) == 1
    (manager,) = managers
    assert manager.get("currentValueTemplate") == "integration"
    assert any(_js_regex(p).search(target) for p in manager["managerFilePatterns"])
    text = (REPO_ROOT / target).read_text()
    digests = {
        m["currentDigest"] for p in manager["matchStrings"] for m in _js_regex(p).finditer(text)
    }
    assert digests == {header_pin()}


# @spec PRIOR-SCR-005
def test_harvester_reference_doc() -> None:
    """The reference gives the command, its options, its files and its exit statuses."""
    text = HARVESTER_MD.read_text()
    assert "uv run --script" in text
    for option in ("--service", "--round", "--run-dir", "--max-results", "--show"):
        assert option in text
    for name in ("queries.jsonl", "records.jsonl", "ledger.jsonl", "harvest.log", "raw/"):
        assert name in text
    statuses = re.findall(r"^\|\s*`([0-9])`\s*\|", text, re.MULTILINE)
    assert statuses == ["0", "3", "4"]
    assert "references/harvester.md" in (SKILL / "SKILL.md").read_text()


@pytest.mark.network
# @spec PRIOR-SCR-011, PRIOR-SCR-092
def test_script_runs_under_uv_and_exits_4_on_bad_arguments(tmp_path: Path) -> None:
    """Run as uv runs it, a bad service exits 4 and writes nothing."""
    run_dir = tmp_path / "run"
    argv = ["search", "--service", "nope", "--round", "1", "--run-dir", str(run_dir), "q"]
    result = subprocess.run(  # noqa: S603
        ["uv", "run", "--script", str(HARVEST), *argv],  # noqa: S607
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 4, result.stderr
    assert not (run_dir / "queries.jsonl").exists()
