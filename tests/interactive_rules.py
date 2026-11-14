"""Rules for interactive scenarios, spec markers, manual scripts and latest-results tables.

Each rule takes a repo root and returns its violations as messages, empty when the rule holds.
The rules read files only: `@spec` annotations as text lines, and `replaces` markers from each
scenario module's syntax tree, so they never import pytest-claude-code-evals.

Design: docs/intent/interactive-evals/interactive-evals-design.md
"""

from __future__ import annotations

import ast
import datetime as dt
import re
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# A LID spec ID: path segments, then a zero-padded three-digit number (`WRAP-RUN-008`).
SPEC_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)*-[0-9]{3}\b")
DIGITS = re.compile(r"[0-9]+")
UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")
FENCE = re.compile(r"^\s*(```|~~~)")
ANNOTATION = re.compile(r"^\s*#\s*@spec\s+(.+)$", flags=re.MULTILINE)
SPEC_LINE = re.compile(r"^- \[[ xD]\] \*\*([A-Z0-9-]+)\*\*:")
MARKER = re.compile(r"\*\(([^()]*)\)\*\s*$")
SEPARATOR_ROW = re.compile(r"^\|(?:\s*:?-+:?\s*\|)+$")
ISO_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
NOTES_SCENARIO_SKILL = "session-wrap-up"
INTERACTIVE = "interactive"
BOTH = "eval, interactive"
NEVER_RUN = "never run"
ROW_CELLS = 10


def skills(root: Path) -> list[str]:
    """The names of this repo's skills: directories in `skills/` that hold a `SKILL.md`."""
    return sorted(path.parent.name for path in (root / "skills").glob("*/SKILL.md"))


def module_name(skill: str) -> str:
    """A skill's name as it appears in its scenario modules' names."""
    return skill.replace("-", "_")


def scenario_modules(root: Path, skill: str) -> list[Path]:
    """A skill's scenario modules."""
    return sorted((root / "evals" / skill / "interactive").glob("test_*.py"))


def cited_ids(text: str) -> set[str]:
    """The spec IDs that the `@spec` annotation lines of a file's text cite."""
    return {spec for line in ANNOTATION.findall(text) for spec in SPEC_ID.findall(line)}


def scenario_citations(root: Path) -> set[str]:
    """Every spec ID a scenario module's annotations cite."""
    return {
        spec
        for skill in skills(root)
        for module in scenario_modules(root, skill)
        for spec in cited_ids(module.read_text())
    }


def eval_cases(root: Path, skill: str) -> list[Path]:
    """A skill's eval case directories: those under `evals/<skill>/` that hold a `case.yaml`."""
    base = root / "evals" / skill
    return sorted(
        path.parent
        for path in base.rglob("case.yaml")
        if not {"interactive", "results"} & set(path.relative_to(base).parts)
    )


def eval_citations(root: Path) -> set[str]:
    """Every spec ID an eval case's `case.yaml` cites."""
    return {
        spec
        for skill in skills(root)
        for case in eval_cases(root, skill)
        for spec in cited_ids((case / "case.yaml").read_text())
    }


def level_two_headings(text: str) -> list[str]:
    """The text of each `##` heading outside fenced code blocks, trailing whitespace removed."""
    headings: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        if opening := FENCE.match(line):
            marker = str(opening.group(1))
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
        elif fence is None and line.startswith("## "):
            headings.append(line[3:].rstrip())
    return headings


def manual_scripts(text: str) -> list[str]:
    """The headings of a `manual.md`'s manual scripts: `##` headings that name a spec ID."""
    return [heading for heading in level_two_headings(text) if SPEC_ID.search(heading)]


def manual_files(root: Path) -> list[Path]:
    """Every `evals/*/manual.md`."""
    return sorted((root / "evals").glob("*/manual.md"))


def script_names(root: Path) -> set[str]:
    """Every spec ID that a manual script names."""
    return {
        spec
        for path in manual_files(root)
        for heading in manual_scripts(path.read_text())
        for spec in SPEC_ID.findall(heading)
    }


def spec_markers(root: Path) -> dict[str, str | None]:
    """Each spec's marker text across every segment's specs file, `None` for an unmarked spec."""
    markers: dict[str, str | None] = {}
    for path in sorted((root / "docs" / "intent").glob("*/*-specs.md")):
        for line in path.read_text().splitlines():
            if spec := SPEC_LINE.match(line):
                marker = MARKER.search(line)
                markers[spec.group(1)] = marker.group(1) if marker else None
    return markers


