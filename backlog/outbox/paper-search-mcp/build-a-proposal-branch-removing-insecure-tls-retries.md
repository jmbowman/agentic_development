---
title: Build a proposal branch removing insecure TLS retries
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- docs/tool-feedback/paper-search-mcp.md#Connectors retry without TLS verification
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
OpenAIRE (`openaire.py:158`) and CiteSeerX (`citeseerx.py:53`) retry with `verify=False` after an SSL error and silence urllib3's warning process-wide; still present on the fork's integration branch. Cut a branch from upstream/main that lets the SSL error surface (or makes the insecure retry an explicit opt-in) and stops silencing warnings globally, with offline tests. Done when the branch passes offline tests and has a fork-notes record.

**Why it matters:** Closes a man-in-the-middle hole for every user of the library.

**Why an agent:** a specified security fix

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
