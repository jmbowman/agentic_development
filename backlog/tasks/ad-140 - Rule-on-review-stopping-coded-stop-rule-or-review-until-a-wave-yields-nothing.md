---
id: AD-140
title: 'Rule on review stopping: coded stop rule or review until a wave yields nothing'
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
  - docs/prior-art/2026-11-10-agentic-development-process-synthesis.md
  - '#98'
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Build
    order
  - docs/high-level-design.md:59-63
priority: high
type: decision
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 4c452121-b77a-43b0-830c-8909ca64d653
    role: created
    date: '2026-11-11'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Synthesis Decision 1 asks whether review waves continue until a wave 'yields nothing worth implementing' or follow a coded stop: one wide wave per phase, a further pass only after a verified high-severity fix or large rewrite, scoped to the change, capped at three, computed from a ledger. The note recommends the coded rule and recording a fix-caused flag so thresholds can be tuned from data. Done when the developer has ruled and the ruling is recorded in a decision doc.

**Why it matters:** Unblocks the ledger, stop-rule and orchestrator slices.

**Why the developer:** chooses between two readings of the process's intent
<!-- SECTION:DESCRIPTION:END -->
