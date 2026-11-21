---
title: Build a proposal branch moving MCP dependencies to an extra
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- tool-feedback
references:
- docs/tool-feedback/paper-search-mcp.md#MCP dependencies are required for library use
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
`fastmcp` and `mcp[cli]<2` are required dependencies (`pyproject.toml:36-38`), so library users like the harvester install the server stack and inherit the `mcp<2` clash. Cut a branch from upstream/main moving them to an extra such as `paper-search-mcp[server]`, with the server entry point guarded. Done when the library imports without the extra and tests pass.

**Why it matters:** Smaller, conflict-free installs for the harvester.

**Why an agent:** packaging change with a clear shape

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
