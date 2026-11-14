"""Tests of the interactive scenarios' layout, dependency, checks, markers and latest results."""

from __future__ import annotations

import ast
import subprocess
import sys
import textwrap
import tomllib
from typing import TYPE_CHECKING, Any

import pytest

from tests import interactive_rules
from tests.interactive_rules import (
    latest_results_violations,
    layout_violations,
    manual_file_violations,
    marker_violations,
    replaces_violations,
)
from tests.support import REPO_ROOT

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

PYPROJECT = REPO_ROOT / "pyproject.toml"
MISE_TOML = REPO_ROOT / "mise.toml"
TY_CONFIG = REPO_ROOT / ".config" / "ty.toml"
COLLECT_SCRIPT = REPO_ROOT / "scripts" / "collect_scenarios.py"

SKILL = "session-wrap-up"
OTHER = "prior-art-search"
SCENARIOS = f"evals/{SKILL}/interactive"
OTHER_SCENARIOS = f"evals/{OTHER}/interactive"
SPECS = "docs/intent/session-wrap-up/session-wrap-up-specs.md"
EVAL_CASE = f"evals/{SKILL}/some-case/case.yaml"
STRICT_PYPROJECT = (
    '[tool.pytest.ini_options]\naddopts = "--strict-markers"\nmarkers = ["replaces: x"]\n'
)
HEADER = (
    "| Case or scenario | Date | Claude Code | Model | Runs | Failed "
    "| Log date | Log component | Log phase | Log wave |\n"
    "|---|---|---|---|---|---|---|---|---|---|\n"
)
NEVER = " | ".join(["never run"] * 9)
# Fixture text writes its annotations through this, so this file's own source never holds an
# annotation line for lidc to count as a citation of a fixture's spec ID.
TAG = "# @" + "spec"
ROW = (
    "| some-case | 2026-11-14 | 2.1.325 | claude-sonnet-5-5 | 3 | 0 "
    "| 2026-11-14 | wrap-up | Evals | 1 |\n"
)
SCENARIO_ROW = f"| test_session_wrap_up.py::test_a | {NEVER} |\n"


def seed(root: Path, files: dict[str, str]) -> Path:
    """Write a synthetic repo: two skills, plus the given files (paths relative to `root`).

    Args:
        root: The directory to write into.
        files: File contents by relative path; text is dedented.

    Returns:
        The repo root.
    """
    for name in (SKILL, OTHER):
        (root / "skills" / name).mkdir(parents=True)
        (root / "skills" / name / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text))
    return root


def scenario(name: str, body: str, directory: str = SCENARIOS) -> dict[str, str]:
    """One scenario module.

    Args:
        name: The module's file name.
        body: The module's source, after an `import pytest` line.
        directory: The scenario directory, relative to the repo root.

    Returns:
        A `seed` file mapping.
    """
    return {f"{directory}/{name}": "import pytest\n\n" + textwrap.dedent(body)}


def spec_line(spec_id: str, marker: str | None, status: str = "x") -> str:
    """One EARS line.

    Args:
        spec_id: The spec's ID.
        marker: The marker's text without its `*(` and `)*`, or `None` for no marker.
        status: The status box's character.

    Returns:
        The line, with a trailing newline.
    """
    suffix = "" if marker is None else f" *({marker})*"
    return f"- [{status}] **{spec_id}**: The agent shall do something.{suffix}\n"


# --- Layout -------------------------------------------------------------------------------


