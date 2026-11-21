"""Tests of the pilot's behaviour in the task tool, against small backlogs built in tmp_path.

The tool is the task-tracker skill's `scripts/tasks.py`; these tests predate its specs, and the
slices that implement the specs replace them with tests in `test_task_tool.py`.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import time
from typing import TYPE_CHECKING

import pytest

from tests.support import REPO_ROOT, TASK_TOOL, load_task_tool

tasks = load_task_tool()

if TYPE_CHECKING:
    from pathlib import Path

TODAY = dt.date(2026, 11, 16)
DEFAULTS = {
    "status": "To Do",
    "performer": "agent",
    "agent_tier": "fast",
    "type": "chore",
    "effort": "M",
    "priority": "medium",
    "created_date": "2026-11-16",
    "priority_set_by": "agent",
}
HUMAN = {"performer": "human", "agent_tier": None}


def write_task(root: Path, task_id: str, body: str = "", raw: str = "", /, **keys: object) -> Path:
    """Write one task file with default keys, overridden by `keys` (None drops a key).

    Args:
        root: The `backlog/` directory.
        task_id: The task's ID, which also names the file.
        body: The Markdown after the frontmatter.
        raw: Extra frontmatter lines, written as given.
        **keys: Frontmatter values, written quoted.
    """
    meta = {"id": task_id, "title": f"Task {task_id}", **DEFAULTS, **keys}
    lines = [f"{key}: {value!r}" for key, value in meta.items() if value is not None]
    folder = root / "tasks"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{task_id.lower()} - Task.md"
    path.write_text("---\n" + "\n".join(lines) + f"\n{raw}---\n\n" + body, encoding="utf-8")
    return path


def write_draft(root: Path, repo: str, slug: str, folder: str = "outbox", **keys: object) -> None:
    """Write one draft for another repo, under `outbox/` or `private/outbox/`."""
    meta = {"title": slug, **DEFAULTS, **keys}
    target = root / folder / repo
    target.mkdir(parents=True, exist_ok=True)
    text = "---\n" + "\n".join(f"{k}: {v!r}" for k, v in meta.items()) + "\n---\n"
    (target / f"{slug}.md").write_text(text, encoding="utf-8")


def load(root: Path, github: dict[str, bool] | None = None) -> tasks.Backlog:
    """Load and resolve a backlog, answering GitHub lookups from a table."""
    backlog = tasks.load(root, TODAY)
    tasks.resolve(backlog, (github or {}).get)
    return backlog


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """An empty backlog directory whose project is called `home`."""
    folder = tmp_path / "backlog"
    folder.mkdir()
    (folder / "config.yml").write_text('project_name: "home"\n', encoding="utf-8")
    return folder


def ids(rows: list[tuple[tasks.Task, float, list[str]]]) -> list[str]:
    """Return the task IDs of ranked rows."""
    return [task.id for task, _, _ in rows]


def test_a_clean_backlog_has_no_problems(root: Path) -> None:
    """Well-formed tasks produce no findings, in every date form Backlog.md and YAML allow."""
    write_task(root, "AD-1")
    write_task(root, "AD-2", type="decision", **HUMAN)
    write_task(root, "AD-3", created_date="2026-11-17T12:18:00Z", due_date="2026-12-01 09:00")
    write_task(root, "AD-4", "", "due_date: 2026-12-01\n", dependencies=["ad-1"])
    backlog = load(root)
    assert tasks.check(backlog) == []
    assert backlog.tasks["AD-4"].blockers == ["AD-1: Task AD-1"]
    assert len(tasks.queue(backlog, "all")) == 3


@pytest.mark.parametrize(
    ("keys", "body", "problem"),
    [
        ({"title": None}, "", "no title"),
        ({"status": "done"}, "", "status must be one of"),
        ({"performer": "robot"}, "", "performer must be"),
        ({"agent_tier": None}, "", "needs agent_tier"),
        ({"type": "decision"}, "", "a decision is the developer's"),
        ({"effort": "XL"}, "", "effort must be"),
        ({"priority": "urgent"}, "", "priority must be"),
        ({"priority_set_by": "robot"}, "", "priority_set_by must be"),
        ({"onStatusChange": "touch x"}, "", "onStatusChange"),
        ({"deadline_kind": "hard"}, "", "deadline_kind without due_date"),
        ({"deadline_kind": "firm", "due_date": "2026-12-01"}, "", "deadline_kind must be"),
        ({"due_date": "Nov 20"}, "", "not a date (YYYY-MM-DD): due_date"),
        ({"created_date": "10 Nov 2026"}, "", "not a date (YYYY-MM-DD): created_date"),
        ({"defer_until": "1 Dec 2026"}, "", "not a date (YYYY-MM-DD): defer_until"),
        ({"dependencies": ["AD-9"]}, "", "AD-9 (unknown)"),
        ({"external_blockers": ["somewhere"]}, "", "external blocker 'somewhere'"),
        ({**HUMAN}, "- [ ] #1 write it [agent]\n", "split it out"),
    ],
)
def test_check_names_the_problem(
    root: Path, keys: dict[str, object], body: str, problem: str
) -> None:
    """Each schema, link and granularity rule reports its own finding, and no command crashes."""
    write_task(root, "AD-1", body, **keys)
    backlog = load(root)
    found = tasks.check(backlog)
    assert any(problem in line for line in found), found
    tasks.board(backlog, root)
    tasks.brief(backlog)


def test_check_finds_problems_that_span_files(root: Path) -> None:
    """Cycles (through a parent too), repeated and missing IDs, parents, pins and file names."""
    write_task(root, "AD-1", dependencies=["AD-2"])
    write_task(root, "AD-2", dependencies=["AD-1"])
    write_task(root, "AD-3", status="Done")
    write_task(root, "AD-3.1", parent_task_id="AD-3")
    write_task(root, "AD-4")
    write_task(root, "AD-4.1", parent_task_id="AD-4", dependencies=["AD-4"])
    write_task(root, "AD-5").rename(root / "tasks" / "misnamed.md")
    tasks_dir = root / "tasks"
    (tasks_dir / "ad-1 - Zcopy.md").write_text("---\nid: AD-1\n---\n", encoding="utf-8")
    (tasks_dir / "ad-7 - No-id.md").write_text("---\nid:\ntitle: x\n---\n", encoding="utf-8")
    (tasks_dir / "ad-8 - Bad.md").write_text("---\ntitle: a: b\n---\n", encoding="utf-8")
    (root / "focus.yml").write_text("pins: [AD-3]\n", encoding="utf-8")
    write_draft(root, "other", "has-an-id", id="OT-1")
    found = "\n".join(tasks.check(load(root)))
    for problem in (
        "AD-1: is in a dependency cycle",
        "AD-4.1: is in a dependency cycle",
        "id AD-1 is already used",
        "ad-7 - No-id.md: no id",
        "ad-8 - Bad.md: frontmatter isn't valid YAML",
        "AD-3: closed while a subtask is open",
        "pin AD-3 isn't an open task",
        "AD-5: file name 'misnamed.md' doesn't start with the id",
        "other/has-an-id: an outbox draft has no id",
    ):
        assert problem in found


def test_config_rules(root: Path) -> None:
    """A status callback in config.yml is a finding, and `types` there limits a task's type."""
    config = 'project_name: "home"\ntypes: ["chore"]\nonStatusChange: "touch x"\n'
    (root / "config.yml").write_text(config, encoding="utf-8")
    write_task(root, "AD-1", type="bogus")
    found = "\n".join(tasks.check(load(root)))
    assert "config.yml: status-change callbacks aren't allowed" in found
    assert "AD-1: type must be one of ['chore']" in found


