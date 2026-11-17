---
id: AD-142
title: Rule on phase state machine versus protected state plus result checks
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
  - docs/high-level-design.md:42
priority: high
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Synthesis Decision 3 asks whether the HLD's planned 'small state machine' stays, or is replaced by sandbox-protected hook-written state plus checks of the result, with in-session hooks advisory and Probity dropped. The recommendation is sandbox baseline first, then result checks (stages 6, 8, 10, 12), revisiting a state machine only if the ledger shows skipped steps that result checks missed. This changes a planned HLD component, so it needs the developer's ruling.

**Why it matters:** Decides how much enforcement machinery every later slice needs.

**Why the developer:** changes a planned HLD component; needs developer ruling
<!-- SECTION:DESCRIPTION:END -->
