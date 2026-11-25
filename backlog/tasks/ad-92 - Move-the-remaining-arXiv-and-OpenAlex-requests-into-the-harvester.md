---
id: AD-92
title: Move the remaining arXiv and OpenAlex requests into the harvester
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-24T06:12:00Z'
labels:
  - open-question
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:524
  - PRIOR-SCR-110
  - docs/intent/prior-art-search/prior-art-search-design.md:524-528
  - docs/prior-art/2026-11-07-search-harvest-pipeline.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 7491ae04-e559-4545-95a8-b20f528642de
    role: worked
    date: '2026-11-23'
  - agent: claude-code
    id: 7491ae04-e559-4545-95a8-b20f528642de
    role: finished
    date: '2026-11-24'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Agents still send some arXiv and OpenAlex requests themselves (OpenAlex DOI and open-access lookups, arXiv ID lookups and listing pages), which bypass the harvester's cross-process limiter and pace separately. Move them into `skills/prior-art-search/scripts/harvest.py`, as Semantic Scholar's lookups already were, with specs, tests and skill-text changes. Done when agents send nothing to these services themselves.

**Why it matters:** One limiter for every request, which unblocks sharing services among subagents.

**Why an agent:** the plan is stated; it's LID build work
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The harvester now sends every request to the arXiv, OpenAlex and Semantic Scholar APIs: new get (paper by arXiv ID; OpenAlex work by DOI or work ID, with open-access fields) and related (OpenAlex related works) actions, --sort submitted for arXiv search in place of listing pages (which also completes AD-322), and get/related exempt from the OpenAlex daily-budget stop until one of them gets a budget response. LLD, specs PRIOR-SCR-123 to 135 and the revised lines, skill text, the harvester-literature eval case and README updated. Verified by 372 harvester tests, mise run check, and a live run of each new action against arXiv and OpenAlex. Not moved: full-text reads from arxiv.org stay with the agent (AD-65), so arXiv is not yet a harvester-only service for AD-96. Risk: the agent-use specs (PRIOR-SCR-100, 106, 110, 134, PRIOR-ACC-014) are eval-verified and no eval has run on the new text (AD-43).
<!-- SECTION:FINAL_SUMMARY:END -->
