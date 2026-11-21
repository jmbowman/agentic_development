---
id: AD-122
title: Run session-wrap-up slice 5 cross-repo evals and manual scripts
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-21T19:18:00Z'
labels:
  - spec
milestone: m-4
dependencies:
  - AD-121
references:
  - docs/intent/session-wrap-up/session-wrap-up-specs.md:266-279
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After slice 5 is built, run its eval cases (WRAP-XREPO-001, -005 to -009) with `mise run eval` and the manual scripts for WRAP-XREPO-002 to -004, -010 and -011, which need another live session, then paste the output for triage. Done when every case and script has a dated result and a review-log row.

**Why it matters:** Verifies that messages and issues sent in the developer's name are screened and self-contained.

**Why the developer:** paid evals and multi-session live runs are the developer's
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Superseded with AD-121 by AD-6 (2026-11-21): the cross-repo message and issue routing this task would have evaluated was removed from the design, and AD-6 carries the evals for outbox drafts.
<!-- SECTION:FINAL_SUMMARY:END -->