def test_blocked_tasks_and_parents_are_not_ready(root: Path) -> None:
    """Open dependencies, open subtasks and a future or unreadable defer date block a task."""
    write_task(root, "AD-1", **HUMAN)
    write_task(root, "AD-2", dependencies=["AD-1"])
    write_task(root, "AD-3", dependencies=["AD-4"])
    write_task(root, "AD-4", status="Done")
    write_task(root, "AD-5")
    write_task(root, "AD-5.1", parent_task_id="AD-5")
    write_task(root, "AD-6", defer_until="2026-12-01")
    write_task(root, "AD-7", defer_until="2026-11-16")
    write_task(root, "AD-8", defer_until="next week")
    backlog = load(root)
    assert sorted(ids(tasks.queue(backlog, "agent"))) == ["AD-3", "AD-5.1", "AD-7"]
    assert ids(tasks.queue(backlog, "human")) == ["AD-1"]


def test_external_blockers_fail_closed_without_failing_lint(root: Path) -> None:
    """Only a blocker read as closed unblocks; open and unreadable ones block, and aren't lint."""
    write_task(root, "AD-1", external_blockers=["gh:o/r#1"])
    write_task(root, "AD-2", external_blockers=["gh:o/r#2"])
    write_task(root, "AD-3", external_blockers=["gh:o/r#3"])
    write_task(root, "AD-4", external_blockers=["other/fix-it"])
    write_task(root, "AD-5", external_blockers=["home#AD-1"])
    write_task(root, "AD-6", external_blockers=["other#OT-3", "other/missing-draft"])
    write_task(root, "AD-7", status="Done")
    write_task(root, "AD-8", external_blockers=["home#AD-7"])
    write_task(root, "AD-9", status="Done", external_blockers=["gh:o/r#3"])
    write_draft(root, "other", "fix-it")
    backlog = load(root, {"gh:o/r#1": True, "gh:o/r#2": False})
    assert ids(tasks.queue(backlog, "all", "home")) == ["AD-1", "AD-8"]
    assert backlog.tasks["AD-2"].blockers == ["gh:o/r#2 (open)"]
    assert backlog.tasks["AD-3"].blockers == ["gh:o/r#3 (unreadable)"]
    assert len(backlog.tasks["AD-6"].blockers) == 2
    assert backlog.tasks["AD-9"].blockers == []
    assert backlog.tasks["other/fix-it"].unblocks == {"AD-4"}
    assert backlog.tasks["AD-1"].unblocks == {"AD-5"}
    assert tasks.check(backlog) == []


