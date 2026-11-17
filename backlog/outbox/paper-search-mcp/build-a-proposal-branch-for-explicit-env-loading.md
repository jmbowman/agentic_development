---
title: Build a proposal branch for explicit .env loading
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- docs/tool-feedback/paper-search-mcp.md#A second settings file is loaded implicitly
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`config.py:14-21,49-66` loads `~/.config/paper-search-mcp/.env` into the process on first use, which the harvester disables by pointing `PAPER_SEARCH_MCP_ENV_FILE` at a missing path. Cut a branch from upstream/main loading the file only from the MCP server's entry point (or documenting the switch for library use). Done when library use loads no implicit file and tests pass.

**Why it matters:** Lets the harvester drop a workaround.

**Why an agent:** small, specified change

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
