---
id: AD-104
title: Probe the connector sources the route list lacks and add those that pass
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-3
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-07-search-harvest-pipeline.md#Limitations checked in
    source
  - https://github.com/jmbowman/agentic_development/issues/158
priority: low
type: spike
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
paper-search-mcp has connectors for sources that references/sources.md does not list and the catalogs note did not judge: OpenReview, HAL, bioRxiv, medRxiv, chemRxiv, CiteSeerX, IACR, PubMed and PMC, and generic OAI-PMH. Each needs the catalogs note's probe (blocked-client behavior, rate limits, license) before joining the route list. Done when each is added to sources.md or excluded with a reason.

**Why it matters:** Broader literature coverage for searches.

**Why an agent:** probing public APIs and editing sources.md
<!-- SECTION:DESCRIPTION:END -->
