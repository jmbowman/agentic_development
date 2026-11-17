---
id: AD-87
title: Prior-art search for a candidate normalizer and merger script
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:516
  - docs/intent/prior-art-search/prior-art-search-design.md:518
  - https://github.com/jmbowman/agentic_development/issues/157
priority: medium
type: spike
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
#157 plans a normalizer and merger that maps every candidate key (`web:`, registry and forge keys) to one canonical `owner/repo` or DOI, keeps aliases, takes the strongest tag, and checks before saving that every verdict-relevant candidate appears in the note or has a drop reason. The design says each such script waits on its own prior-art search. Run the prior-art-search skill for it and save the note. Done when a dated note gives a verdict that a design can start from.

**Why it matters:** Prevents candidates being silently dropped between rounds.

**Why an agent:** an agent runs the prior-art-search skill
<!-- SECTION:DESCRIPTION:END -->
