# Worktrunk

Feedback for [Worktrunk](https://github.com/max-sixty/worktrunk), part of the recommended blend in [the parallel-session note](../prior-art/2026-11-18-parallel-session-and-worktree-management.md). Read in source at 91d9625 (2026-11-18). None of these has been raised upstream.

## Removal doesn't check gitignored files

- **Where:** `src/git/repository/working_tree.rs:695-719,1312-1378`, `src/git/remove.rs:481-548`.
- **What:** `wt remove` decides a worktree is clean with `git status --porcelain --untracked-files=normal`, so ignored files (local config, scratch files, keys) are neither checked nor included in the `--force` backup, and are deleted with the worktree. The Claude Code plugin's `WorktreeRemove` hook goes through the same path.
- **Evidence:** read in source.
- **Suggested fix:** an optional check, or an example `pre-remove` hook, that lists ignored files that differ from or are missing in the primary worktree, skipping regenerable paths, as Orca's removal does.