# @spec IEVAL-LAY-001, IEVAL-LAY-002, IEVAL-LAY-003
@pytest.mark.parametrize(
    ("files", "violations"),
    [
        pytest.param(scenario("test_session_wrap_up.py", "def test_a(): pass\n"), 0, id="bare"),
        pytest.param(
            scenario("test_session_wrap_up_gate.py", "def test_a(): pass\n"), 0, id="suffix"
        ),
        pytest.param(scenario("test_gate.py", "def test_a(): pass\n"), 1, id="no-skill-prefix"),
        pytest.param(
            scenario("test_session_wrap_upgate.py", "def test_a(): pass\n"), 1, id="no-separator"
        ),
        pytest.param(
            scenario("test_prior_art_search.py", "def test_a(): pass\n"), 1, id="other-skills-name"
        ),
        pytest.param(
            {f"{SCENARIOS}/conftest.py": f"{TAG} WRAP-RUN-008\n"}, 1, id="conftest-annotation"
        ),
        pytest.param(
            {f"{SCENARIOS}/conftest.py": '"""Mentions @spec in prose only."""\n'},
            0,
            id="conftest-prose",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up_notes.py", f"{TAG} NOTES-LIVE-001\ndef test_a(): pass\n"
            ),
            0,
            id="notes-in-wrap-up",
        ),
        pytest.param(
            scenario(
                "test_prior_art_search.py",
                f"{TAG} PRIOR-RUN-001, NOTES-LIVE-001\ndef test_a(): pass\n",
                OTHER_SCENARIOS,
            ),
            1,
            id="notes-elsewhere-second-in-list",
        ),
        pytest.param(
            scenario(
                "test_prior_art_search.py",
                f"{TAG} PRIOR-RUN-001\n{TAG} NOTES-LIVE-001\ndef test_a(): pass\n",
                OTHER_SCENARIOS,
            ),
            1,
            id="notes-elsewhere-second-line",
        ),
        pytest.param(
            scenario(
                "test_prior_art_search.py",
                f"{TAG} PRIOR-NOTES-001\ndef test_a(): pass\n",
                OTHER_SCENARIOS,
            ),
            0,
            id="notes-inside-an-id-isnt-a-notes-spec",
        ),
    ],
)
def test_layout_rules(tmp_path: Path, files: dict[str, str], violations: int) -> None:
    """Scenario modules are named for their skill; `NOTES-` ones live with the session wrap-up."""
    assert len(layout_violations(seed(tmp_path, files))) == violations


