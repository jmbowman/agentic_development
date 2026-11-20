---
id: AD-5.1
title: 'Task tracker slice 1: the task-tracker skill'
status: In Progress
assignee: []
created_date: '2026-11-20T13:25:00Z'
labels: []
milestone: m-1
dependencies: []
parent_task_id: AD-5
priority: high
type: feature
ordinal: 20000
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
sessions:
  - agent: claude-code
    id: febc0a58-71fe-4ef9-b3c7-3cc6205db7f4
    role: created
    date: '2026-11-20'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
First slice of AD-5: make the task tracker usable by agents as a skill, with the tool behaving as the pilot does. Unblocks the skills that will write their follow-ups as tasks (AD-6, AD-12). Scope: move scripts/tasks.py into skills/task-tracker/scripts/ unchanged in behaviour; SKILL.md, references/task-format.md, the structure tests and the four evals (TASK-SKILL); TASK-REPO-001, 005, 006, 007 and 008, with `board` printing to standard output and backlog/BOARD.md untracked; the data changes the skill rules need (`target` on every outbox draft, `session:` references moved into `sessions`, the search tasks retyped from `spike` to `search`); backlog/README.md, CLAUDE.md Tasks rule and README.md updated. The pilot tests and the check over this repo backlog stay green.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The TASK-SKILL specs and TASK-REPO-001, 005, 006, 007 and 008 are covered by tests or evals that cite them, and pass
- [ ] #2 mise run check passes, including the task tool check over this repo backlog
<!-- AC:END -->
