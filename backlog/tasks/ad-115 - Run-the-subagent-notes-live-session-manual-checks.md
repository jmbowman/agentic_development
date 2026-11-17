---
id: AD-115
title: Run the subagent-notes live-session manual checks
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
  - partly-done
milestone: m-4
dependencies: []
references:
  - docs/intent/subagent-notes/subagent-notes-specs.md:95-97
  - docs/prior-art/2026-11-11-subagent-process-notes.md#Probe of the platform
  - session:6faee248 2026-11-13
  - session:da2581da 2026-11-13
  - evals/session-wrap-up/manual.md:237
priority: medium
type: eval
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Specs NOTES-LIVE-001, -002 and -003 are manual: in an attended session a finished subagent's report reaches the main agent unchanged and its notes file appears before the turn ends; in a `-p` run the result is the main agent's own last message; with hooks registered both by the plugin and in .claude/settings.json each subagent is asked exactly once. Run them on the current Claude Code, record results in docs/review-log.md as the repo rule says, and tick the specs.

**Why it matters:** Confirms the shipped hooks behave in real sessions.

**Why the developer:** manual runs in a live attended session

**Status when filed (partly-done):** hooks and specs implemented (#214, #221, #223, #226); the three NOTES-LIVE specs are still [ ]
<!-- SECTION:DESCRIPTION:END -->
