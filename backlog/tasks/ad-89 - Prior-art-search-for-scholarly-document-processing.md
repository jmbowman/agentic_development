---
id: AD-89
title: Prior-art search for scholarly document processing
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:516
  - docs/intent/prior-art-search/prior-art-search-design.md:520
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
#157 plans scholarly document processing: arXiv full text (HTML, then PDF) with math kept, reference extraction, artifact links, and a read state for open copies that can't be fetched by machine, so the paper goes to 'Worth retrieving manually' instead of being dropped. The design says it waits on its own prior-art search. Run the skill and save the note. Done when a dated note gives a verdict.

**Why it matters:** Lets papers be read in full more often, raising evidence quality.

**Why an agent:** an agent runs the prior-art-search skill
<!-- SECTION:DESCRIPTION:END -->
