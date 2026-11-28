---
id: AD-163
title: Build the review ledger and generate docs/review-log.md from it
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-27T21:44:06Z'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-140
  - AD-199
  - AD-372
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
Slice 2: one JSON Lines record per review finding with fingerprint (category plus structural address), lens, verdict with evidence, disposition, a 'caused by a fix' flag and the content hash of what was reviewed. the review log becomes a table generated from the ledger, with per-lens yield, forks per slice and overhead by change size, plus the per-wave counts that docs/decisions/review-wave-stopping.md uses for its escalation triggers (wave number; findings raised, accepted, deferred, rejected; accepted findings caused by the previous wave's fixes). It also records what the stop and escalation check (AD-164), the merge gate (AD-193) and reviewer briefs read beyond single findings: each wave (its number, the content hash of the tree it reviewed, and its triage's ruling on whether it accepted anything to fix now, recorded once triage is complete), the developer's rulings on forks and on escalations (patch, rework or stop; a ruling to patch or rework restarts the wave count), the reason for each rejected finding and the task ID for each deferred one. Borrow from review-convergence, layered-code-review, disensor and deep-review-loop; the rows the developer keeps by hand today are the migration source.

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
