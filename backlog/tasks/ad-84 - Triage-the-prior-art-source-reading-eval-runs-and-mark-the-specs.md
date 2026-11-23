---
id: AD-84
title: Triage the prior-art source-reading eval runs and mark the specs
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-3
dependencies:
  - AD-83
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:252-269
  - docs/review-log/README.md
priority: medium
type: review
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Triage the output of offline-local-candidates, snippet-reads, links-in-report and privacy-public, fix faults, append the review-log row, update latest-results, and mark PRIOR-SRC-007, -011 to -014, -016, PRIOR-CLS-013, -014, PRIOR-LIC-007, -008, PRIOR-RPT-008 and -009 `[x]` once they pass. PRIOR-SRC-010 (subagent prompt rules) is checked via settings-canary.

**Why it matters:** Closes the read-depth and lookalike spec gaps.

**Why an agent:** triage and doc updates are agent work
<!-- SECTION:DESCRIPTION:END -->
