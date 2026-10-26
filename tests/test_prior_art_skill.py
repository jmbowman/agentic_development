"""Structure tests of the prior-art search skill, its plugin packaging and its eval suite."""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from tests.support import REPO_ROOT

if TYPE_CHECKING:
    from pathlib import Path

SKILLS = REPO_ROOT / "skills"
SKILL = SKILLS / "prior-art-search"
SKILL_MD = SKILL / "SKILL.md"
REFERENCES = SKILL / "references"
PLUGIN_JSON = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
EVALS = REPO_ROOT / "evals"
SPECS = REPO_ROOT / "docs" / "intent" / "prior-art-search" / "prior-art-search-specs.md"

EVIDENCE_RECORD = (
    "{candidate, url, criterion, claim, support, evidence, "
    "evidence_kind, read_depth, commit, as_of}"
)
LEDGER_RECORD = "{route, state, queries, reason, as_of}"
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
NOTE_SECTIONS = [
    "Need and criteria",
    "Verdict",
    "Candidates and matrix",
    "Limitations checked in source",
    "Coverage ledger",
    "Snowball rounds",
    "Refresh trigger",
]


def frontmatter(path: Path) -> dict[str, Any]:
    """The YAML frontmatter of a Markdown file."""
    match = re.match(r"---\n(.*?)\n---\n", path.read_text(), flags=re.DOTALL)
    assert match, f"{path} has no frontmatter"
    return yaml.safe_load(match.group(1))


def eval_cases() -> list[Path]:
    """Every eval case directory: one that holds a `prompt.md` or a `case.yaml`."""
    return sorted(
        {p.parent for p in EVALS.rglob("prompt.md")} | {p.parent for p in EVALS.rglob("case.yaml")}
    )


def eval_spec_ids() -> list[str]:
    """The IDs of the specs marked as verified only by behavior evals."""
    pattern = r"\*\*(PRIOR-[A-Z]+-\d{3})\*\*:.*\*\(eval\)\*$"
    return [m.group(1) for m in re.finditer(pattern, SPECS.read_text(), re.MULTILINE)]


def cited_by_evals() -> dict[str, list[str]]:
    """Each spec ID cited in an eval case's `case.yaml`, with the cases that cite it."""
    cited: dict[str, list[str]] = {}
    for case in eval_cases():
        text = (case / "case.yaml").read_text() if (case / "case.yaml").exists() else ""
        for line in re.findall(r"^#\s*@spec\s+(.+)$", text, flags=re.MULTILINE):
            for spec in re.split(r",\s*", line.strip()):
                cited.setdefault(spec, []).append(case.name)
    return cited


# @spec PRIOR-PKG-001
def test_plugin_manifest() -> None:
    """The repo root is the plugin, and APM's tags version it rather than a manifest field."""
    manifest = json.loads(PLUGIN_JSON.read_text())
    assert manifest["name"] == "agentic-development"
    assert manifest["description"].strip()
    assert manifest["author"]["name"].strip()
    assert manifest["license"] == "Apache-2.0"
    assert manifest["repository"].startswith("https://")
    assert "version" not in manifest


# @spec PRIOR-PKG-002
def test_marketplace_lists_the_root_plugin() -> None:
    """A developer can install the package as a local plugin from this repo."""
    plugins = json.loads(MARKETPLACE_JSON.read_text())["plugins"]
    assert [(p["name"], p["source"]) for p in plugins] == [("agentic-development", "./")]


# @spec PRIOR-PKG-003
def test_skill_frontmatter_uses_only_agent_skills_fields() -> None:
    """Frontmatter limited to the spec's fields keeps the skill portable."""
    meta = frontmatter(SKILL_MD)
    assert sorted(meta) == ["description", "license", "name"]
    assert meta["name"] == "prior-art-search" == SKILL.name
    assert 0 < len(meta["description"].strip()) <= 1024
    assert meta["license"] == "Apache-2.0"


# @spec PRIOR-PKG-004
def test_skill_md_is_under_500_lines() -> None:
    """The Agent Skills spec asks for a short main file, with detail in references."""
    assert len(SKILL_MD.read_text().splitlines()) < 500


# @spec PRIOR-PKG-005
def test_skill_md_references_exist() -> None:
    """Every relative path the skill points the agent at is there to read."""
    text = SKILL_MD.read_text()
    links = [
        link
        for link in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text)
        if not re.match(r"[a-z]+:", link)
    ]
    paths = links + re.findall(r"`((?:references|scripts|assets)/[^`\s]+)`", text)
    assert paths
    inside = SKILL.resolve()
    missing = [
        path
        for path in paths
        if not (SKILL / path).is_file() or not (SKILL / path).resolve().is_relative_to(inside)
    ]
    assert not missing, missing


# @spec PRIOR-PKG-006
@pytest.mark.parametrize("name", ["sources.md", "verification.md", "note-template.md"])
def test_reference_file_exists(name: str) -> None:
    """The skill's detail lives in three reference files."""
    assert (REFERENCES / name).is_file()


