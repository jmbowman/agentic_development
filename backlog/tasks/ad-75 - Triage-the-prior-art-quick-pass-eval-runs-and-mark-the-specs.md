---
id: AD-75
title: Triage the prior-art quick-pass eval runs and mark the specs
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-3
dependencies:
  - AD-74
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:42-53
  - docs/intent/prior-art-search/prior-art-search-specs.md:246-249
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
Triage the pasted output of the quick-pass cases, trace each failure to the skill, grader or case, fix the skill or grader as needed, append the review-log row and update `evals/prior-art-search/latest-results.md`. Mark PRIOR-EFF-005, PRIOR-EFF-008, PRIOR-SRCH-017, PRIOR-SRCH-022, PRIOR-LIC-007, PRIOR-LIC-009, PRIOR-LIC-010 and PRIOR-RPT-003 `[x]` once they pass.

**Why it matters:** Closes the spec gaps and fixes whatever the runs expose.

**Why an agent:** triage of pasted output and doc updates are agent work
<!-- SECTION:DESCRIPTION:END -->
