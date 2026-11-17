---
id: AD-243
title: Write a delta patch that shows each changed line once
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
  - upstream
milestone: m-7
dependencies:
  - AD-291
references:
  - docs/prior-art/2026-10-30-change-presentation.md#Verdict
  - docs/tool-feedback/delta.md
priority: medium
type: upstream
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement merged lines in delta: it already pairs minus and plus lines for within-line highlights (`src/edits.rs:24`); only the painting step, which draws the minus block then the plus block (`src/paint.rs:671-700` at 3c2269c), needs to change. Prepare the patch against delta main following its contributing guide, keep a fork with ready patches if the PR stalls. A person opens the PR. Done when a branch passes delta's tests and shows merged lines behind an option.

**Why it matters:** Delivers P3 (each changed line once) in the pager already used.

**Why an agent:** Rust patch with clear extension point; PR text stays human
<!-- SECTION:DESCRIPTION:END -->