# @spec IEVAL-LAY-004
def test_results_directories_are_ignored() -> None:
    """Every skill's scenario results directory is gitignored."""
    skills = sorted(p.parent.name for p in (REPO_ROOT / "skills").glob("*/SKILL.md"))
    assert skills
    paths = [f"evals/{name}/interactive/results/x.json" for name in skills]
    result = subprocess.run(  # noqa: S603
        ["git", "check-ignore", "--no-index", *paths],  # noqa: S607
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert sorted(result.stdout.split()) == sorted(paths)


# --- Dependency and checks ----------------------------------------------------------------


def pyproject() -> dict[str, Any]:
    """This repo's parsed `pyproject.toml`."""
    return tomllib.loads(PYPROJECT.read_text())


def mise_toml() -> dict[str, Any]:
    """This repo's parsed `mise.toml`."""
    return tomllib.loads(MISE_TOML.read_text())


# @spec IEVAL-DEP-002
def test_check_installs_every_dependency_group() -> None:
    """The check task's install step includes every group, `interactive` among them."""
    tasks = mise_toml()["tasks"]
    assert "sync" in tasks["test"]["depends"]
    assert "--all-groups" in tasks["sync"]["run"]


# @spec IEVAL-DEP-003
def test_pytest_collects_only_tests_by_default() -> None:
    """`testpaths` is set and names nothing under `evals/`, so a plain run starts no scenario."""
    testpaths = pyproject()["tool"]["pytest"]["ini_options"].get("testpaths")
    assert testpaths
    assert not [path for path in testpaths if path.strip("./").startswith("evals")]


# @spec IEVAL-CHK-002
def test_type_check_covers_the_evals_tree() -> None:
    """The type checker's config, wherever it lives, doesn't narrow it away from `evals/`."""
    assert mise_toml()["env"]["TY_CONFIG_FILE"] == "{{config_root}}/.config/ty.toml"
    assert mise_toml()["tasks"]["typecheck"]["run"] == "ty check"
    configs = [tomllib.loads(TY_CONFIG.read_text())]
    configs.append(pyproject().get("tool", {}).get("ty", {}))
    for config in configs:
        source = config.get("src", {})
        assert "include" not in source or any("evals" in path for path in source["include"])
        assert not [path for path in source.get("exclude", []) if "evals" in path]


# @spec IEVAL-MARK-007
def test_replaces_marker_is_registered() -> None:
    """The repo runs pytest with `--strict-markers`, so `replaces` must be registered."""
    markers = pyproject()["tool"]["pytest"]["ini_options"].get("markers", [])
    names = [marker.split(":")[0].split("(")[0].strip() for marker in markers]
    assert "replaces" in names


# @spec IEVAL-CHK-001
def test_check_task_collects_scenarios() -> None:
    """`check` depends on a task that runs the collection script."""
    tasks = mise_toml()["tasks"]
    collectors = [
        name
        for name, task in tasks.items()
        if "scripts/collect_scenarios.py" in str(task.get("run"))
    ]
    assert collectors
    assert set(collectors) & set(tasks["check"]["depends"])


def collect(root: Path) -> subprocess.CompletedProcess[str]:
    """Run the collection script on a synthetic repo, from inside it.

    Args:
        root: The synthetic repo.

    Returns:
        The finished process.
    """
    return subprocess.run(  # noqa: S603
        [sys.executable, str(COLLECT_SCRIPT), str(root)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


# @spec IEVAL-CHK-001
def test_collection_script_fails_without_an_evals_directory(tmp_path: Path) -> None:
    """A root with no `evals/` is a wrong path, not a repo with nothing to collect."""
    result = collect(tmp_path)
    assert result.returncode != 0
    assert "evals" in result.stdout + result.stderr


# @spec IEVAL-CHK-001
@pytest.mark.parametrize(
    ("files", "fails_on"),
    [
        pytest.param({"evals/README.md": "Evals.\n"}, None, id="no-scenarios"),
        pytest.param(
            scenario("test_session_wrap_up.py", "def test_a():\n    raise AssertionError\n"),
            None,
            id="collects-without-running",
        ),
        pytest.param(
            scenario("test_session_wrap_up.py", "import no_such_module_anywhere\n"),
            "no_such_module_anywhere",
            id="broken-import",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                "@pytest.mark.no_such_marker_anywhere\ndef test_a(): pass\n",
            ),
            "no_such_marker_anywhere",
            id="unregistered-marker",
        ),
    ],
)
def test_collection_script(tmp_path: Path, files: dict[str, str], fails_on: str | None) -> None:
    """Collection uses the repo's own pytest config, runs nothing, and fails on a broken module."""
    files = {"pyproject.toml": STRICT_PYPROJECT, **files}
    result = collect(seed(tmp_path, files))
    output = result.stdout + result.stderr
    if fails_on is None:
        assert result.returncode == 0, output
        assert "AssertionError" not in output
    else:
        assert result.returncode != 0, output
        assert fails_on in output


# --- Markers ------------------------------------------------------------------------------


# @spec IEVAL-MARK-001, IEVAL-MARK-002, IEVAL-MARK-003
@pytest.mark.parametrize(
    ("marker", "scenario_cites", "eval_cites", "script_names", "violations"),
    [
        pytest.param("interactive", True, False, False, 0, id="interactive-ok"),
        pytest.param("interactive", False, False, False, 1, id="interactive-uncited"),
        pytest.param("interactive", True, True, False, 1, id="interactive-but-eval-cites"),
        pytest.param("interactive", True, False, True, 1, id="interactive-but-script-names"),
        pytest.param("eval, interactive", True, True, False, 0, id="both-ok"),
        pytest.param("eval, interactive", True, False, False, 1, id="both-without-eval"),
        pytest.param("eval, interactive", False, True, False, 1, id="both-without-scenario"),
        pytest.param("eval, interactive", True, True, True, 1, id="both-but-script-names"),
        pytest.param("interactive, eval", True, True, False, 1, id="both-in-the-wrong-order"),
        pytest.param("manual", True, False, False, 1, id="manual-left-behind"),
        pytest.param("eval", True, True, False, 1, id="eval-left-behind"),
        pytest.param("manual", True, False, True, 0, id="manual-still-scripted"),
        pytest.param(None, True, False, False, 0, id="unmarked-cited-in-passing"),
    ],
)
def test_marker_rules(  # noqa: PLR0913
    tmp_path: Path,
    marker: str | None,
    *,
    scenario_cites: bool,
    eval_cites: bool,
    script_names: bool,
    violations: int,
) -> None:
    """A marker agrees with what cites the spec and whether a manual script still names it."""
    files = {SPECS: "# Specs\n\n" + spec_line("WRAP-RUN-008", marker)}
    if scenario_cites:
        files |= scenario(
            "test_session_wrap_up.py", f"{TAG} WRAP-RUN-007, WRAP-RUN-008\ndef test_a(): pass\n"
        )
    if eval_cites:
        files[EVAL_CASE] = f"{TAG} WRAP-RUN-007\n{TAG} WRAP-RUN-008\nschema_version: '1.1'\n"
    if script_names:
        files[f"evals/{SKILL}/manual.md"] = (
            "# Manual\n\n## Interactive run (WRAP-RUN-007, WRAP-RUN-008)\n\nSteps.\n"
        )
    assert len(marker_violations(seed(tmp_path, files))) == violations


# @spec IEVAL-MARK-001
@pytest.mark.parametrize("status", ["x", " ", "D"])
def test_marker_rules_cover_every_status(tmp_path: Path, status: str) -> None:
    """The marker rules apply to a spec whatever its status box says."""
    files = {SPECS: "# Specs\n\n" + spec_line("WRAP-RUN-008", "interactive", status)}
    assert len(marker_violations(seed(tmp_path, files))) == 1


# @spec IEVAL-MARK-004, IEVAL-MARK-005
@pytest.mark.parametrize(
    ("files", "violations"),
    [
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces("Interactive run (WRAP-RUN-008)")\ndef test_a(): pass\n',
            )
            | {f"evals/{SKILL}/manual.md": "# M\n\n## Other (WRAP-RUN-009)\n"},
            0,
            id="script-gone",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces("Interactive run (WRAP-RUN-008)")\ndef test_a(): pass\n',
            )
            | {f"evals/{SKILL}/manual.md": "# M\n\n## Interactive run (WRAP-RUN-008)   \n"},
            1,
            id="script-still-there",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces("Interactive run (WRAP-RUN-008)")\ndef test_a(): pass\n',
            )
            | {f"evals/{SKILL}/manual.md": "# M\n\n### Interactive run (WRAP-RUN-008)\n"},
            0,
            id="only-a-level-3-heading-matches",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces("Interactive run (WRAP-RUN-008)")\ndef test_a(): pass\n',
            )
            | {f"evals/{OTHER}/manual.md": "# M\n\n## Interactive run (WRAP-RUN-008)\n"},
            0,
            id="same-heading-in-another-skill",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces("A (WRAP-RUN-008)")\ndef test_a(): pass\n',
            )
            | scenario(
                "test_prior_art_search.py",
                '@pytest.mark.replaces("A (WRAP-RUN-008)")\ndef test_a(): pass\n',
                OTHER_SCENARIOS,
            ),
            0,
            id="same-argument-in-two-skills",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces("A (WRAP-RUN-008)", "B (WRAP-RUN-009)")\n'
                "def test_a(): pass\n",
            ),
            1,
            id="two-arguments",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces(heading="A (WRAP-RUN-008)")\ndef test_a(): pass\n',
            ),
            1,
            id="keyword-argument",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                'HEADING = "A (WRAP-RUN-008)"\n\n'
                "@pytest.mark.replaces(HEADING)\ndef test_a(): pass\n",
            ),
            1,
            id="non-literal-argument",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                'pytestmark = pytest.mark.replaces("A (WRAP-RUN-008)")\ndef test_a(): pass\n',
            ),
            1,
            id="module-level",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces("A (WRAP-RUN-008)")\nclass TestA:\n'
                "    def test_a(self): pass\n",
            ),
            1,
            id="class-level",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                'from pytest import mark\n\n@mark.replaces("A (WRAP-RUN-008)")\n'
                "def test_a(): pass\n",
            )
            | {f"evals/{SKILL}/manual.md": "# M\n\n## A (WRAP-RUN-008)\n"},
            1,
            id="imported-mark-still-retires-the-script",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces("A (WRAP-RUN-008)")\ndef test_a(): pass\n\n'
                '@pytest.mark.replaces("A (WRAP-RUN-008)")\ndef test_b(): pass\n',
            ),
            1,
            id="two-scenarios-one-script",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces("A (WRAP-RUN-008)")\ndef helper(): pass\n',
            ),
            1,
            id="on-a-helper",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                'class TestA:\n    @pytest.mark.replaces("A (WRAP-RUN-008)")\n'
                "    def test_a(self): pass\n",
            ),
            1,
            id="on-a-method",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                'pytestmark: list = [pytest.mark.replaces("A (WRAP-RUN-008)")]\n'
                "def test_a(): pass\n",
            ),
            1,
            id="annotated-module-level",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                'm = pytest.mark\n\n@m.replaces("A (WRAP-RUN-008)")\ndef test_a(): pass\n',
            )
            | {f"evals/{SKILL}/manual.md": "# M\n\n## A (WRAP-RUN-008)\n"},
            1,
            id="aliased-mark-still-retires-the-script",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces.with_args("A (WRAP-RUN-008)")\ndef test_a(): pass\n',
            ),
            1,
            id="with-args",
        ),
        pytest.param(
            scenario(
                "test_session_wrap_up.py",
                '@pytest.mark.replaces("A (WRAP-RUN-008) ")\ndef test_a(): pass\n',
            ),
            1,
            id="trailing-whitespace-argument",
        ),
    ],
)
def test_replaces_rules(tmp_path: Path, files: dict[str, str], violations: int) -> None:
    """A `replaces` marker takes one literal heading, on one function, and retires that script."""
    assert len(replaces_violations(seed(tmp_path, files))) == violations


