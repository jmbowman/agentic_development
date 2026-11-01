"""Structure tests of the session wrap-up skill and its eval suite."""

from __future__ import annotations

import re

import pytest

from tests.support import EVALS, REPO_ROOT, SKILLS, cited_by_evals, eval_cases, frontmatter

SKILL = SKILLS / "session-wrap-up"
SKILL_MD = SKILL / "SKILL.md"
ROUTING = SKILL / "references" / "routing.md"
SUITE = EVALS / "session-wrap-up"
MANUAL = SUITE / "manual.md"
INTENT = REPO_ROOT / "docs" / "intent" / "session-wrap-up"
SPECS = INTENT / "session-wrap-up-specs.md"
DESIGN = INTENT / "session-wrap-up-design.md"
THIS_FILE = REPO_ROOT / "tests" / "test_session_wrap_up_skill.py"

# The slices whose specs are delivered. Each slice adds its number when it lands.
DELIVERED_SLICES = {1, 2}

FILTER_TESTS = ["reusable", "non-obvious", "stable", "actionable"]


def table_rows(text: str) -> list[list[str]]:
    """The cells of the first Markdown table in a text, header row included."""
    rows = []
    for line in text.splitlines():
        if line.startswith("|"):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        elif rows:
            break
    return [row for row in rows if not set("".join(row)) <= set("-: ")]


def delivered_spec_ids(marker: str) -> list[str]:
    """The IDs of the delivered slices' specs that carry a marker such as `eval` or `manual`."""
    ids: list[str] = []
    slice_number = 0
    for line in SPECS.read_text().splitlines():
        if heading := re.match(r"^## .*\(slice (\d+)\)$", line):
            slice_number = int(heading.group(1))
        elif slice_number in DELIVERED_SLICES and line.endswith(f"*({marker})*"):
            spec = re.search(r"\*\*(WRAP-[A-Z]+-\d{3})\*\*", line)
            assert spec, line
            ids.append(spec.group(1))
    return ids


def design_roles() -> list[str]:
    """The routing roles, in the design's Routing roles table."""
    section = DESIGN.read_text().split("## Routing roles", 1)[1]
    return [row[0] for row in table_rows(section)[1:]]


# @spec WRAP-PKG-001
def test_skill_frontmatter_uses_only_agent_skills_fields() -> None:
    """Frontmatter limited to the spec's fields keeps the skill portable."""
    meta = frontmatter(SKILL_MD)
    assert sorted(meta) == ["description", "license", "name"]
    assert meta["name"] == "session-wrap-up" == SKILL.name
    assert 0 < len(meta["description"].strip()) <= 1024
    assert meta["license"] == "Apache-2.0"


# @spec WRAP-PKG-002
def test_skill_md_is_under_500_lines() -> None:
    """The Agent Skills spec asks for a short main file, with detail in references."""
    assert len(SKILL_MD.read_text().splitlines()) < 500


# @spec WRAP-PKG-003
def test_skill_md_links_exist() -> None:
    """Every file the skill links to is there to read, inside the skill."""
    links = [
        link
        for link in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", SKILL_MD.read_text())
        if not re.match(r"[a-z]+:", link)
    ]
    assert links
    inside = SKILL.resolve()
    missing = [
        link
        for link in links
        if not (SKILL / link).is_file() or not (SKILL / link).resolve().is_relative_to(inside)
    ]
    assert not missing, missing


# @spec WRAP-PKG-004
def test_skill_carries_its_files_and_license() -> None:
    """A copy of the skill in another repo keeps its references, license and notices."""
    assert ROUTING.is_file()
    assert (SKILL / "LICENSE.txt").read_text() == (REPO_ROOT / "LICENSE").read_text()
    assert (SKILL / "NOTICE").is_file()


# @spec WRAP-PKG-005
def test_notice_carries_each_adapted_source_license() -> None:
    """MIT and BSD-2-Clause require their full text with copies of adapted text."""
    notice = (SKILL / "NOTICE").read_text()
    for source in ["goagrawal-genai/wrap-up", "RyanPenn-coder/wrap-skill", "kdeldycke/dotfiles"]:
        assert source in notice, source
    # Two full MIT texts and one full BSD 2-Clause text, each with its copyright line.
    assert notice.count("MIT License") == 2
    assert notice.count("Permission is hereby granted") == 2
    assert notice.count('THE SOFTWARE IS PROVIDED "AS IS"') == 2
    assert notice.count("BSD 2-Clause License") == 1
    assert "Redistribution and use in source and binary forms" in notice
    assert 'PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"' in notice
    assert notice.count("Copyright") >= 3


# @spec WRAP-PKG-006
def test_routing_table_has_exactly_the_design_roles() -> None:
    """The skill routes by the same roles the design defines, no more and no fewer."""
    rows = table_rows(ROUTING.read_text().split("| Role | Holds | Default home |", 1)[1])
    assert sorted(row[0] for row in rows) == sorted(design_roles())


