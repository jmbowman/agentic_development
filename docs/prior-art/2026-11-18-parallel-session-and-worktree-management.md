# Prior art: managing parallel Claude Code sessions and their worktrees (2026-11-18)

- **Effort:** full method. The result shapes how every repo gets worked once several sessions run at once, and the developer chose it.
- **Already known:** the developer knew of [Orca](https://www.onorca.dev), [Herdr](https://github.com/herdrdev/herdr) and iTerm2's Claude Code support (no link found), but hadn't used any of them. iTerm2 is macOS-only, so it fails the Linux criterion; the other two are candidates below. No earlier note covers this topic. Related notes: [task management](2026-11-12-task-management-for-humans-and-agents.md), on claiming tasks across parallel worktrees, and [doctrine](2026-11-13-doctrine.md), on how `isolation: worktree` behaves.
- **Credit:** this note used data from Semantic Scholar.

## Need and criteria

| Requirement | Underlying need |
|---|---|
| N1. See every open session and its state: working, waiting on the developer, done, and how long it has been idle | Keep sessions unblocked without visiting each terminal |
| N2. See when one session is waiting for another to finish | Know why a session is stalled, and when to start the dependent work |
| N3. Limit how many sessions run at once | Keep review load and usage within what one person can supervise |
| N4. Create an isolated workspace and start a session in it in one step | Start parallel work cheaply, including while the main checkout holds uncommitted work under review |
| N5. Remove a workspace safely | Lose no uncommitted work, unpushed commits or important gitignored files (scratch scripts, local config, keys) |
| N6. Avoid conflicting concurrent changes | Find out early when two sessions are changing the same files |
| N7. Alternatives to git worktrees | Any isolation approach that serves N4 to N6 better |

**Common uses** (from the request):

1. Glance at all sessions to see which need the developer, which are done and which are stuck.
2. Start an agent on a new problem in its own workspace while the main checkout holds uncommitted work under review.
3. Clean up a finished workspace without losing anything.
4. Run several sessions in one repo without them making conflicting changes.

**Hard criteria:** runs on Linux (the developer's machine); works with the Claude Code CLI; a license that permits personal use, read from the license file.

**Preferences:**

- open source;
- maintained;
- commits, merges and pushes only when the developer acts, since the developer commits and controls branch state;
- low setup;
- any interface (TUI, desktop GUI or local web).

## Verdict

**Blend:**

- **Base: Claude Code's own [agent view](https://code.claude.com/docs/en/agent-view.md) and [worktree support](https://code.claude.com/docs/en/worktrees.md).** It is already installed and covers N1 and N4 natively: `claude agents`, `claude --worktree`, `claude --bg` and `.worktreeinclude`.
- **[Worktrunk](https://github.com/max-sixty/worktrunk), built on,** for the worktree lifecycle. Use it either as Claude Code's `WorktreeCreate`/`WorktreeRemove` hook backend or directly with `wt switch -c -x claude`. Its blocking `pre-remove` hooks are the place for the N5 guard.
- **[Clash](https://github.com/clash-sh/clash), adopted,** as a `PreToolUse` hook for N6.
- **Two small custom pieces:**
  - a pre-remove guard that refuses to delete a worktree holding gitignored files, unless they are on a reproducible-content allowlist;
  - a status-line count of busy and blocked sessions from `claude agents --json`, with a warning threshold for N3.

N2 stays partly met. Claude Code's cross-session "notify when idle" lets one session wait on another, but no surveyed tool shows a dependency view of interactive sessions.

Only Orca checks gitignored files before removing a worktree, and only inside its GUI. Claude Code's documented checks don't, and neither do Worktrunk, workmux or Herdr (verified in source). That gap is the main reason for the custom guard, which should borrow Orca's design: list the ignored files, skip regenerable ones, and compare the rest with the main checkout.

## Candidates and matrix

### Ranked shortlist

1. **[Claude Code agent view and `--worktree`](https://code.claude.com/docs/en/agent-view.md)** (native, v2.1.328).
   - **Why it ranks first:**
     - groups sessions under Needs input, Working, Ready for review and Completed;
     - shows the wait time in the peek panel;
     - sends notifications when a session needs input or finishes;
     - `claude agents --json` reports interactive sessions too;
     - one-step worktree creation, with removal checks for uncommitted and unpushed work;
     - zero setup.
   - **Limits:** a research preview; no concurrency cap; no check of gitignored files on removal; closed source, so every limitation is docs only.
   - **What would change it:** losing the research preview, or a need for time-in-state on every row (workmux has that).
2. **[Worktrunk](https://github.com/max-sixty/worktrunk).**
   - **Why it ranks here:** the best worktree lifecycle, all verified in source:
     - a clean gate before removal, run twice;
     - `--force` backups to `refs/wt-backup/`;
     - branch deletion only when the branch is integrated;
     - reflink `copy-ignored`;
     - blocking `pre-remove` hooks;
     - no push anywhere.
   - **What would change it:** its Claude Code plugin writing agent markers into the repo's git config, if the developer objects. The worktree hooks can be configured without the marker hooks.
3. **[Clash](https://github.com/clash-sh/clash).**
   - **Why it ranks here:**
     - the only verified N6 tool with a Claude Code hook;
     - it asks before an edit to a file that another worktree has changed but not committed;
     - it simulates merges of every worktree pair's committed HEADs.
   - **What would change it:** it would rank lower if the loose objects its gix merges leave in `.git/objects` turn out to matter.
4. **[workmux](https://github.com/raine/workmux).**
   - **Why it ranks here:** the strongest third-party all-in-one, verified in source:
     - hook-fed status with time in state;
     - `workmux wait` for one agent to reach a state;
     - tmux, Zellij, Kitty or WezTerm backends;
     - it adopts worktrees made by other tools.
   - **Why it isn't the base:**
     - it duplicates agent view;
     - it needs a multiplexer;
     - `--max-concurrent` counts only the windows of one batch `add`;
     - removal has the same gitignored-files gap and force-deletes the branch after its checks;
     - its bundled coordinator skill can have agents run `/merge`.
   - **What would change it:** agent view being withdrawn, or N1's time in state becoming essential.
5. **[Orca](https://github.com/stablyai/orca)** (verified in source at 3c19574). An Electron app; Linux builds are AppImage, deb and rpm.
   - **What it does best:** removal safety. It is the only surveyed tool that checks gitignored files before removing a worktree:
     - it lists ignored files and skips regenerable ones;
     - it compares each remaining file with the main checkout and shows the ones that would be lost;
     - it keeps an unmerged branch.
   - **N1:** hook-fed status. N4: one-step `orca worktree create --agent claude`.
   - **Why it isn't the base:** it duplicates agent view, can't see sessions started outside Orca, and offers N2 and N3 only through an experimental orchestration feature. Its defaults conflict with this developer's rules:
     - it installs hooks and a `statusLine` into the user-global `~/.claude/settings.json` at startup;
     - it launches Claude with `--dangerously-skip-permissions` (default permission "full-access");
     - it renames auto-named branches with `git branch -m` after the first prompt;
     - the GUI delete forces removal after its warning dialog;
     - official builds opt new profiles into PostHog telemetry.
   - **What would change it:** a decision to work in a GUI, with those defaults changed.
   - Its at-risk-files check is the design to borrow for this blend's custom guard.
6. **[Herdr](https://github.com/herdrdev/herdr).** Detects state by pattern-matching the screen, shows no time in state, and can't see sessions started outside its own panes (all verified in source). It is ranked for completeness. **What would change it:** none of this changes while the developer also runs sessions outside herdr.

The other candidates went unverified because they rank below these on the evidence read: either they duplicate the base's N1 and N4, or they fail a preference.

### Classification

| Candidate | Class | License (file:line at commit) | Reason |
|---|---|---|---|
| [Claude Code agent view / `--worktree`](https://code.claude.com/docs/en/agent-view.md) | adopt (base) | proprietary (Anthropic terms) | Native; covers N1 and N4; N2 and N5 partly |
| [Worktrunk](https://github.com/max-sixty/worktrunk) | build on | MIT OR Apache-2.0: LICENSE-MIT:1-21 and LICENSE-APACHE:1-190 at 91d9625; Cargo.toml:66 | Worktree lifecycle; `pre-remove` hook carries the N5 guard |
| [Clash](https://github.com/clash-sh/clash) | adopt (building block) | MIT, LICENSE:1-21 at 2ac931c | N6 hook |
| [workmux](https://github.com/raine/workmux) | borrow ideas | MIT, LICENSE:1-21 at e9b16d5 | Time in state, `wait`; duplicates the base |
| [Herdr](https://github.com/herdrdev/herdr) | reject | Apache-2.0, LICENSE:1-201 at ee5bfb5 | Sees only its own panes; heuristic state; no time in state |
| [ccmanager](https://github.com/kbwo/ccmanager) | borrow ideas | MIT, LICENSE:1-21 at b0948dd | busy/waiting/idle, `.worktreeinclude`; overlaps the base (docs only) |
| [Agent Deck](https://github.com/asheshgoplani/agent-deck) | borrow ideas | MIT, LICENSE:1-21 at 80494e5 | tmux TUI, worktrees, Docker sandbox; overlaps the base |
| [Agent of Empires](https://github.com/agent-of-empires/agent-of-empires) | borrow ideas | MIT, LICENSE:1-21 at dd7827c | Container isolation option (N7) |
| [claude-squad](https://github.com/smtg-ai/claude-squad) | reject | AGPL-3.0, LICENSE.md:1-660 at 070eb93 | No session states in its README; `-y` auto-accept |
| [ccdeck](https://github.com/BarganConstantin/ccdeck) | borrow ideas | AGPL-3.0, LICENSE:1-661 at 4.0.1 | "Blocked on you" queue ordered by wait time |
| [cctop](https://github.com/stefanprodan/cctop) | borrow ideas | Apache-2.0, LICENSE:1-201 at 5f54e27 | Shows time since last activity for every session |
| [tmux-agent-plane](https://github.com/zazencodes/tmux-agent-plane) | borrow ideas | GPL-3.0, LICENSE:1-674 at 0.8.0 | State and how long it has held |
| [Gas Town](https://github.com/gastownhall/gastown) | reject | MIT, LICENSE:1-21 at 94cc822 | Covers N2, N3 and N6, but its merge queue merges to main automatically |
| [ntm](https://github.com/Dicklesworthstone/ntm) | reject | MIT plus a rider, LICENSE:1-73 at d137b1c | The rider grants no rights to OpenAI, Anthropic or anyone acting for them, and its "use" includes running it in an automated pipeline |
| [amux (mixpeek)](https://github.com/mixpeek/amux) | reject | MIT plus Commons Clause, LICENSE:1-46 at a809f2b | Source-available; tmux-bound; overlaps |
| [Multica](https://github.com/multica-ai/multica) | reject | Apache-2.0 plus additional conditions, LICENSE:1-75 at e67937b | Team issue workspace, beyond the need |
| [cezar](https://github.com/open-mercato/cezar) | borrow ideas | MIT, LICENSE:1-21 at 430ad1b | Task queue with "nothing auto-merges" (N3 idea) |
| [dagq](https://github.com/hisamekms/dagq) | borrow ideas | MIT, LICENSE:1-21 at 0.2.0 | Dependency DAG plus `--parallel N` (N2/N3 idea); needs cmux |
| [orc](https://github.com/leighmcculloch/orc) | borrow ideas | Apache-2.0 at 2cebbdc | `max_concurrent` queue, for headless `claude -p` only |
| [hcom](https://github.com/aannoo/hcom) | borrow ideas | MIT, LICENSE:1-21 at de33e31 | Agents watch and message each other (N2) |
| [Grove](https://github.com/NathanDrake2406/grove) | borrow ideas | Apache-2.0, LICENSE-APACHE:1-190 at 0fce00c (other license files unchecked) | Hunk and symbol overlap between worktrees (N6) |
| [git-parsec](https://github.com/erishforG/git-parsec), [agent-ws](https://github.com/mendoanjoe/agent-ws) | borrow ideas | MIT, LICENSE:1-21 at 1.0.0 / 0.4.0 | Overlap and conflict status per workspace pair |
| [claude-code-merge-queue](https://github.com/funador/claude-code-merge-queue) | reject | MIT, LICENSE:1-21 at f777574 | Its agents land work by design |
| [treehouse](https://github.com/kunchenguid/treehouse) | borrow ideas | MIT, LICENSE:1-21 at 3.1.8 | Prunes only clean, landed worktrees (N5) |
| [simgit](https://github.com/abendrothj/simgit) | borrow ideas | MIT, LICENSE:1-21 at cf63fa8 | Copy-on-write worktrees with a Claude Code hook; removal gated by `--discard-dirty` (N5/N7) |
| [git-twig](https://github.com/leostera/git-twig) | borrow ideas | MIT, LICENSE:1-21 at b5d7692 | CoW worktrees; moves keep ignored files; 3 days old |
| [Jujutsu](https://github.com/jj-vcs/jj) | borrow ideas | Apache-2.0, LICENSE:1-202 at 52518a6 | `jj workspace` as an N7 alternative; [jjfx](https://github.com/Jarvvski/jjfx) adds a status TUI |
| [container-use](https://github.com/dagger/container-use) | borrow ideas | Apache-2.0, LICENSE:1-191 at 2e43e62 | Container plus branch per agent (N7); last release 2025-08 |
| [Claude Desktop, Linux beta](https://code.claude.com/docs/en/desktop-linux.md) | borrow ideas | proprietary | A GUI over the same sessions and worktrees; Debian-based distros only |
| [Orca](https://github.com/stablyai/orca) | borrow ideas | MIT, LICENSE:1-21 at 3c19574 (Lovecast Inc.) | Only tool that checks gitignored files before removing a worktree. Its defaults conflict with this developer's rules (see the shortlist) |
| Desktop worktree apps: [Parallel Code](https://github.com/johannesjo/parallel-code), [Emdash](https://github.com/generalaction/emdash), [Nimbalyst](https://github.com/nimbalyst/nimbalyst), [Paradev](https://github.com/ParadevAI/Paradev), [Agent Orchestrator](https://github.com/OrchestratorInc/agent-orchestrator), [Paseo](https://github.com/getpaseo/paseo) | borrow ideas | MIT or Apache-2.0 (each file read at the commits in the subagent records) | Session boards sorted by "needs you"; each replaces the CLI workflow and duplicates the base |
| [GitButler](https://github.com/gitbutlerapp/gitbutler) | reject | FSL-1.0-MIT, LICENSE.md:1-114 at 0.10.0 | Virtual branches share one working tree, which isolates no concurrent processes; source-available |

**Licenses with added terms:**

- amux (mixpeek): Commons Clause.
- ntm: a rider aimed at OpenAI and Anthropic.
- Multica: additional conditions on Apache-2.0.
- cmux: BUSL-1.1 for its server directories (macOS-only, not shortlisted).
- GitButler: FSL.

**Lookalike copies:**

- workmux, Worktrunk, Grove, Herdr and Orca each had copies. Orca's upstream returned 404 on 2026-11-18 and loaded again on 2026-11-19; its copies' LICENSE files are byte-identical to upstream's. The originals were found, so the copies were rejected.

### Matrix

Values: native, partial, extensible, unsupported, unverified. **S** = verified in source (see below); **D** = docs only. All five candidates run on Linux and support Claude Code.

| Need | Agent view + `--worktree` | Worktrunk | Clash | workmux | Herdr |
|---|---|---|---|---|---|
| N1 status | native (D: agent-view.md "Read session state") | partial, markers in `wt list` (S) | unsupported | native (S) | native, heuristic (S) |
| N1 idle time | partial: "waiting 3m" in peek, row age (D) | unsupported | unsupported | native, time in state (S) | unsupported (S) |
| N2 | partial: notify when idle (D: cross-session-messaging.md) | unsupported | unsupported | partial, `wait` (S) | partial, single-target `agent wait` (S) |
| N3 | unsupported (D) | unsupported (S, listing) | unsupported | partial, batch only (S) | unsupported (S, listing) |
| N4 | native (D) | native, `switch -c -x claude` (S) | unsupported | native (S) | native, worktree API (S) |
| N5 | partial: uncommitted and unpushed checks; ignored files not checked (D) | extensible: clean gate plus `pre-remove` hook; ignored files not checked (S) | unsupported | partial: dirty and unmerged checks; ignored deleted (S) | partial: relies on git's refusal (S) |
| N6 | unsupported (D) | unsupported | native: overlap on hook, committed conflicts (S) | unsupported | unsupported |
| N7 | `WorktreeCreate` hooks allow other VCS or CoW (D) | unsupported | unsupported | partial, sandboxes (D) | unsupported |
| Developer-only git actions | partial: background sessions commit and push unless instructions say the developer commits (D) | native: no push; commit only on `wt step commit`/`merge` (S) | native: no refs or index writes; loose objects only (S) | partial: bundled skills can trigger agent merges (S) | native (S, listing) |
| License | proprietary | MIT OR Apache-2.0 | MIT | MIT | Apache-2.0 |

### Blends considered

- **Agent view alone.** Fails N3, N6 and the gitignored half of N5.
- **workmux alone.** Gives time in state, but needs a multiplexer, duplicates agent view, and has the same N5 gap.
- **Chosen blend: agent view, Worktrunk, Clash and the two custom pieces.**
  - Each part does one job.
  - All of them sit on Claude Code's own hook points (`WorktreeCreate`/`WorktreeRemove`, `PreToolUse`) or on `claude agents --json`.
  - Any part can be dropped without disturbing the rest.
  - A caveat: once a `WorktreeCreate` hook is configured, Claude Code no longer processes `.worktreeinclude`, so Worktrunk's `copy-ignored` (which honors the same file) takes over.

### Scenario walk (chosen blend)

1. **Glance at all sessions.**
   - `claude agents` lists background sessions by state.
   - Interactive sessions open in other terminals appear only in `claude agents --json` until backgrounded with `←` or `/bg`.
   - The developer either backgrounds them or relies on the status-line count.
2. **Start work while main holds uncommitted work under review.**
   - `claude --worktree <name>`, or `wt switch -c -x claude <branch>`, branches from the default branch.
   - The uncommitted work in the main checkout is untouched.
3. **Clean up a finished workspace.**
   - `wt remove` checks for a clean tree, runs the custom guard as a `pre-remove` hook, then removes the worktree.
   - The branch is kept unless it is integrated.
   - Agent view's `Ctrl+X` twice deletes a Claude-created worktree, uncommitted changes included. With the Worktrunk hook backend, removal goes through `wt remove` instead.
4. **Avoid conflicts.** Clash asks before an agent edits a file that another worktree has changed. Committed divergence shows in `clash status`.
5. **New requirement: a cap on concurrent sessions.** The status-line script gives a warning, not a hard cap. A hard cap would need a dispatch wrapper, which nothing found provides for interactive sessions.
6. **Automated upgrade.**
   - Claude Code updates itself, and agent view is a research preview, so its shortcuts and JSON fields may change.
   - Worktrunk moves fast: the clone's HEAD was committed on the day it was read.
   - Pin both with mise where the repo pins tools.
7. **Fresh machine.** Install Worktrunk and Clash, add the hooks to user settings and copy the guard. Nothing is repo-specific except `.worktreeinclude`.

## Limitations checked in source

Verified:

- **Worktrunk** (91d9625):
  - removal's clean gate is `git status --porcelain --untracked-files=normal`, so ignored files are neither checked nor backed up (`src/git/repository/working_tree.rs:695-719,1312-1378`), and the directory, ignored files included, goes to trash for deletion (`src/git/remove.rs:481-548`);
  - `pre-remove` hooks fail fast and abort the removal (`src/output/handlers.rs:1828-1869,2107-2112`), but `--no-hooks` skips them (`src/commands/remove.rs:422-457`);
  - the branch is deleted only when integrated, through a compare-and-swap `update-ref -d` (`src/git/remove.rs:643-691,739-759`);
  - no `git push` in production code (listing: `grep -rn '"push"' src --include=*.rs`);
  - the Claude plugin writes `worktrunk.state.<branch>.marker` into the repo's git config on every prompt, stop and session end (`src/commands/config/plugins.rs:182-187,264-283`);
  - the `WorktreeRemove` hook routes to `wt remove --foreground <path>` (`src/commands/config/plugins.rs:166-170,220-234`);
  - no concurrency limit (listing over `src/`).
- **Clash** (2ac931c):
  - conflicts come from an in-process gix tree merge of each worktree pair's HEAD commits, so uncommitted changes aren't simulated (`src/worktree/conflict.rs:30-76`);
  - the hook flags overlap with another worktree's uncommitted changes at the same path (`src/check.rs:143-153,301-343`);
  - it answers `permissionDecision: "ask"` and never denies (`src/check.rs:26-44,168-183`);
  - its own code writes no refs, index or config (listing over `src/`), but gix `merge_trees` writes merged blobs as loose objects (gitoxide a5225a7 `gix/src/repository/merge.rs:119-160`);
  - watch mode misses the per-worktree index changes of linked worktrees (`src/watch/watcher.rs:90-102`).
- **workmux** (e9b16d5):
  - status comes from Claude Code hooks it merges into the user's `~/.claude/settings.json` (`src/agent_setup/claude.rs:145-171`);
  - time in state comes from `status_ts` (`src/state/mod.rs:282-302`, `src/command/dashboard/ui/dashboard.rs:461-465`);
  - `--max-concurrent` counts only the windows of the same `add` (`src/command/add.rs:1059-1085`);
  - removal checks `git status --porcelain` without `--ignored` and then runs `git branch -D` (`src/command/remove.rs:220-265`, `src/git/branch.rs:218-231`);
  - its coordinator skill tells an agent to send `/merge` (`skills/coordinator/SKILL.md:250-284`);
  - backends are tmux, WezTerm, Kitty, Zellij and Rex (`src/multiplexer/types.rs:297-307`).
- **Herdr** (ee5bfb5):
  - Claude state comes from screen and OSC rule matching (`src/detect/manifests/claude.toml:1-242`);
  - no time in state (`src/api/schema/agents.rs:210-251` plus a listing);
  - its hooks act only inside herdr panes (`src/integration/assets/claude/herdr-agent-state.sh:20-23`);
  - `agent wait` takes a single target (`src/api/wait.rs:132-175`);
  - no commit or push outside tests (listing).
- **Orca** (3c19574, read 2026-11-19):
  - the at-risk check lists ignored files with `git ls-files --others --ignored --directory`, excludes regenerable paths, and byte-compares the rest with the main checkout; nothing is backed up (`src/main/git/worktrees/removal/worktree-at-risk-local-files.ts:12-328`);
  - the GUI delete passes `force` by default (`src/renderer/src/components/sidebar/workspace-actions/deletion/DeleteWorktreeDialog.tsx:96,233-266`);
  - branches are deleted with `git branch -d`, and an unmerged branch is kept (`src/main/git/worktrees/removal/worktree-branch-removal.ts:17-182`);
  - hooks go into the user-global `~/.claude/settings.json`, on by default (`src/main/claude/hooks/hook-settings.ts:44-61`, `src/shared/settings/default-global-settings.ts:269`);
  - the default permission "full-access" launches Claude with `--dangerously-skip-permissions` (`default-global-settings.ts:267`, `src/shared/agent-launch/permissions/tui-agent-permission-choice.ts:47-57`);
  - auto-named branches are renamed after the first prompt (`src/main/agent-hooks/first-work/first-work-branch-rename.ts:91-130`);
  - hooks do nothing outside Orca panes (`src/main/claude/hooks/hook-script.ts:98-106`);
  - a global concurrency limit is absent (listing over `src/`);
  - official builds opt new profiles into telemetry (`src/main/telemetry/consent.ts:71-91`).
- **Claude Code** (installed 2.1.328): `claude agents --json` listed interactive sessions with `status` busy or idle when run on 2026-11-18. That run is the only check made on the installed binary.

Docs only:

- **Agent view** ([agent-view.md](https://code.claude.com/docs/en/agent-view.md), read in full on 2026-11-18): the states, the peek panel's wait time and the notifications; background sessions commit and push unless instructions say the developer commits; `Ctrl+X` deletes a Claude-created worktree, uncommitted changes included; `claude rm` keeps one with uncommitted changes; no concurrency cap is mentioned.
- **Worktrees** ([worktrees.md](https://code.claude.com/docs/en/worktrees.md)): exit cleanup checks changed and untracked files, submodules and new commits; ignored files aren't mentioned.
- **The unverified candidates:** ccmanager, Agent Deck, ccdeck, cctop, Gas Town and the rest of the table, from their READMEs.

Could not verify:

- workmux's copy-at-create (`src/workflow/file_ops.rs`): located but not read in full.
- Whether Claude Code's exit cleanup counts ignored files: closed source.
- The literature snowball stopped after round 3, which still added one paper ([Fan-out](https://doi.org/10.1145/985692.985722)), so it didn't reach a round with nothing new. The verdict doesn't depend on papers.

## Papers

| Paper | Read state | Evidence strength | Review status | Class | Claim (tag) |
|---|---|---|---|---|---|
| [ParallelPilot](https://arxiv.org/abs/2609.33113) | read in part (§4.2, §4.5, §7, §9, App. A.3) | experiment | preprint | borrow ideas | Developers intervene on four signals: completion, a clarification request, an error and a stall. A triage dashboard raised the number of agents participants were comfortable supervising from about 2.6 to 4 (paper-reported) |
| [CAID: Effective Strategies for Asynchronous SE Agents](https://arxiv.org/abs/2603.21489) | read in part (§2, §4.1, §4.2) | experiment | preprint | borrow ideas | Worktree isolation beat isolation by instruction alone. Going from 2 to 4 agents helped and 8 hurt, limited by integration overhead (paper-reported) |
| [STORM](https://arxiv.org/abs/2605.20563) | read in part (§2.2, §3.3, App. E) | experiment | preprint | borrow ideas | Per-file optimistic concurrency control beat worktrees on Commit0-Lite. Writes through bash bypass it (paper-reported) |
| [NP-Bench and a scheduling planner](https://arxiv.org/abs/2610.07261) | read in part (§4, §7) | experiment | preprint | borrow ideas | Batches with declared, non-overlapping write scopes avoid structural conflicts by construction (paper-reported) |
| [Claim Plane](https://arxiv.org/abs/2607.21909) | abstract only | experiment | preprint | borrow ideas | The abstract reports that declaring change intent before writing raised integration success from 65.6% to 96.7% |
| [The Work Behind Delegation](https://arxiv.org/abs/2609.24234) | abstract only | qualitative study | preprint | borrow ideas | The abstract reports a 7-stage supervisory-control model of supervising coding agents |
| [Codellaborator](https://doi.org/10.1145/3706598.3713357) | abstract only | experiment | peer-reviewed | borrow ideas | The abstract reports that proactive agents disrupted workflow, and that showing the agent's presence and context helped |
| [Fan-out: measuring human control of multiple robots](https://doi.org/10.1145/985692.985722) (Olsen and Wood, CHI 2004) | read in full | experiment | peer-reviewed | borrow ideas | How many robots one person can keep working (fan-out) is a robot's activity time divided by the interaction time it needs per command. Interaction time has four parts: monitoring and choosing which robot needs attention, switching context, solving its problem, and giving the command. The first two grow with fan-out. In four races of 8 participants, more autonomous robots and simpler tasks raised fan-out from about 1 to 9, while interaction effort stayed roughly constant for a given interface; a worse interface raised it 25-46%. The model breaks down when fan-out falls near 1, and adding robots stops helping once the task can't use them (paper-reported) |
| [Palantír](https://doi.org/10.1109/tse.2011.64) | abstract only | experiment | peer-reviewed | borrow ideas | The abstract reports early, unobtrusive notice of same-file changes across private workspaces |
| [Crystal: proactive conflict detection](https://doi.org/10.1145/2025113.2025139) | abstract only | weak experiment | peer-reviewed | borrow ideas | The abstract reports speculative merging of developers' copies to catch conflicts early, the method Clash applies |
| [Cassandra](https://doi.org/10.1109/icse.2013.6606619) | abstract only | experiment | peer-reviewed | borrow ideas | The abstract reports ordering tasks to minimize conflicts |
| [AgenticFlict](https://arxiv.org/abs/2604.03551) | abstract only | observational study | preprint | borrow ideas | The abstract reports a 27.67% textual merge-conflict rate across agent pull requests |
| [CooperBench](https://arxiv.org/abs/2601.13295) | abstract only | experiment | preprint | borrow ideas | The abstract reports that two agents on separable features succeed about 30% less often than one |

The literature supports the blend's shape:

- surface "needs you" and stalls (ParallelPilot);
- isolate each agent in its own worktree (CAID);
- warn about overlap early, which is the Palantír and Crystal line of work and what Clash implements;
- stay near 2 to 4 concurrent agents, which is what the N3 threshold encodes (CAID, ParallelPilot).

Fan-out suggests the threshold shouldn't be fixed. The number of sessions one person can keep working rises with how long each session runs unattended between prompts, and falls with the time each prompt or review takes. The dashboard's job is to cut the parts of that time that grow with the number of sessions: monitoring, choosing which session needs you, and switching context. Carrying the robot model over to coding agents is this note's reading, not a finding of the paper.

Coordination by declared intent (Claim Plane, NP-Bench) is the next step if overlap warnings prove too late.

## Worth retrieving manually

- **[Palantír](https://doi.org/10.1109/tse.2011.64)** (doi:10.1109/tse.2011.64). Controlled evidence on whether workspace-awareness notices reduce conflicts, which is the claim behind Clash. Ways to get it: the authors' institutional pages, IEEE Xplore through a library, or a request to the authors. The developer plans to get a library copy.
- **"Informed but Still Colliding"** (no link found; replication package doi:10.5281/zenodo.23113537). A direct test of whether awareness reduces merge conflicts between parallel LLM agents. Ways to get it: the authors, once the manuscript is out. As of 2026-11-21 it doesn't appear to be available yet.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | Claude Code 2.1.328: `claude --help`, `claude agents --help` and `claude agents --json`; docs read verbatim (`.md`): agent-view, worktrees, agents, desktop, desktop-linux, cross-session-messaging |
| Earlier notes and decisions | searched | `grep -rli 'worktree\|multiple sessions\|session manager\|tmux\|herdr\|orca'` over `docs/` and `backlog/`: no note on this topic. Related: the task-management and doctrine notes, and tasks AD-19, AD-256 and AD-327 |
| GitHub repository search | searched | 19 need wordings, both sorts in round 1 (claude sessions; claude worktree; parallel agents; agent orchestrator tmux; coding agents dashboard; agent sessions manager; claude code monitor; agent multiplexer; worktree manager; claude status; jujutsu agents; agent sandbox; agents waiting input; claude notifications; worktree conflicts; agents merge queue; worktree gitignored; claude container; overlayfs agents). Named-candidate queries by stars only, a deviation. Round 4: six saturation wordings |
| GitHub topics | searched | Topic lookups for 22 terms and candidate names; 31 `topic:` searches (e.g. parallel-coding-agents, worktree-manager, agent-session-manager, tmux-agents, herdr-plugin, orca-ide) |
| GitHub code search | searched | 6 README searches for candidates and awesome lists |
| GitLab search | searched | claude code sessions; agent worktree; claude worktree; coding agents tmux; worktree conflict |
| Codeberg search | excluded | Blocks scripted clients. Web search `site:codeberg.org claude code worktree` and `site:codeberg.org coding agents sessions tmux manager` returned no codeberg.org hits; the search tool ignored `site:` |
| npm | searched | 19 queries, e.g. claude sessions; claude worktree; agent session waiting input; worktree conflict detection; worktreeinclude |
| PyPI | searched | Web search (`site:pypi.org`): claude code sessions monitor waiting tmux; parallel claude code agents git worktree TUI; worktree conflict detection parallel agents. Also libraries.io with platform PyPI |
| crates.io | searched | 13 API queries, e.g. claude session; worktree; agent multiplexer; worktree conflict; jj workspace agent; copy on write agents workspace |
| Language registries (Go) | searched | pkg.go.dev: claude code sessions; claude worktree; agent tmux worktree; coding agents parallel; claude squad |
| libraries.io | searched | claude sessions monitor; claude worktree; agent worktree tmux; coding agent sessions dashboard; plus two latest-release-sorted queries |
| Homebrew formulae | searched | formula.json and cask.json, with two jq regexes (claude, coding agent, ai agent, worktree, agent session, multiplex; then gitbutler, jujutsu, vibe) |
| nixpkgs | excluded | Condition unmet: no brotli decompressor installed |
| LibHunt | searched | /r/claude-squad, /r/ccmanager |
| AUR | searched | claude code; worktree; coding agent; ai agents; agent session |
| ecosyste.ms | searched | Keywords: claude-code, git-worktree, ai-agents, worktree, tmux-agents, agent-orchestration |
| Cross-language equivalents | searched | Linux equivalents of the Mac-only cmux, Conductor, Zentty, Mux0, c9watch and claude-control |
| Awesome lists | searched | awesome claude code; awesome coding agents; awesome agent orchestration; awesome git worktree; awesome agentic development. Read hesreallyhim/awesome-claude-code, andyrewlee/awesome-agent-orchestrators, bradAGI/awesome-cli-coding-agents, kyrolabs/awesome-ade, LysCongThanh/awesome-parallel-agents and jqueryscript/awesome-claude-code |
| alternativeto.net | excluded | Blocks scripted clients. Searched instead through web search for alternatives to claude-squad, Conductor, Herdr, Orca and workmux |
| General web search | searched | 6 rounds, e.g. "manage multiple claude code sessions dashboard"; "git worktree copy gitignored files"; "detect file conflicts between parallel AI agent worktrees"; "limit number of concurrent claude code agents" |
| Hosted services | searched | Anthropic's desktop, web, Remote Control and Projects docs, read verbatim. Conductor, Codex cloud, Cursor and Copilot agents at snippet depth |
| Skill directories | searched | skills.sh: worktree; parallel sessions; session status; worktree cleanup |
| Claude Code plugin marketplaces | searched | The official marketplace.json (317 plugins), grepped twice (session/status/worktree/notif/parallel/monitor/…; fleet/isolat/sandbox/branch/git) |
| MCP Registry | searched | worktree; sessions; tmux |
| Anthropic's skills repo | excluded | The need is a tool, not an agent skill. The plugin and skill catalogs above cover skills that might serve it |
| GitHub topics for agent skills | searched | Both sorts: "topic:claude-code-plugin sessions", "topic:claude-code-hooks status", "topic:claude-code-hooks notify", "topic:claude-code-plugin worktree" |
| aitoolnet.com | searched | sitemap.xml grepped for claude, worktree, orchestr, herdr, orca, parallel and session; read 3 tool pages |
| arXiv | searched | Through the harvester; 23 phrase queries. 11 phrases of four or more words came back empty because the harvester sends exact phrases |
| OpenAlex | searched | 13 searches; citations of Palantír, CAID, ParallelPilot, Claim Plane and Cassandra; references of CAID; 5 DOI open-access lookups |
| Semantic Scholar | searched | Recommendations from 2603.21489, 2609.24234, 2610.07261, 2609.33113 and 2605.20563. Two lookups: Fan-out matched; "Informed but Still Colliding" came back empty |
| OpenAIRE | searched | parallel coding agents; merge conflict awareness; supervising coding agents; workspace awareness merge conflicts LLM |
| Hugging Face papers | searched | parallel coding agents; multi-agent merge conflicts; supervising multiple coding agents; workspace awareness parallel coding agents |
| papers.cool | searched | parallel coding agents worktree; human supervision multiple coding agents |
| Crossref | excluded | The classic proactive-conflict-detection literature was searched through OpenAlex keyword and citation queries (its substitute), which found Palantír, Crystal and Cassandra |

## Snowball rounds

- **GitHub:** 5 rounds.
  - Round 1 found the core field (about 40 candidates).
  - Round 2 added Agent Orchestrator, kandev, cezar, Codeman, tty7, workmux, CliDeck, tmux-ccm, agent-lanes and git-twig.
  - Round 3 added agentbox.
  - Rounds 4 and 5 added nothing, so the route stopped.
- **Registries:** 3 rounds.
  - Round 2 added vibe-kanban, GitButler, Clash, git-parsec, jjfx, agent-ws, simgit and dagq.
  - Round 3 added nothing serious, so the route stopped.
- **Web:** 6 rounds.
  - Round 4 added Paseo, Parallel Code, Emdash, T3 Code and Agent of Empires.
  - Round 5 added orc, bouquet, Agent Orchestrator and Grove.
  - Round 6 added nothing, so the route stopped.
- **Literature:** 3 rounds. Round 3 added Fan-out. The search stopped there for economy, not because a round added nothing.

## Refresh trigger

Search again when any of these happens:

- agent view leaves research preview or changes `claude agents --json`;
- Claude Code adds a concurrency cap or an ignored-files check to worktree removal;
- the custom guard turns out to need more than about 50 lines.
