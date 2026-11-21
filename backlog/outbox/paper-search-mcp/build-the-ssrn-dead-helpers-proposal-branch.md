---
title: Build the ssrn-dead-helpers proposal branch
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- paper-search-mcp:fork-notes/shared-http-layer.md#Moved out of scope (separate PRs)
priority: medium
type: feature
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
target: github.com/jmbowman/paper-search-mcp
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SSRN's `_throttle()` and `_fetch_page()` are never called, but the maintainer kept them deliberately in 870d8a0, so a removal PR has to argue for it. Cut `ssrn-dead-helpers` from upstream/main removing them, and write the argument in a fork-notes record. Done when the branch passes offline tests and the record holds the case.

**Why it matters:** Low value; mainly keeps the shared layer's story clean.

**Why an agent:** small removal plus written rationale

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
