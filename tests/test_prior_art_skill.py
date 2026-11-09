"""Structure tests of the prior-art search skill, its plugin packaging and its eval suite."""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from typing import Any

import pytest

from tests.support import EVALS, REPO_ROOT, SKILLS, cited_by_evals, frontmatter

SKILL = SKILLS / "prior-art-search"
SKILL_MD = SKILL / "SKILL.md"
REFERENCES = SKILL / "references"
SOURCES_MD = REFERENCES / "sources.md"
SETTINGS_EXAMPLE = REFERENCES / "settings.example.toml"
SETTINGS_FILE = ".config/prior-art-sources.toml"
PLUGIN_JSON = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
SUITE = EVALS / "prior-art-search"
SPECS = REPO_ROOT / "docs" / "intent" / "prior-art-search" / "prior-art-search-specs.md"

EVIDENCE_RECORD = (
    "{candidate, url, criterion, claim, support, evidence, "
    "evidence_kind, read_depth, commit, as_of}"
)
LEDGER_RECORD = "{route, state, queries, reason, as_of}"
PAPER_RECORD = "{paper, doi, url, claim, read_state, evidence_strength, review_status, as_of}"
NOTE_SECTIONS = [
    "Need and criteria",
    "Verdict",
    "Candidates and matrix",
    "Limitations checked in source",
    "Papers",
    "Worth retrieving manually",
    "Coverage ledger",
    "Snowball rounds",
    "Refresh trigger",
]
ROUTE_COLUMNS = {"route", "trigger", "good for", "tactics", "kind", "substitute"}


def _plain(cell: str) -> str:
    """A table cell without Markdown links or backticks, so names can be compared as text."""
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell).replace("`", "").strip()


def _cells(line: str) -> list[str]:
    """The cells of a table row, splitting on pipes that aren't inside a code span."""
    inner = line.strip().strip("|")
    return [cell.strip() for cell in re.split(r"\|(?=(?:[^`]*`[^`]*`)*[^`]*$)", inner)]


def route_table() -> list[dict[str, str]]:
    """The rows of the first table in `sources.md`, each keyed by its lower-cased column name."""
    table: list[str] = []
    for line in SOURCES_MD.read_text().splitlines():
        if line.lstrip().startswith("|"):
            table.append(line)
        elif table:
            break
    assert table, "sources.md has no table"
    header = [_plain(cell).lower() for cell in _cells(table[0])]
    return [dict(zip(header, map(_plain, _cells(line)), strict=False)) for line in table[2:]]


def settings_named_in_sources() -> set[tuple[str, str]]:
    """Every `section.key` setting named in backticks anywhere in `sources.md`."""
    not_settings = {"md", "json", "toml", "xml", "txt", "yaml", "yml", "html", "py", "sh", "org"}
    found = re.findall(r"`([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)`", SOURCES_MD.read_text())
    return {(section, key) for section, key in found if key not in not_settings}


def access_settings_section() -> str:
    """The text of the `Access settings` section of `sources.md`, or an empty string."""
    match = re.search(
        r"^##\s+Access settings\s*$(.*?)(?=^##\s|\Z)",
        SOURCES_MD.read_text(),
        flags=re.MULTILINE | re.DOTALL,
    )
    return str(match.group(1)) if match else ""


def sources_section(heading: str) -> str:
    """The text of a `##` section of `sources.md`, or an empty string."""
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)",
        SOURCES_MD.read_text(),
        flags=re.MULTILINE | re.DOTALL,
    )
    return str(match.group(1)) if match else ""


def settings_in_example() -> dict[str, Any]:
    """The settings template, parsed: each section mapped to its keys and values."""
    return tomllib.loads(SETTINGS_EXAMPLE.read_text())


def eval_spec_ids() -> list[str]:
    """The IDs of the specs marked as verified only by behavior evals."""
    pattern = r"\*\*(PRIOR-[A-Z]+-\d{3})\*\*:.*\*\(eval\)\*$"
    return [m.group(1) for m in re.finditer(pattern, SPECS.read_text(), re.MULTILINE)]


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
    header = set(route_table()[0]) if route_table() else set()
    assert header >= ROUTE_COLUMNS
    triggers = [row["trigger"].lower() for row in route_table()]
    assert any(re.search(r"skill|plugin|mcp", trigger) for trigger in triggers)


# @spec PRIOR-PKG-009
@pytest.mark.parametrize("record", [EVIDENCE_RECORD, LEDGER_RECORD, PAPER_RECORD])
def test_verification_defines_record_shape(record: str) -> None:
    """Subagents return records in these exact shapes."""
    assert record in (REFERENCES / "verification.md").read_text()


