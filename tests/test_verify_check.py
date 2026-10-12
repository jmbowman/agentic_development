"""Unit tests of the verification script's logic, with mise replaced by a lookup table."""

from __future__ import annotations

import ast
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest

from scripts import verify_check
from tests.support import REPO_ROOT

if TYPE_CHECKING:
    from pathlib import Path

CONF_D = "/repo/.config/mise/conf.d/"
FRAGMENT = CONF_D + "checks.toml"


def lookup_from(tasks: dict[str, dict[str, Any]]) -> verify_check.Lookup:
    """Build a task lookup that answers from a table, failing like mise for unknown tasks."""

    def lookup(name: str) -> dict[str, Any]:
        if name not in tasks:
            msg = f"mise ERROR no task {name} found"
            raise verify_check.TaskLookupError(msg)
        defaults = {"name": name, "aliases": [], "source": FRAGMENT, "run": []}
        return {**defaults, "depends": [], "depends_post": [], **tasks[name]}

    return lookup


def violations(tasks: dict[str, dict[str, Any]]) -> list[str]:
    """Run the walk against a table of tasks."""
    return verify_check.find_violations(lookup_from(tasks), (CONF_D,))


# @spec CHECK-RUN-009
def test_valid_dependency_forms_are_followed() -> None:
    """Each form mise emits leads the walk to the named task."""
    outside = {"source": "/repo/mise.toml"}
    tasks = {
        "check": {"depends": ["a", "b --flag", ["c", "-x"], {"task": "d", "args": []}]},
        "a": outside,
        "b": outside,
        "c": outside,
        "d": outside,
    }
    found = violations(tasks)
    assert [line.split('"')[1] for line in found] == ["a", "b", "c", "d"], found


# @spec CHECK-RUN-009
@pytest.mark.parametrize("entry", ["", [], [1], [""], {"task": ""}, {"name": "a"}, 5, None])
def test_unrecognized_dependency_forms_fail(entry: object) -> None:
    """A dependency in any other form fails verification instead of being skipped."""
    found = violations({"check": {"depends": [entry]}})
    assert len(found) == 1
    assert "unrecognized depends entry" in found[0]


# @spec CHECK-RUN-010
def test_missing_dependency_is_named_with_mises_error() -> None:
    """A dependency mise can't look up is named, with mise's own error output."""
    found = violations({"check": {"depends": ["gone"]}})
    assert found == ['error: dependency "gone" was not found: mise ERROR no task gone found']


def test_missing_check_task_is_reported() -> None:
    """With no `check` task, the walk stops with the standard message."""
    found = violations({})
    assert len(found) == 1
    assert 'no "check" task' in found[0]


# @spec CHECK-RUN-011
def test_every_violation_is_reported() -> None:
    """The walk continues past each violation and reports them all."""
    tasks = {
        "check": {"depends": ["lint", "test", "x:*", "gone"], "depends_post": ["post"]},
        "lint": {"source": "/repo/mise.toml"},
        "test": {"source": "/repo/.config/mise/config.toml"},
        "post": {"source": "/repo/mise.toml"},
    }
    found = violations(tasks)
    assert len(found) == 5, found
    for name in ("lint", "test", "x:*", "gone", "post"):
        assert any(f'"{name}"' in line for line in found), name


# @spec CHECK-RUN-007
def test_extra_tasks_are_not_descended() -> None:
    """A `-extra` task and what only it reaches are skipped."""
    tasks = {
        "check": {"depends": ["check-extra"]},
        "check-extra": {"source": "/repo/mise.toml", "depends": ["own"]},
    }
    assert violations(tasks) == []


# @spec CHECK-RUN-012
def test_output_without_a_source_is_a_violation() -> None:
    """Task info with no string `source` fails verification and names the task."""
    found = violations({"check": {"depends": ["a"]}, "a": {"source": None}})
    assert found == ['error: mise\'s report for task "a" is unreadable: it has no source path.']


# @spec CHECK-RUN-012
def test_unreadable_mise_output_is_a_violation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Output from mise that isn't a JSON object names the task as unreadable."""
    for stdout in ("not json", "[1, 2]"):
        completed = subprocess.CompletedProcess([], 0, stdout=stdout, stderr="")
        monkeypatch.setattr(verify_check.subprocess, "run", lambda *_, out=completed, **__: out)
        found = verify_check.find_violations(verify_check.mise_lookup, (CONF_D,))
        assert len(found) == 1, stdout
        assert 'task "check" is unreadable' in found[0], stdout


# @spec CHECK-RUN-007
def test_tasks_referenced_from_run_are_checked() -> None:
    """Task references in `run` join the walk; plain scripts don't."""
    tasks = {
        "check": {"run": [{"task": "a --flag"}, {"tasks": ["b", "c x-extra"]}, "echo plain"]},
        "a": {},
        "b": {"source": "/repo/mise.toml"},
        "c": {"source": "/repo/mise.toml"},
    }
    found = violations(tasks)
    assert [line.split('"')[1] for line in found] == ["b", "c"], found


