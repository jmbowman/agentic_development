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
  - session:6faee248 2026-11-13
  - session:da2581da 2026-11-13
  - docs/prior-art/2026-11-11-subagent-process-notes.md#Probe of the platform
priority: medium
type: upstream
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After approving the drafts, raise the four SubagentStop and agent-ID items on anthropics/claude-code (new issues; #85917 is closed and locked). Outward-facing action in the developer's name. Done when the issues exist and docs/tool-feedback/claude-code.md records them. The tool-feedback README says upstream issues for a tool are held until local use works end to end, so confirm that condition with the developer.

**Why it matters:** Could remove the need for the hooks' fallbacks.

**Why the developer:** outward-facing action in the developer's name
<!-- SECTION:DESCRIPTION:END -->