# @spec PRIOR-PKG-009
def test_verification_says_a_snippet_read_cannot_verify() -> None:
    """A snippet-depth record is a lead, never the basis of a *verified in source* tag."""
    text = (REFERENCES / "verification.md").read_text()
    pattern = r"\bsnippet\b[^.\n]*\b(?:never|can't|cannot|not)\b[^.\n]*verified in source"
    assert re.search(pattern, text)


# @spec PRIOR-PKG-010
def test_note_template_has_every_section() -> None:
    """A saved note has the same sections every time, so notes can be compared."""
    headings = re.findall(
        r"^##\s+(.+?)\s*$", (REFERENCES / "note-template.md").read_text(), flags=re.MULTILINE
    )
    assert [h.lower() for h in headings] == [s.lower() for s in NOTE_SECTIONS]


# @spec PRIOR-PKG-016
def test_literature_routes_exist_and_each_names_a_different_substitute() -> None:
    """A literature outage has a named substitute, so one failing API doesn't end the search."""
    literature = [row for row in route_table() if row.get("kind", "").lower() == "literature"]
    assert any(re.search(r"approach|technique", row["trigger"].lower()) for row in literature)
    names = {row["route"].lower() for row in literature}
    for row in literature:
        own = row["route"].lower()
        named = {name for name in names - {own} if name in row["substitute"].lower()}
        assert named, f"{row['route']} names no other literature route as its substitute"
        assert own not in row["substitute"].lower(), f"{row['route']} names itself"


# @spec PRIOR-PKG-015
def test_skill_carries_its_license() -> None:
    """A copy of the skill in another repo keeps the license text Apache-2.0 requires."""
    assert (SKILL / "LICENSE.txt").read_text() == (REPO_ROOT / "LICENSE").read_text()


# @spec PRIOR-PKG-017
def test_settings_template_values_are_all_empty() -> None:
    """The template ships blank, so copying it can never publish someone's key."""
    sections = settings_in_example()
    assert sections
    values = [(s, k, v) for s, keys in sections.items() for k, v in keys.items()]
    assert values
    assert all(value == "" for _, _, value in values), values


# @spec PRIOR-PKG-017
def test_every_setting_that_sources_names_is_in_the_template() -> None:
    """A setting the route table points at can be found, and filled in, in the template."""
    named = settings_named_in_sources()
    assert named, "sources.md names no `section.key` setting"
    in_template = {(s, k) for s, keys in settings_in_example().items() for k in keys}
    assert named <= in_template, sorted(named - in_template)


# @spec PRIOR-PKG-018
def test_each_setting_is_marked_and_says_where_to_register_and_its_terms() -> None:
    """Each setting's comment says required or optional, where to register, and its terms."""
    blocks = re.findall(
        r"^\[(\w+)\]\n((?:#.*\n)+)", SETTINGS_EXAMPLE.read_text(), flags=re.MULTILINE
    )
    assert blocks
    for section, comment in blocks:
        text = " ".join(line.lstrip("# ").strip() for line in comment.splitlines()).lower()
        assert text.startswith(("required", "optional")), f"[{section}] isn't marked"
        assert "https://" in comment, f"[{section}] gives no address"
        assert re.search(
            r"terms read|terms:\s*https?://|(?:not|n't) (?:yet )?(?:been )?read", text
        ), f"[{section}] says neither where its terms are nor that they weren't read"
        assert re.search(r"register|sign[ -]?up|no registration|account page", text), (
            f"[{section}] says neither where to register nor that no registration is needed"
        )
    assert {section for section, _ in blocks} == set(settings_in_example())
    assert all(len(keys) == 1 for keys in settings_in_example().values()), (
        "one comment block per setting means one setting per section"
    )


