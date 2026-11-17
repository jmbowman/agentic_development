---
id: AD-139
title: Run session-wrap-up approval scenarios three times
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-5
dependencies:
  - AD-138
references:
  - evals/session-wrap-up/manual.md:100-103
  - docs/intent/session-wrap-up/session-wrap-up-specs.md:185
  - evals/session-wrap-up/manual.md
  - evals/session-wrap-up/latest-results.md
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the approval-gate scenarios that replace the slice 3b manual scripts three times each on the same skill text and paste the output for triage, so the review log gets an Interactive row and `evals/session-wrap-up/latest-results.md` gets a row per scenario. Re-check WRAP-GATE-019 in particular, since its last manual run failed before the skill was changed.

**Why it matters:** Shows the approval gate holds across runs, not just once.

**Why the developer:** the developer runs paid evals
<!-- SECTION:DESCRIPTION:END -->
