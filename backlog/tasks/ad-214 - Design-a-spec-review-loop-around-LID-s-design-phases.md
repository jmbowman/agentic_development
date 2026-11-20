---
id: AD-214
title: Design a spec-review loop around LID's design phases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-6
dependencies:
  - AD-140
references:
  - docs/high-level-design.md:63
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#4. Spec
    and plan review
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The HLD lists a spec-review loop around LID's design phases as a planned component not yet designed. Write its LLD and specs through LID, starting from the synthesis note's 'Spec and plan review' stage. Done when an LLD exists and the HLD links it.

Input from AD-5's edge audit (2026-11-20), as the probe subagents reported it: a word cap and a target number of findings pulled against each other in four briefs, so findings were merged and lost detail; blind readers kept drawing on outside knowledge (the language's libraries, the adopted tool's conventions) and asked for the likely sources to be named in the brief; and the spec file's definitions produced cross-spec forks that per-line readers missed, which a cross-spec reader caught.

**Why it matters:** Catches spec defects before they cascade to tests and code.

**Why an agent:** agent drafts under LID; developer reviews at the stops
<!-- SECTION:DESCRIPTION:END -->
