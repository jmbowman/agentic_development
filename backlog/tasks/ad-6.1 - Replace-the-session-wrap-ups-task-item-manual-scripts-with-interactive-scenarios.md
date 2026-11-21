---
id: AD-6.1
title: >-
  Replace the session wrap-up's task-item manual scripts with interactive
  scenarios
status: To Do
assignee: []
created_date: '2026-11-21T23:08:00Z'
labels:
  - loose-end
milestone: m-1
dependencies:
  - AD-138
parent_task_id: AD-6
priority: medium
type: eval
ordinal: 27000
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: febc0a58-71fe-4ef9-b3c7-3cc6205db7f4
    role: created
    date: '2026-11-21'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The rest of AD-6. Slice 5 of the session wrap-up (task items and outbox drafts) is built and its eval cases pass, but its manual specs (WRAP-TASK-009, 014, 016, 017, 019, 020, 021, 022, 024 and WRAP-XREPO-015, 016, 017) need a live session that applies items, and their scripts in evals/session-wrap-up/manual.md (from "Setting up the task runs" on) have never run. That is also the half of AD-6 acceptance criterion about a wrap-up producing task files in a scratch repo. Write scenarios in evals/session-wrap-up/interactive/ that replace those scripts, with replaces markers, once AD-138 has built the approval-gate scenarios they extend.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each task-item manual script is replaced by a scenario that mise run check collects, and the replaced scripts are gone from manual.md
- [ ] #2 The scenarios pass three runs of the same skill text, as the review-log rule requires
<!-- AC:END -->
