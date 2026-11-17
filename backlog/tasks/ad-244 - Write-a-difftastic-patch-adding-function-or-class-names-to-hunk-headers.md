---
id: AD-244
title: Write a difftastic patch adding function or class names to hunk headers
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
  - upstream
milestone: m-7
dependencies:
  - AD-291
references:
  - docs/prior-art/2026-10-30-change-presentation.md#Verdict
  - docs/tool-feedback/difftastic.md
priority: medium
type: upstream
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement scope names in difftastic hunk headers (issue #304): the tree-sitter node kind is dropped at `src/parse/syntax.rs:116-131` and headers carry only path and hunk number (`src/display/style.rs:539-579` at 4618021). Small as a regex lookback, medium with tree-sitter scopes. Difftastic asks for AI disclosure and bars LLM-written comments, so a person writes the PR text. Done when a branch passes its tests and shows scope in headers.

**Why it matters:** Gives structural diffs the location context reviewers need.

**Why an agent:** Rust patch with documented extension point
<!-- SECTION:DESCRIPTION:END -->