def test_forge_qualified_blockers_are_read_like_short_ones(root: Path) -> None:
    """The form the skill's format reference gives passes lint, and resolves in this backlog.

    The pilot compares only the repo's name with `project_name`; AD-5.3 replaces this with the
    forge-path comparison its specs give.
    """
    write_task(root, "AD-1", status="Done")
    write_task(root, "AD-2", external_blockers=["github.com/o/home#AD-1"])
    write_task(root, "AD-3", external_blockers=["github.com/o/other#OT-3"])
    backlog = load(root)
    assert ids(tasks.queue(backlog, "all", "home")) == ["AD-2"]
    assert backlog.tasks["AD-3"].blockers == ["github.com/o/other#OT-3 (unreadable)"]
    assert tasks.check(backlog) == []


def test_rank_is_pins_then_hard_deadlines_then_score(root: Path) -> None:
    """Pins keep their order; a hard deadline within a week comes next; the rest go by score."""
    write_task(root, "AD-1", priority="high")
    write_task(root, "AD-2", priority="low")
    write_task(root, "AD-3", priority="low", due_date="2026-11-18", deadline_kind="hard")
    write_task(root, "AD-4", priority="low")
    write_task(root, "AD-5", priority="high", due_date="2026-11-18", deadline_kind="soft")
    write_task(root, "AD-6", priority="low", due_date="2026-12-16", deadline_kind="hard")
    (root / "focus.yml").write_text("pins: [ad-4, AD-2]\n", encoding="utf-8")
    order = ids(tasks.queue(load(root), "agent"))
    assert order == ["AD-4", "AD-2", "AD-3", "AD-5", "AD-1", "AD-6"]


def test_a_single_pin_may_be_written_without_a_list(root: Path) -> None:
    """`pins: AD-2` pins that task rather than its characters."""
    write_task(root, "AD-1", priority="high")
    write_task(root, "AD-2", priority="low")
    (root / "focus.yml").write_text("pins: AD-2\n", encoding="utf-8")
    backlog = load(root)
    assert ids(tasks.queue(backlog, "agent")) == ["AD-2", "AD-1"]
    assert tasks.check(backlog) == []


