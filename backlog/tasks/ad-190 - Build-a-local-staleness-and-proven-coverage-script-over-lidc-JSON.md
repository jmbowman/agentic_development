---
id: AD-190
title: Build a local staleness and proven-coverage script over lidc JSON
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-156
  - AD-189
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#11.
    Traceability and staleness
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Tensions
    and open questions for the developer
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fallback if upstream stays quiet for the agreed period: a separate script that reads lidc's JSON output plus the runner's JUnit report and per-spec hash verdicts in a protected directory, reporting states cited, proven and stale, blocking at commit and in CI. Never a patched lidc binary.

**Why it matters:** A local path if lidc upstream is inactive.

**Why an agent:** script through LID
<!-- SECTION:DESCRIPTION:END -->
