---
id: AD-2
title: Rule on the pilot's provisional answers to the 20 task-tracking decisions
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-17T12:19:00Z'
labels:
  - open-question
milestone: m-1
dependencies:
  - AD-1
references:
  - docs/task-tracking-pilot.md
  - docs/prior-art/2026-11-12-task-management-for-humans-and-agents.md
  - docs/prior-art/2026-11-16-cross-repo-task-coordination.md
  - '#166'
  - >-
    docs/prior-art/2026-11-12-task-management-for-humans-and-agents.md#Open
    decisions for the developer
  - tmp/prior-art-next/HANDOFF.md
priority: high
type: decision
performer: human
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 26c85309-65ed-4104-ac8a-5d535bdaccc6
    role: worked
    date: '2026-11-16'
  - agent: claude-code
    id: b966c1df-280e-4b70-b53b-f6a647dc9423
    role: created
    date: '2026-11-14'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The two task prior-art notes leave 8 and 12 decisions open. The pilot had to pick an answer for each to exist; docs/task-tracking-pilot.md lists the 20 with the answer the pilot took, what it learned, and where it departs from the notes' recommendation (human decisions live in one human-owned file instead of protected fields; the ranking never writes Backlog.md's fields; drafts for other repos are named by slug). Accept, change or defer each row. Done when each row carries the developer's ruling.

**Why it matters:** Unblocks the LID pass and every integration that depends on the schema.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-17: the developer reviewed the 20 rows in docs/task-tracking-pilot.md and accepted the pilot's answers for now. X5 and X8 held no answer and remain open as AD-4 and AD-316.
<!-- SECTION:NOTES:END -->
