---
id: AD-189
title: Propose runner-proven coverage and per-spec staleness to lidc
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
  - upstream
milestone: m-6
dependencies:
  - AD-148
  - AD-220
references:
  - docs/tool-feedback/lid-tooling.md#(a) Staleness per spec by content hash
  - docs/tool-feedback/lid-tooling.md#(b) Coverage proven by the test runner
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#11.
    Traceability and staleness
priority: medium
type: upstream
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Slice 9: propose upstream that a spec counts as proven only when a citing test was reported as executed and passed (JUnit XML input) and that each spec's evidence goes stale when its text or its citing tests change (content-hash verdicts, IDs fixed). Open question: how to stop an agent re-stamping, answered here by making the stamp file a protected path. Coordinate with the Habeas Codicem conversation.

**Why it matters:** Closes the biggest open traceability gap: nothing marks spec evidence stale.

**Why the developer:** outward-facing proposal
<!-- SECTION:DESCRIPTION:END -->
