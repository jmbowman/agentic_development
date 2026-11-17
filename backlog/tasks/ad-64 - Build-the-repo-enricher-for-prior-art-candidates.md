---
id: AD-64
title: Build the repo enricher for prior-art candidates
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
  - docs/prior-art/2026-11-07-search-harvest-pipeline.md#Need and criteria
  - docs/intent/prior-art-search/prior-art-search-design.md:519
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #157 item 3: a script (after a quick prior-art pass) that adds to each candidate its license at a SHA with a rider grep, last push and release, fork and lookalike flags, registry presence, and cheap hard-criterion pre-filters such as a README grep for sqlite or home-directory stores. Output to the run directory so the LLM sees a compact table. Use the GitHub contents API and raw.githubusercontent.com as the #260 comment advises. Done means a tested script under skills/prior-art-search/scripts/ and a reference doc.

**Why it matters:** Removes 3 or more lookups per candidate across about 150 candidates.

**Why an agent:** scripted tooling with written requirements
<!-- SECTION:DESCRIPTION:END -->
