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
  - AD-5.3
references:
  - docs/tool-feedback/backlog-md.md
  - docs/prior-art/2026-11-12-task-management-for-humans-and-agents.md
  - docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md
  - docs/intent/task-tracker/task-tracker-design.md
priority: low
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two agents in parallel worktrees can both take the top ready task. Add a claim command: under a lock in the git common directory, which every worktree sees, check the task is unclaimed, then record the claim with the claiming session's ID. The task tracker's design leaves `assignee` empty and keeps live state out of task files, because agents don't commit, so a marker in a task file reaches other worktrees and machines only after a commit, and stays behind when a session dies. Only worth building once agents pick their own work from the queue. Done when two concurrent claims in a test give one winner.

Design input: which session is working on a task now can be computed rather than stored, by joining the task's `sessions` entries (task-tracker LLD) with the live sessions and their busy or idle state from `claude agents --json`, which the parallel-session note adopts as its base. A claim then expires when its session no longer appears, and `why` and the board can show which session holds an in-progress task and whether it is still running.

**Why it matters:** Safe parallel agent sessions.
<!-- SECTION:DESCRIPTION:END -->
