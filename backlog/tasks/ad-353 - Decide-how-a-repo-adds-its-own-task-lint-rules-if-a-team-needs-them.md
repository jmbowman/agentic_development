---
id: AD-353
title: Decide how a repo adds its own task lint rules, if a team needs them
status: To Do
assignee: []
created_date: '2026-11-24T04:53:00Z'
labels:
  - open-question
milestone: m-1
dependencies: []
priority: low
type: decision
ordinal: 44000
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: d5de0f02-d865-48c6-82a7-a60f7b5669eb
    role: created
    date: '2026-11-23'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The task tool has no way for a repo to add lint rules of its own: each repo checks its own conventions in its tests, as this repo does for TASK-REPO-004. If a team needs custom rules shared across its repos, decide how. What is known (2026-11-23): jsonschema cannot be vendored, since it needs rpds-py, a Rust extension with no pure-Python wheel; fastjsonschema (BSD-3-Clause, pure Python, tagged releases, so Renovate vendir tag pins work) supports drafts 4, 6 and 7 and parts of 2019-09 but not 2020-12, collects all errors only with fast_fail=False (recently fixed), and fetches remote $ref with urlopen unless handlers refuse it. A plain repo test remains the zero-cost option. Design: docs/intent/task-tracker/task-tracker-design.md, Open Questions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A ruling on whether and how the task tool checks per-repo rules, recorded in the task-tracker LLD
<!-- AC:END -->
