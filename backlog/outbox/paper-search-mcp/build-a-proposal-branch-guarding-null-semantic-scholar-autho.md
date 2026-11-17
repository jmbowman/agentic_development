---
title: Build a proposal branch guarding null Semantic Scholar authors
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- docs/tool-feedback/paper-search-mcp.md#A Semantic Scholar paper with null authors is dropped
priority: medium
type: feature
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`semantic.py:103` iterates `item.get("authors", [])`, which is `None` when the key is null, so the paper is silently dropped and ranks shift. Cut a branch from upstream/main using `item.get("authors") or []` and the same guard for other iterated list fields, with an offline test. Done when the branch passes offline tests.

**Why it matters:** Prevents silent result loss in the harvester's Semantic Scholar searches.

**Why an agent:** a one-line fix with a test

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
