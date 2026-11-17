---
id: AD-182
title: Build the source-only re-run check judged with the base commit's config
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-141
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#8.
    Verification of tests against requirements
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Slice 7b: reimplement promptwheel's idea in Python as a CI and commit-time check: revert edits to tests, config, graders and golden files, re-run the gate on base plus source changes only, and flag the change as gamed if less than half the gain survives, with thresholds and protected paths read from the base commit. Use tamperward's threat model (case folding, file modes, replaced git objects, child processes) as the test list and avoid the trailer override. Fall back to adopting promptwheel if fiddly.

**Why it matters:** Catches tests, config or graders loosened in the same change.

**Why an agent:** deterministic check with fixtures
<!-- SECTION:DESCRIPTION:END -->
