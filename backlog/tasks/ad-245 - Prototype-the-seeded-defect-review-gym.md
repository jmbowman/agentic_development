---
id: AD-245
title: Prototype the seeded-defect review gym
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-7
dependencies: []
references:
  - docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Verdict
priority: low
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
An agent plants one to three realistic defects in a copy of a real slice; the reviewer reviews it blind; hits, misses and time are logged by defect category. This is the only route found to feedback on review accuracy (confidence does not track accuracy: Kaufman 2026, Perry 2023). Borrow the scoring loop from CodeReview-Coach and the attacker role from Code Defenders; no tool builds drills from one's own codebase. Done when one drill runs end to end; the note says it starts as an unproven trial.

**Why it matters:** Gives the developer measured feedback on review accuracy.

**Why an agent:** Build the drill generator and log; the developer later takes the drills
<!-- SECTION:DESCRIPTION:END -->
