---
id: AD-327
title: Design task IDs that don't collide across developers and machines in one repo
status: To Do
assignee: []
created_date: '2026-11-18T13:15:00Z'
labels: []
milestone: m-1
dependencies: []
references:
  - docs/intent/task-tracker/task-tracker-design.md
priority: medium
type: spike
ordinal: 14000
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Backlog.md assigns sequential IDs. Its lock and worktree scan prevent collisions within one checkout and between worktrees on one machine, but two developers who each create a task before either pushes get the same ID, and the file names differ, so git merges both without a conflict. The task tracker's lint reports the duplicate after the merge, and the skill's renumbering step fixes it by hand. That is enough for one developer, not for a team. Run the prior-art-search skill on how file-based and git-backed trackers keep IDs unique across clones (collision-free IDs at creation, such as random or hash tokens or a per-developer prefix; IDs assigned at merge; a central allocator; detection and renumbering), including what each costs in readability and in compatibility with Backlog.md's CLI and views. Then propose a replacement for the assignment step alone: the task tool assumes only the shape <prefix>-<letters and digits>. Done when a docs/prior-art/ note classifies the candidates with licenses read from files, and the task-tracker LLD's open question 6 carries the chosen design or a recorded decision to keep sequential IDs.
<!-- SECTION:DESCRIPTION:END -->
