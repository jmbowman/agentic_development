---
id: AD-10
title: Show the task brief at session start
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-1
dependencies:
  - AD-5.3
references:
  - skills/task-tracker/scripts/tasks.py
  - docs/prior-art/2026-11-12-task-management-for-humans-and-agents.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wire `skills/task-tracker/scripts/tasks.py brief` into a SessionStart hook for local sessions, so an agent sees in-progress work, the top ready agent tasks with their tier, and how many items wait on the developer. Keep within Claude Code's hook output cap and give the GitHub lookups a timeout (or run `--offline`). Done when a new local session shows the brief and the hook's tests pass.

**Why it matters:** Agents find their next task without the developer relaying it.
<!-- SECTION:DESCRIPTION:END -->
