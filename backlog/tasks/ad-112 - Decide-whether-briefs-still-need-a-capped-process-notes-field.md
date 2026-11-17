---
id: AD-112
title: Decide whether briefs still need a capped process-notes field
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
  - maybe-done
milestone: m-4
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/160
  - https://github.com/jmbowman/agentic_development/issues/159
  - skills/prior-art-search/references/verification.md
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #160 and #159 proposed that skills briefing subagents ask for a capped process_note field (at most 5 items, none allowed) and that prior-art-search have an optional process_note record type. The subagent-notes hooks now collect notes without changing briefs, which may make this unnecessary. Decide for prior-art-search whether its records still need a process_note type (see skills/prior-art-search/references/verification.md), and if not, note the decision in the issues and drop it.

**Why it matters:** Avoids duplicate mechanisms for the same notes.

**Why the developer:** design choice between two mechanisms

**Status when filed (maybe-done):** the hooks design chose resume-with-a-question over brief fields (docs/intent/subagent-notes)
<!-- SECTION:DESCRIPTION:END -->
