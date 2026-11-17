---
id: AD-45
title: Implement the new stop rule and developer-stop verdict in prior-art-search
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies:
  - AD-42
references:
  - https://github.com/jmbowman/agentic_development/issues/260
  - https://github.com/jmbowman/agentic_development/issues/159
  - skills/prior-art-search/SKILL.md
  - docs/intent/prior-art-search/
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Apply the stop rule and verdict wording the developer chose (issues #260 items 1-2 and #159 first bullet) to skills/prior-art-search/SKILL.md (step 6 Snowball, the Report section's inconclusive verdict at line 172, the approach-only paragraph at line 118), references/note-template.md and the design at docs/intent/prior-art-search/. This needs a LID pass: design doc, EARS specs, tests and an eval case. A convergence stop must be reported separately from the round cap and list the remaining open leads. Done means the skill text, specs, tests and eval agree and `mise run check` passes.

**Why it matters:** Every future search stops at the point it converges instead of at the cap.

**Why an agent:** skill text and spec edits once the reading is chosen
<!-- SECTION:DESCRIPTION:END -->
