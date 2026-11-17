---
id: AD-105
title: Add a local dblp bibliography snapshot as a literature route
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:105
  - docs/intent/prior-art-search/prior-art-search-design.md:535
  - PRIOR-LIT-015
priority: low
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
PRIOR-LIT-015 (deferred) has the agent search a locally cached dblp snapshot (CC0, about 1 GB compressed, published monthly) refreshed monthly, to reach computer-science venue papers the live literature APIs reach unreliably. It needs a build step and a cache location. It is deferred until paper searches show a gap that the live literature routes can't fill; when that happens, design it in the prior-art-search LLD, then implement. Done when PRIOR-LIT-015 is `[x]`.

**Why it matters:** Fills coverage of CS venue papers if live routes prove unreliable.

**Why an agent:** design and build once the trigger is met

**Also waits on (not tracked as a task):** paper searches show a gap that the live literature routes can't fill
<!-- SECTION:DESCRIPTION:END -->
