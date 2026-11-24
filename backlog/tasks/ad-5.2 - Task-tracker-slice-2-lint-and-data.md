---
id: AD-5.2
title: 'Task tracker slice 2: lint and data'
status: To Do
assignee: []
created_date: '2026-11-20T13:25:00Z'
updated_date: '2026-11-24T05:59:00Z'
labels: []
milestone: m-1
dependencies:
  - AD-5.1
  - AD-332
  - AD-336
  - AD-354
parent_task_id: AD-5
priority: high
type: feature
ordinal: 21000
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
Second slice of AD-5: the specified data layer and lint, with each data fix landing in the same change as the rule that requires it, so check passes at the end of the slice. Unblocks AD-13 and AD-329, and the delivery of the copier-python scaffolding draft, since everything that can turn a consumer check red ships here. Scope: the TASK-LAYOUT, TASK-FILE, TASK-MS and TASK-FOCUS specs, TASK-LINT except 043 and 044, all in code with no schema files, TASK-REPO-002 and 004. Data fixes: milestone descriptions (the agent drafts Description; the developer writes each Importance), references to ignored tmp/ files (AD-7, AD-147, AD-219), the AD-31 label and the AD-308 milestone, merging AD-230 into AD-270 and AD-189 into AD-147 and splitting out AD-189 agent drafting. Then, after AD-332, update the copier-python outbox draft that ships the backlog scaffolding.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The specs in scope are covered by tests that cite them, and pass
- [ ] #2 mise run check passes over this repo backlog with the new lint
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-21, from the AD-5.1 code review: the pilot tool still loads completed/ as ordinary tasks and never reads archive/tasks/ (TASK-LAYOUT-007, TASK-LAYOUT-008), and requires `type` whenever config.yml lists types, which the format reference now states. Repo with no backlog directory: see the question raised at the AD-5.1 stop.

Edge audit for AD-336 (2026-11-24) left forks in specs this slice implements, to settle in this slice’s own edge audit before its tests: (1) TASK-LINT-042, whether priorities must be exactly high, medium, low (subset, order, missing key); (2) TASK-LINT-042, whether "sets" default_assignee, default_reporter or definition_of_done includes empty values ("", null, []); (3) TASK-LINT-001, whether "open tasks and drafts" means open tasks plus all drafts or open drafts only for the link rules, and whether a file TASK-LINT-005 drops is still "loaded" for other rules; (4) TASK-LINT-045, which pairs of TASK-LINT-006 to 033 describe the same defect (for example a decision task with no performer: a missing key and a performer that isn't human), and which finding is shown.
<!-- SECTION:NOTES:END -->
