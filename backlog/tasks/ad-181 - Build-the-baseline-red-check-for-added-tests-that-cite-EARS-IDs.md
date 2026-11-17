---
id: AD-181
title: Build the baseline-red check for added tests that cite EARS IDs
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
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#6. Tests
    first
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Slice 7a, at commit time and in CI: each test the diff adds that cites an EARS ID must fail on the base tree and pass on the candidate. The list of new tests comes from the diff (never a file the agent writes); results are parsed fail-closed from pytest JUnit XML; empty, duplicated or stale result files are errors; a check out of scope reads inconclusive, never pass. Reimplement red-first-gate's idea (MIT, about 300 lines) in Python with must-reject fixtures.

**Why it matters:** Proves tests were red before the code made them green.

**Why an agent:** deterministic Python check with fixtures
<!-- SECTION:DESCRIPTION:END -->
