---
id: AD-50
title: Add the run-test step and sandbox recipe to prior-art-search
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies:
  - AD-49
references:
  - https://github.com/jmbowman/agentic_development/issues/196
  - docs/prior-art/2026-11-06-agent-reference-clones.md
  - docs/tool-feedback/vendir.md
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
If the developer allows the carve-out, add to skills/prior-art-search the run test after step 9 (full-method verdicts that adopt or build on a tool): run the pinned finalist against key scenarios and stated costs in throwaway directories, record results under verified by running separately from verified in source, and keep the ban on running during the search itself. Include the bwrap sandbox recipe from the #196 comment (npm pack with sha256, read-only root, tmpfs HOME, no network, snapshot and diff). Needs LID pass: design, EARS specs, tests, eval case, and a note-template section.

**Why it matters:** Catches wrong verdicts before review instead of after.

**Why an agent:** skill and spec edits once the carve-out is decided
<!-- SECTION:DESCRIPTION:END -->
