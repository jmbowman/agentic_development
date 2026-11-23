# Orca

[Orca](https://github.com/stablyai/orca) is a desktop app for running several coding agents (Claude Code among them) at once, each in its own git worktree. It shows which agents are working, done or waiting on you, and creates and deletes worktrees for them. It's MIT-licensed, ships for macOS, Windows and Linux, and releases about once a day.

This page is a working guide. Checked against Orca's source and docs at v1.4.269 (2026-11-22), and tried on Linux. The macOS and Windows notes come from Orca's docs and haven't been tried; corrections from those platforms are welcome. This repo's scripts in `tools/parallel-sessions/` (Linux only) were tried on Linux x86_64 with Orca 1.4.269 on 2026-11-22: setup with and without `--apply`, the installer recording an existing hand-made install, the settings check, and starting Orca from the menu entry. Their Clash steps and arm64 haven't been tried.

## Why use it

Running several Claude Code sessions in one repo needs two things: a view of every session's state, so none sits blocked, and a cheap, safe way to give each session its own worktree. [The parallel-session prior-art note](../prior-art/2026-11-18-parallel-session-and-worktree-management.md) compared about 60 tools for this. Orca and a blend built on Claude Code's own agent view came out ahead. Orca is being tried first ([AD-335](../../backlog/tasks/ad-335%20-%20Trial-Orca-and-the-parallel-session-blend-then-choose-one.md)), since it also serves as a session and terminal manager; the blend gets built only if Orca falls short.

What Orca does well:
- **One window for every agent,** with a state dot per session (working, done, waiting on you), fed by Claude Code hooks rather than guessed from the screen.
- **One step from task to agent:** create a worktree and launch Claude Code in it, from the window or with `orca worktree create --agent claude`.
- **Careful worktree removal.** It's the only tool in the survey that checks gitignored files before deleting a worktree. It lists them, skips ones that can be regenerated (`node_modules`, `.venv`, build output) and shows any that would be lost, `.env` first. It also keeps a branch that isn't merged.
- **Works across repos.** It's installed once per machine and holds every repo you add, so nothing is installed per repo.

What to keep in mind:
- It tracks only sessions started inside Orca. A `claude` started in another terminal is invisible to it.
- Waiting on another session, and a cap on concurrent agents, exist only in its experimental orchestration feature.
- It installs hooks into your user-wide `~/.claude/settings.json` (see [What Orca changes outside itself](#what-orca-changes-outside-itself)).
- Several defaults need changing first (see [Settings to change before running an agent](#settings-to-change-before-running-an-agent)).

## Installation

Orca's [install docs](https://orca.dev/docs/install) list the packages for each platform. Whatever the platform, take a release at least a few days old, check it before installing (below), and upgrade only when you choose to.

### Linux: choose a package

The three Linux packages hold the same app, for x86_64 and arm64, and differ in how updates reach you ([install docs](https://orca.dev/docs/install#linux)):

| Package | Updates |
|---|---|
| AppImage | Orca downloads an update when you click **Update** and replaces the AppImage file in place |
| `.deb` / `.rpm` | Orca downloads the new package and gives you an install command to run yourself with `sudo` |

The AppImage needs no root and makes rollback easy: keep the previous file. The `.deb` puts every upgrade through your package manager, and `apt-mark hold orca-ide` pins it. Either works with a pinned, vetted version. This page assumes the AppImage.

### Linux: where to put the AppImage

An AppImage is the application itself, not an installer: a single executable that mounts its own bundled files when it runs. Nothing goes into system directories. Common places for it:
- **`~/Applications/`**, the convention AppImage tooling such as AppImageLauncher uses;
- **`~/.local/bin/`**, which is on `PATH` on most distributions;
- **`/opt/<app>/`**, for a copy shared by every user.

Avoid `/usr/local/bin/`. It's owned by root, so Orca's own **Update** can't replace the file there, and it's meant for command-line programs rather than desktop apps.

A layout that keeps old versions for rollback:

```bash
mkdir -p ~/Applications/orca
mv orca-linux.AppImage ~/Applications/orca/orca-1.4.269.AppImage
chmod +x ~/Applications/orca/orca-1.4.269.AppImage
ln -sfn orca-1.4.269.AppImage ~/Applications/orca/orca.AppImage
```

On Linux, `uv run --script tools/parallel-sessions/orca_install.py orca-linux.AppImage --tag v1.4.269` from this repo builds this layout for you, after the checks in [Verify the download](#verify-the-download): it refuses a prerelease, a release younger than 3 days (`--allow-young` skips that), and a file whose size or sha512 differs from the release's manifest. It also saves Orca's icon for the menu entry. To install somewhere other than `~/Applications/orca`, or to change the 3-day minimum, create `~/.config/parallel-sessions/config.toml` with `install_dir = "~/somewhere/orca"` or `min_release_age_days = 7`; every script in `tools/parallel-sessions/` reads it, and none writes it.

To move to a new version, add its file and repoint the link. To roll back, point the link at the old file. Orca says it won't force-downgrade your worktree data if you go back. Don't use Orca's in-app **Update** with this layout: it replaces the running file in place, which through the link rewrites a versioned file with another version.

### macOS and Windows

Not tried here; from Orca's [install docs](https://orca.dev/docs/install):
- **macOS:** a `.dmg` for Apple Silicon or Intel, or the Homebrew cask, `brew install --cask stablyai/orca/orca`. Use the full name: bare `orca` is an unrelated cask. `brew upgrade --cask stablyai/orca/orca` takes new stable releases, so run it only once you've vetted the new one. The CLI command is `orca`.
- **Windows:** the installer, `orca-windows-setup.exe`.

Both update themselves from inside the app. With **Automatic updates** off and an update delay set (see the settings table), Orca only offers an update and waits for you to accept it.

### Verify the download

Each release carries a manifest per platform listing each package's sha512, base64-encoded: `latest-linux.yml`, `latest-linux-arm64.yml`, `latest-mac.yml` and `latest.yml` (Windows). On Linux, compare it with the file you downloaded:

```bash
sha512sum orca-linux.AppImage | cut -d' ' -f1 | xxd -r -p | base64 -w0; echo
gh release download -R stablyai/orca v1.4.269 -p latest-linux.yml -O - | grep -A1 'orca-linux.AppImage'
```

The hashes must match, and the file size should match the `size` line. This proves the file arrived intact, not who built it. Releases are published by GitHub Actions, but they carry no signature or build attestation (`gh attestation verify` finds none). [AD-333](../../backlog/tasks/ad-333%20-%20Run-a-prior-art-search-on-vetting-a-third-party-tool-release-before-installing-or-upgrading.md) searches for a better vetting procedure.

Check the release's age and open issues before taking it:

```bash
gh release list -R stablyai/orca --limit 10 --exclude-pre-releases
gh issue list -R stablyai/orca --state all --search "1.4.269"
gh issue list -R stablyai/orca --state open --label os:linux
```

On macOS, `shasum -a 512` gives the same hex digest, and on Windows `Get-FileHash -Algorithm SHA512` in PowerShell; convert the hex to base64 to compare it with the manifest.

### Back up your Claude Code settings

Orca writes into `~/.claude/settings.json` when it starts (below), so keep a copy first:

```bash
cp -n ~/.claude/settings.json ~/.claude/settings.json.pre-orca
```

### First launch

Start it with telemetry off, every time. While `DO_NOT_TRACK=1` (or `ORCA_TELEMETRY_DISABLED=1`) is set, the **Share anonymous usage data** toggle is locked, because Orca doesn't let an environment override be changed from the app (`src/main/telemetry/consent.ts`). Turning the toggle off instead would mean one launch without the variable, and official builds opt new profiles in, so that launch would send events before you could switch it off. Launch through a script or menu entry that always sets the variable. On Linux:

```bash
DO_NOT_TRACK=1 ~/Applications/orca/orca.AppImage
```

On Linux, this repo's `tools/parallel-sessions/setup.py` installs a launcher, `~/.local/bin/orca-launch`, and a menu entry that starts Orca through it, so every start from the menu or dock gets the variables. Run `uv run --script tools/parallel-sessions/setup.py` to see the changes, and add `--apply` to make them; it backs up any file it changes under `~/.local/state/parallel-sessions/backups/`. It also adds a [Clash](https://github.com/clash-sh/clash) hook to `~/.claude/settings.json` when `clash` is on `PATH`. Alternatively, set `DO_NOT_TRACK=1` for your whole desktop session, so every way of starting Orca gets it. That also tells every other program that reads `DO_NOT_TRACK` not to send usage data, which you may or may not want. Ways to set it session-wide (not tried here):
- **Linux** with a systemd user session: a file in `~/.config/environment.d/`, such as `telemetry.conf` holding `DO_NOT_TRACK=1`, read at your next login.
- **macOS:** apps started from Finder or the Dock don't see your shell's variables. `launchctl setenv DO_NOT_TRACK 1` sets it for apps started afterwards, until you log out, so it needs to run at each login.
- **Windows:** a user environment variable, set in System Properties → Environment Variables, which apps started afterwards see.

To confirm Orca saw the variable, open **Settings → Privacy**: the **Share anonymous usage data** toggle is locked. On Linux, don't check with `/proc/<pid>/environ` of an `orca-ide` process. Chromium overwrites that memory to set its process titles, so it reads as empty whatever Orca was started with (seen with 1.4.269). The AppImage runtime, the process named `orca.AppImage`, keeps its environment readable there, and shows what the launcher passed on.

If the AppImage fails to start, there are two common causes on recent Ubuntu (not yet seen with Orca itself):
- **A FUSE error:** install `libfuse2t64`, or run it with `--appimage-extract-and-run`.
- **A Chromium sandbox error,** which comes from Ubuntu's AppArmor limits on unprivileged user namespaces: use the `.deb` instead.

On first launch Orca asks for access to your home directory and offers to import `~/.claude`, `~/.codex` and Ghostty settings. What the `~/.claude` import copies hasn't been checked here.

### Settings to change before running an agent

| Setting | Default | Change to | Where |
|---|---|---|---|
| Share anonymous usage data (`telemetry.optedIn`) | on for new profiles in official builds | leave it: `DO_NOT_TRACK=1` at every launch overrides it, and locks the toggle | Settings → Privacy |
| Agent permission default (`agentPermissionDefault`) | `full-access`, which launches Claude Code with `--dangerously-skip-permissions` | your normal permission mode | Settings → Agents (launch settings) |
| Chat permission mode (`nativeChatPermissionMode`) | `full-access` | your normal permission mode | Settings → Agents |
| Rename branches from work (`autoRenameBranchFromWork`) | on: after the first prompt, a model names the branch and Orca runs `git branch -m` | off, if you decide when branches change | Settings → Source Control |
| Update delay (`updateDelayDays`) | 0 days | 3 days or more | Settings → General → Updates |
| Automatic updates (`automaticUpdates`) | off: Orca checks daily and offers updates, but installs only when you click | leave off | Settings → General → Updates |
| Coordinator approvals (`orchestrationCoordinatorApprovalsEnabled`) | off | leave off: it lets an agent approve another agent's permission prompts | Settings → orchestration |
| Delete agent history when a workspace is deleted (`deleteChatHistoryWithWorkspace`) | off | leave off: on, workspace cleanup also deletes Claude Code chats of removed workspaces | Settings → Agents |
| Always force-delete worktrees (`alwaysForceDeleteWorktrees`), always force-delete preserved branches (`alwaysForceDeletePreservedBranches`), skip the delete confirmation (`skipDeleteWorktreeConfirm`) | off | leave off: each lets a delete remove more than you've seen | set from delete dialogs and Settings |

Orca keeps these in a SQLite profile database that it locks and migrates (on Linux, `~/.config/orca/profiles/local-default/profile-state.db`), and it has no command-line way to change settings, so set them in the app. Settings migrations can rewrite defaults on upgrade, so check the table again after each upgrade. On Linux, `uv run --script tools/parallel-sessions/orca_settings_check.py`, run with Orca closed, does that check. It also checks the installed packages against the installer's record, and Orca's hook entries in `~/.claude/settings.json` against those Orca 1.4.269 installs for your Claude Code version, missing or extra. It exits 0 when everything matches, 1 when something differs, and 2 when it couldn't check something, such as an Orca version whose defaults it doesn't know yet.

### Register the CLI

Register the CLI from **Settings → General → Orca CLI**. On Linux it's `orca-ide`, not `orca`, because GNOME's screen reader already owns `/usr/bin/orca`: with the AppImage, registering installs `~/.local/bin/orca-ide`, and the `.deb` and `.rpm` install `/usr/bin/orca-ide`. On macOS and Windows it's `orca`. Inside Orca's own terminals a bare `orca` works everywhere. The commands on this page use `orca-ide`; elsewhere, read them as `orca`.

## What Orca changes outside itself

- **`~/.claude/settings.json`:** at every startup, while agent status hooks are on (the default), Orca writes its hook entries for about 20 Claude Code events. It also adds a `statusLine` if you have none. Turning the setting off stops new installs but doesn't remove existing entries, so take them out by hand if you stop using Orca. The hooks exit at once outside an Orca terminal, so other Claude Code sessions are unaffected apart from a short script run per event.
- **Your Claude login:** Orca uses your existing Claude Code login to fetch usage and rate-limit figures for its status bar.
- **The network:** a daily update check against GitHub releases, a download of state-detection rules from GitHub every 4 hours, and telemetry unless turned off.
- **Worktrees:** Orca creates them under its own workspace directory (`workspaceDir`), not under `.claude/worktrees/`.
- **A background process:** Orca's terminals, and the agents running in them, live in a daemon that keeps running after you quit Orca, so they survive a restart (`src/main/daemon/providers/adapter/daemon-pty-event-subscriptions.ts`). On Linux its process is named `orca-agents` (`src/main/daemon/daemon-process-name.ts`). A relaunched Orca reattaches to the running daemon, so its terminals keep the environment of the launch that started it. If that launch wasn't through the launcher, quit Orca and end the daemon (`pkill -x orca-agents`) before relaunching. That also ends every session running in Orca's terminals. The settings check doesn't count the daemon as Orca running, because the daemon doesn't hold the profile database.

## Key usage notes

- **Start every session inside Orca.** Its status dots and notifications cover only its own terminals.
- **Default agent: Claude, not Claude Agent Teams.** The default only picks what a new worktree launches; either can be chosen per session. Agent teams (a lead session that spawns teammates sharing a task list and messaging each other; Orca shows each teammate in its own pane) are experimental in Claude Code. Teammates share the lead's checkout rather than getting worktrees of their own, start in the lead's permission mode, aren't restored by `/resume`, and cost a full session's tokens each ([agent teams docs](https://code.claude.com/docs/en/agent-teams.md)). They pay off for work where parallel agents need to talk: research and review, debugging competing hypotheses, or a feature split into pieces that touch separate files. Reach for them in that session rather than by default.
- **Chat UI or Terminal.** Set the default per agent in Settings → Agents (**Chat | CLI**). A session can move to the other form with **Continue in terminal** or **Continue in chat**, which copy the conversation. For Claude Code, Terminal keeps more of what the CLI does; Chat UI suits quick, self-contained tasks. See [Chat UI compared with Terminal](#chat-ui-compared-with-terminal).
- **Remove worktrees with the CLI:** `orca-ide worktree rm --worktree <selector>`, without `--force`. It refuses a worktree with uncommitted or untracked changes.
  - The GUI's **Delete** forces removal after its summary dialog, with no backup. Read the at-risk list it shows, gitignored files included.
  - Don't pass `--delete-branch`: [#19728](https://github.com/stablyai/orca/issues/19728) reports it deleting a pushed, unmerged branch.
  - `rm` also removes a worktree whose terminal is still live ([#23479](https://github.com/stablyai/orca/issues/23479)).
- **Gitignored files in new worktrees:** Orca reads `.worktreeinclude` at the repo root, but takes literal paths only (no globs or `!`), copies files up to 256 KB each, and copies at most 1,000 entries. Use **Settings → Repository → Worktree Shared Paths**, or `worktree.sharedDirectories` in `orca.yaml`, for directories to share by link.
- **Restart by quitting and relaunching.** The AppImage's in-app relaunch can crash ([#41373](https://github.com/stablyai/orca/issues/41373)).
- **Workspace cleanup rules** are all off by default. `orca-ide workspace cleanup preview` shows what a rule would remove before you turn it on.
- **Orchestration** (Settings → Experimental) adds coordinator-run tasks with dependencies, a blocked status and messages between agents. It's useful when one agent hands work to others, and it changes how workers ask questions (`orca orchestration ask` instead of the prompt in their pane).
- **Plugins** can rewrite or block Claude Code tool calls through Orca's pre-tool hook. Install only plugins you've read.

### Chat UI compared with Terminal

Chat UI runs your installed `claude` through the Agent SDK in print mode, with stream-json input and output, not as the interactive CLI. Checked in Orca's source at v1.4.269 and by running Claude Code 2.1.328 the same way.

What stays the same:
- **Configuration loads.** Chat sessions load your user, project and local settings and use Claude Code's own system prompt, so `CLAUDE.md`, hooks, skills and permission rules apply (`src/main/claude/structured/launch/claude-structured-launch-resolution.ts`).
- **Questions come through whole.** `AskUserQuestion` cards show several questions at once, multi-select, option previews on single-select questions, and free text (`src/main/claude/structured/journal/claude-structured-prompt-items.ts`).
- **The session is visible to other Claude Code tools.** A session run this way appears in `claude agents --json` with a busy or idle status, and gets a cross-session messaging socket.

What differs:
- **Claude Code treats the session as unattended.** It sets `CLAUDE_CODE_SESSION_ATTENDED=0` (and Orca sets `CLAUDE_CODE_ENTRYPOINT=orca`). Hooks that act only in attended sessions stay silent: this repo's subagent notes hooks are one, so the session wrap-up gets no process notes from subagents run in a Chat session.
- **Permission prompts have three answers:**
  - **Allow** and **Allow for this session.** The second allows matching calls only until the session ends; it never saves the "don't ask again" rule to your settings the way the CLI's prompt can.
  - **Deny,** which tells Claude only "User denied this action." The CLI also lets you add a comment to steer it.
- **Cross-session messages can expire.** A message that waits for your approval expires after five minutes, because a print-mode session can't show the approval dialog (Claude Code's [cross-session messaging docs](https://code.claude.com/docs/en/cross-session-messaging.md)). Setting `crossSessionInbound` to `accept` avoids the wait, for every session.
- **Terminal-only features are missing:** agent view and its `←` switch, and built-in commands that open a terminal dialog. Which other built-in commands Chat UI's `/` menu offers hasn't been checked.
- **The transcript is cleaner.** Chat shows messages, tool activity and file links; the terminal shows everything the CLI prints.

## References

- [Orca docs](https://orca.dev/docs). Start with:
  - [Your first 3-agent session](https://orca.dev/docs/first-session);
  - [Install](https://orca.dev/docs/install) (Linux packages, updates, the `orca-ide` CLI);
  - [Worktrees](https://orca.dev/docs/model/worktrees) (lifecycle, shared and gitignored files, cleanup);
  - [Claude Code in Orca](https://orca.dev/docs/agents/claude-code);
  - [CLI reference](https://orca.dev/docs/cli/reference);
  - [Orchestration](https://orca.dev/docs/cli/orchestration);
  - [Privacy & Telemetry](https://orca.dev/docs/telemetry).
- [Releases](https://github.com/stablyai/orca/releases) and [issues](https://github.com/stablyai/orca/issues) (the `os:linux` label narrows to Linux reports).
- The docs' source is in the repo under `docs/site/content/docs/`, so the docs for any version can be read at its tag.
- [The parallel-session prior-art note](../prior-art/2026-11-18-parallel-session-and-worktree-management.md): how Orca compares with the alternatives, and what was verified in its source.
- [Tool feedback for Orca](../tool-feedback/orca.md): problems found in its source, to raise upstream.
