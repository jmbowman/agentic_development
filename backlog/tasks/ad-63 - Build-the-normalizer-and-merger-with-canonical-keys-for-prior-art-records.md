---
id: AD-63
title: Build the normalizer and merger with canonical keys for prior-art records
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/157
  - skills/prior-art-search/scripts/harvest.py
  - docs/prior-art/2026-11-07-search-harvest-pipeline.md#Verdict
  - docs/intent/prior-art-search/prior-art-search-design.md:518
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #157 item 2 plus its #167 comment: write a script (after a quick prior-art pass) that merges harvested candidates keyed by owner/repo and makes the next round's seeds a diff. It must map web:, bulk: and registry keys (npm:, crates:) to owner/repo via repository URLs and keep the original as an alias; take the strongest tag across aliases; list aliases in the merged record; and fail a pre-save check if any key tagged could change the verdict or shortlist is absent from the note without a recorded reason. A candidate whose description claims a core mechanism needs a README read before tagging. Examples of the miss: ticket tk (wedow/ticket) and ccpm.

**Why it matters:** Prevents candidates being lost when the same tool appears under two keys.

**Why an agent:** scripted tooling with a written spec
<!-- SECTION:DESCRIPTION:END -->
