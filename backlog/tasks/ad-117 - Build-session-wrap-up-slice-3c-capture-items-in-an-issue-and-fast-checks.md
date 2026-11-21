---
id: AD-117
title: 'Build session-wrap-up slice 3c: capture items in an issue, and fast checks'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-4
dependencies: []
references:
  - docs/intent/session-wrap-up/session-wrap-up-specs.md:233
  - docs/intent/session-wrap-up/session-wrap-up-specs.md:237-254
  - docs/intent/session-wrap-up/session-wrap-up-design.md:161
  - docs/intent/session-wrap-up/session-wrap-up-design.md:316-327
  - README.md#Status
  - WRAP-GATE-024
  - WRAP-GATE-025
  - WRAP-GATE-026
  - WRAP-GATE-027
  - WRAP-GATE-028
  - WRAP-GATE-029
  - WRAP-GATE-030
  - WRAP-GATE-034
  - WRAP-GATE-037
  - WRAP-GATE-038
  - WRAP-GATE-039
  - WRAP-GATE-011
  - WRAP-GATE-012
  - WRAP-GATE-032
  - WRAP-GATE-033
  - >-
    docs/intent/session-wrap-up/session-wrap-up-specs.md#Capture and fast checks
    (slice 3c)
  - >-
    docs/intent/session-wrap-up/session-wrap-up-design.md#Open Questions &
    Future Decisions
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 5af90670-4925-4893-9f63-86ccfe5510bf
    role: created
    date: '2026-11-04'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the session-wrap-up skill's slice 3c in `skills/session-wrap-up/`: after the developer confirms item text, offer to apply now, capture in one GitHub issue on the host repo (via `gh repo view` / `gh issue create`), or leave open, and run the instruction files' fast checks after applying items. Specs: WRAP-GATE-024, WRAP-GATE-025, WRAP-GATE-026, WRAP-GATE-027, WRAP-GATE-028, WRAP-GATE-029, WRAP-GATE-030, WRAP-GATE-034, WRAP-GATE-037, WRAP-GATE-038, WRAP-GATE-039 (issue capture) and WRAP-GATE-011, WRAP-GATE-012, WRAP-GATE-032, WRAP-GATE-033 (fast checks). Walk it through LID (edge audit, tests first, code, review wave), add an eval case citing WRAP-GATE-034 and manual scripts (or scenarios) for the *(manual)* specs in `evals/session-wrap-up/manual.md`, and update the README status line. Done when the skill text carries every spec, `mise run check` passes, and the specs are marked per the repo's marker convention.

**Why it matters:** Lets a wrap-up park lessons in an issue when in-progress work shouldn't be committed with them, and catches broken checks after applying items.

**Why an agent:** specs are written; implementation, tests and skill text are agent work
<!-- SECTION:DESCRIPTION:END -->
