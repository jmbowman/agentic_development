---
id: AD-113
title: Run the six notes-* wrap-up eval cases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
milestone: m-4
dependencies: []
references:
  - session:da2581da 2026-11-13
  - evals/session-wrap-up/
priority: medium
type: eval
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the six new eval cases under evals/session-wrap-up/notes-* (written for slice 6, reading subagent notes) with the exact command given by the agent (model claude-sonnet-5-5, judge, --no-publish, --keep-temp, one --case per run, TMPDIR prefix). Triage the pasted output, then tick the WRAP-NOTES specs that pass. Done when each case has a recorded result in docs/review-log.md and evals/session-wrap-up/latest-results.md.

**Why it matters:** Moves the slice 6 eval-only specs from [ ] to [x].

**Why the developer:** the developer runs paid evals themselves
<!-- SECTION:DESCRIPTION:END -->
