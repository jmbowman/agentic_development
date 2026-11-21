"""Tests of the task-tracker skill's task tool against its specs, on backlogs built in tmp_path."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support import load_task_tool, small_backlog

if TYPE_CHECKING:
    from pathlib import Path

tasks = load_task_tool()


def files_under(root: Path) -> set[Path]:
    """Every file under a directory, so a test can see whether a command wrote one."""
    return {path for path in root.rglob("*") if path.is_file()}


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