# @spec IEVAL-MARK-008
@pytest.mark.parametrize(
    ("relative", "text", "violations"),
    [
        pytest.param(
            f"evals/{SKILL}/manual.md", "# M\n\n## Run (WRAP-RUN-008)\n", 0, id="has-script"
        ),
        pytest.param(
            f"evals/{SKILL}/manual.md",
            "# M\n\nIntro.\n\n## Setting up the runs\n",
            1,
            id="prose-only",
        ),
        pytest.param(
            f"evals/{SKILL}/manual.md",
            "# M\n\n```markdown\n## Working rules (WRAP-RUN-008)\n```\n",
            1,
            id="heading-only-in-code-block",
        ),
        pytest.param(
            f"evals/{SKILL}/manual.md",
            "# M\n\n## Run (see the notes)\n",
            1,
            id="heading-without-an-id",
        ),
        pytest.param(
            f"evals/{SKILL}/manual.md",
            "# M\n\n~~~markdown\n## Working rules (WRAP-RUN-008)\n~~~\n",
            1,
            id="heading-only-in-tilde-block",
        ),
        pytest.param(
            f"evals/{SKILL}/manual.md", "# M\n\n## UTF-8 output\n", 1, id="id-like-but-not-an-id"
        ),
        pytest.param("evals/retired-skill/manual.md", "# M\n\nIntro.\n", 1, id="not-a-skill"),
    ],
)
def test_manual_file_rule(tmp_path: Path, relative: str, text: str, violations: int) -> None:
    """A `manual.md` with no manual script left shouldn't exist."""
    assert len(manual_file_violations(seed(tmp_path, {relative: text}))) == violations


