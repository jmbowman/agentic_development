"""Tests of the task-tracker skill's task tool against its specs, on backlogs built in tmp_path."""

from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest

from tests.support import TASK_TOOL, load_task_tool, require_tool, small_backlog

if TYPE_CHECKING:
    from pathlib import Path

tasks = load_task_tool()

# The interpreter the project venv was made from, so a dev dependency can't satisfy an import.
BASE_PYTHON = getattr(sys, "_base_executable", sys.executable)
# Every command but `help`, with the arguments that make it run on `small_backlog`.
COMMANDS = [["check"], ["next", "--for", "agent"], ["why", "EX-1"], ["board"], ["brief"]]
COMMAND_IDS = [command[0] for command in COMMANDS]


def files_under(root: Path) -> set[Path]:
    """Every file under a directory, so a test can see whether a command wrote one."""
    return {path for path in root.rglob("*") if path.is_file()}


def run(
    command: list[str], cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Run a command in `cwd`, failing the test if it printed a Python traceback."""
    result = subprocess.run(  # noqa: S603
        command, cwd=cwd, env=env, capture_output=True, text=True, check=False
    )
    output = result.stdout + result.stderr
    assert "Traceback (most recent call last)" not in output, output
    return result


def tool_arguments(backlog: Path, command: list[str]) -> list[str]:
    """The tool's arguments for one command on a backlog, offline so no run asks GitHub."""
    return ["--offline", "--root", str(backlog), *command]


# @spec TASK-CMD-017
@pytest.mark.parametrize("private", [False, True], ids=["public", "private"])
def test_board_prints_markdown_and_writes_no_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    *,
    private: bool,
) -> None:
    """`board` prints one Markdown page to standard output, and leaves the backlog as it was.

    `--offline` keeps the GitHub lookup, the one writer TASK-LAYOUT-010 allows, out of the run.
    """
    backlog = small_backlog(tmp_path)
    (backlog / "private" / "outbox").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    before = files_under(tmp_path)
    options = ["--private"] if private else []
    assert tasks.main(["--root", str(backlog), "--offline", *options, "board"]) == 0
    shown = capsys.readouterr().out
    assert shown.startswith("# ")
    assert "EX-1" in shown
    assert files_under(tmp_path) == before


# --- Reading YAML ------------------------------------------------------------------------------


def write_task(backlog: Path, frontmatter: str) -> Path:
    """Write one task file, EX-2, with the given frontmatter text."""
    path = backlog / "tasks" / "ex-2 - Second.md"
    path.write_text(f"---\n{frontmatter}---\n\nA task.\n", encoding="utf-8")
    return path


def limit_values(limits: object) -> dict[str, object]:
    """A `oneyaml.Limits` as its fields, since it doesn't define equality."""
    return {name: getattr(limits, name) for name in getattr(type(limits), "__slots__")}  # noqa: B009


