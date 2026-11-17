---
id: AD-256
title: Decide what to do with the docs-site worktree
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
  - stale
milestone: m-8
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/54
  - git worktree list
priority: medium
type: chore
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A local worktree of agentic_development sits beside the main checkout, on branch `docs-site` at d931ec3, with no commits ahead of main, 9 behind, and a clean tree. Its only content beyond main is gitignored `tmp/`: three reference clones (fm-strip, mdbook-lint, mdbook-llms) and an empty `spike-docs-site/`. So it holds no unmerged work for issue #54, whose task list is all unchecked. Decide whether to restart the #54 spike there or remove the worktree. Done when it is in use or removed.

**Why it matters:** Clears a misleading checkout, or restarts the docs-site effort.

**Why the developer:** removing a worktree or branch changes git state

**Status when filed (stale):** branch tip is an ancestor of main; spike directory empty
<!-- SECTION:DESCRIPTION:END -->
