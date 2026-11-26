---
id: AD-5.3
title: 'Task tracker slice 3: readiness, ranking, GitHub lookup and other repos'
status: To Do
assignee: []
created_date: '2026-11-20T13:25:00Z'
updated_date: '2026-11-26T13:02:35Z'
labels: []
milestone: m-1
dependencies:
  - AD-5.2
parent_task_id: AD-5
priority: high
type: feature
ordinal: 22000
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
Third slice of AD-5: readiness, ranking, the batched GitHub lookup with its two lint findings, reading other repos, and the commands. Unblocks AD-10, AD-16 and AD-19. Reaches consumers as updates that do not change what check reports, apart from the cache-based GitHub findings. Scope: TASK-READY, TASK-RANK, TASK-GH, TASK-XREPO, TASK-CMD, TASK-LINT-043 and 044; forge-qualified blocker parsing, with outbox and private drafts blockers on agentic_development tasks migrated to the forge-qualified form; reduce docs/task-tracking-pilot.md to history. Done when mise run lid covers the tool.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The specs in scope are covered by tests that cite them, and pass
- [ ] #2 mise run lid reports no uncovered TASK spec
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-21, from the AD-5.1 code review: as a stopgap, the pilot accepts forge-qualified blockers by widening TASK_REF, but local_id compares only the last path segment with project_name, case-sensitively. So any host or owner with a repo of the same name resolves to this backlog, and a blocker on another repo is always unreadable (open). TASK-FILE-013, TASK-LAYOUT-011, TASK-LAYOUT-019 and TASK-XREPO replace this.

Edge audit for AD-336 (2026-11-24) left a fork in TASK-CMD-022/023 for this slice’s own edge audit: whether a zero lint count or an empty developer queue counts as an empty part, so that brief on a clean backlog prints nothing.

AD-336 (2026-11-25) added team support to specs this slice implements: the per-machine user key (TASK-XREPO-001, TASK-XREPO-003), queues narrowed to a person (TASK-RANK-001, TASK-RANK-003), next --assignee and --mine (TASK-CMD-026 to TASK-CMD-029), assignees in every view (TASK-CMD-003, TASK-CMD-010, TASK-CMD-030), the board and milestone never narrowed (TASK-CMD-031), the brief narrowed to the user (TASK-CMD-032), and the user command (TASK-CMD-001, TASK-CMD-033, TASK-CMD-034). AD-364, the skill text, waits on these commands.

Also from AD-336: TASK-CMD-035, with TASK-LAYOUT-004 and TASK-LAYOUT-018 revised: the user command reads nothing in the repo and needs no backlog.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: a20b213e-9cc5-4bd1-8407-62658bae5e42
created: 2026-11-26T13:02:35Z

---

AD-336's edge audit (2026-11-25) left forks in specs this slice implements, for its own edge audit: (1) TASK-XREPO-001, -003 and -004: whether a per-machine settings file that is empty, or holds only comments, is "missing" or "not a mapping"; whether an unknown key is ignored silently or reported; and what happens when the file exists but can't be read. (2) TASK-CMD-003: whether the tier column shows `-` only for a task with no `performer`, or also for an agent task with no `agent_tier`.

---
<!-- COMMENTS:END -->
