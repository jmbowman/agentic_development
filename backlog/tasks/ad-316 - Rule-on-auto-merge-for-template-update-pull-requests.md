---
id: AD-316
title: Rule on auto-merge for template update pull requests
status: To Do
assignee: []
created_date: '2026-11-17T12:18:00Z'
labels:
  - open-question
milestone: m-1
dependencies: []
references:
  - docs/prior-art/2026-11-16-cross-repo-task-coordination.md
  - docs/high-level-design.md
  - docs/task-tracking-pilot.md
priority: medium
type: decision
ordinal: 3000
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The cross-repo coordination note's decision 8 recommends turning auto-merge off for Renovate's Copier manager, so a person merges each template update and the follow-up tasks it carries. That conflicts with the HLD's tenet 6 and with the shared preset, which merges updates automatically once CI passes. The pilot didn't touch it. Choose: keep auto-merge and rely on CI (including the test that custom task keys survive Backlog.md); turn it off for Copier updates only; or turn it off only for updates that carry a follow-up task file. Done when the ruling is noted in this task and, if the preset changes, a task for that change exists; the HLD or a decision doc records it when LID's arrow is walked for the task tracker (AD-5), since it touches tenet 6.
<!-- SECTION:DESCRIPTION:END -->
