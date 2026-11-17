---
id: AD-143
title: Rule on where the sandbox's hard settings live
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
  - global
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Tensions
    and open questions for the developer
priority: high
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Synthesis Decision 9: the repo (and template) carries the sandbox switch, protected gate-state path, permission denies and a SessionStart check that reports when the sandbox is off, while the non-negotiable keys (no unsandboxed escape, fail if unavailable, write-deny on gate state) go in managed settings on the developer's machines, or user settings if managed is impractical. The developer chooses.

**Why it matters:** Needed before the sandbox baseline slice can be finished.

**Why the developer:** concerns the developer's machine-level configuration
<!-- SECTION:DESCRIPTION:END -->
