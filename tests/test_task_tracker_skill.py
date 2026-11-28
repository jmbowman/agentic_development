"""Structure tests of the task-tracker skill, its eval suite, and this repo's wiring of its tool.

The skill's rules are checked by the commands, options, keys and values each one depends on,
not by their wording; a rule that names none is left to review (see the specs file's preamble).
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.support import (
    EVALS,
    REPO_ROOT,
    SKILLS,
    TASK_TOOL,
    StepRunner,
    cited_by_evals,
    eval_cases,
    frontmatter,
    git_repo,
    load_workflow,
    only_job,
    require_tool,
    small_backlog,
    step_by_id,
    step_index,
)

SKILL = SKILLS / "task-tracker"
SKILL_MD = SKILL / "SKILL.md"
FORMAT = SKILL / "references" / "task-format.md"
SUITE = EVALS / "task-tracker"
SPECS = REPO_ROOT / "docs" / "intent" / "task-tracker" / "task-tracker-specs.md"
MISE_TOML = REPO_ROOT / "mise.toml"

AGENT_SKILLS_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}

# Every key the task tool reads (TASK-FILE-002, TASK-FILE-003), with the values the format allows.
KEY_VALUES: dict[str, tuple[str, ...]] = {
    "id": (),
    "title": (),
    "status": ("To Do", "In Progress", "Done"),
    "priority": ("high", "medium", "low"),
    "type": (
        "bug",
        "chore",
        "decision",
        "docs",
        "eval",
        "feature",
        "review",
        "search",
        "spike",
        "upstream",
    ),
    "labels": (),
    "milestone": (),
    "dependencies": (),
    "parent_task_id": (),
    "created_date": (),
    "due_date": (),
    "references": (),
    "performer": ("human", "agent"),
    "agent_tier": ("fast", "moderate", "strong"),
    "effort": ("S", "M", "L"),
    "external_blockers": (),
    "deadline_kind": ("hard", "soft", "target"),
    "defer_until": (),
    "waiting": (),
    "priority_set_by": ("agent", "human"),
    "sessions": ("created", "worked", "finished"),
    "target": (),
}
BLOCKER_FORMS = (
    "gh:<owner>/<repo>#<number>",
    "<host>/<owner>/<repo>#<ID>",
    "<outbox folder>/<slug>",
)
SESSION_FIELDS = ("agent", "id", "role", "date")
# The design's examples of labels that record where a task came from.
ORIGIN_LABELS = ("issue", "loose-end", "prior-art")

# The commands, options, keys and values each rule in the Skill section depends on, which SKILL.md
# (where the design puts the agents' rules) must name in code spans. Rules that name none
# (TASK-SKILL-005, 008, 014, 020, 027, 029, 030) are verified by review.
RULE_TOKENS: dict[str, tuple[str, ...]] = {
    "TASK-SKILL-007": ("dependencies", "parent_task_id"),
    "TASK-SKILL-010": ("sessions", "worked", "finished", "CLAUDE_CODE_SESSION_ID"),
    "TASK-SKILL-011": ("labels", "type"),
    "TASK-SKILL-012": ("next --for agent", "## Comments", "In Progress"),
    "TASK-SKILL-013": ("--comment", "--append-notes", "decision"),
    "TASK-SKILL-015": ("--check-ac", "--final-summary", "Done", "decision"),
    "TASK-SKILL-016": ("milestone", "## Importance"),
    "TASK-SKILL-017": ("outbox/", "target", "<host>/<owner>/<repo>"),
    "TASK-SKILL-018": ("private_root", "backlog/private/"),
    "TASK-SKILL-019": ("<outbox folder>/<slug>", "<host>/<owner>/<repo>#<ID>", "check"),
    "TASK-SKILL-022": ("priority_set_by", "human", "assignee"),
    "TASK-SKILL-023": ("onStatusChange", "backlog board"),
    "TASK-SKILL-024": (
        "--acceptance-criteria",
        "--dep",
        "--ref",
        "-l",
        "--notes",
        "-a",
        "--add-ref",
        "--add-label",
        "--append-notes",
    ),
    "TASK-SKILL-026": ("git log --diff-filter=A", "check"),
    "TASK-SKILL-045": ("title:", "task edit -t"),
    "TASK-SKILL-028": (
        "next",
        "task list",
        "references",
        "--dod",
        "definition_of_done",
        "--draft",
        "backlog doc",
        "backlog decision",
        "task delete",
        "doctor --fix",
        "board export",
        "agents --update-instructions",
    ),
}


def skill_text() -> str:
    """SKILL.md and every reference file, which together are what the agent can read."""
    files = [SKILL_MD, *sorted((SKILL / "references").glob("*.md"))]
    return "\n".join(path.read_text(encoding="utf-8") for path in files)


def code_spans(text: str) -> list[str]:
    """The contents of every inline code span in Markdown text."""
    return [str(span) for span in re.findall(r"`([^`\n]+)`", text)]


def names(spans: list[str], token: str) -> bool:
    """Whether a code span holds `token` as a whole word, command or option.

    `--dep` doesn't match inside `--depends-on`, nor `backlog doc` inside `backlog doctor`.
    """
    after = r"(?![\w-])" if re.match(r"[\w-]", token[-1]) else ""
    pattern = re.compile(rf"(?<![\w-]){re.escape(token)}{after}")
    return any(pattern.search(span) for span in spans)


def eval_spec_ids() -> list[str]:
    """The Skill section's specs that its behavior evals verify, marked *(eval)*."""
    text = SPECS.read_text(encoding="utf-8")
    return [str(spec) for spec in re.findall(r"\*\*(TASK-SKILL-\d{3})\*\*:.*\*\(eval\)\*", text)]


