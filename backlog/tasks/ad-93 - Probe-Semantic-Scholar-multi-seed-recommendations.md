---
id: AD-93
title: Probe Semantic Scholar multi-seed recommendations
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:525
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Semantic Scholar's `POST /recommendations/v1/papers` accepts several seed papers in one request (deeper-research uses it). Probe whether it accepts the `from=all-cs` pool and whether its results serve snowballing as well as one seed at a time, before the harvester's `recommend` uses it. Done when the LLD's open question is answered with evidence.

**Why it matters:** Could cut Semantic Scholar requests, its scarcest budget.

**Why an agent:** a scripted probe an agent can run and record
<!-- SECTION:DESCRIPTION:END -->
