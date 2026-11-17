---
title: Keep the IEEE API key out of URLs in the fork
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- docs/tool-feedback/paper-search-mcp.md#IEEE's key travels in the URL
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
external_blockers:
- paper-search-mcp/check-whether-ieee-accepts-its-api-key-in-a-header
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`ieee.py:150` sends the key as the `apikey` query parameter, which can leak into logs and errors. Check whether IEEE accepts a header and use it; otherwise ensure no log line or exception carries the full URL, and check whether any connector logs full URLs (not checked). Done when the entry records the finding and a tested change is ready.

**Why it matters:** Prevents key leaks for anyone using the IEEE connector.

**Why an agent:** a code and docs check with a clear fix

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
