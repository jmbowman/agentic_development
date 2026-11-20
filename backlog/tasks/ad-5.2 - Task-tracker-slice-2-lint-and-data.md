---
id: AD-5.2
title: 'Task tracker slice 2: lint and data'
status: To Do
assignee: []
created_date: '2026-11-20T13:25:00Z'
labels: []
milestone: m-1
dependencies:
  - AD-5.1
  - AD-332
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
Second slice of AD-5: the specified data layer and lint, with each data fix landing in the same change as the rule that requires it, so check passes at the end of the slice. Unblocks AD-13 and AD-329, and the delivery of the copier-python scaffolding draft, since everything that can turn a consumer check red ships here. Scope: the TASK-LAYOUT, TASK-FILE, TASK-MS and TASK-FOCUS specs, TASK-LINT except 043 and 044, the schemas (settling the schema engine, open question 14), TASK-REPO-002 and 004. Data fixes: milestone descriptions (the agent drafts Description; the developer writes each Importance), references to ignored tmp/ files (AD-7, AD-147, AD-219), the AD-31 label and the AD-308 milestone, merging AD-230 into AD-270 and AD-189 into AD-147 and splitting out AD-189 agent drafting. Then, after AD-332, update the copier-python outbox draft that ships the backlog scaffolding.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The specs in scope are covered by tests that cite them, and pass
- [ ] #2 mise run check passes over this repo backlog with the new lint
<!-- AC:END -->
