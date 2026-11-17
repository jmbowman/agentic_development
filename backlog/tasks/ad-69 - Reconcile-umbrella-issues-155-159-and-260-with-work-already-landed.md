---
id: AD-69
title: 'Reconcile umbrella issues #155-#159 and #260 with work already landed'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-3
dependencies:
  - AD-14
references:
  - https://github.com/jmbowman/agentic_development/issues/155
  - https://github.com/jmbowman/agentic_development/issues/156
  - https://github.com/jmbowman/agentic_development/issues/157
  - https://github.com/jmbowman/agentic_development/issues/158
  - https://github.com/jmbowman/agentic_development/issues/159
  - https://github.com/jmbowman/agentic_development/issues/260
priority: medium
type: chore
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issues #155-#159 and #260 overlap (stop rule appears in #159 and #260; verification hardening in #156 and #260; scripts in #157; sources in #158 and #260) and parts have landed: the literature harvester (49b1ff9), OpenAlex default (aec8b25), search tactics (2d835c7). Walk each issue's checklist against skills/prior-art-search at HEAD, tick or comment what is done, and close or retitle issues that are fully done, so the backlog shows only remaining items. Also check docs/intent/prior-art-search specs match.

**Why it matters:** One source of truth for remaining prior-art-search work.

**Why the developer:** editing and closing issues in the developer's name
<!-- SECTION:DESCRIPTION:END -->
