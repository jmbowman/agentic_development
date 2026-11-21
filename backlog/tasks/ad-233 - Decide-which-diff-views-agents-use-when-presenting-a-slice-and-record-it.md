---
id: AD-233
title: Decide which diff views agents use when presenting a slice and record it
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-7
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/91
  - docs/prior-art/2026-10-30-change-presentation.md
  - docs/tool-feedback/difftastic.md
  - '#91'
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: a94b37f9-a8eb-4e27-abc2-8eb9da8159f2
    role: created
    date: '2026-11-12'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #91: decide which of delta, difftastic and git word diff agents should use when presenting a slice for review, then write it into agent rules (CLAUDE.md or the review-wave guidance). Note the issue comment's warning: keep difftastic as an alias, not a global git setting, because agents run plain git diff. Done means a rule in the repo docs.

**Why it matters:** Agents present slices in the form the developer reads best.

**Why the developer:** developer chooses what presentation they want
<!-- SECTION:DESCRIPTION:END -->
