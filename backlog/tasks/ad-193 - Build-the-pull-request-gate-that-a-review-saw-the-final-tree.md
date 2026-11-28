---
id: AD-193
title: Build the pull-request gate that a review saw the final tree
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-26T14:03:47Z'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-164
  - AD-191
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#12.
    Commit, pull request and merge autonomy
  - docs/decisions/review-wave-stopping.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rung 2 mechanism in CI: pass only if a recorded review (from the ledger) saw the final tree per path, using git objects between merge base and head (disensor); the AD-164 check returns stop for the final tree, or the loop escalated and the developer ruled to stop (docs/decisions/review-wave-stopping.md); and CI judged with the base commit's configuration. One slice per pull request before stacking is tried.

**Why it matters:** Answers 'converged, then changed' mechanically.

**Why an agent:** CI check code
<!-- SECTION:DESCRIPTION:END -->
