---
id: AD-266
title: 'Write a single-turn eval: does a recorded decision change agent behavior'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies: []
references:
  - docs/prior-art/2026-11-06-decision-records-and-lid.md#Verdict
  - 'docs/tool-feedback/lid.md#6. Evidence for #79''s premise'
priority: medium
type: eval
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build an eval case modeled on keep-the-why's experiment: ask the agent to 'simplify' a retry wrapper whose rejected alternative is recorded or not recorded, and grade whether it offers to drop the Retry-After handling (0 of 10 with the record vs 7 of 10 without in that tool's weak, author-graded run). It gives evidence for LID issue #79's premise without waiting for a multi-turn harness. Done when the case and graders exist; the developer runs it.

**Why it matters:** First evidence that decision docs change agent behavior.

**Why an agent:** writing eval cases and graders
<!-- SECTION:DESCRIPTION:END -->
