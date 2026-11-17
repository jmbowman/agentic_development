---
id: AD-174
title: Trial Habit Hooks on this repo's strict lint profile
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#7. The
    implementation loop
priority: medium
type: eval
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wire Habit Hooks (Python, uv, ruff) as a mise task and Stop hook mapping each lint violation to a named code smell and a coaching guide that states the gaming anti-pattern and a done condition, with a content-hash ratchet. The HLD names 'relax a check rather than fix the code' as a failure and this is the only tool found aimed at it. Done when a trial on real slices records whether findings are fixed genuinely, with the result in docs/.

**Why it matters:** Counters check-relaxing behavior.

**Why an agent:** integration and a small trial
<!-- SECTION:DESCRIPTION:END -->
