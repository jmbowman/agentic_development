---
title: Check whether IEEE accepts its API key in a header
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- docs/tool-feedback/paper-search-mcp.md#IEEE's key travels in the URL
priority: medium
type: spike
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`ieee.py:151` sends the key as the `apikey` query parameter, so it can leak into logs or error messages. Check IEEE Xplore's API docs for a header form; if one exists, cut a proposal branch using it, otherwise confirm no log line or exception carries the full URL. Done when the answer is recorded in `docs/tool-feedback/paper-search-mcp.md` and, if applicable, a branch exists.

**Why it matters:** Reduces key-leak risk; the harvester doesn't use IEEE, so low priority.

**Why an agent:** doc lookup and a small change

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
