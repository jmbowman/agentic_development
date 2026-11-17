---
id: AD-311
title: Fix the stale PyrateLimiter advice in the paper-search-mcp feedback
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-9
dependencies: []
references:
  - docs/tool-feedback/paper-search-mcp.md:9
  - docs/tool-feedback/paper-search-mcp.md:35
  - >-
    paper-search-mcp:fork-notes/shared-http-layer.md#Decisions, with the
    alternatives rejected
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`docs/tool-feedback/paper-search-mcp.md:9` says the proposal 'should make the case for PyrateLimiter explicitly, and offer an in-memory fallback'. The fork's decision record (decision 2) rejected PyrateLimiter for a stdlib SQLite limiter, and the same file's line 35 already says so. Rewrite line 9 to match the built design. Done when the file no longer contradicts itself.

**Why it matters:** Keeps the PR-drafting source consistent.

**Why an agent:** a factual doc correction
<!-- SECTION:DESCRIPTION:END -->
