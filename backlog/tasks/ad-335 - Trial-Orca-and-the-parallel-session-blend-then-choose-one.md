---
id: AD-335
title: Trial Orca and the parallel-session blend, then choose one
status: To Do
assignee: []
created_date: '2026-11-20T13:51:00Z'
updated_date: '2026-11-22T15:33:00Z'
labels: []
milestone: m-6
dependencies:
  - AD-334
references:
  - docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md
priority: medium
type: decision
ordinal: 25000
performer: human
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once AD-334's setups are installable, use each for about a week of parallel sessions in this repo: Orca pinned to a vetted release with worktrees deleted through its CLI (orca worktree rm, not the GUI's Delete, which forces removal), and the blend (claude agents, --worktree or Worktrunk, Clash, the gitignored-files guard and the session-count status line). Compare how well each keeps sessions unblocked, how setup, cleanup and conflicts felt, and anything either lost. Then choose one, or a mix, and update the verdict in docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md if it changes.
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: d7b6ac42-ae0a-43d4-910b-471bd3b28ac7
created: 2026-11-22T15:33:00Z

---

2026-11-22: the developer chose to try Orca first, since it also serves as a session and terminal manager. The blend is built (AD-348) only if Orca falls short, so this trial is now: use Orca with Clash, then decide whether it's good enough or the blend is needed.

---
<!-- COMMENTS:END -->
