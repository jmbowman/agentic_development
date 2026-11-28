---
id: AD-200
title: Trial craftsman against a plain lens wave on seeded and escape cases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-155
  - AD-168
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Tensions
    and open questions for the developer
  - docs/decisions/review-wave-stopping.md
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run craftsman (MIT, Python, never commits) and a plain lens wave on the same seeded and escape cases from the reviewer corpus and adopt craftsman for code diffs if it wins on recall, precision and cost. Paid runs; the developer starts them. Includes the cost-and-value triage of its 71-86% precision. Also check whether craftsman can run full-scope later waves rather than fix-diff-only re-review, which docs/decisions/review-wave-stopping.md requires (see AD-155); if it can't, it can't be adopted as it stands.

**Why it matters:** Settles build-or-adopt for code-diff review.

**Why the developer:** paid eval runs
<!-- SECTION:DESCRIPTION:END -->