# --- The skill's files -------------------------------------------------------------------------


# @spec TASK-SKILL-001
@pytest.mark.parametrize(
    "path",
    [
        "SKILL.md",
        "scripts/tasks.py",
        "references/task-format.md",
        "scripts/_vendor/oneyaml-python/src/oneyaml/__init__.py",
    ],
)
def test_skill_holds_its_files(path: str) -> None:
    """The skill ships its instructions, its tool and its format reference together.

    The schemas TASK-SKILL-001 also lists join this list with the lint that uses them (AD-5.2).
    """
    assert (SKILL / path).is_file()


# @spec TASK-SKILL-002
def test_skill_frontmatter_uses_only_agent_skills_fields() -> None:
    """Any agent that reads Agent Skills can load the skill."""
    meta = frontmatter(SKILL_MD)
    assert set(meta) <= AGENT_SKILLS_FIELDS
    assert meta["name"] == "task-tracker"
    assert 0 < len(str(meta["description"]).strip()) <= 1024


# @spec TASK-SKILL-003
def test_tool_declares_no_dependencies_and_has_no_lock() -> None:
    """`uv run --script` needs only a Python 3.11 or later, never a package index."""
    script = TASK_TOOL.read_text(encoding="utf-8")
    block = re.search(r"^# /// script\n(.*?)^# ///$", script, re.MULTILINE | re.DOTALL)
    assert block, "the tool has no PEP 723 metadata block"
    metadata = tomllib.loads(re.sub(r"^# ?", "", block.group(1), flags=re.MULTILINE))
    assert metadata.get("requires-python") == ">=3.11"
    assert metadata.get("dependencies") == []
    assert not TASK_TOOL.with_name("tasks.py.lock").exists()


