---
id: AD-67
title: 'Extend the harvester: adaptive 429 backoff, substitute handover, more lookups'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
  - partly-done
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/157
  - skills/prior-art-search/scripts/harvest.py
  - docs/tool-feedback/paper-search-mcp.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #157 comments: Semantic Scholar still throttles under its keyed limit (about half of requests got 429 at one request per 3.5-10 s), so the harvester needs backoff that adapts to 429s on top of the rate bucket and, when a route stays throttled, a handover to a substitute (OpenAlex cites: filter returned the citing works in one request). Also route exact-title, open-access and recommendation lookups through skills/prior-art-search/scripts/harvest.py, summarize or cap queries per call so output does not overflow, and try arXiv HTML then PDF. The current harvester skips remaining queries after one failure by design.

**Why it matters:** Literature searches survive throttling without losing queries.

**Why an agent:** code change with measured evidence in the issue

**Status when filed (partly-done):** harvester landed in #244 (49b1ff9) covering keyword search and citations; these extensions remain
<!-- SECTION:DESCRIPTION:END -->
