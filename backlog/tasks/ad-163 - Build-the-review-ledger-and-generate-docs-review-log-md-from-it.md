---
id: AD-163
title: Build the review ledger and generate docs/review-log.md from it
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
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#9. Review
    waves and triage
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Build
    order
  - docs/review-log.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Slice 2: one JSON Lines record per review finding with fingerprint (category plus structural address), lens, verdict with evidence, disposition, a 'caused by a fix' flag and the content hash of what was reviewed. docs/review-log.md becomes generated from the ledger, with per-lens yield, forks per slice and overhead by change size. Borrow from review-convergence, layered-code-review, disensor and deep-review-loop; the rows the developer keeps by hand today are the migration source.

**Why it matters:** Replaces hand counts and feeds the stop rule, merge gate and process evaluation.

**Why an agent:** a coding agent can design and build the schema and generator through LID
<!-- SECTION:DESCRIPTION:END -->