# @spec PRIOR-PKG-019
def test_git_ignores_the_real_settings_file() -> None:
    """A filled-in settings file can't be committed by accident in this repo."""
    result = subprocess.run(  # noqa: S603
        ["git", "check-ignore", "-q", SETTINGS_FILE],  # noqa: S607
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0


# @spec PRIOR-PKG-020
def test_sources_has_an_access_settings_section() -> None:
    """The route table's companion says which route uses which setting, and how to ignore it."""
    section = access_settings_section()
    assert section, "sources.md has no `Access settings` section"
    assert SETTINGS_FILE in section
    assert ".gitignore" in section
    routes = [row["route"].lower() for row in route_table()]
    in_template = {f"{s}.{k}" for s, keys in settings_in_example().items() for k in keys}
    for name in sorted(in_template | {f"{s}.{k}" for s, k in settings_named_in_sources()}):
        lines = [line.lower() for line in section.splitlines() if f"`{name}`" in line]
        assert lines, f"the Access settings section doesn't name `{name}`"
        assert any(route in line for line in lines for route in routes), (
            f"`{name}` isn't paired with the route that uses it"
        )


# @spec PRIOR-PKG-021
def test_rate_limits_section_names_every_queried_route() -> None:
    """Every route the agent queries has its stated rate limit, or a note that none is stated."""
    section = sources_section("Rate limits").lower()
    assert section, "sources.md has no `Rate limits` section"
    assert "default" in section
    queried = [row["route"] for row in route_table() if row.get("kind", "").lower() != "local"]
    missing = [route for route in queried if route.lower() not in section]
    assert not missing, f"no rate limit given for: {missing}"


# Each settings section in the template, and the name its service's bullet uses in `sources.md`.
SETTING_SERVICES = {
    "openalex": "OpenAlex",
    "librariesio": "libraries.io",
    "crossref": "Crossref",
    "semanticscholar": "Semantic Scholar",
}


def rate_limit_bullet(service: str) -> str:
    """The Rate limits bullet whose bold name is `service`, or an empty string."""
    for bullet in re.split(r"\n(?=- )", sources_section("Rate limits")):
        if re.match(rf"- \*\*{re.escape(service)}:?\*\*", bullet.strip()):
            return str(bullet)
    return ""


def value_carriers(text: str) -> set[str]:
    """Backticked names that `text` calls a parameter or header, other than the user agent.

    Matches "the `x-api-key` header", "the `api_key` query parameter", "header `x-api-key`".
    """
    after = re.findall(r"`([^`]+)`\s+(?:[\w-]+\s+)?(?:parameter|header)\b", text)
    before = re.findall(r"\b(?:parameter|header)\s+`([^`]+)`", text)
    return {name for name in after + before if name.lower() != "user-agent"}


@pytest.mark.parametrize(
    ("text", "carriers"),
    [
        ("sent in the `x-api-key` request header", {"x-api-key"}),
        ("as the `api_key` query parameter", {"api_key"}),
        ("the header `Authorization`", {"Authorization"}),
        ("Crossref also asks for a `User-Agent` header", set()),
    ],
)
def test_value_carriers(text: str, carriers: set[str]) -> None:
    """The carrier check accepts the usual phrasings and ignores the user agent."""
    assert value_carriers(text) == carriers


# @spec PRIOR-PKG-020
@pytest.mark.parametrize(
    "setting",
    sorted(f"{s}.{k}" for s, keys in settings_in_example().items() for k in keys),
)
def test_access_settings_name_how_each_value_is_sent(setting: str) -> None:
    """An agent can send each setting's value the way its service expects, without guessing."""
    lines = [line for line in access_settings_section().splitlines() if f"`{setting}`" in line]
    assert lines, f"the Access settings section doesn't name `{setting}`"
    assert value_carriers(" ".join(lines)), (
        f"`{setting}` doesn't say which parameter or header carries its value"
    )


def test_every_template_setting_has_a_service_name() -> None:
    """The service-name mapping covers every setting the template has."""
    assert set(settings_in_example()) == set(SETTING_SERVICES)


# Every service with a setting today states a limit for requests that carry its value (a key, or
# Crossref's polite-pool address), so PRIOR-PKG-022 applies to all four. A future setting whose
# service states no such limit would need its own entry here.
# @spec PRIOR-PKG-022
@pytest.mark.parametrize(("section", "service"), sorted(SETTING_SERVICES.items()))
def test_rate_limits_give_the_limit_with_each_setting(section: str, service: str) -> None:
    """A run with a key or contact address set paces to the limit for requests that carry it."""
    bullet = rate_limit_bullet(service)
    assert bullet, f"the Rate limits section has no bullet for {service}"
    with_value = r"\bwith (?:a|an|its|the|one)\b[^.;]*\b(?:key|address)\b|polite pool|\bper key\b"
    clauses = [c for c in re.split(r";|\.\s", bullet) if re.search(with_value, c, re.IGNORECASE)]
    assert any(re.search(r"\d", clause) for clause in clauses), (
        f"the {service} bullet gives no limit for requests that carry `{section}`'s value"
    )
    assert "https://" in bullet, f"the {service} bullet doesn't say where its limit is stated"


def test_eval_citations_name_eval_specs() -> None:
    """Eval cases cite only specs that the specs file marks as verified by evals."""
    stray = sorted(set(cited_by_evals(SUITE)) - set(eval_spec_ids()))
    assert not stray, stray


# The behavior evals run by hand, and lidc reads `@spec` only in test code, so this test
# carries the citations for every eval-verified spec and checks an eval case exercises each.
# @spec PRIOR-TRIG-001, PRIOR-TRIG-002, PRIOR-TRIG-003, PRIOR-TRIG-004
# @spec PRIOR-EFF-001, PRIOR-EFF-002, PRIOR-EFF-003, PRIOR-EFF-004
# @spec PRIOR-EFF-005, PRIOR-EFF-006, PRIOR-EFF-007
# @spec PRIOR-SRCH-001, PRIOR-SRCH-002, PRIOR-SRCH-003, PRIOR-SRCH-004, PRIOR-SRCH-005
# @spec PRIOR-SRCH-006, PRIOR-SRCH-007, PRIOR-SRCH-008, PRIOR-SRCH-009, PRIOR-SRCH-010
# @spec PRIOR-SRCH-011, PRIOR-SRCH-012, PRIOR-SRCH-013, PRIOR-SRCH-014, PRIOR-SRCH-015
# @spec PRIOR-SRCH-016
# @spec PRIOR-CLS-001, PRIOR-CLS-002, PRIOR-CLS-003, PRIOR-CLS-004, PRIOR-CLS-005, PRIOR-CLS-006
# @spec PRIOR-CLS-007, PRIOR-CLS-008, PRIOR-CLS-009, PRIOR-CLS-010, PRIOR-CLS-011, PRIOR-CLS-012
# @spec PRIOR-LIC-001, PRIOR-LIC-002, PRIOR-LIC-003, PRIOR-LIC-004, PRIOR-LIC-005, PRIOR-LIC-006
# @spec PRIOR-SRC-001, PRIOR-SRC-002, PRIOR-SRC-003, PRIOR-SRC-004, PRIOR-SRC-005
# @spec PRIOR-SRC-006, PRIOR-SRC-007, PRIOR-SRC-008, PRIOR-SRC-009, PRIOR-SRC-010
# @spec PRIOR-CLS-013, PRIOR-CLS-014
# @spec PRIOR-LIT-001, PRIOR-LIT-002, PRIOR-LIT-003, PRIOR-LIT-004, PRIOR-LIT-005
# @spec PRIOR-LIT-006, PRIOR-LIT-007, PRIOR-LIT-008, PRIOR-LIT-009, PRIOR-LIT-010
# @spec PRIOR-LIT-011, PRIOR-LIT-012, PRIOR-LIT-013, PRIOR-LIT-014, PRIOR-LIT-016, PRIOR-LIT-017
# @spec PRIOR-ACC-001, PRIOR-ACC-002, PRIOR-ACC-003, PRIOR-ACC-004, PRIOR-ACC-005
# @spec PRIOR-ACC-006, PRIOR-ACC-007, PRIOR-ACC-008, PRIOR-ACC-009
# @spec PRIOR-ACC-010, PRIOR-ACC-011, PRIOR-ACC-012, PRIOR-ACC-013
# @spec PRIOR-SKL-001, PRIOR-SKL-002, PRIOR-SKL-003, PRIOR-SKL-004, PRIOR-SKL-005
# @spec PRIOR-RPT-001, PRIOR-RPT-002, PRIOR-RPT-003, PRIOR-RPT-004, PRIOR-RPT-005, PRIOR-RPT-006
# @spec PRIOR-RPT-007, PRIOR-RPT-008, PRIOR-RPT-009
# @spec PRIOR-SAVE-001, PRIOR-SAVE-002, PRIOR-SAVE-003, PRIOR-SAVE-004
# @spec PRIOR-SAVE-005, PRIOR-SAVE-006, PRIOR-SAVE-007, PRIOR-SAVE-008, PRIOR-SAVE-009
# @spec PRIOR-PRIV-001, PRIOR-PRIV-002, PRIOR-PRIV-003, PRIOR-PRIV-004
@pytest.mark.parametrize("spec", eval_spec_ids())
def test_eval_spec_is_exercised_by_an_eval_case(spec: str) -> None:
    """Every eval-verified spec has at least one eval case that exercises it."""
    assert spec in cited_by_evals(SUITE)
