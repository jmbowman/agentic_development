---
id: AD-198
title: Trial a Showboat demo per slice for the ease-of-human-review lens
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#7. The
    implementation loop
priority: medium
type: eval
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Showboat (Apache-2.0, one binary via uvx, no git operations) lets an agent build a demo document only through exec, which records each command's real output, and verify re-runs every block and fails on a byte difference. Try one demo for a real slice and record whether it helps the developer review and whether CI re-checks it reliably. Done when the trial result is in docs/ with a keep-or-drop call.

**Why it matters:** Gives the developer something to read that CI can re-check.

**Why an agent:** small trial
<!-- SECTION:DESCRIPTION:END -->
