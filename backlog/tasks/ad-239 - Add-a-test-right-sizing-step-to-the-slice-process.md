---
id: AD-239
title: Add a test right-sizing step to the slice process
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-7
dependencies:
  - AD-236
references:
  - https://github.com/jmbowman/agentic_development/issues/90
  - docs/prior-art/2026-10-27-review-and-comprehension-burden.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #90: before a slice goes to review, for each EARS ID added or changed keep the smallest test set that pins the spec. Structure signals first (one test per failure clause, combinations only with 3 or more interacting factors, one integration wiring test per spec); then planted-bug signals (a new test killing no mutant the others miss is removed, using musthold per-test kill data or cosmic-ray/Mull). Removed tests are listed in the review's lowest tier with reasons. Write it into the process guidance, spec and tests. The planted-bug half depends on #89's musthold evaluation.

**Why it matters:** Cuts review burden from redundant tests.

**Why an agent:** process rule and tooling design after evaluation
<!-- SECTION:DESCRIPTION:END -->
