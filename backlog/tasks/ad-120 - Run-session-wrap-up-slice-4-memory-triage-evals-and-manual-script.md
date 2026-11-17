---
id: AD-120
title: Run session-wrap-up slice 4 memory-triage evals and manual script
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-4
dependencies:
  - AD-119
references:
  - docs/intent/session-wrap-up/session-wrap-up-specs.md:258-264
  - evals/session-wrap-up/latest-results.md
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After slice 4 is built, run its eval cases (WRAP-MEM-001, -002, -003, -005, -006) with `mise run eval` and the WRAP-MEM-004 manual script in a live session, then paste the output for triage and the review log. Done when every case and script has a dated result.

**Why it matters:** Confirms memory moves and retirements are safe before the skill edits memory for real.

**Why the developer:** the developer runs paid evals and live sessions
<!-- SECTION:DESCRIPTION:END -->
