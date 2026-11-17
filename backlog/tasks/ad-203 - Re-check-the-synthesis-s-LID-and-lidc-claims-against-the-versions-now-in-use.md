---
id: AD-203
title: Re-check the synthesis's LID and lidc claims against the versions now in use
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Appendix
    A: sources read in source
  - docs/tool-feedback/lid.md
  - AGENTS.md
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The synthesis reads LID at 1.4.4 and lid-tooling at 1f5627d (installed here then 1.4.0), but apm now locks LID 1.4.6 (see commit 5c20e2f) and mise pins lidc 0.3.0; AGENTS.md still says LID Version 1.4.0. Re-check the claims the proposals rest on (no hooks shipped, thirteen checks, staleness not emitted, setup.md:59 wording) against the current versions and update the note and tool-feedback pages. Done when stale version statements are corrected or confirmed.

**Why it matters:** Keeps upstream proposals accurate when they are filed.

**Why an agent:** reading source and updating docs
<!-- SECTION:DESCRIPTION:END -->