def files_git_would_track(*paths: str) -> list[str]:
    """The files git tracks under `paths`, or would once added: tracked plus unignored untracked.

    Skips when the tests aren't run from a git checkout of this repo, as in a staged-tree copy
    under the gitignored `tmp/`.
    """
    top = git(REPO_ROOT, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != REPO_ROOT.resolve():
        pytest.skip("not run from a git checkout of this repo, so there is no index to read")
    result = git(REPO_ROOT, "ls-files", "--cached", "--others", "--exclude-standard", "--", *paths)
    assert result.returncode == 0, result.stderr
    return sorted(set(result.stdout.splitlines()))


VENDORED = "skills/task-tracker/scripts/_vendor/oneyaml-python"


# @spec TASK-SKILL-033
def test_vendored_parser_holds_only_the_package_and_its_licenses() -> None:
    """`src/oneyaml/` without `compat/`, and the two license files, are all that is vendored.

    That nothing upstream's `src/oneyaml/` holds is missing is checked by CI's `vendir sync
    --locked` (TASK-REPO-011), which needs the network.
    """
    files = [path.removeprefix(f"{VENDORED}/") for path in files_git_would_track(VENDORED)]
    assert {"LICENSE-MIT", "LICENSE-APACHE", "src/oneyaml/__init__.py"} <= set(files)
    stray = [
        path
        for path in files
        if path not in {"LICENSE-MIT", "LICENSE-APACHE"}
        and not (path.startswith("src/oneyaml/") and not path.startswith("src/oneyaml/compat/"))
    ]
    assert not stray, stray


def test_skill_text_has_no_spec_annotations() -> None:
    """Annotations in skill text would load into the agent's context on every run."""
    assert "@spec" not in skill_text()


# --- The format reference ----------------------------------------------------------------------


# @spec TASK-SKILL-004
@pytest.mark.parametrize("key", sorted(KEY_VALUES))
def test_format_reference_describes_each_key(key: str) -> None:
    """A person or agent writing a task by hand finds every key the tool reads, and its values."""
    spans = code_spans(FORMAT.read_text(encoding="utf-8"))
    assert key in spans
    missing = [value for value in KEY_VALUES[key] if value not in spans]
    assert not missing, f"{key}: {missing}"


# @spec TASK-SKILL-004
def test_format_reference_describes_blockers_drafts_and_sessions() -> None:
    """The three blocker forms, the draft form, a session record's fields and what labels mean."""
    text = FORMAT.read_text(encoding="utf-8")
    spans = code_spans(text)
    missing = [token for token in (*BLOCKER_FORMS, *SESSION_FIELDS) if token not in spans]
    missing += [label for label in ORIGIN_LABELS if label not in spans]
    assert not missing, missing
    assert any(re.search(r"outbox/<[^>]+>/<slug>\.md", span) for span in spans), "no draft path"


# @spec TASK-SKILL-031
def test_format_reference_welcomes_other_writers() -> None:
    """A tool that writes task files without Backlog.md's CLI finds the contract it must follow.

    What the section says is verified by review; the test pins that it exists and names `check`.
    """
    text = FORMAT.read_text(encoding="utf-8")
    section = re.search(r"^## Other writers$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    assert section, "no `## Other writers` section"
    assert names(code_spans(section.group(1)), "check")


# --- The agents' rules -------------------------------------------------------------------------


# @spec TASK-SKILL-007, TASK-SKILL-010, TASK-SKILL-011, TASK-SKILL-012, TASK-SKILL-013
# @spec TASK-SKILL-015, TASK-SKILL-016, TASK-SKILL-017, TASK-SKILL-018, TASK-SKILL-019
# @spec TASK-SKILL-022, TASK-SKILL-023, TASK-SKILL-024, TASK-SKILL-026, TASK-SKILL-028
# @spec TASK-SKILL-045
@pytest.mark.parametrize(("spec", "tokens"), sorted(RULE_TOKENS.items()))
def test_rule_names_what_it_depends_on(spec: str, tokens: tuple[str, ...]) -> None:
    """Each rule names the commands, options, keys and values it depends on, in SKILL.md."""
    spans = code_spans(SKILL_MD.read_text(encoding="utf-8"))
    missing = [token for token in tokens if not names(spans, token)]
    assert not missing, f"{spec}: {missing}"


# The section of SKILL.md that holds each rule naming no command, option, key or value.
REVIEWED_RULE_SECTIONS = {
    "TASK-SKILL-005": "When to create a task",
    "TASK-SKILL-008": "Recording work",
    "TASK-SKILL-014": "Doing the work",
    "TASK-SKILL-020": "Work for another repo",
    "TASK-SKILL-027": "When to create a task",
    "TASK-SKILL-029": "A repo with no backlog",
    "TASK-SKILL-030": "When the backlog CLI won't run",
}


# @spec TASK-SKILL-005, TASK-SKILL-008, TASK-SKILL-014, TASK-SKILL-020, TASK-SKILL-027
# @spec TASK-SKILL-029, TASK-SKILL-030
@pytest.mark.parametrize(("spec", "section"), sorted(REVIEWED_RULE_SECTIONS.items()))
def test_reviewed_rule_has_its_section(spec: str, section: str) -> None:
    """A rule that names nothing checkable keeps its place; review verifies what it says."""
    headings = re.findall(r"^## (.+)$", SKILL_MD.read_text(encoding="utf-8"), re.MULTILINE)
    assert section in headings, f"{spec}: no section {section!r}"


@pytest.mark.parametrize(
    ("token", "text", "found"),
    [
        ("--dep", "`--depends-on`", False),
        ("--dep", "`task edit 3 --dep AD-1`", True),
        ("backlog doc", "`backlog doctor --fix`", False),
        ("-l", "`--add-label`", False),
        ("next", "pick the next one", False),
        ("backlog/private/", "`backlog/private/outbox/`", True),
    ],
)
def test_names_matches_whole_tokens_in_code_spans(token: str, text: str, *, found: bool) -> None:
    """The rule check can't be satisfied by a longer option or by ordinary prose."""
    assert names(code_spans(text), token) is found


# --- Evals -------------------------------------------------------------------------------------


def test_specs_mark_the_four_eval_rules() -> None:
    """The specs file marks the rules the evals verify; the test below depends on reading them."""
    assert eval_spec_ids() == [
        "TASK-SKILL-006",
        "TASK-SKILL-009",
        "TASK-SKILL-021",
        "TASK-SKILL-025",
    ]


# @spec TASK-SKILL-006, TASK-SKILL-009, TASK-SKILL-021, TASK-SKILL-025
@pytest.mark.parametrize("spec", eval_spec_ids())
def test_eval_spec_is_exercised_by_an_eval_case(spec: str) -> None:
    """Every eval-verified rule has a case in this skill's suite."""
    assert eval_cases(SUITE)
    assert spec in cited_by_evals(SUITE)


def test_eval_citations_name_eval_specs() -> None:
    """Eval cases cite only specs that the specs file marks as verified by evals."""
    stray = sorted(set(cited_by_evals(SUITE)) - set(eval_spec_ids()))
    assert not stray, stray


# --- This repo's wiring ------------------------------------------------------------------------


def mise_config() -> dict[str, Any]:
    """This repo's parsed `mise.toml`."""
    return tomllib.loads(MISE_TOML.read_text(encoding="utf-8"))


# @spec TASK-REPO-001
def test_tasks_task_runs_the_skills_tool_as_a_script() -> None:
    """The `tasks` mise task runs the skill's tool as a script, with no lock file to honour."""
    run = shlex.split(str(mise_config()["tasks"]["tasks"]["run"]))
    assert run[:2] == ["uv", "run"]
    assert "--script" in run
    assert "--locked" not in run
    assert run[-1].endswith("skills/task-tracker/scripts/tasks.py")


# @spec TASK-REPO-001
def test_tasks_task_passes_every_argument_on(tmp_path: Path) -> None:
    """Options and a command given after `mise run tasks --` all reach the tool."""
    backlog = small_backlog(tmp_path)
    arguments = ["--offline", "--root", str(backlog), "next", "--for", "agent"]
    result = subprocess.run(  # noqa: S603
        [require_tool("mise"), "-C", str(REPO_ROOT), "run", "--quiet", "tasks", "--", *arguments],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "EX-1" in result.stdout


# @spec TASK-REPO-005
@pytest.mark.parametrize(
    "names",
    [
        ("gh", "aqua:cli/cli", "github:cli/cli"),
        ("github:MrLesk/Backlog.md",),
        ("vendir", "aqua:carvel-dev/vendir"),
    ],
    ids=["gh", "backlog", "vendir"],
)
def test_mise_pins_the_trackers_tools(names: tuple[str, ...]) -> None:
    """The GitHub lookup's `gh`, Backlog.md's CLI and vendir are the same version everywhere.

    Backlog.md is pinned as its release binary, which is the whole CLI in one file. The npm
    package's `.bin` holds only a launcher for code in a sibling folder, which a sandbox that
    allows reading just the folders on `PATH` (as `claude plugin eval`'s does) can't load.
    """
    tools = mise_config()["tools"]
    assert isinstance(tools, dict)
    pins = [tools[name] for name in names if name in tools]
    assert len(pins) == 1, f"expected one pin among {names}"
    pin = pins[0]["version"] if isinstance(pins[0], dict) else pins[0]
    assert re.fullmatch(r"v?\d+\.\d+\.\d+", str(pin)), pin


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git in a directory, with no global or system configuration or excludes."""
    env = {"PATH": os.environ["PATH"], "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
    return subprocess.run(  # noqa: S603
        [require_tool("git"), "-c", "core.excludesFile=/dev/null", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


# @spec TASK-REPO-007
@pytest.mark.parametrize("path", ["backlog/.cache/", "backlog/.locks/", "backlog/private/"])
def test_backlog_scratch_folders_are_ignored(tmp_path: Path, path: str) -> None:
    """The lookup cache, Backlog.md's edit locks and the private stopgap never reach a commit.

    The rules are read from a copy of this repo's `.gitignore` in a fresh repo, so the result
    doesn't depend on the directory around the checkout or on the developer's own excludes.
    """
    assert git(tmp_path, "init", "--quiet").returncode == 0
    shutil.copy(REPO_ROOT / ".gitignore", tmp_path / ".gitignore")
    assert git(tmp_path, "check-ignore", "--quiet", "--no-index", path).returncode == 0


# @spec TASK-REPO-008
def test_board_is_not_tracked() -> None:
    """The board is printed on demand, so a status change modifies only the task's own file."""
    top = git(REPO_ROOT, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != REPO_ROOT.resolve():
        pytest.skip("not run from a git checkout of this repo, so there is no index to read")
    result = git(REPO_ROOT, "ls-files", "--", "backlog/BOARD.md", "backlog/private/BOARD.md")
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


# --- The vendored parser's wiring --------------------------------------------------------------

VENDIR_FILES = ["vendir.yml", "vendir.lock.yml"]
VENDOR_DIR = "skills/task-tracker/scripts/_vendor"
VENDOR_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "vendor.yml"
RUFF_CONFIG = REPO_ROOT / ".ruff.toml"
TY_CONFIG = REPO_ROOT / ".config" / "ty.toml"
OWN_RENOVATE = REPO_ROOT / ".github" / "renovate.json"
PREK = REPO_ROOT / ".config" / "prek.toml"


# @spec TASK-REPO-009
def test_vendir_follows_oneyamls_main_into_the_skill() -> None:
    """One directory, one source: the package and its licenses from oneyaml-python's `main`."""
    config = yaml.safe_load((REPO_ROOT / "vendir.yml").read_text(encoding="utf-8"))
    [directory] = config["directories"]
    assert directory["path"] == VENDOR_DIR
    [contents] = directory["contents"]
    assert contents["path"] == "oneyaml-python"
    assert contents["git"] == {
        "url": "https://github.com/recursive-ai-oss/oneyaml-python",
        "ref": "origin/main",
    }
    assert contents["includePaths"] == ["src/oneyaml/**/*"]
    assert contents["excludePaths"] == ["src/oneyaml/compat/**/*"]
    assert sorted(contents["legalPaths"]) == ["LICENSE-APACHE", "LICENSE-MIT"]


# @spec TASK-REPO-009
def test_vendir_lock_records_the_commit_and_is_tracked() -> None:
    """The lock beside `vendir.yml` names the commit vendored, and git tracks it."""
    lock = yaml.safe_load((REPO_ROOT / "vendir.lock.yml").read_text(encoding="utf-8"))
    [directory] = lock["directories"]
    assert directory["path"] == VENDOR_DIR
    [contents] = directory["contents"]
    assert contents["path"] == "oneyaml-python"
    assert re.fullmatch(r"[0-9a-f]{40}", contents["git"]["sha"])
    assert files_git_would_track("vendir.lock.yml") == ["vendir.lock.yml"]


# @spec TASK-REPO-010
def test_renovate_keeps_lock_file_maintenance_on_for_vendir() -> None:
    """A package rule for the root `vendir.yml` turns lock-file maintenance on."""
    rules = json.loads(OWN_RENOVATE.read_text(encoding="utf-8")).get("packageRules", [])
    matching = [
        rule
        for rule in rules
        if rule.get("matchManagers", ["vendir"]) == ["vendir"]
        and rule.get("matchFileNames") == ["vendir.yml"]
        and rule.get("lockFileMaintenance", {}).get("enabled") is True
    ]
    assert len(matching) == 1, rules


# @spec TASK-REPO-010
@pytest.mark.renovate
def test_own_renovate_config_passes_the_validator() -> None:
    """The pinned Renovate accepts lock-file maintenance inside a package rule."""
    validator = require_tool("renovate-config-validator")
    completed = subprocess.run(  # noqa: S603
        [validator, "--no-global", "--strict", str(OWN_RENOVATE)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


# @spec TASK-REPO-011
def test_vendor_workflow_has_no_other_trigger() -> None:
    """No schedule or manual run: the check runs only on changes to the vendored files."""
    assert sorted(load_workflow(VENDOR_WORKFLOW)["on"]) == ["pull_request", "push"]


# @spec TASK-REPO-011
@pytest.mark.parametrize("event", ["push", "pull_request"])
def test_vendor_workflow_runs_only_on_changes_to_the_vendored_files(event: str) -> None:
    """Pull requests and pushes to `main` trigger the check only when they touch these paths.

    Every change reaches `main` through a pull request, which runs the check first.
    """
    trigger = load_workflow(VENDOR_WORKFLOW)["on"][event]
    expected = {"paths"} | ({"branches"} if event == "push" else set())
    assert set(trigger) == expected
    if event == "push":
        assert trigger["branches"] == ["main"]
    assert sorted(trigger["paths"]) == sorted([*VENDIR_FILES, f"{VENDOR_DIR}/**"])


# @spec TASK-REPO-011
def test_vendor_workflow_syncs_locked_before_comparing() -> None:
    """The job syncs from the lock with vendir pinned by mise, then compares the tree."""
    job = only_job(load_workflow(VENDOR_WORKFLOW))
    assert step_by_id(job, "sync")["run"].strip() == "vendir sync --locked"
    assert step_index(job, "mise") < step_index(job, "sync") < step_index(job, "compare")


def vendored_repo(root: Path) -> Path:
    """A committed repo holding the vendir files, one vendored file and one unrelated file."""
    return git_repo(
        root,
        {
            "vendir.yml": "directories: []\n",
            "vendir.lock.yml": "directories: []\n",
            f"{VENDOR_DIR}/oneyaml-python/LICENSE-MIT": "MIT\n",
            "README.md": "readme\n",
        },
    )


# @spec TASK-REPO-011
@pytest.mark.parametrize(
    ("change", "fails"),
    [
        ({}, False),
        ({"README.md": "changed\n"}, False),
        ({"vendir.yml": "changed\n"}, True),
        ({"vendir.lock.yml": "changed\n"}, True),
        ({f"{VENDOR_DIR}/oneyaml-python/LICENSE-MIT": "changed\n"}, True),
        ({f"{VENDOR_DIR}/oneyaml-python/new.py": "new\n"}, True),
    ],
    ids=["clean", "unrelated", "config", "lock", "vendored", "added"],
)
def test_vendor_workflow_fails_when_the_sync_changed_anything(
    tmp_path: Path, change: dict[str, str], *, fails: bool
) -> None:
    """After the sync, any change to the vendored files or the vendir files fails the job."""
    repo = vendored_repo(tmp_path / "repo")
    for name, content in change.items():
        (repo / name).write_text(content)
    job = only_job(load_workflow(VENDOR_WORKFLOW))
    result = StepRunner(tmp_path, repo, job).run("compare")
    assert (result.returncode != 0) is fails, result.output


# @spec TASK-REPO-011
def test_vendor_workflow_compare_step_reports_a_deleted_file(tmp_path: Path) -> None:
    """A file the sync removed counts as a change too."""
    repo = vendored_repo(tmp_path / "repo")
    (repo / VENDOR_DIR / "oneyaml-python" / "LICENSE-MIT").unlink()
    job = only_job(load_workflow(VENDOR_WORKFLOW))
    result = StepRunner(tmp_path, repo, job).run("compare")
    assert result.returncode != 0
    assert "LICENSE-MIT" in result.output


def task_runs(name: str, seen: set[str] | None = None) -> list[str]:
    """The `run` text of a mise task and of every task it depends on, transitively."""
    seen = set() if seen is None else seen
    if name in seen:
        return []
    seen.add(name)
    task = mise_config()["tasks"][name]
    run = task.get("run", [])
    runs = [run] if isinstance(run, str) else [str(line) for line in run]
    for dependency in task.get("depends", []):
        runs += task_runs(dependency, seen)
    return runs


# @spec TASK-REPO-012
def test_check_never_syncs_the_vendored_parser() -> None:
    """`mise run check` works offline; only CI's vendor workflow runs vendir."""
    runs = task_runs("check")
    assert runs
    assert not [run for run in runs if "vendir" in run]


# @spec TASK-REPO-013
def test_ruff_skips_the_vendored_parser() -> None:
    """The exclusion holds even when file names are passed, as a hook passes them."""
    config = tomllib.loads(RUFF_CONFIG.read_text(encoding="utf-8"))
    assert VENDOR_DIR in [path.rstrip("/") for path in config.get("extend-exclude", [])]
    assert config.get("force-exclude") is True


# @spec TASK-REPO-013
def test_ruff_passes_a_vendored_file_named_on_the_command_line() -> None:
    """Upstream's code isn't held to this repo's strict profile, even named explicitly."""
    named = f"{VENDOR_DIR}/oneyaml-python/src/oneyaml/_api.py"
    for command in (["check"], ["format", "--check"]):
        completed = subprocess.run(  # noqa: S603
            [require_tool("ruff"), *command, named],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr


# @spec TASK-REPO-014
def test_ty_skips_the_vendored_parser_and_resolves_it() -> None:
    """The type checker leaves `_vendor/` unchecked but finds `oneyaml` there for imports."""
    config = tomllib.loads(TY_CONFIG.read_text(encoding="utf-8"))
    excluded = [path.rstrip("/") for path in config.get("src", {}).get("exclude", [])]
    assert VENDOR_DIR in excluded
    extra = config.get("environment", {}).get("extra-paths", [])
    assert f"{VENDOR_DIR}/oneyaml-python/src" in extra


def ty_commands() -> list[list[str]]:
    """Every `ty` command line in this repo's mise tasks, commit hooks and workflows."""
    texts = [run for name in mise_config()["tasks"] for run in task_runs(name)]
    texts += [
        hook["entry"] for repo in tomllib.loads(PREK.read_text())["repos"] for hook in repo["hooks"]
    ]
    for workflow in (REPO_ROOT / ".github" / "workflows").glob("*.yml"):
        for job in load_workflow(workflow)["jobs"].values():
            texts += [step["run"] for step in job.get("steps", []) if "run" in step]
    lines = [line for text in texts for line in text.splitlines()]
    return [shlex.split(line) for line in lines if re.search(r"(^|\s)ty\s+check\b", line)]


# @spec TASK-REPO-014
def test_ty_runs_that_name_files_force_the_exclusion() -> None:
    """A `ty check` given file names passes `--force-exclude`, so `_vendor/` stays skipped."""
    commands = ty_commands()
    assert commands
    takes_value = {"--python", "--config-file", "--project", "--output-format", "--python-version"}
    for command in commands:
        arguments = command[command.index("check") + 1 :]
        named = [
            argument
            for index, argument in enumerate(arguments)
            if not argument.startswith("-") and not (index and arguments[index - 1] in takes_value)
        ]
        assert not named or "--force-exclude" in arguments, command


# @spec TASK-REPO-014
def test_hooks_that_run_ty_pass_no_file_names_or_force_the_exclusion() -> None:
    """A hook passes staged file names unless told not to, and mise hands them on to ty."""
    hooks = [hook for repo in tomllib.loads(PREK.read_text())["repos"] for hook in repo["hooks"]]
    for hook in hooks:
        entry = shlex.split(hook["entry"])
        runs = task_runs(entry[2]) if entry[:2] == ["mise", "run"] else [hook["entry"]]
        ty_lines = [
            line for run in runs for line in run.splitlines() if re.search(r"\bty\s+check\b", line)
        ]
        if ty_lines and hook.get("pass_filenames", True):
            assert all("--force-exclude" in line for line in ty_lines), hook
