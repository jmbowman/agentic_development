---
id: AD-92
title: Move the remaining arXiv and OpenAlex requests into the harvester
status: To Do
assignee: []
created_date: '2026-11-16'
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
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Agents still send some arXiv and OpenAlex requests themselves (OpenAlex DOI and open-access lookups, arXiv ID lookups and listing pages), which bypass the harvester's cross-process limiter and pace separately. Move them into `skills/prior-art-search/scripts/harvest.py`, as Semantic Scholar's lookups already were, with specs, tests and skill-text changes. Done when agents send nothing to these services themselves.

**Why it matters:** One limiter for every request, which unblocks sharing services among subagents.

**Why an agent:** the plan is stated; it's LID build work
<!-- SECTION:DESCRIPTION:END -->