# @spec TASK-YAML-001
def test_every_yaml_document_is_parsed_with_the_untrusted_limits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The settings and focus files, a task, a draft and a milestone go through `oneyaml.loads`.

    The board reads milestones itself, outside `load`, so the test builds the board too.
    """
    backlog = small_backlog(tmp_path)
    (backlog / "focus.yml").write_text("pins: [EX-1]\n", encoding="utf-8")
    (backlog / "outbox" / "other").mkdir(parents=True)
    draft = "title: A draft\nperformer: agent\ntarget: github.com/o/other\n"
    (backlog / "outbox" / "other" / "a-draft.md").write_text(f"---\n{draft}---\n", encoding="utf-8")
    (backlog / "milestones").mkdir()
    milestone = "id: m-1\ntitle: First milestone"
    (backlog / "milestones" / "m-1 - First.md").write_text(
        f"---\n{milestone}\n---\n", encoding="utf-8"
    )
    oneyaml = tasks.yaml_parser()
    real_loads = oneyaml.loads
    calls: list[tuple[str, dict[str, Any]]] = []

    def spy(data: str, **options: Any) -> object:  # noqa: ANN401
        calls.append((data, options))
        return real_loads(data, **options)

    monkeypatch.setattr(oneyaml, "loads", spy)
    loaded = tasks.load(backlog)
    tasks.resolve(loaded, lambda _ref: None)
    tasks.board(loaded, backlog)
    parsed = {data.strip() for data, _ in calls}
    assert (backlog / "config.yml").read_text(encoding="utf-8").strip() in parsed
    assert "pins: [EX-1]" in parsed
    assert draft.strip() in parsed
    assert milestone in parsed
    assert any(data.startswith("id: EX-1") for data in parsed)
    untrusted = limit_values(oneyaml.Limits.untrusted())
    assert all(set(options) == {"limits"} for _, options in calls), calls
    assert all(limit_values(options["limits"]) == untrusted for _, options in calls)


# An alias expansion of 300,000 nodes: within oneyaml's default limit, beyond the untrusted one.
ALIAS_BOMB = """\
a: &a [x, x, x, x, x, x, x, x, x, x]
b: &b [*a, *a, *a, *a, *a, *a, *a, *a, *a, *a]
c: &c [*b, *b, *b, *b, *b, *b, *b, *b, *b, *b]
d: &d [*c, *c, *c, *c, *c, *c, *c, *c, *c, *c]
e: &e [*d, *d, *d, *d, *d, *d, *d, *d, *d, *d]
f: [*e, *e, *e]
"""


# @spec TASK-YAML-001, TASK-YAML-003
@pytest.mark.parametrize(
    ("frontmatter", "reason"),
    [("id: EX-2\ntitle: [unclosed\n", "syntax"), (f"id: EX-2\n{ALIAS_BOMB}", "limit")],
    ids=["syntax", "limit"],
)
def test_frontmatter_the_parser_rejects_is_reported(
    tmp_path: Path, frontmatter: str, reason: str
) -> None:
    """Bad syntax, or more than the untrusted limits allow, leaves the task out and lints it."""
    backlog = small_backlog(tmp_path)
    path = write_task(backlog, frontmatter)
    oneyaml = tasks.yaml_parser()
    if reason == "limit":  # the document is valid YAML that only the untrusted limits refuse
        assert oneyaml.loads(frontmatter)["f"]
    loaded = tasks.load(backlog)
    assert "EX-2" not in loaded.tasks
    assert any(problem.startswith(f"{path.name}: ") for problem in loaded.problems)


# @spec TASK-YAML-003
@pytest.mark.parametrize("error", [RuntimeError, ValueError])
def test_other_exceptions_while_parsing_propagate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error: type[Exception]
) -> None:
    """Only the parser's own errors mark a document as unparseable; anything else is a bug.

    `oneyaml.YAMLError` subclasses `ValueError`, so catching `ValueError` would fail this.
    """
    backlog = small_backlog(tmp_path)
    oneyaml = tasks.yaml_parser()

    def broken(_data: str, **_options: object) -> object:
        message = "a bug, not bad YAML"
        raise error(message)

    monkeypatch.setattr(oneyaml, "loads", broken)
    with pytest.raises(error, match="a bug"):
        tasks.load(backlog)


# @spec TASK-YAML-002
@pytest.mark.parametrize(
    ("written", "read"),
    [
        ("2026-11-30", "2026-11-30"),
        ("yes", "yes"),
        ("no", "no"),
        ("on", "on"),
        ("off", "off"),
        ("true", True),
        ("False", False),
    ],
)
def test_yaml_is_read_under_the_yaml_1_2_core_schema(
    tmp_path: Path, written: str, read: object
) -> None:
    """Unquoted dates and YAML 1.1's yes/no/on/off stay strings; the core booleans don't."""
    backlog = small_backlog(tmp_path)
    write_task(backlog, f"id: EX-2\ntitle: Second\nvalue: {written}\n")
    value = tasks.load(backlog).tasks["EX-2"].meta["value"]
    assert value == read
    assert type(value) is type(read)


def copy_tool_without_parser(tmp_path: Path) -> Path:
    """A copy of the tool with no `_vendor/` beside it, so the parser can't be imported."""
    script = tmp_path / "skill" / "scripts" / "tasks.py"
    script.parent.mkdir(parents=True)
    shutil.copy2(TASK_TOOL, script)
    return script


# @spec TASK-YAML-004
@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_a_missing_parser_stops_every_command_with_one_line(
    tmp_path: Path, command: list[str]
) -> None:
    """Without the vendored parser, each command names the problem on one line and exits 2."""
    script = copy_tool_without_parser(tmp_path)
    backlog = small_backlog(tmp_path)
    result = run([BASE_PYTHON, "-I", str(script), *tool_arguments(backlog, command)], tmp_path)
    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stdout == ""
    assert len(result.stderr.splitlines()) == 1, result.stderr
    assert "oneyaml" in result.stderr


# @spec TASK-YAML-004
@pytest.mark.parametrize(
    "module_text",
    ["def broken(:\n", "raise RuntimeError('broken at import')\n"],
    ids=["syntax-error", "runtime-error"],
)
def test_a_parser_that_fails_to_import_stops_with_one_line(
    tmp_path: Path, module_text: str
) -> None:
    """Any exception while importing the parser, not only a missing module, is a setup error.

    A newer upstream using syntax this Python lacks fails with `SyntaxError`, for example.
    """
    script = copy_tool_without_parser(tmp_path)
    package = script.parent / "_vendor" / "oneyaml-python" / "src" / "oneyaml"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(module_text, encoding="utf-8")
    backlog = small_backlog(tmp_path)
    command = [BASE_PYTHON, "-I", str(script), *tool_arguments(backlog, ["check"])]
    result = run(command, tmp_path)
    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stdout == ""
    assert len(result.stderr.splitlines()) == 1, result.stderr
    assert "oneyaml" in result.stderr


