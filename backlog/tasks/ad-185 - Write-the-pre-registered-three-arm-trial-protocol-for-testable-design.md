---
id: AD-185
title: Write the pre-registered three-arm trial protocol for testable design
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-167
  - AD-184
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#6. Tests
    first
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#What to
    measure
priority: medium
type: docs
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per the synthesis: arm 1 tests in the same context, arm 2 a sequential split, arm 3 a testable-design agent then parallel test and implementation agents. Measure faults caught (mutation kills), review findings that escaped, integration mismatches, wall-clock time and tokens, with the A/A noise bar. Done when a protocol file is committed before any run.

**Why it matters:** Needed before a paid trial is meaningful.

**Why an agent:** protocol writing
<!-- SECTION:DESCRIPTION:END -->
