---
id: AD-91
title: Decide whether to promote the prior-art-search LLD to a sub-HLD
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:523
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The prior-art-search LLD is about 115 KB, and the design says promoting it to a sub-HLD over child leaves (which renames every `PRIOR-` spec ID) is weighed when the next #157 script is designed. Decide before that design starts, since it changes where the new `PRIOR-SCR-` specs go. Done when the decision is recorded in the LLD's Decisions table.

**Why it matters:** Settles the doc structure before more harvester specs are added.

**Why the developer:** a structural choice about the design tree that renames every spec ID
<!-- SECTION:DESCRIPTION:END -->