# @spec CHECK-RUN-009
@pytest.mark.parametrize(
    "fields",
    [
        {"depends": "a"},
        {"depends_post": {"task": "a"}},
        {"run": "echo"},
        {"run": [{"other": "a"}]},
        {"run": [{"tasks": ["a", 1]}]},
        {"run": [{"tasks": "a"}]},
        {"run": [{"task": ""}]},
        {"run": [5]},
    ],
)
def test_unrecognized_task_fields_fail(fields: dict[str, Any]) -> None:
    """A non-list field or an unfamiliar `run` entry fails verification."""
    found = violations({"check": fields, "a": {}})
    assert len(found) == 1, found
    assert "unrecognized" in found[0]


# @spec CHECK-RUN-008
@pytest.mark.parametrize("pattern", ["lint:*", "lint:?", "lint:[ab]", "lint:{a,b}"])
def test_pattern_dependencies_fail(pattern: str) -> None:
    """Any glob syntax in a dependency fails verification and names it."""
    found = violations({"check": {"depends": [pattern]}})
    assert found == [f'error: dependency "{pattern}" uses a pattern; list the tasks by name.']


# @spec CHECK-RUN-008
def test_a_task_reported_under_another_name_fails() -> None:
    """Mise resolving a dependency to a different task is a violation; an alias isn't."""
    tasks = {
        "check": {"depends": ["x", "short"]},
        "x": {"name": "y"},
        "short": {"name": "long-name", "aliases": ["short"]},
    }
    found = violations(tasks)
    assert len(found) == 1, found
    assert '"x"' in found[0]
    assert '"y"' in found[0]


# @spec CHECK-RUN-002
def test_main_accepts_the_logical_path_from_pwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`main` passes `$PWD` through, so a source under the logical path is accepted."""
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    source = f"{link}/.config/mise/conf.d/checks.toml"
    info = {"name": "check", "aliases": [], "source": source, "depends": [], "run": []}
    monkeypatch.setattr(verify_check, "mise_lookup", lambda _task: info)
    monkeypatch.chdir(link)
    monkeypatch.setenv("PWD", str(link))
    assert verify_check.main() == 0
    monkeypatch.delenv("PWD")
    assert verify_check.main() == 1


# @spec CHECK-RUN-002
def test_logical_path_is_allowed_when_it_names_the_directory(tmp_path: Path) -> None:
    """`$PWD` adds the logical prefix only when it resolves to the current directory."""
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    assert verify_check.allowed_prefixes(real, str(link)) == (
        f"{link}/.config/mise/conf.d/",
        f"{real}/.config/mise/conf.d/",
    )
    assert verify_check.allowed_prefixes(real, str(tmp_path)) == (f"{real}/.config/mise/conf.d/",)
    assert verify_check.allowed_prefixes(real, None) == (f"{real}/.config/mise/conf.d/",)


# @spec CHECK-013
def test_script_imports_only_the_standard_library() -> None:
    """The script needs no installed packages."""
    tree = ast.parse((REPO_ROOT / "scripts" / "verify_check.py").read_text())
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "relative imports need a package"
            modules.add(str(node.module).split(".")[0])
    assert modules
    assert modules <= sys.stdlib_module_names, modules - sys.stdlib_module_names


# @spec CHECK-RUN-007
@pytest.mark.parametrize("relative", ["../../../evil.toml", "./../x.toml", "sub/../../x.toml"])
def test_source_escaping_conf_d_through_dot_segments_fails(relative: str) -> None:
    """A source under conf.d's prefix that climbs out with `..` counts as outside."""
    found = violations({"check": {"source": CONF_D + relative}})
    assert found == [
        f'error: task "check" is defined in {CONF_D}{relative}, outside .config/mise/conf.d/.'
    ]


# @spec CHECK-RUN-008
def test_monorepo_root_names_match_plain_names() -> None:
    """In monorepo mode mise reports root tasks as `//:name`; that isn't a different task."""

    def lookup(name: str) -> dict[str, Any]:
        bare = name.removeprefix("//:").removeprefix(":")
        if bare not in {"check", "lint", "fmt"}:
            msg = f"no task {name}"
            raise verify_check.TaskLookupError(msg)
        depends = ["lint", "//:fmt", ":lint"] if bare == "check" else []
        return {"name": f"//:{bare}", "aliases": [], "source": FRAGMENT, "depends": depends}

    assert verify_check.find_violations(lookup, (CONF_D,)) == []


# @spec CHECK-RUN-008
def test_monorepo_prefix_does_not_hide_a_different_task() -> None:
    """Removing the root prefix still leaves a different task a violation."""
    found = violations({"check": {"depends": ["x"]}, "x": {"name": "//:y"}})
    assert found == ['error: dependency "x" resolved to task "//:y"; list tasks by name.']
