---
id: AD-48
title: Make prior-art-search ask for real use cases and walk them first
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/196
  - docs/prior-art/2026-11-06-agent-reference-clones.md
  - skills/prior-art-search/SKILL.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #196 (first and last proposals): step 1 should ask the developer for the two or three most common ways the result will be used and record them in the note's Need section (non-interactive run: record the question as unanswered); step 11 walks those cases before generic scenarios; for each borrowed paper idea record whether the paper's setting matches the design's (who reads what, through which channel) and drop ideas whose threat model does not apply. Edit skills/prior-art-search/SKILL.md, references/note-template.md and the design, specs, tests and an eval case under a LID pass. Evidence: the reference-clones refresh, where the developer's own two cases reshaped the design and a links-only llms.txt defense did not apply.

**Why it matters:** Verdicts get tested against how the result will really be used.

**Why an agent:** skill and spec edits following a written proposal
<!-- SECTION:DESCRIPTION:END -->
