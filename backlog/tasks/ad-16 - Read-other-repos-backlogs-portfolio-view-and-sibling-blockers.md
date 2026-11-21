---
id: AD-16
title: 'Read other repos'' backlogs: portfolio view and sibling blockers'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-1
dependencies:
  - AD-4
  - AD-5.3
references:
  - skills/task-tracker/scripts/tasks.py
  - docs/prior-art/2026-11-16-cross-repo-task-coordination.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend `skills/task-tracker/scripts/tasks.py` to load several backlog roots from a portfolio file (each repo's `backlog/`, and a private root), so the board ranks across repos and an external blocker `repo#ID` resolves against the sibling checkout's task file (Done wherever the file lives; unreadable or stale counts as open). Done when the board shows two real repos and a blocker in one clears when the other's task is Done.

**Why it matters:** The weekly cross-repo ranking, and blockers that clear without re-checking by hand.
<!-- SECTION:DESCRIPTION:END -->
