---
id: AD-179
title: Use the BMAD edge-case lens as the prompt for LID's LLD probe
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#2.
    Design: the LLD
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reimplement BMAD's edge-case hunter (enumerate every branch and boundary, report only unhandled paths, then try to falsify the author's claims; MIT) as the prompt for LID's LLD-level probe run by a blind subagent, and add the GSD-style decision-coverage check (every row of an LLD's Decisions table reflected in at least one EARS line). The developer finds this lens most useful on plans before implementation. Done when the probe prompt and check exist and are used in a review.

**Why it matters:** Strengthens the stage where the developer's attention pays most.

**Why an agent:** prompt authoring and a small check
<!-- SECTION:DESCRIPTION:END -->
