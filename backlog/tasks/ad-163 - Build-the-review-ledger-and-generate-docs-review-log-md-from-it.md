---
id: AD-163
title: Build the review ledger and generate docs/review-log.md from it
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-23T11:18:00Z'
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
  - docs/review-log/history-to-2026-11-22.md
  - docs/review-log/README.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Slice 2: one JSON Lines record per review finding with fingerprint (category plus structural address), lens, verdict with evidence, disposition, a 'caused by a fix' flag and the content hash of what was reviewed. the review log becomes a table generated from the ledger, with per-lens yield, forks per slice and overhead by change size. Borrow from review-convergence, layered-code-review, disensor and deep-review-loop; the rows the developer keeps by hand today are the migration source.

**Why it matters:** Replaces hand counts and feeds the stop rule, merge gate and process evaluation.

**Why an agent:** a coding agent can design and build the schema and generator through LID
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: 27e13044-1d02-40c4-90d7-0134d1214b1d
created: 2026-11-23T11:18:00Z

---

From 2026-11-23 the review log has one file per day and component in docs/review-log/ (named <date>-<component>.md, a table row per wave), so parallel worktree sessions on different components never edit the same file; docs/review-log/history-to-2026-11-22.md is frozen at the waves up to 2026-11-22. The migration source is now both. If the ledger is built, generating a single table from it is for reading, not for adding to by hand.

---
<!-- COMMENTS:END -->
