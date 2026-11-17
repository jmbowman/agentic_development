---
id: AD-31
title: Add job timeout and concurrency limits to the check workflow
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-2
dependencies:
  - AD-30
references:
  - docs/intent/check-workflow/check-workflow-design.md:118
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
If decided, add `timeout-minutes` and a `concurrency` group to `.github/workflows/check.yml`, with CHECK specs and structure tests, and remove the Deferred entry. Done when `mise run check` passes.

**Why it matters:** Bounds runaway CI minutes.

**Why an agent:** small workflow change once decided
<!-- SECTION:DESCRIPTION:END -->