# @spec PRIOR-PKG-007
def test_skill_text_has_no_spec_annotations() -> None:
    """Annotations in skill text would load into the agent's context on every run."""
    annotated = [p for p in SKILL.rglob("*") if p.is_file() and "@spec" in p.read_text()]
    assert not annotated, annotated


# @spec PRIOR-PKG-008
def test_route_table_has_its_columns_and_a_skill_catalog_route() -> None:
    """The route table drives route selection, including for agent-skill needs."""
    rows = [
        [cell.strip().lower() for cell in line.strip().strip("|").split("|")]
        for line in (REFERENCES / "sources.md").read_text().splitlines()
        if line.lstrip().startswith("|")
    ]
    assert rows
    assert rows[0][:4] == ["route", "trigger", "good for", "tactics"]
    triggers = [row[1] for row in rows[2:]]
    assert any(re.search(r"skill|plugin|mcp", trigger) for trigger in triggers)


# @spec PRIOR-PKG-009
@pytest.mark.parametrize("record", [EVIDENCE_RECORD, LEDGER_RECORD])
def test_verification_defines_record_shape(record: str) -> None:
    """Subagents return records in these exact shapes."""
    assert record in (REFERENCES / "verification.md").read_text()


# @spec PRIOR-PKG-010
def test_note_template_has_every_section() -> None:
    """A saved note has the same sections every time, so notes can be compared."""
    headings = re.findall(
        r"^##\s+(.+?)\s*$", (REFERENCES / "note-template.md").read_text(), flags=re.MULTILINE
    )
    assert [h.lower() for h in headings] == [s.lower() for s in NOTE_SECTIONS]


# @spec PRIOR-PKG-015
def test_skill_carries_its_license() -> None:
    """A copy of the skill in another repo keeps the license text Apache-2.0 requires."""
    assert (SKILL / "LICENSE.txt").read_text() == (REPO_ROOT / "LICENSE").read_text()


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


def test_eval_citations_name_eval_specs() -> None:
    """Eval cases cite only specs that the specs file marks as verified by evals."""
    stray = sorted(set(cited_by_evals()) - set(eval_spec_ids()))
    assert not stray, stray


# The behavior evals run by hand, and lidc reads `@spec` only in test code, so this test
# carries the citations for every eval-verified spec and checks an eval case exercises each.
# @spec PRIOR-TRIG-001, PRIOR-TRIG-002, PRIOR-TRIG-003
# @spec PRIOR-EFF-001, PRIOR-EFF-002, PRIOR-EFF-003, PRIOR-EFF-004
# @spec PRIOR-EFF-005, PRIOR-EFF-006, PRIOR-EFF-007
# @spec PRIOR-SRCH-001, PRIOR-SRCH-002, PRIOR-SRCH-003, PRIOR-SRCH-004, PRIOR-SRCH-005
# @spec PRIOR-SRCH-006, PRIOR-SRCH-007, PRIOR-SRCH-008, PRIOR-SRCH-009, PRIOR-SRCH-010
# @spec PRIOR-SRCH-011, PRIOR-SRCH-012
# @spec PRIOR-CLS-001, PRIOR-CLS-002, PRIOR-CLS-003, PRIOR-CLS-004, PRIOR-CLS-005, PRIOR-CLS-006
# @spec PRIOR-CLS-007, PRIOR-CLS-008, PRIOR-CLS-009, PRIOR-CLS-010, PRIOR-CLS-011, PRIOR-CLS-012
# @spec PRIOR-LIC-001, PRIOR-LIC-002, PRIOR-LIC-003, PRIOR-LIC-004, PRIOR-LIC-005, PRIOR-LIC-006
# @spec PRIOR-SRC-001, PRIOR-SRC-002, PRIOR-SRC-003, PRIOR-SRC-004, PRIOR-SRC-005
# @spec PRIOR-SRC-006, PRIOR-SRC-007, PRIOR-SRC-008, PRIOR-SRC-009
# @spec PRIOR-SKL-001, PRIOR-SKL-002, PRIOR-SKL-003, PRIOR-SKL-004, PRIOR-SKL-005
# @spec PRIOR-RPT-001, PRIOR-RPT-002, PRIOR-RPT-003, PRIOR-RPT-004, PRIOR-RPT-005, PRIOR-RPT-006
# @spec PRIOR-RPT-007
# @spec PRIOR-SAVE-001, PRIOR-SAVE-002, PRIOR-SAVE-003, PRIOR-SAVE-004
# @spec PRIOR-SAVE-005, PRIOR-SAVE-006, PRIOR-SAVE-007, PRIOR-SAVE-008
# @spec PRIOR-PRIV-001, PRIOR-PRIV-002, PRIOR-PRIV-003, PRIOR-PRIV-004
@pytest.mark.parametrize("spec", eval_spec_ids())
def test_eval_spec_is_exercised_by_an_eval_case(spec: str) -> None:
    """Every eval-verified spec has at least one eval case that exercises it."""
    assert spec in cited_by_evals()
