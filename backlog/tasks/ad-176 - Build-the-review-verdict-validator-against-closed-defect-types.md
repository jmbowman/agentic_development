---
id: AD-176
title: Build the review verdict validator against closed defect types
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-175
references:
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
A small script that validates a reviewer's structured verdict against a versioned catalogue of defect types (letspecify's gate): an unknown type, or a finding with no remedy or provenance, voids the whole verdict as 'not critiqued'; a finding counts only when a strict majority of passes report it; a critic from the author's model family is rejected where possible. Done when fixtures show each rejection path.

**Why it matters:** Stops findings outside the list padding a wave.

**Why an agent:** deterministic script with fixtures
<!-- SECTION:DESCRIPTION:END -->
