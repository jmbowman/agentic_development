---
id: AD-144
title: Decide when an eval-only spec is marked implemented
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-6
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:3
  - evals/prior-art-search/latest-results.md
  - docs/intent/interactive-evals/interactive-evals-design.md:86
  - AGENTS.md#Terminology
priority: high
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Specs files mark eval-only specs inconsistently: 66 prior-art-search *(eval)* specs are `[x]` though most of their cases are 'never run' in `evals/prior-art-search/latest-results.md` (22 of 29 cases), while newer eval-only specs whose skill text exists stay `[ ]` (about 80 IDs). The interactive-evals design says markers change on how a spec is checked, not on pass/fail. Decide whether `[x]` means 'carried by the skill' or 'passed its eval', and record it in AGENTS.md or the LID workflow notes. Done when the rule is written and the specs files follow it.

**Why it matters:** Makes `[ ]` a trustworthy gap list for this tracker and for lidc coverage.

**Why the developer:** a choice between two readings of the marker convention
<!-- SECTION:DESCRIPTION:END -->
