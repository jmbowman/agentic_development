# Clash

Feedback for [Clash](https://github.com/clash-sh/clash), part of the recommended blend in [the parallel-session note](../prior-art/2026-11-18-parallel-session-and-worktree-management.md). Read in source at 2ac931c (2026-11-18). None of these has been raised upstream.

## Conflict checks write loose objects

- **Where:** `src/worktree/conflict.rs:61-66`, calling gix `merge_trees` (gitoxide a5225a7, `gix/src/repository/merge.rs:119-160`).
- **What:** the merge simulation writes merged blobs into `.git/objects` as unreferenced loose objects, because gix's object memory isn't enabled. A tool that otherwise writes no refs, index or config adds objects on every check.
- **Evidence:** read in source; Clash's own `src/` has no write calls (listing), so the writes come from the dependency.
- **Suggested fix:** enable gix's `with_object_memory` for simulated merges.

## Watch mode misses changes in linked worktrees

- **Where:** `src/watch/watcher.rs:22-38,90-116`.
- **What:** watch mode reacts only to paths containing `/.git/index`, `/.git/HEAD` and `/.git/refs/`, so a linked worktree's own index and HEAD under `.git/worktrees/<id>/` don't trigger it. It also filters events through the main worktree's root `.gitignore`, which drops events from worktrees under an ignored directory such as `.claude/worktrees/`.
- **Evidence:** read in source.
- **Suggested fix:** watch each worktree's git directory, and filter each event against the ignore rules of the worktree that contains it.
