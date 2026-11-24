---
id: AD-5.3
title: 'Task tracker slice 3: readiness, ranking, GitHub lookup and other repos'
status: To Do
assignee: []
created_date: '2026-11-20T13:25:00Z'
updated_date: '2026-11-24T06:11:00Z'
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
<!-- SECTION:NOTES:END -->
