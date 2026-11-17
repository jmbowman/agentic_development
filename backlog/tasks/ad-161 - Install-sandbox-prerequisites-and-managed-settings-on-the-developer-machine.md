---
id: AD-161
title: Install sandbox prerequisites and managed settings on the developer machine
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
  - global
milestone: m-6
dependencies:
  - AD-143
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#13.
    Enforcement and its calibration
priority: medium
type: chore
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Install bubblewrap and socat for the Linux sandbox, and put the non-negotiable keys (no unsandboxed escape, fail if unavailable, write-deny on gate state) in managed or user settings according to the Decision 9 ruling. Add the install step to the repo's setup task if the repo carries it. Done when a session reports the sandbox active and a deliberate write to the protected directory is refused.

**Why it matters:** Prerequisite for testing protected paths on Linux.

**Why the developer:** machine-level configuration and package installs on the developer's machine
<!-- SECTION:DESCRIPTION:END -->
