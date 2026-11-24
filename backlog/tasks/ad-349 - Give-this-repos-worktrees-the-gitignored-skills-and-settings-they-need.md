---
id: AD-349
title: Give this repo's worktrees the gitignored skills and settings they need
status: To Do
assignee: []
created_date: '2026-11-22T22:03:00Z'
updated_date: '2026-11-24T00:17:00Z'
labels: []
milestone: m-2
dependencies: []
references:
  - docs/intent/parallel-sessions/parallel-sessions-design.md
priority: medium
type: feature
ordinal: 40000
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A new worktree of this repo, made by Orca, Claude Code's --worktree or git, has none of the main checkout's gitignored files. It therefore loads none of the APM-installed skills under .claude/skills/ (the LID skills), and the prior-art search finds no .config/prior-art-sources.toml. The parallel-sessions design (docs/intent/parallel-sessions/parallel-sessions-design.md, Related segments) says repo setup owns this. Walk it through LID as a change to the repo-setup segment (docs/intent/repo-setup/repo-setup-design.md): a committed .worktreeinclude listing gitignored files to copy (.config/prior-art-sources.toml; Orca and Claude Code both read it, Orca taking literal paths only), and a committed orca.yaml whose worktree.sharedDirectories lists the gitignored skill directories to link. Check what Claude Code's --worktree does with directories (its .worktreeinclude accepts gitignore patterns) so both tools work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A new Orca worktree and a new claude --worktree worktree of this repo both load the APM-installed skills and see .config/prior-art-sources.toml
- [ ] #2 The repo-setup design and specs cover the files, and mise run check passes
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: 27e13044-1d02-40c4-90d7-0134d1214b1d
created: 2026-11-24T00:17:00Z

---

On the developer's machine Orca's worktree setup command is set locally (mise trust, then mise run skills) with Command source "Local only", so Orca ignores orca.yaml. When this task commits a shared orca.yaml, tell the developer to switch Command source to "orca.yaml only" (deleting the local script) or "Run both", or the shared setup won't run there.

---
<!-- COMMENTS:END -->
