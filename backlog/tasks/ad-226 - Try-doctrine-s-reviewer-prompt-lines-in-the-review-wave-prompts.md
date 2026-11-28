---
id: AD-226
title: Try doctrine's reviewer prompt lines in the review-wave prompts
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-26T15:25:51Z'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-199
references:
  - docs/prior-art/2026-11-13-doctrine.md#Ideas worth testing
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#10.
    Convergence and stopping
  - docs/decisions/review-wave-stopping.md
priority: low
type: eval
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Test adding to reviewer prompts: re-derive your acquittals, and a review counts as done only with a stated basis; zero findings is not done (doctrine rated the first its most useful line, and enforces done-needs-basis in code). Reconcile with docs/decisions/review-wave-stopping.md, whose briefs tell reviewers that reporting nothing is a good outcome, and with BMAD's removal of a zero-findings halt that pressured reviewers into inventing findings. Done when a trial on two waves records whether findings invent or sharpen.

**Why it matters:** A cheap prompt change that may improve review quality.

**Why an agent:** prompt edits and trial
<!-- SECTION:DESCRIPTION:END -->
