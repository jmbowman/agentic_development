---
id: AD-348
title: Design and build the parallel-session blend's custom pieces if Orca falls short
status: To Do
assignee: []
created_date: '2026-11-22T15:28:00Z'
labels: []
milestone: m-6
dependencies:
  - AD-335
references:
  - docs/intent/parallel-sessions/parallel-sessions-design.md
  - docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md
priority: low
type: feature
ordinal: 39000
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The parallel-sessions design (docs/intent/parallel-sessions/parallel-sessions-design.md) covers Orca's setup only. Orca is tried first (AD-335). If it falls short, design and build the blend from the prior-art note: Claude Code's agent view and --worktree, Worktrunk for the worktree lifecycle, Clash (already in the design), and two custom pieces, added to the same design through LID. Don't start unless AD-335 decides the blend is needed; otherwise close this task.

A draft design for the custom pieces was written and reviewed on 2026-11-22, then cut from the design doc to keep it to what's being built. Its settled points, to start from:
- Gitignored-files guard, modelled on Orca's at-risk check (src/main/git/worktrees/removal/worktree-at-risk-local-files.ts at Orca v1.4.269). It runs as Worktrunk's pre-remove hook, which runs inside the worktree being removed; its non-zero exit aborts wt remove. It's also run by hand before other removals.
  - It lists the worktree's gitignored files with git's own matcher, expanding ignored directories into files. A nested repository or submodule inside an ignored path is at risk as a whole.
  - It drops files matching regenerable patterns. These use .gitignore syntax, so they match at any depth. They come from a built-in list (node_modules/, .venv/, __pycache__/, *.pyc, .pytest_cache/, .ruff_cache/, .mypy_cache/, target/, dist/, build/) plus the repo's .worktree-regenerable or .config/worktree-regenerable, used together. Both repo files are read from the main checkout, so a change inside the worktree can't widen what's skipped, and a differing worktree copy is reported.
  - It compares each remaining file with the main checkout by type first. Sockets, FIFOs and devices are skipped and counted. A type mismatch or an unreadable file is at risk. Symlinks are compared by link text. Regular files are compared byte for byte, streaming. Identical means safe; different or missing means at risk. With no main checkout (a bare repository, or a moved main), every remaining file is at risk.
  - Exit 1 if anything is at risk, 0 only after a completed check, 2 on any other failure including a crash. It never moves or deletes a file.
- Session-count status line: reads Claude Code's input once, runs claude agents --json with a 1-second timeout, and counts waiting (status waiting or state blocked), then working (busy or working), then idle (idle, done, failed, stopped), then other. A text marker shows when working plus waiting exceed a configurable threshold (default 4). It says when the count is unavailable.
- Sharing the statusLine slot with Orca: Orca's status line only forwards rate-limit data to its usage meter and prints nothing. Orca installs it only into an empty slot, and treats any other command as the user's. Setup would take the slot only when empty or holding Orca's command (recognized by Orca's script file name), record Orca's command, and chain it with its own 1-second timeout. Any other command is reported and left alone. Open: Orca doesn't refresh its script once it no longer holds the slot.
- Worktrunk's user config: setup appends the pre-remove hook as text and checks it by re-reading, because Python's standard library can't write TOML. When a pre-remove hook already exists, it changes nothing and prints the lines to add by hand.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AD-335 decided whether the blend is needed, and this task was closed or its pieces were designed, specified, tested and built through LID with mise run check passing
<!-- AC:END -->
