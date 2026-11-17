---
id: AD-19
title: Add an atomic claim for parallel agents
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-1
dependencies:
  - AD-5
references:
  - docs/tool-feedback/backlog-md.md
  - docs/prior-art/2026-11-12-task-management-for-humans-and-agents.md
priority: low
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two agents in parallel worktrees can both take the top ready task. Add `tasks.py claim <ID>`: under a lock in the git common directory, check the task is unclaimed, then set `status: In Progress` and the assignee. Only worth building once agents pick their own work from the queue. Done when two concurrent claims in a test give one winner.

**Why it matters:** Safe parallel agent sessions.
<!-- SECTION:DESCRIPTION:END -->
