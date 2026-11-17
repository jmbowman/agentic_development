---
id: AD-225
title: Trial the re-derive-cited-text review lens from doctrine
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-175
references:
  - docs/prior-art/2026-11-13-doctrine.md#Ideas worth testing
priority: low
type: eval
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a review lens that re-derives each cited design or spec text and compares it with the citing text. In doctrine, 5 of 9 defects in one plan review cited the design correctly and restated it wrongly, which a coverage check passes. Trial it on one LLD and its specs and on a plan review, record yield against the plain lens wave. It is a gap beside lidc coverage.

**Why it matters:** Finds misquoted specs that traceability checks cannot.

**Why an agent:** lens prompt and a small trial
<!-- SECTION:DESCRIPTION:END -->
