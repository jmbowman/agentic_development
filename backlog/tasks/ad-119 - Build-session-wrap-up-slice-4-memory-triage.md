---
id: AD-119
title: 'Build session-wrap-up slice 4: memory triage'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-4
dependencies: []
references:
  - docs/intent/session-wrap-up/session-wrap-up-specs.md:256-264
  - docs/intent/session-wrap-up/session-wrap-up-design.md:295
  - docs/intent/session-wrap-up/session-wrap-up-design.md:316-327
  - README.md#Status
  - WRAP-MEM-001
  - WRAP-MEM-002
  - WRAP-MEM-003
  - WRAP-MEM-004
  - WRAP-MEM-005
  - WRAP-MEM-006
  - WRAP-MEM-007
  - docs/intent/session-wrap-up/session-wrap-up-specs.md#Memory (slice 4)
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 5af90670-4925-4893-9f63-86ccfe5510bf
    role: created
    date: '2026-11-04'
  - agent: claude-code
    id: da2581da-380d-47f8-8550-ee00c4dcc713
    role: worked
    date: '2026-11-13'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement step 5 of the session-wrap-up skill: when the harness or developer states the memory directory, give each memory entry one verdict (keep, move, merge, retire), show keeps only as a count, propose moves as one item that adds the text to its repo home and removes the entry and index line, and skip memory with a note when no location is stated. Specs: WRAP-MEM-001, WRAP-MEM-002, WRAP-MEM-003, WRAP-MEM-004, WRAP-MEM-005, WRAP-MEM-006, WRAP-MEM-007 (the verdicts defined in `skills/session-wrap-up/references/routing.md`). Walk it through LID with eval cases for the *(eval)* specs, a manual script for WRAP-MEM-004, a structure test for WRAP-MEM-007, and make memory items selectable. Done when `mise run check` passes and the README status line no longer lists memory triage as to come.

**Why it matters:** Stops agent memory drifting away from the repo, moving durable intent into the arrow where every tool sees it.

**Why an agent:** specs are written; implementation and tests are agent work
<!-- SECTION:DESCRIPTION:END -->
