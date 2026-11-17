---
id: AD-157
title: Rule on the full arrow for small changes and on when agents start committing
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
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Synthesis Decisions 6 and 8. Decision 6: keep the rule that every change, including small fixes, walks the full arrow, and measure overhead by change size from the ledger. Decision 8: stay at commit rung 0 (developer commits) until the stage 6 and 8 checks and the ledger have run on several slices, then move to rung 1 with sealed messages. Both come with recommendations; the developer confirms or changes each.

**Why it matters:** Settles two standing policies the later slices assume.

**Why the developer:** policy on the developer's own commits and workflow
<!-- SECTION:DESCRIPTION:END -->