# @spec IEVAL-LAY-001, IEVAL-LAY-002, IEVAL-LAY-003
def layout_violations(root: Path) -> list[str]:
    """Scenario module names, `conftest.py` annotations and where `NOTES-` scenarios live.

    Args:
        root: The repo root.

    Returns:
        One message per violation.
    """
    violations: list[str] = []
    for skill in skills(root):
        directory = root / "evals" / skill / "interactive"
        name = re.compile(rf"test_{re.escape(module_name(skill))}(?:_\w+)?\.py")
        for module in scenario_modules(root, skill):
            if not name.fullmatch(module.name):
                violations.append(f"IEVAL-LAY-001: {module} isn't named for {skill}")
            notes = sorted(s for s in cited_ids(module.read_text()) if s.startswith("NOTES-"))
            if notes and skill != NOTES_SCENARIO_SKILL:
                violations.append(f"IEVAL-LAY-003: {module} checks {notes} outside session-wrap-up")
        conftest = directory / "conftest.py"
        if conftest.is_file() and cited_ids(conftest.read_text()):
            violations.append(f"IEVAL-LAY-002: {conftest} has an @spec annotation")
    return violations


# @spec IEVAL-MARK-001, IEVAL-MARK-002, IEVAL-MARK-003
def marker_violations(root: Path) -> list[str]:
    """Spec markers against scenario citations, eval case citations and manual scripts.

    Args:
        root: The repo root.

    Returns:
        One message per violation.
    """
    by_scenario = scenario_citations(root)
    by_eval = eval_citations(root)
    named = script_names(root)
    violations: list[str] = []
    for spec, marker in spec_markers(root).items():
        cited, evaluated, scripted = spec in by_scenario, spec in by_eval, spec in named
        if marker == INTERACTIVE and not (cited and not evaluated and not scripted):
            violations.append(f"IEVAL-MARK-001: {spec} is marked ({marker}) but isn't only tested")
        elif marker == BOTH and not (cited and evaluated and not scripted):
            violations.append(f"IEVAL-MARK-002: {spec} is marked ({marker}) without both checks")
        elif cited and not scripted and marker not in {INTERACTIVE, BOTH, None}:
            violations.append(f"IEVAL-MARK-003: {spec} is tested but marked ({marker})")
    return violations


def is_pytest_mark(node: ast.expr) -> bool:
    """Whether an expression is `pytest.mark` (or `<alias>.mark`)."""
    return (
        isinstance(node, ast.Attribute) and node.attr == "mark" and isinstance(node.value, ast.Name)
    )


def pytest_mark_names(tree: ast.Module) -> set[str]:
    """Local names bound to `pytest.mark`, by `from pytest import mark` or `m = pytest.mark`."""
    names = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "pytest"
        for alias in node.names
        if alias.name == "mark"
    }
    names |= {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign) and is_pytest_mark(node.value)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    return names


def is_replaces(node: ast.expr, mark_names: set[str]) -> bool:
    """Whether an expression is the `replaces` marker in any form: called or not, `with_args`."""
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Attribute) and target.attr == "with_args":
        target = target.value
    if not (isinstance(target, ast.Attribute) and target.attr == "replaces"):
        return False
    owner = target.value
    return is_pytest_mark(owner) or (isinstance(owner, ast.Name) and owner.id in mark_names)


def replaces_argument(node: ast.expr) -> str | None:
    """The heading of a well-formed marker, else `None`.

    Well-formed means called directly, with exactly one positional string literal that has no
    trailing whitespace, and no keywords.

    Args:
        node: A `replaces` marker expression.

    Returns:
        The heading, or `None`.
    """
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "replaces"
        and not node.keywords
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
        and node.args[0].value == node.args[0].value.rstrip()
    ):
        return node.args[0].value
    return None


def module_replaces(module: Path) -> tuple[list[str], list[str]]:
    """A scenario module's `replaces` headings, and its violations of IEVAL-MARK-005.

    Args:
        module: The scenario module.

    Returns:
        The headings of its well-formed markers, and one message per malformed or misplaced one.
    """
    tree = ast.parse(module.read_text())
    marks = pytest_mark_names(tree)
    scenarios = {id(node) for node in tree.body if is_scenario(node)}
    headings: list[str] = []
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in node.decorator_list:
                if not is_replaces(decorator, marks):
                    continue
                heading = replaces_argument(decorator)
                if id(node) not in scenarios:
                    violations.append(f"IEVAL-MARK-005: {module}::{node.name} isn't a scenario")
                elif heading is None:
                    violations.append(f"IEVAL-MARK-005: {module}::{node.name} has a malformed one")
                else:
                    headings.append(heading)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if not any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in targets):
                continue
            value = node.value
            values = value.elts if isinstance(value, (ast.List, ast.Tuple)) else [value]
            if any(is_replaces(item, marks) for item in values):
                violations.append(f"IEVAL-MARK-005: {module} sets it for the whole module")
    return headings, violations


def is_scenario(node: ast.stmt) -> bool:
    """Whether a module-level statement defines a scenario: a `test*` function."""
    return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
        "test"
    )


