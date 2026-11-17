---
id: AD-226
title: Try doctrine's reviewer prompt lines in the review-wave prompts
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - docs/prior-art/2026-11-13-doctrine.md#Ideas worth testing
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#10.
    Convergence and stopping
priority: low
type: eval
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Test adding to reviewer prompts: re-derive your acquittals, and a review counts as done only with a stated basis; zero findings is not done (doctrine rated the first its most useful line, and enforces done-needs-basis in code). Reconcile with the synthesis rule that 'zero findings' is never the stop condition and BMAD's removal of a zero-findings halt that pressured reviewers into inventing findings. Done when a trial on two waves records whether findings invent or sharpen.

**Why it matters:** A cheap prompt change that may improve review quality.

**Why an agent:** prompt edits and trial
<!-- SECTION:DESCRIPTION:END -->
