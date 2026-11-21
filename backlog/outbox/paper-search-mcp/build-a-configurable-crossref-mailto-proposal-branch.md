---
title: Build a configurable Crossref mailto proposal branch
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- docs/tool-feedback/paper-search-mcp.md#Crossref's contact address is hard-coded
- paper-search-mcp:fork-notes/shared-http-layer.md:98
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
target: github.com/jmbowman/paper-search-mcp
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`crossref.py:69` sends `mailto=paper-search@example.org` for everyone; the fork record calls this 'Branch 2', which will use `mailto` as Crossref's polite-pool credential. Cut a branch from upstream/main reading `get_env("CROSSREF_MAILTO")` and sending `mailto` only when set, with offline tests and a fork-notes record, then merge into integration. Done when the branch passes offline tests.

**Why it matters:** Lets the harvester use Crossref's polite pool honestly.

**Why an agent:** a specified small change

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
