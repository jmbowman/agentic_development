---
id: AD-138
title: Replace session-wrap-up approval manual scripts with interactive scenarios
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-5
dependencies:
  - AD-134
  - AD-136
references:
  - docs/intent/session-wrap-up/session-wrap-up-specs.md:185
  - evals/session-wrap-up/manual.md:5
  - evals/session-wrap-up/manual.md:100-103
  - docs/intent/interactive-evals/interactive-evals-design.md:85-88
  - evals/session-wrap-up/manual.md
  - evals/README.md
  - docs/intent/interactive-evals/interactive-evals-specs.md
  - IEVAL-RUN-001
  - IEVAL-RUN-002
  - IEVAL-RUN-003
  - IEVAL-MARK-006
  - NOTES-LIVE-003
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The approval-gate specs of slice 3b (WRAP-GATE-001 to -048 marked *(manual)*, plus WRAP-RUN-013) are carried by the skill but their manual scripts in `evals/session-wrap-up/manual.md` (from 'Setting up the approval runs' on) have never passed; one run failed WRAP-GATE-019 and the skill was then changed. The specs file says they wait for the interactive harness to replace them. Write scenarios in `evals/session-wrap-up/interactive/` that each replace one script (with `replaces` markers per IEVAL-MARK-005/-006), delete replaced scripts and move their result lines to the review log. Done when `mise run check` collects them and each replaced script is gone.

**Why it matters:** Turns the riskiest part of the wrap-up skill (where it starts writing) from unrun manual scripts into repeatable tests.

**Why an agent:** scenario code is agent work once the plugin is pinned
<!-- SECTION:DESCRIPTION:END -->
