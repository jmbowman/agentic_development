---
id: AD-68
title: Build a GitHub and registry harvester that keeps raw payloads out of context
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
  - docs/intent/prior-art-search/prior-art-search-design.md:517
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #157 item 1 beyond literature: a per-service harvester for GitHub search and the package registries that paces, retries, inserts keys itself, writes raw results to disk and ledger lines from what actually ran, and prints a compact summary. A throwaway GitHub harvester written for the #167 search worked and kept raw payloads out of context but lived in a gitignored tmp directory. Productize it in skills/prior-art-search/scripts/ with tests. Do a quick prior-art pass first.

**Why it matters:** Removes the largest token cost from software routes.

**Why an agent:** scripted tooling
<!-- SECTION:DESCRIPTION:END -->
