"""Tests of the Backlog.md behaviour the task backlog depends on, run against the pinned CLI."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import yaml

from scripts import tasks
from tests.support import REPO_ROOT, git_repo, require_tool

CONFIG = REPO_ROOT / "backlog" / "config.yml"
# The keys this repo adds to a task. Backlog.md must copy them through as written, so the block
# mixes the styles hand-written files use (an unindented list, an unquoted date) with its own.
CUSTOM = """\
performer: human
effort: M
external_blockers:
- gh:example/repo#12
- other-repo/a-draft
deadline_kind: soft
defer_until: 2026-12-01
waiting: the template's first consumer
priority_set_by: human
provenance:
  repo: other-repo
  filed_by: agent
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


def test_a_cli_edit_keeps_custom_keys_and_the_body(tmp_path: Path) -> None:
    """A status change through the pinned CLI leaves the custom keys and the body as written."""
    name = "backlog/tasks/ad-1 - Keep-the-custom-keys.md"
    files = {"backlog/config.yml": CONFIG.read_text(encoding="utf-8"), name: TASK}
    repo = git_repo(tmp_path / "repo", files)
    home = tmp_path / "home"
    home.mkdir()
    # The CLI is a launcher that runs `node`, so the pinned node goes on PATH beside it.
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
    assert yaml.safe_load(CUSTOM).items() <= meta.items(), "a custom key was lost or changed"
    assert CUSTOM in text, "the custom keys were re-serialized, not copied"
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
    return tasks.check(backlog)
