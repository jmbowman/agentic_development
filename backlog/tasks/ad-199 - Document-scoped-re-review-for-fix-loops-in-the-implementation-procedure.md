---
id: AD-199
title: Document scoped re-review for fix loops in the implementation procedure
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-140
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#7. The
    implementation loop
priority: medium
type: docs
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Borrow superpowers' bounded fix loop for implementation: findings go back to the same implementer for up to three rounds then to a fresh one; every re-review is scoped to the findings and the fix diff; anything outside scope goes to a ledger instead of widening the loop. Write it into the delegation/dispatch guidance (skill or AGENTS.md) alongside the stop rule.

**Why it matters:** Keeps re-review from widening and growing in cost.

**Why an agent:** procedure text
<!-- SECTION:DESCRIPTION:END -->
