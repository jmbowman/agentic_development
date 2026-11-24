---
id: AD-335
title: Trial Orca and the parallel-session blend, then choose one
status: To Do
assignee: []
created_date: '2026-11-20T13:51:00Z'
updated_date: '2026-11-24T00:17:00Z'
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

author: 27e13044-1d02-40c4-90d7-0134d1214b1d
created: 2026-11-23T12:08:00Z

---

2026-11-23: Orca's side of the trial can start. Orca 1.4.269 is installed through tools/parallel-sessions/ and starts from its menu entry with usage reporting off; Clash 0.2.0 is installed and its PreToolUse entry is in ~/.claude/settings.json. Still to do first: a smoke test (edit a file in one worktree, then have an agent edit it in another, and expect a prompt naming the first), and run `mise run skills` in each new worktree until AD-349. The blend's custom pieces are now AD-348.

---

author: 27e13044-1d02-40c4-90d7-0134d1214b1d
created: 2026-11-24T00:17:00Z

---

The Clash prompts rule (tell the developer about a flagged edit; run clash check after a rejected one) is in this repo's AGENTS.md for the trial. Clash runs in every repo on the machine, so if the trial keeps Clash, move the rule to the developer's user-level instructions, which are edited from a session in the repo that holds them.

---
<!-- COMMENTS:END -->
