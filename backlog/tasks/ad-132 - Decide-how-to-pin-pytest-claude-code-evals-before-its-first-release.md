---
id: AD-132
title: Decide how to pin pytest-claude-code-evals before its first release
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-5
dependencies: []
references:
  - docs/intent/interactive-evals/interactive-evals-design.md:93
  - IEVAL-DEP-001
priority: high
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The interactive-evals design leaves open whether the `interactive` dependency group should pin pytest-claude-code-evals to a git commit now, or wait for the plugin's first release before writing scenarios here; it depends on how far the plugin's first slice goes. Decide, so that IEVAL-DEP-001 and -002 can be implemented. Done when the decision is recorded in the interactive-evals design's Decisions table and the open question is removed.

**Why it matters:** Unblocks every interactive scenario in this repo.

**Why the developer:** a choice between readings of intent and of the plugin's readiness
<!-- SECTION:DESCRIPTION:END -->
