---
id: AD-156
title: 'Rule on traceability upgrades: upstream to lidc or a local checker'
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
  - docs/tool-feedback/lid-tooling.md
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Synthesis Decision 5: file the three lidc bugs and the small proposals first (recording them in docs/tool-feedback/ per project rules), use the response as the test of whether upstream is alive, talk to Habeas Codicem's author before fixing a staleness design, and keep any local check a separate script that reads lidc's JSON, not a patched binary. The developer decides, including the agreed quiet period before asking LID's author where lidc should live.

**Why it matters:** Unblocks staleness and runner-proven coverage work.

**Why the developer:** choosing upstream versus local fork is the developer's call
<!-- SECTION:DESCRIPTION:END -->
