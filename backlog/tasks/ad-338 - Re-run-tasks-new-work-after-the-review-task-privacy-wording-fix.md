---
id: AD-338
title: Re-run tasks-new-work after the review-task privacy wording fix
status: To Do
assignee: []
created_date: '2026-11-21T23:20:00Z'
labels:
  - loose-end
milestone: m-4
dependencies: []
references:
  - evals/session-wrap-up/tasks-new-work
  - docs/review-log.md
priority: low
type: eval
ordinal: 29000
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: febc0a58-71fe-4ef9-b3c7-3cc6205db7f4
    role: created
    date: '2026-11-21'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The last session-wrap-up eval round failed `review-task-screened` in one of three tasks-new-work runs: a task title hinted that a colleague was on leave. `skills/session-wrap-up/references/tasks.md` now gives that phrase as the example to avoid, but no run has tested the change. Run the case three times with the Sonnet judge (the command in `evals/README.md`, plus `--judge-model claude-sonnet-5-5`), then record the round in the review log and `latest-results.md`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A three-run round of tasks-new-work on the current skill text is in docs/review-log.md and evals/session-wrap-up/latest-results.md
<!-- AC:END -->
