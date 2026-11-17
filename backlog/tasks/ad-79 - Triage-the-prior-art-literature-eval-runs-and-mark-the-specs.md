---
id: AD-79
title: Triage the prior-art literature eval runs and mark the specs
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-3
dependencies:
  - AD-78
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:91-107
  - docs/intent/prior-art-search/prior-art-search-design.md#Testing
  - docs/review-log.md
priority: medium
type: review
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Triage the literature cases' output, fix skill or grader faults, append the review-log row and update `evals/prior-art-search/latest-results.md`. Mark PRIOR-TRIG-004, PRIOR-LIT-001 to -014, -016, -017, PRIOR-SRCH-013, -015, PRIOR-ACC-006, -014, PRIOR-SRC-015, PRIOR-RPT-001, -002, -008, -009 and PRIOR-SAVE-009 `[x]` once they pass (some, such as PRIOR-LIT-013 and PRIOR-ACC-006, are only covered when a live outage arises).

**Why it matters:** Closes the largest block of open specs in the repo.

**Why an agent:** triage and doc updates are agent work
<!-- SECTION:DESCRIPTION:END -->
