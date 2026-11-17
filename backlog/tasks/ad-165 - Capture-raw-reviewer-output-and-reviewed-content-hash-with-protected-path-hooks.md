---
id: AD-165
title: >-
  Capture raw reviewer output and reviewed-content hash with protected-path
  hooks
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-160
  - AD-163
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#9. Review
    waves and triage
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Build
    order
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The hook-captured part of the ledger: a SubagentStop hook writes each reviewer's raw output and the hash of what was reviewed into a protected directory the agent cannot write through the shell or file tools; triage rulings stay agent-written. This depends on the sandbox baseline showing protected paths hold.

**Why it matters:** Makes the ledger tamper-resistant at the OS layer.

**Why an agent:** hook code and fixtures
<!-- SECTION:DESCRIPTION:END -->