def test_unblocking_more_work_ranks_higher_and_is_explained(root: Path) -> None:
    """Open tasks that wait on a task, through other tasks or a parent, raise its rank."""
    write_task(root, "AD-1", **HUMAN)
    write_task(root, "AD-2", **HUMAN)
    write_task(root, "AD-3", dependencies=["AD-2"])
    write_task(root, "AD-4", dependencies=["AD-3"], **HUMAN)
    write_task(root, "AD-5", dependencies=["AD-2"], status="Done")
    write_task(root, "AD-6")
    write_task(root, "AD-6.1", parent_task_id="AD-6")
    write_task(root, "AD-7", dependencies=["AD-6"])
    backlog = load(root)
    rows = tasks.queue(backlog, "human")
    assert ids(rows) == ["AD-2", "AD-1"]
    assert backlog.tasks["AD-2"].unblocks == {"AD-3", "AD-4"}
    assert "unblocks 2 (1 for agents) 2.8" in rows[0][2]
    assert "unblocks: AD-4 Task AD-4" in tasks.why(backlog, "ad-2")
    assert backlog.tasks["AD-6.1"].unblocks == {"AD-6", "AD-7"}


@pytest.mark.parametrize(
    ("keys", "term"),
    [
        ({"status": "In Progress"}, "in progress 4.0"),
        ({"waiting": "a reviewer"}, "a reviewer is waiting 3.0"),
        ({"created_date": "2026-05-18"}, "age 182d 1.0"),
        ({"effort": "S"}, "effort S 2.0"),
        ({"due_date": "2026-11-18", "deadline_kind": "hard"}, "hard deadline in 2d 7.9"),
    ],
)
def test_each_score_term_is_shown(root: Path, keys: dict[str, object], term: str) -> None:
    """Work in progress, someone waiting, age, small effort and a deadline each add a term."""
    write_task(root, "AD-1", **keys)
    backlog = load(root)
    assert term in tasks.score(backlog, backlog.tasks["AD-1"])[2]


def test_weights_come_from_the_focus_file(root: Path) -> None:
    """A weight in focus.yml replaces the default and can reorder the queue."""
    write_task(root, "AD-1", priority="high", effort="L")
    write_task(root, "AD-2", priority="low", effort="S")
    assert ids(tasks.queue(load(root), "agent")) == ["AD-1", "AD-2"]
    (root / "focus.yml").write_text("weights: {effort_S: 9.0}\n", encoding="utf-8")
    assert ids(tasks.queue(load(root), "agent")) == ["AD-2", "AD-1"]
    (root / "focus.yml").write_text("- AD-1\n", encoding="utf-8")
    assert "focus.yml: must be a mapping with `pins` and `weights`" in tasks.check(load(root))


def test_board_and_brief_separate_the_developer_from_agents(root: Path) -> None:
    """The board lists ready work per performer, with links, and drafts for other repos."""
    write_task(root, "AD-1", type="decision", title="p | q", **HUMAN)
    write_task(root, "AD-2", dependencies=["AD-1"])
    write_task(root, "AD-3", agent_tier="strong")
    write_task(root, "AD-4")
    write_task(root, "AD-4.1", parent_task_id="AD-4")
    write_draft(root, "other", "fix-it")
    (root / "focus.yml").write_text("pins: [AD-2]\n", encoding="utf-8")
    backlog = load(root)
    page = tasks.board(backlog, root)
    developer, agents = page.split("## For agents: ready now")
    assert "[AD-1](tasks/ad-1%20-%20Task.md) | p \\| q |" in developer.split("## For the dev")[1]
    assert "Task AD-2 (blocked)" in developer.split("## For the developer")[0]
    ready_agents, rest = agents.split("## Bottlenecks")
    assert "[AD-3]" in ready_agents
    assert "[AD-2]" not in ready_agents
    assert "| p \\| q | human | yes | 1 |" in rest
    assert "Task AD-4: waits on its open subtasks" in rest
    assert "| For the agents | 2 | 2 | 4 |" in page
    assert "| For other repos (outbox) | | | 1 |" in page
    assert "## For other" in page
    assert "AD-3 [strong, M] Task AD-3" in tasks.brief(backlog)


