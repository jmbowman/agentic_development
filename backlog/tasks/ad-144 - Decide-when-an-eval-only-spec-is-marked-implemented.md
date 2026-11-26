---
id: AD-144
title: Decide when an eval-only spec is marked implemented
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-26T13:02:35Z'
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

## Comments

<!-- COMMENTS:BEGIN -->
author: a20b213e-9cc5-4bd1-8407-62658bae5e42
created: 2026-11-26T13:02:35Z

---

A fact for this decision, from AD-336 (2026-11-25): `tests/test_task_tracker_skill.py` requires an eval case for every spec marked *(eval)*, whatever its `[ ]` or `[x]` marker, and checks the list of eval specs against a fixed four. So a design-only slice can't add an *(eval)* spec without also adding its case. AD-336 worded two agent-behaviour specs (TASK-SKILL-035 and TASK-SKILL-044) as skill-text rules until AD-364 adds the case.

---
<!-- COMMENTS:END -->
