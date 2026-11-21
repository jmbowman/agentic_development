---
id: AD-337
title: Decide which task type read-only claim checks get
status: To Do
assignee: []
created_date: '2026-11-21T23:20:00Z'
labels:
  - loose-end
milestone: m-1
dependencies: []
references:
  - AD-108
  - AD-294
  - docs/intent/task-tracker/task-tracker-design.md
priority: low
type: decision
ordinal: 28000
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: febc0a58-71fe-4ef9-b3c7-3cc6205db7f4
    role: created
    date: '2026-11-21'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A task that checks one claim in a tool's source (AD-108, AD-203, AD-283, AD-294) is neither a `spike` (a hands-on trial or probe) nor a `search` (its main output is a research record), so AD-5.1's data migration left these as `spike` and listed them as borderline. Decide whether an existing type covers them, with its definition reworded, or a new type does.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The task-tracker design's type definitions say which type such a check gets
- [ ] #2 The tasks named above carry that type
<!-- AC:END -->