def test_private_drafts_stay_off_the_public_board(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Drafts under private/ load only with --private."""
    write_task(root, "AD-1")
    write_draft(root, "secret", "hidden-work", folder="private/outbox")
    assert tasks.main(["--root", str(root), "--offline", "board"]) == 0
    assert "hidden-work" not in capsys.readouterr().out
    assert tasks.main(["--root", str(root), "--offline", "--private", "board"]) == 0
    assert "hidden-work" in capsys.readouterr().out


def test_the_command_line_reports_problems_and_stays_offline(
    root: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """`check` exits 1 on a finding, and --offline leaves a GitHub blocker blocking, unasked."""
    monkeypatch.setenv("PATH", str(root))  # no gh to find, should the tool look for one
    write_task(root, "AD-1", external_blockers=["gh:o/r#1"])
    assert tasks.main(["--root", str(root), "--offline", "check"]) == 0
    assert tasks.main(["--root", str(root), "--offline", "next"]) == 0
    assert "AD-1" not in capsys.readouterr().out.replace("1 tasks", "")
    write_task(root, "AD-2", effort="XL")
    assert tasks.main(["--root", str(root), "--offline", "check"]) == 1
    assert "AD-2: effort must be" in capsys.readouterr().out


def test_help_lists_the_commands_without_a_backlog(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`help` prints the usage and needs no backlog directory."""
    assert tasks.main(["--root", str(tmp_path / "missing"), "help"]) == 0
    shown = capsys.readouterr().out
    assert shown.startswith("usage: tasks ")
    for command in ("check", "next", "why", "board", "brief"):
        assert command in shown


def fake_gh(folder: Path, state: str, status: int = 0) -> None:
    """Put a `gh` in `folder` that prints `state`, counts its calls and exits with `status`."""
    script = f'#!/bin/sh\necho call >> "{folder}/calls"\necho {state}\nexit {status}\n'
    (folder / "gh").write_text(script, encoding="utf-8")
    (folder / "gh").chmod(0o755)


def test_github_state_is_cached_and_unreadable_when_gh_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A lookup is cached for six hours; a failed `gh` or a damaged cache reads as unknown."""
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}/usr/bin{os.pathsep}/bin")
    cache = tmp_path / "cache" / "github.json"
    fake_gh(tmp_path, "closed")
    assert tasks.github_state("gh:o/r#1", cache) is True
    fake_gh(tmp_path, "open")
    assert tasks.github_state("gh:o/r#1", cache) is True  # answered from the cache
    assert (tmp_path / "calls").read_text(encoding="utf-8").count("call") == 1
    stale = {"gh:o/r#1": {"closed": True, "at": time.time() - tasks.CACHE_SECONDS - 1}}
    cache.write_text(json.dumps(stale), encoding="utf-8")
    assert tasks.github_state("gh:o/r#1", cache) is False
    cache.write_text("{not json", encoding="utf-8")
    assert tasks.github_state("gh:o/r#2", cache) is False
    fake_gh(tmp_path, "closed", status=1)
    assert tasks.github_state("gh:o/r#3", cache) is None
    fake_gh(tmp_path, "merged")
    assert tasks.github_state("gh:o/r#4", cache) is None
    (tmp_path / "gh").unlink()
    assert tasks.github_state("gh:o/r#5", cache) is None


def test_the_repo_backlog_passes_its_own_check(tmp_path: Path) -> None:
    """This repo's backlog has no findings; GitHub blockers aren't looked up."""
    command = [sys.executable, str(TASK_TOOL), "--offline"]
    command += ["--root", str(REPO_ROOT / "backlog"), "check"]
    result = subprocess.run(  # noqa: S603
        command, capture_output=True, text=True, cwd=tmp_path, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_every_view_renders_the_repo_backlog() -> None:
    """The queues, the board and the brief all build from this repo's real task files."""
    root = REPO_ROOT / "backlog"
    backlog = tasks.load(root)
    tasks.resolve(backlog, lambda _ref: None)
    assert tasks.queue(backlog, "all")
    assert "## Bottlenecks" in tasks.board(backlog, root)
    assert backlog.home in tasks.brief(backlog)