# @spec WRAP-PKG-007
@pytest.mark.parametrize("word", FILTER_TESTS)
def test_routing_states_the_lesson_filter(word: str) -> None:
    """The four filter tests are written down where the agent reads them."""
    assert re.search(rf"\b{word}\b", ROUTING.read_text(), flags=re.IGNORECASE)


# @spec WRAP-PKG-008
def test_skill_text_has_no_spec_annotations() -> None:
    """Annotations in skill text would load into the agent's context on every run."""
    annotated = [p for p in SKILL.rglob("*") if p.is_file() and "@spec" in p.read_text()]
    assert not annotated, annotated


def test_delivered_slices_have_specs() -> None:
    """The slice list in this file names slices the specs file defines."""
    headings = {
        int(n) for n in re.findall(r"^## .*\(slice (\d+)\)$", SPECS.read_text(), re.MULTILINE)
    }
    assert headings >= DELIVERED_SLICES


# @spec WRAP-PKG-009
@pytest.mark.parametrize("spec", delivered_spec_ids("eval"))
def test_eval_spec_is_exercised_by_an_eval_case(spec: str) -> None:
    """Every eval-verified spec of a delivered slice has a case in this skill's suite."""
    assert eval_cases(SUITE)
    assert spec in cited_by_evals(SUITE)


def test_eval_citations_name_eval_specs() -> None:
    """Eval cases cite only specs that the specs file marks as verified by evals."""
    eval_specs = set(delivered_spec_ids("eval"))
    stray = sorted(set(cited_by_evals(SUITE)) - eval_specs)
    assert not stray, stray


# @spec WRAP-RUN-008, WRAP-RUN-009, WRAP-RUN-013, WRAP-LES-027
@pytest.mark.parametrize("spec", delivered_spec_ids("manual"))
def test_manual_spec_is_in_the_manual_script(spec: str) -> None:
    """Every manually verified spec of a delivered slice has a step in the manual script."""
    assert spec in MANUAL.read_text()


# Evals and manual runs are run by hand, and lidc reads `@spec` only in test code. So this file
# cites every eval- and manual-verified spec of the delivered slices, here and on the manual
# test above, and the test below keeps those citations complete as slices are added.
# @spec WRAP-RUN-001, WRAP-RUN-002, WRAP-RUN-006, WRAP-RUN-007, WRAP-RUN-010, WRAP-RUN-011
# @spec WRAP-RUN-012, WRAP-RUN-014, WRAP-RUN-015
# @spec WRAP-RUN-003, WRAP-RUN-004, WRAP-RUN-005, WRAP-RUN-016, WRAP-RUN-017, WRAP-RUN-018
# @spec WRAP-RUN-019, WRAP-RUN-020, WRAP-RUN-021, WRAP-RUN-022, WRAP-RUN-023, WRAP-RUN-024
# @spec WRAP-RUN-025, WRAP-RUN-026, WRAP-RUN-027, WRAP-RUN-028, WRAP-RUN-029
# @spec WRAP-RULE-001, WRAP-RULE-002, WRAP-RULE-003, WRAP-RULE-004, WRAP-RULE-005
# @spec WRAP-RULE-006, WRAP-RULE-007, WRAP-RULE-008
# @spec WRAP-LES-001, WRAP-LES-002, WRAP-LES-003, WRAP-LES-004, WRAP-LES-005, WRAP-LES-006
# @spec WRAP-LES-007, WRAP-LES-008, WRAP-LES-009, WRAP-LES-010, WRAP-LES-011, WRAP-LES-012
# @spec WRAP-LES-017, WRAP-LES-018, WRAP-LES-019, WRAP-LES-020
# @spec WRAP-LES-013, WRAP-LES-014, WRAP-LES-015, WRAP-LES-016, WRAP-LES-021, WRAP-LES-022
# @spec WRAP-LES-023, WRAP-LES-024, WRAP-LES-025, WRAP-LES-026, WRAP-LES-028, WRAP-LES-029
# @spec WRAP-LES-030, WRAP-LES-031, WRAP-LES-032
# @spec WRAP-RPT-001, WRAP-RPT-002, WRAP-RPT-003, WRAP-RPT-004, WRAP-RPT-005, WRAP-RPT-006
# @spec WRAP-RPT-007, WRAP-RPT-008, WRAP-RPT-009, WRAP-RPT-010, WRAP-RPT-011, WRAP-RPT-012
# @spec WRAP-RPT-013
@pytest.mark.parametrize("spec", delivered_spec_ids("eval") + delivered_spec_ids("manual"))
def test_hand_run_spec_is_cited_in_this_file(spec: str) -> None:
    """Lidc sees a citation for every delivered spec that only an eval or a manual run checks."""
    cited = re.findall(r"^# @spec (.+)$", THIS_FILE.read_text(), flags=re.MULTILINE)
    assert spec in ", ".join(cited)
