---
id: AD-287
title: File the Claude Code feedback upstream
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies:
  - AD-286
references:
  - docs/tool-feedback/claude-code.md
  - docs/prior-art/2026-11-11-subagent-process-notes.md#Probe of the platform
priority: medium
type: upstream
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 6faee248-a06c-4571-af3c-1b0fbcadae67
    role: created
    date: '2026-11-13'
  - agent: claude-code
    id: da2581da-380d-47f8-8550-ee00c4dcc713
    role: worked
    date: '2026-11-13'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After approving the drafts, raise the four SubagentStop and agent-ID items on anthropics/claude-code (new issues; #85917 is closed and locked). Outward-facing action in the developer's name. Done when the issues exist and docs/tool-feedback/claude-code.md records them. The tool-feedback README says upstream issues for a tool are held until local use works end to end, so confirm that condition with the developer.

**Why it matters:** Could remove the need for the hooks' fallbacks.

**Why the developer:** outward-facing action in the developer's name
<!-- SECTION:DESCRIPTION:END -->
