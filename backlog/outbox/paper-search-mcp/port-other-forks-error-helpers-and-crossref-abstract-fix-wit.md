---
title: Port other forks' error helpers and Crossref abstract fix, with credit
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- docs/tool-feedback/paper-search-mcp.md#Related work in other forks
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
target: github.com/jmbowman/paper-search-mcp
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/tool-feedback/paper-search-mcp.md says ArturShirokov/paper-search-mcp's error helpers (`d4078ef`: URL-free error messages, non-JSON/XML rejection) and Crossref fix (`34fcb1c`: strip JATS markup, no 1970-01-01 dates) are worth taking into proposals with credit, as upstream's CONTRIBUTING asks. Check each fork's license (GitHub metadata only so far), port the changes as separate small branches with co-author credit. Done when branches pass tests.

**Why it matters:** Fixes credential leakage in error text and bad Crossref abstracts and dates.

**Why an agent:** porting and testing code, with a license read first

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
