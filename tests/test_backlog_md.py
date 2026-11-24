"""Tests of the Backlog.md behaviour the task backlog depends on, run against the pinned CLI."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from tests.support import REPO_ROOT, git_repo, load_task_tool, require_tool

tasks = load_task_tool()

CONFIG = REPO_ROOT / "backlog" / "config.yml"
# Every custom key a task or draft can carry. Backlog.md must keep their values, so the block
# mixes the styles hand-written files use (an unindented list, an unquoted date) with its own.
CUSTOM = """\
performer: human
agent_tier: moderate
effort: M
external_blockers:
- gh:example/repo#12
- github.com/example/other-repo#OR-3
- other-repo/a-draft
deadline_kind: soft
defer_until: 2026-12-01
waiting: the template's first consumer
priority_set_by: human
sessions:
- agent: claude-code
  id: 0b5c3f7e-1d2a-4c8b-9e6f-123456789abc
  role: created
  date: '2026-11-16'
- agent: claude-code
  id: 7d0e9a41-5b6c-4f3e-8a2d-abcdef012345
  role: worked
  date: 2026-11-17
target: github.com/example/other-repo
"""
BODY = """
## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A task with `inline code` and a path, `backlog/config.yml`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The draft is written [agent]
- [ ] #2 The developer files it
<!-- AC:END -->
"""
TASK = f"""\
---
id: AD-1
title: Keep the custom keys
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
dependencies: []
priority: medium
type: chore
{CUSTOM}---
{BODY}"""


def test_this_repos_config_keeps_backlog_md_from_git_and_shell() -> None:
    """The config turns off remote git operations and auto-commit, and sets no status callback."""
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert config["remote_operations"] is False
    assert config["auto_commit"] is False
    assert not {"onStatusChange", "on_status_change"} & set(config)


# @spec TASK-REPO-006
def test_a_cli_edit_keeps_custom_keys_and_the_body(tmp_path: Path) -> None:
    """A status change through the pinned CLI leaves the custom keys and the body as written."""
    name = "backlog/tasks/ad-1 - Keep-the-custom-keys.md"
    files = {"backlog/config.yml": CONFIG.read_text(encoding="utf-8"), name: TASK}
    repo = git_repo(tmp_path / "repo", files)
    home = tmp_path / "home"
    home.mkdir()
    # The CLI is a launcher that runs `node`, so the pinned node goes on PATH beside it.
    if shutil.which("backlog") is None:
        pytest.skip("the pinned Backlog.md CLI isn't on PATH")
    tools = [str(Path(require_tool(tool)).parent) for tool in ("backlog", "node")]
    result = subprocess.run(  # noqa: S603
        [require_tool("backlog"), "task", "edit", "1", "-s", "In Progress"],
        cwd=repo,
        env={"HOME": str(home), "PATH": os.pathsep.join([*tools, "/usr/bin", "/bin"])},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    text = (repo / name).read_text(encoding="utf-8")
    meta, body = tasks.split_frontmatter(text)
    assert meta["status"] == "In Progress"
    # Read with the tool's own parser, so an unquoted date compares as the tool reads it.
    expected = tasks.parse_yaml(CUSTOM)
    lost = {key: value for key, value in expected.items() if meta.get(key) != value}
    assert not lost, f"a custom key was lost or changed: {lost}"
    assert body == BODY
    assert "split it out" in "\n".join(_lint(repo / "backlog"))
    changed = subprocess.run(
        ["git", "status", "--porcelain"],  # noqa: S607
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    assert changed.stdout.strip() == f'M "{name}"'
    assert not list(home.iterdir())


def _lint(root: Path) -> list[str]:
    """Return the task tool's findings for a backlog, without asking GitHub."""
    backlog = tasks.load(root)
    tasks.resolve(backlog, lambda _ref: None)
    return [str(problem) for problem in tasks.check(backlog)]
