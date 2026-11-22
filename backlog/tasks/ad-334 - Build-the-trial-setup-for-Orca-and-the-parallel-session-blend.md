---
id: AD-334
title: Build the trial setup for Orca and the parallel-session blend
status: In Progress
assignee: []
created_date: '2026-11-20T13:51:00Z'
updated_date: '2026-11-22T15:33:00Z'
labels: []
milestone: m-6
dependencies: []
references:
  - docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md
priority: medium
type: feature
ordinal: 24000
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md recommends a blend for running several Claude Code sessions in one repo: Claude Code's agent view and --worktree, Worktrunk for the worktree lifecycle, Clash as a PreToolUse hook warning about edits that overlap another worktree's changes, and two custom pieces. The developer wants to trial that blend against Orca (stablyai/orca) with adjusted settings, and both setups live in this repo as shared tooling. Walk LID's arrow for it (HLD check, LLD, EARS, tests, code). Pieces: (1) a gitignored-files guard, run as a Worktrunk pre-remove hook, that refuses removal when the worktree holds ignored files that differ from or are missing in the main checkout, skipping regenerable paths; Orca's at-risk check (src/main/git/worktrees/removal/worktree-at-risk-local-files.ts) is the design to borrow. (2) A status line that counts busy and blocked sessions from claude agents --json, with a warning threshold. Orca installs its own status line only when none exists, so the order of setup matters. (3) Clash's hook, shared by both setups. (4) A .worktreeinclude for this repo covering the APM-installed LID skills under .claude/skills/ and .config/prior-art-sources.toml. Orca's .worktreeinclude takes literal paths only, with a 256 KB cap per file, so it needs its shared-paths setting for directories. (5) An Orca post-install script that checks and sets, after every install or upgrade: agent status hooks on, the default permission mode not full-access (so Claude doesn't launch with --dangerously-skip-permissions), autoRenameBranchFromWork off, telemetry off, orchestrationCoordinatorApprovalsEnabled off, auto-update off (setting name unverified), and that its hooks in ~/.claude/settings.json are the expected ones. Settings migrations may rewrite defaults, which is why it runs after every upgrade. Done when both setups can be installed from the repo and checks pass.
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: d7b6ac42-ae0a-43d4-910b-471bd3b28ac7
created: 2026-11-22T15:28:00Z

---

2026-11-22: the design is drafted at docs/intent/parallel-sessions/parallel-sessions-design.md (HLD and design stops done). Its Build order section splits the work: this task now covers slice 1, Orca's core (launcher and menu entry, installer, settings check, Clash's hook, and setup for those). Slice 2, the blend's pieces, moved to its own task.

---

author: d7b6ac42-ae0a-43d4-910b-471bd3b28ac7
created: 2026-11-22T15:33:00Z

---

2026-11-22: the design is now pruned to Orca's option: the launcher and menu entry, the installer, the settings check, Clash's hook, and setup for those. This task builds all of it. The blend's custom pieces are cut from the design; AD-348 holds them in case Orca falls short.

---
<!-- COMMENTS:END -->
