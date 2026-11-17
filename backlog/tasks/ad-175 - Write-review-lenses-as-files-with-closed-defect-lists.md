---
id: AD-175
title: Write review lenses as files with closed defect lists
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-140
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#9. Review
    waves and triage
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
Slice 6 part 1: lenses as files in the skills package, each a method with a closed defect list per phase: edge case (BMAD lens, MIT), verification gap, intent alignment, cold read, ease of human review (with brooks-lint's finding format and what-not-to-flag lists, severity left to triage). Done when the lens files exist, each stating its defect types, and the current review waves can use them.

**Why it matters:** Makes review lenses reusable, measurable and reviewable.

**Why an agent:** prompt and doc authoring
<!-- SECTION:DESCRIPTION:END -->
