---
id: AD-110
title: Reduce the flaky session-wrap-up eval misses
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - process
milestone: m-4
dependencies: []
references:
  - docs/review-log/history-to-2026-11-22.md:40
  - docs/review-log/history-to-2026-11-22.md:74
  - evals/session-wrap-up/latest-results.md
  - docs/process-lessons.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/review-log/history-to-2026-11-22.md and evals/session-wrap-up/latest-results.md record three misses left at their rate: `repeat-run` (a dropped lesson returned 1 of 3), `routes-by-house-rules` (a dropped guess became a loose end 1 of 3) and `notes-compacted-transcript` (a declined item re-proposed, 1 miss in 5; WRAP-RUN-005, WRAP-RPT-010). Try one bounded round of wording changes in the skill's report template (process-lessons: put an output rule in the output's template), then record rates. Done when each case passes three runs or the rate is logged with the next stop decision.

**Why it matters:** Improves reliability of wrap-up reports.

**Why an agent:** skill-text edits; reruns are the developer's
<!-- SECTION:DESCRIPTION:END -->
