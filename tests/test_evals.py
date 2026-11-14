"""Checks that every skill's eval suite loads in `claude plugin eval`."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
import yaml

from tests.support import EVALS, SKILLS, eval_cases, frontmatter

if TYPE_CHECKING:
    from pathlib import Path

# What `claude plugin eval` accepts (code.claude.com/docs/en/plugin-evals); anything else fails.
PROMPT_KEYS = {
    "schema_version",
    "name",
    "description",
    "tags",
    "plugins",
    "runs",
    "expected_outcome",
    "model",
    "max_turns",
    "timeout_seconds",
    "allowed_tools",
    "append_system_prompt",
    "env",
}
GRADER_TYPES = {"regex", "tool_used", "tool_order", "file_exists", "llm", "baseline"}
GRADER_ARMS = {"with-only", "both"}


@pytest.mark.parametrize("case", eval_cases(), ids=lambda p: p.name)
def test_eval_case_loads(case: Path) -> None:
    """Each eval case has a case file named for its directory, a prompt and a grader."""
    meta = yaml.safe_load((case / "case.yaml").read_text())
    assert meta["schema_version"] == "1.1"
    assert meta["name"] == case.name
    assert (case / "prompt.md").is_file()
    assert list((case / "graders").glob("*.md"))
    if scaffold := meta.get("context", {}).get("scaffold_script"):
        assert (case / scaffold).is_file()


@pytest.mark.parametrize("case", eval_cases(), ids=lambda p: p.name)
def test_eval_case_is_grouped_under_its_skill(case: Path) -> None:
    """Each skill's cases live in `evals/<skill>/` and carry its tag, so one suite runs alone."""
    skill = case.parent
    assert skill.parent == EVALS
    assert (SKILLS / skill.name / "SKILL.md").is_file()
    assert skill.name in frontmatter(case / "prompt.md")["tags"]


@pytest.mark.parametrize("case", eval_cases(), ids=lambda p: p.name)
def test_eval_prompt_frontmatter_is_valid(case: Path) -> None:
    """Prompt settings stay within what the runner accepts, and say whether a case needs network."""
    meta = frontmatter(case / "prompt.md")
    assert set(meta) <= PROMPT_KEYS
    assert len({"online", "offline"} & set(meta["tags"])) == 1
    assert 0 < meta["max_turns"] <= 200
    assert 0 < meta["timeout_seconds"] <= 3600


@pytest.mark.parametrize(
    "grader",
    sorted(EVALS.glob("*/*/graders/*.md")),
    ids=lambda p: f"{p.parent.parent.name}/{p.stem}",
)
def test_eval_grader_frontmatter_is_valid(grader: Path) -> None:
    """Each grader has a known type, and an arm only where the runner defines one."""
    meta = frontmatter(grader)
    assert meta["type"] in GRADER_TYPES
    assert meta.get("arm", "with-only") in GRADER_ARMS


REGEX_KEYS = ("pattern", "input_match")
# Inline flag groups (`(?i)`, `(?-i)`, `(?i-m:`), not `(?:`, lookarounds or named groups.
INLINE_FLAGS = re.compile(r"\(\?(?=-?[a-zA-Z])[a-zA-Z]*(?:-[a-zA-Z]+)?[):]")


@pytest.mark.parametrize(
    "grader",
    [g for g in sorted(EVALS.glob("*/*/graders/*.md")) if set(REGEX_KEYS) & set(frontmatter(g))],
    ids=lambda p: f"{p.parent.parent.name}/{p.stem}",
)
def test_eval_grader_regex_has_no_inline_flags(grader: Path) -> None:
    """The runner compiles regexes as JavaScript, which rejects inline flags; use `flags:`."""
    meta = frontmatter(grader)
    assert not [key for key in REGEX_KEYS if INLINE_FLAGS.search(str(meta.get(key, "")))]


@pytest.mark.parametrize(
    ("regex", "flagged"),
    [
        ("(?i)crlf", True),
        ("(?im)crlf", True),
        ("(?-i)crlf", True),
        ("(?i:crlf)", True),
        ("(?i-m:crlf)", True),
        ("(?-i:crlf)", True),
        ("(?:crlf)", False),
        ("(?=crlf)", False),
        ("(?!crlf)", False),
        ("(?<=crlf)", False),
        ("(?<!crlf)", False),
        ("(?<name>crlf)", False),
    ],
)
def test_inline_flag_detector(regex: str, *, flagged: bool) -> None:
    """The detector catches every inline-flag form and passes over other group syntax."""
    assert bool(INLINE_FLAGS.search(regex)) is flagged
