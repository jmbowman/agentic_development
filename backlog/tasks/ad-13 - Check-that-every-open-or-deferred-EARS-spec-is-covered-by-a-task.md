---
id: AD-13
title: Check that every open or deferred EARS spec is covered by a task
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-1
dependencies:
  - AD-5.2
references:
  - skills/task-tracker/scripts/tasks.py
  - docs/intent/
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Unimplemented `[ ]` and deferred `[D]` specs are backlog items that live outside the backlog. Add a check to `skills/task-tracker/scripts/tasks.py check`: every such spec ID under `docs/intent/` must appear in an open task's `references` or body, and a task that cites a spec now marked `[x]` is flagged as possibly done. Done when the check runs in `mise run check` and has tests.

**Why it matters:** Keeps the spec files and the backlog from drifting apart.
<!-- SECTION:DESCRIPTION:END -->
