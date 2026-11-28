---
id: AD-155
title: 'Rule on craftsman: trial for code review or build the orchestrator code mode'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Tensions
    and open questions for the developer
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Synthesis Decision 4: build the ledger, stop rule and document mode here (nothing covers them), and before building a code mode run craftsman and a plain lens wave on the same seeded and escape cases, adopting craftsman for code diffs if it wins. Craftsman's planner re-reviews only the fix diff, which docs/decisions/review-wave-stopping.md rules out for review waves, so a trial checks whether full-scope later waves can be configured. Done when the developer rules, and records it.

**Why it matters:** Avoids rebuilding dispatch that an MIT tool already provides, or adopting one that does not fit.

**Why the developer:** build versus adopt choice for the developer
<!-- SECTION:DESCRIPTION:END -->
