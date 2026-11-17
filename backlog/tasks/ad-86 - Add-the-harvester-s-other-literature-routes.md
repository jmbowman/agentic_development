---
id: AD-86
title: Add the harvester's other literature routes
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies:
  - AD-91
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:516-517
  - https://github.com/jmbowman/agentic_development/issues/157
  - docs/prior-art/2026-11-07-search-harvest-pipeline.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend `skills/prior-art-search/scripts/harvest.py` to the literature routes beyond arXiv, OpenAlex and Semantic Scholar that the harvest pipeline note's verdict includes (#157). Design it in the LLD's Harvester section with new `PRIOR-SCR-` specs, then tests and code. Done when the new routes go through the harvester's limiter and ledger and `mise run check` passes.

**Why it matters:** Moves more mechanical request work out of agent context, cutting subagent tokens.

**Why an agent:** prior art already covered by the pipeline note; LID work with developer review stops
<!-- SECTION:DESCRIPTION:END -->
