---
id: AD-66
title: Build the record validator and ledger renderer for prior-art notes
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/157
  - https://github.com/jmbowman/agentic_development/issues/156
  - skills/prior-art-search/references/verification.md
  - docs/prior-art/2026-11-07-search-harvest-pipeline.md#Need and criteria
  - docs/intent/prior-art-search/prior-art-search-design.md:521
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #157 item 5: a script that checks subagent records, renders the ledger, matrix and papers table, and provides the link and SHA checks before a note is saved (see the #156 item on checking links and SHAs). Done means a tested script under skills/prior-art-search/scripts/ wired into the skill's Save the note step.

**Why it matters:** Records and note rendering stop depending on the LLM's memory.

**Why an agent:** scripted tooling with written requirements
<!-- SECTION:DESCRIPTION:END -->