# --- Latest results -----------------------------------------------------------------------


PARAMETRIZED_MODULE = (
    "@pytest.fixture\ndef thing(): return 1\n\n"
    "def _helper(): return 2\n\n"
    '@pytest.mark.parametrize("x", [1, 2])\ndef test_a(x, thing): pass\n'
)


# @spec IEVAL-STAT-001, IEVAL-STAT-002
@pytest.mark.parametrize(
    ("table", "violations"),
    [
        pytest.param(HEADER + ROW + SCENARIO_ROW, 0, id="complete"),
        pytest.param(None, 1, id="missing-file"),
        pytest.param(HEADER + ROW, 1, id="missing-scenario-row"),
        pytest.param(HEADER + ROW + SCENARIO_ROW + ROW, 1, id="duplicate-row"),
        pytest.param(
            HEADER + ROW + SCENARIO_ROW + f"| gone-case | {NEVER} |\n", 1, id="row-for-nothing"
        ),
        pytest.param(HEADER + ROW + "\nText.\n\n" + HEADER + SCENARIO_ROW, 1, id="two-tables"),
        pytest.param(ROW + SCENARIO_ROW, 1, id="no-header-row"),
        pytest.param(
            HEADER + ROW.replace(" | 3 | 0 |", " | 3 |") + SCENARIO_ROW, 1, id="short-row"
        ),
        pytest.param(
            HEADER
            + ROW
            + "| test_session_wrap_up.py::test_a | never run | 2.1.325 | m "
            + "| 1 | 0 | d | c | p | 1 |\n",
            1,
            id="partial-never-run",
        ),
        pytest.param(
            HEADER + ROW.replace("| 3 | 0 |", "| three | 0 |") + SCENARIO_ROW,
            1,
            id="runs-not-a-number",
        ),
        pytest.param(
            HEADER + ROW.replace("| 3 | 0 |", "| 3 | 4 |") + SCENARIO_ROW,
            1,
            id="more-failures-than-runs",
        ),
        pytest.param(
            HEADER + ROW.replace("| 2026-11-14 | 2.1.325", "| 14 Nov | 2.1.325") + SCENARIO_ROW,
            1,
            id="date-not-iso",
        ),
        pytest.param(
            HEADER + ROW.replace("| 3 | 0 |", "| 3 | ² |") + SCENARIO_ROW,
            1,
            id="superscript-digit",
        ),
        pytest.param(
            HEADER + ROW.replace("| wrap-up |", "| wrap-up \\| evals |") + SCENARIO_ROW,
            0,
            id="escaped-pipe-in-a-cell",
        ),
    ],
)
def test_latest_results_rules(tmp_path: Path, table: str | None, violations: int) -> None:
    """One table, a row per eval case and scenario function, ten well-formed cells each."""
    files = {EVAL_CASE: "schema_version: '1.1'\n"}
    files |= scenario("test_session_wrap_up.py", PARAMETRIZED_MODULE)
    if table is not None:
        files[f"evals/{SKILL}/latest-results.md"] = "# Latest results\n\n" + table
    assert len(latest_results_violations(seed(tmp_path, files))) == violations


