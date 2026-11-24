# Orca

Feedback for [Orca](https://github.com/stablyai/orca), a trial candidate in [the parallel-session note](../prior-art/2026-11-18-parallel-session-and-worktree-management.md). Read in source at 3c19574 (2026-11-19). None of these has been raised upstream.

## Deleting a worktree from the GUI forces removal

- **Where:** `src/renderer/src/components/sidebar/workspace-actions/deletion/DeleteWorktreeDialog.tsx:96,233-266`, `DeleteWorktreeChangesSummary.tsx:205-216` in the same folder.
- **What:** the sidebar's Delete passes `force` by default after its summary of changes, so a worktree with uncommitted or untracked changes is removed once confirmed, with no backup. The docs describe deletion as "with confirmation" and don't mention force.
- **Evidence:** read in source.
- **Suggested fix:** default to a non-forced removal that refuses a dirty worktree, with force as an explicit second choice; or say in the docs that confirming forces removal.

## Turning off agent status hooks leaves them installed

- **Where:** `src/shared/agent-hook-listener/configuration/agent-status-hooks-setting.ts:11-15`, `src/main/agent-hooks/installation/managed-agent-hook-controls.ts:49-56,133-199,246-255`.
- **What:** setting `agentStatusHooksEnabled` to false stops new installs, but doesn't remove the hooks already written to the user-wide `~/.claude/settings.json`.
- **Evidence:** read in source.
- **Suggested fix:** remove Orca's managed hooks when the setting is turned off, or offer a command that does.

## Docs and code disagree on the orchestration concurrency cap

- **Where:** `src/main/runtime/orchestration/coordinator/coordinator.ts:17-24,224-233`, `docs/site/content/docs/cli/orchestration.mdx:17-21`.
- **What:** `maxConcurrent` (default 4) is live in the `orchestration.run` RPC, while the docs say `orchestration run` is retired and does nothing. The current Run flow has no concurrency limit.
- **Evidence:** read in source and docs.
- **Suggested fix:** document whether a cap exists, or add one to the worker-start flow.

## The CLI crashes in Orca's own terminals where user namespaces are restricted

- **Where:** `orca-ide` run in an Orca terminal, 1.4.269 AppImage, Ubuntu with `kernel.apparmor_restrict_unprivileged_userns = 1` (so `unshare -Ur true` fails), 2026-11-23.
- **What:** `orca-ide worktree rm …` aborted at once: "The SUID sandbox helper binary was found, but is not configured correctly. Rather than run without sandboxing I'm aborting now. You need to make sure that /tmp/.mount_orca.…/chrome-sandbox is owned by root and has mode 4755", then a core dump. The same command from a regular terminal, through the registered `~/.local/bin/orca-ide` (a launcher that runs the CLI in Electron's Node mode), worked.
- **Evidence:** observed once on Linux x86_64. What `orca-ide` resolves to inside Orca's terminals wasn't checked, so whether the session's CLI path starts Chromium before handing off to the CLI is inferred, not confirmed. Orca's CLI does add `--no-sandbox` when it starts an Electron next to an AppImage's `AppRun` and the user-namespace probe fails (`src/cli/runtime/app-launch/electron-sandbox-switch.ts`), and its own CLI contract test passes `--no-sandbox` to the binary (`config/docker/cli-launch-contract/run-cli-case.sh`), so the gap seems to be in the first step.
- **Suggested fix:** have the command Orca puts on its terminals' `PATH` run the CLI in Node mode, as the registered launcher does, or apply the same user-namespace check before Chromium starts.
