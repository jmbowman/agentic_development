---
id: AD-172
title: Write the commit-message and PR-description skill
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-6
dependencies:
  - AD-171
references:
  - docs/high-level-design.md:60
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Build
    order
  - docs/high-level-design.md:59-60
  - README.md#Status
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#12.
    Commit, pull request and merge autonomy
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
HLD planned component: a skill giving a clear style and detail calibrated for review that does not restate the diff, with linting only as a form check. It is the other half of the commit-form work in synthesis stage 12 (rung 0 now, sealed messages at rung 1 later). Done when a skill exists in skills/ through LID with evals, and the trial verdict on lint is wired in.

**Why it matters:** Better review-ready commit messages without restating diffs.

**Why an agent:** skill authoring through LID
<!-- SECTION:DESCRIPTION:END -->