# --- This repo ----------------------------------------------------------------------------


# @spec IEVAL-MARK-009
def test_rules_never_import_the_plugin() -> None:
    """The rules read files only; they don't import pytest-claude-code-evals."""
    tree = ast.parse((REPO_ROOT / "tests" / "interactive_rules.py").read_text())
    imported = [
        name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for name in (
            [alias.name for alias in node.names]
            if isinstance(node, ast.Import)
            else [node.module or ""]
        )
    ]
    assert imported
    assert not [name for name in imported if name.startswith("pytest_claude_code_evals")]
    assert interactive_rules.__name__ == "tests.interactive_rules"


# @spec IEVAL-LAY-001, IEVAL-LAY-002, IEVAL-LAY-003, IEVAL-MARK-001, IEVAL-MARK-002
# @spec IEVAL-MARK-003, IEVAL-MARK-004, IEVAL-MARK-005, IEVAL-MARK-008, IEVAL-MARK-009
# @spec IEVAL-STAT-001, IEVAL-STAT-002
@pytest.mark.parametrize(
    "rule",
    [
        layout_violations,
        marker_violations,
        replaces_violations,
        manual_file_violations,
        latest_results_violations,
    ],
    ids=lambda rule: rule.__name__,
)
def test_this_repo_follows_the_rules(rule: Callable[[Path], list[str]]) -> None:
    """Every rule holds across this repo's specs files, manual scripts, scenarios and tables."""
    assert rule(REPO_ROOT) == []
