---
id: AD-258
title: Write the authoring rules file for knowledge pages
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies: []
references:
  - docs/prior-art/2026-10-23-progressive-disclosure-knowledge-base.md#Verdict
  - >-
    docs/prior-art/2026-10-23-progressive-disclosure-knowledge-base.md#Limitations
    checked in source
  - https://github.com/jmbowman/agentic_development/issues/166
priority: medium
type: docs
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Write one rules file that each repo's agent instructions point to, covering the knowledge-base page conventions: Diataxis-style content types and one purpose per page (adapted from developer-docs-framework), seiso's one-home-per-fact and no-narration rules, LID's current-intent rule, a page-size budget, a one-line description and an overview page per area. Each rule should map to a lint check where one exists, so a lint failure points at a rule. Done when the file exists and is referenced from AGENTS.md. This maps how many of the framework's 27 rules map to seiso or Vale, which the note lists as design work.

**Why it matters:** Gives agents one checkable contract for writing knowledge pages.

**Why an agent:** Drafting a rules doc from named sources; developer reviews
<!-- SECTION:DESCRIPTION:END -->