# @spec IEVAL-MARK-004, IEVAL-MARK-005
def replaces_violations(root: Path) -> list[str]:
    """`replaces` markers: their form, uniqueness and the scripts they retire.

    Args:
        root: The repo root.

    Returns:
        One message per violation.
    """
    violations: list[str] = []
    for skill in skills(root):
        headings: list[str] = []
        for module in scenario_modules(root, skill):
            found, problems = module_replaces(module)
            headings += found
            violations += problems
        for heading, count in Counter(headings).items():
            if count > 1:
                violations.append(f"IEVAL-MARK-005: {count} scenarios in {skill} replace {heading}")
        manual = root / "evals" / skill / "manual.md"
        remaining = set(level_two_headings(manual.read_text())) if manual.is_file() else set()
        violations += [
            f"IEVAL-MARK-004: {manual} still has the replaced script {heading}"
            for heading in sorted(set(headings) & remaining)
        ]
    return violations


# @spec IEVAL-MARK-008
def manual_file_violations(root: Path) -> list[str]:
    """`evals/*/manual.md` files that hold no manual script.

    Args:
        root: The repo root.

    Returns:
        One message per violation.
    """
    return [
        f"IEVAL-MARK-008: {path} holds no manual script"
        for path in manual_files(root)
        if not manual_scripts(path.read_text())
    ]


def scenario_functions(root: Path, skill: str) -> list[str]:
    """A skill's scenario functions, as `<module file>::<function>`."""
    return [
        f"{module.name}::{node.name}"
        for module in scenario_modules(root, skill)
        for node in ast.parse(module.read_text()).body
        if is_scenario(node) and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def tables(text: str) -> list[list[str]]:
    """The Markdown tables in a text, each as its lines."""
    found: list[list[str]] = []
    current: list[str] = []
    for line in [*text.splitlines(), ""]:
        if line.startswith("|"):
            current.append(line.strip())
        elif current:
            found.append(current)
            current = []
    return found


def cells(row: str) -> list[str]:
    """A table row's cells, stripped."""
    return [
        cell.strip()
        for cell in UNESCAPED_PIPE.split(row.strip().removeprefix("|").removesuffix("|"))
    ]


def is_date(text: str) -> bool:
    """Whether a cell holds a real `YYYY-MM-DD` date."""
    if not ISO_DATE.match(text):
        return False
    try:
        dt.date.fromisoformat(text)
    except ValueError:
        return False
    return True


def row_problem(row: list[str]) -> str | None:
    """What's wrong with a body row's cells, if anything (IEVAL-STAT-002)."""
    if len(row) != ROW_CELLS:
        return f"has {len(row)} cells, not {ROW_CELLS}"
    results = row[1:]
    if NEVER_RUN in results:
        return None if set(results) == {NEVER_RUN} else "says never run in only some cells"
    date, _version, _model, runs, failed, log_date, _component, _phase, _wave = results
    if not (is_date(date) and is_date(log_date)):
        return "has a date that isn't YYYY-MM-DD"
    if not (DIGITS.fullmatch(runs) and DIGITS.fullmatch(failed)):
        return "has a count that isn't a whole number"
    if int(failed) > int(runs):
        return "has more failures than runs"
    return None


# @spec IEVAL-STAT-001, IEVAL-STAT-002
def latest_results_violations(root: Path) -> list[str]:
    """Each skill's latest-results table against its eval cases and scenario functions.

    Args:
        root: The repo root.

    Returns:
        One message per violation.
    """
    violations: list[str] = []
    for skill in skills(root):
        expected = [case.name for case in eval_cases(root, skill)]
        expected += scenario_functions(root, skill)
        if not expected:
            continue
        path = root / "evals" / skill / "latest-results.md"
        if not path.is_file():
            violations.append(f"IEVAL-STAT-001: {path} is missing")
            continue
        found = tables(path.read_text())
        if len(found) != 1:
            violations.append(f"IEVAL-STAT-001: {path} has {len(found)} tables, not one")
            continue
        lines = found[0]
        if len(lines) < 2 or not SEPARATOR_ROW.match(lines[1]):
            violations.append(f"IEVAL-STAT-001: {path}'s table has no header row")
            continue
        rows = [cells(line) for line in lines[2:]]
        names = Counter(row[0] for row in rows)
        violations += [
            f"IEVAL-STAT-001: {path} has {count} rows for {name}"
            for name, count in names.items()
            if count > 1
        ]
        violations += [
            f"IEVAL-STAT-001: {path} has a row for {name}, which doesn't exist"
            for name in names
            if name not in expected
        ]
        violations += [
            f"IEVAL-STAT-001: {path} has no row for {name}"
            for name in expected
            if name not in names
        ]
        violations += [
            f"IEVAL-STAT-002: {path}'s row for {row[0]} {problem}"
            for row in rows
            if (problem := row_problem(row)) is not None
        ]
    return violations
