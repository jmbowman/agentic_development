---
id: AD-178
title: Build the coded dispatch plan for review waves
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-155
  - AD-175
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#9. Review
    waves and triage
  - docs/high-level-design.md:62
  - README.md#Status
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Compute the review plan in code from artifact kind and change size: which lenses each document or hunk owes, coverage credited by hunk digest, re-rounds reviewing only changed or referencing hunks. Design from craftsman (code diffs) extended to documents. Done when a plan function has fixtures and the wave procedure uses it.

**Why it matters:** Rule-driven dispatch beat agent discretion in the evidence read.

**Why an agent:** pure code
<!-- SECTION:DESCRIPTION:END -->
