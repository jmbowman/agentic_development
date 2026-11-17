---
id: AD-192
title: Build sealed commit messages recorded from the developer's own prompt
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-160
  - AD-181
  - AD-191
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#12.
    Commit, pull request and merge autonomy
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rung 1 mechanism: an agent may commit only after the developer has seen that exact message; a UserPromptSubmit hook writes the approval (digest of the message) to a protected path, and a pre-commit check compares digests and spends the approval on use (DAW's design, with foreman's fuller guard over command spellings). Applies only once the rung is raised.

**Why it matters:** Lets agents commit without losing the developer's review record.

**Why an agent:** hook and check code
<!-- SECTION:DESCRIPTION:END -->