# @spec TASK-YAML-006
def test_help_works_without_the_parser(tmp_path: Path) -> None:
    """`help` never imports the parser, so it works where the parser is missing."""
    script = copy_tool_without_parser(tmp_path)
    result = run([BASE_PYTHON, "-I", str(script), "help"], tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "check" in result.stdout


def old_python(tmp_path: Path) -> str:
    """A Python 3.10 interpreter.

    When uv has none, it installs one into its own Python directory, outside the test's
    temporary directory, as `uv run --python` would.
    """
    find = [require_tool("uv"), "python", "find", "--no-project", "3.10"]
    result = run(find, tmp_path)
    if result.returncode != 0:
        install = run([require_tool("uv"), "python", "install", "3.10"], tmp_path)
        assert install.returncode == 0, install.stderr
        result = run(find, tmp_path)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


# @spec TASK-YAML-004
@pytest.mark.network
@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_an_old_interpreter_stops_every_command_with_one_line(
    tmp_path: Path, command: list[str]
) -> None:
    """Started directly by Python 3.10, each command names the problem on one line and exits 2."""
    backlog = small_backlog(tmp_path)
    arguments = tool_arguments(backlog, command)
    result = run([old_python(tmp_path), "-I", str(TASK_TOOL), *arguments], tmp_path)
    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stdout == ""
    assert len(result.stderr.splitlines()) == 1, result.stderr
    assert "3.11" in result.stderr


# @spec TASK-YAML-006
@pytest.mark.network
def test_help_works_on_an_old_interpreter(tmp_path: Path) -> None:
    """`help` checks neither the interpreter's version nor the parser."""
    result = run([old_python(tmp_path), "-I", str(TASK_TOOL), "help"], tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "check" in result.stdout


# @spec TASK-YAML-005
def test_the_parser_is_imported_with_the_pure_backend_set() -> None:
    """The tool sets `pure` in its own environment, so the pure backend is the one running."""
    oneyaml = tasks.yaml_parser()
    assert os.environ["ONEYAML_BACKEND"] == "pure"
    assert oneyaml.backend == "pure"


# @spec TASK-YAML-005
@pytest.mark.parametrize("backend", ["native", "bogus"])
def test_the_backend_setting_found_in_the_environment_is_overridden(
    tmp_path: Path, backend: str
) -> None:
    """`native` (not vendored) or an invalid value would stop the import; the tool sets `pure`."""
    backlog = small_backlog(tmp_path)
    env = {"PATH": "/usr/bin:/bin", "ONEYAML_BACKEND": backend}
    command = [BASE_PYTHON, "-I", str(TASK_TOOL), *tool_arguments(backlog, ["check"])]
    result = run(command, tmp_path, env)
    assert result.returncode == 0, result.stdout + result.stderr


# @spec TASK-YAML-007
def test_the_vendored_parser_wins_over_an_installed_one(tmp_path: Path) -> None:
    """Another `oneyaml` earlier on the import path is never the one imported."""
    installed = tmp_path / "site" / "oneyaml"
    installed.mkdir(parents=True)
    (installed / "__init__.py").write_text(
        "raise SystemExit('the installed oneyaml was imported')\n", encoding="utf-8"
    )
    backlog = small_backlog(tmp_path)
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(installed.parent)}
    # Not isolated with -I, which would ignore PYTHONPATH; -s still leaves user site-packages out.
    command = [BASE_PYTHON, "-s", str(TASK_TOOL), *tool_arguments(backlog, ["check"])]
    result = run(command, tmp_path, env)
    assert result.returncode == 0, result.stdout + result.stderr


# --- Running on the standard library alone -----------------------------------------------------


# @spec TASK-SKILL-032
@pytest.mark.parametrize("command", [*COMMANDS, ["help"]], ids=[*COMMAND_IDS, "help"])
def test_every_command_runs_isolated_on_the_base_interpreter(
    tmp_path: Path, command: list[str]
) -> None:
    """With `-I` on the venv's base interpreter, only the standard library and `_vendor/` exist."""
    backlog = small_backlog(tmp_path)
    result = run([BASE_PYTHON, "-I", str(TASK_TOOL), *tool_arguments(backlog, command)], tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout


# @spec TASK-SKILL-032
def test_the_tool_imports_only_the_standard_library_and_the_parser() -> None:
    """Every import in the tool, at any depth, names a standard-library module or `oneyaml`.

    An import by name at run time (`importlib.import_module`, `__import__`) would hide from
    this check, so the tool makes none.
    """
    tree = ast.parse(TASK_TOOL.read_text(encoding="utf-8"))
    dynamic = [
        ast.unparse(node)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and ast.unparse(node.func) in {"__import__", "importlib.import_module", "import_module"}
    ]
    assert not dynamic, dynamic
    modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    modules |= {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    tops = {module.split(".")[0] for module in modules}
    assert "oneyaml" in tops
    outside = sorted(tops - set(sys.stdlib_module_names) - {"__future__", "oneyaml"})
    assert not outside, outside


# @spec TASK-SKILL-003
@pytest.mark.network
def test_the_tool_runs_on_python_3_11(tmp_path: Path) -> None:
    """The oldest Python `requires-python` allows runs the tool, so the floor can't creep up."""
    backlog = small_backlog(tmp_path)
    uv = [require_tool("uv"), "run", "--no-project", "--python", "3.11", "--script"]
    result = run([*uv, str(TASK_TOOL), *tool_arguments(backlog, ["check"])], tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "no problems" in result.stdout
