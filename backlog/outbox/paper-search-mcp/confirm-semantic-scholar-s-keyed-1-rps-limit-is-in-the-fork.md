---
title: Confirm Semantic Scholar's keyed 1 rps limit is in the fork's limits table
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
- maybe-done
references:
- docs/tool-feedback/paper-search-mcp.md#Semantic Scholar has no keyed pacing
priority: medium
type: chore
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/tool-feedback/paper-search-mcp.md 'Semantic Scholar has no keyed pacing' proposes an entry in the shared limits table (1 request a second across endpoints per key), which the shared-http-layer branch may already hold. Check the fork's limits table and tests; add the entry if missing; otherwise mark the entry done. Done when the entry records the result.

**Why it matters:** Keeps keyed Semantic Scholar use inside its limit.

**Why an agent:** a source check and a one-line table entry

**Status when filed (maybe-done):** the shared-http-layer limiter was built after cab1b5c, which the entry was written against

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
