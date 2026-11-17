---
id: AD-53
title: Require an end-to-end lens in every review wave on a prior-art note
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/159
  - docs/prior-art/2026-11-06-agent-reference-clones.md
priority: medium
type: docs
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #159: in the reference-clones refresh the cold-read reviewer caught design errors the search could not (a sandbox rule that would block the agent's refresh task, a safety claim resting on wording where the paper needed a parser, uneven custom-piece counts between options). Add a does-the-verdict's-design-work-end-to-end lens to the review-wave guidance for prior-art notes in skills/prior-art-search (and the design under docs/intent/prior-art-search). Done means the guidance names the lens with those examples.

**Why it matters:** Catches design errors that searches cannot.

**Why an agent:** skill text edit
<!-- SECTION:DESCRIPTION:END -->
