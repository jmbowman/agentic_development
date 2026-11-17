---
id: AD-164
title: Build the coded review stop-rule function over the ledger
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-163
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#10.
    Convergence and stopping
  - docs/prior-art/2026-11-13-doctrine.md#Ideas worth testing
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A pure function over the ledger returning continue, stop or escalate-to-developer: one wide wave per phase, a further pass only for a verified high-severity fix or large rewrite scoped to the fix diff, hard cap of three passes, never 'zero findings' as the exit, converged result void when the content hash changes, and pre-existing or already-ruled findings never triggering a pass. Include the escalate rule from doctrine (serious findings not falling across two waves). Fixtures per principle 4.

**Why it matters:** Stops review loops mechanically and cheaply.

**Why an agent:** pure code with fixtures
<!-- SECTION:DESCRIPTION:END -->
