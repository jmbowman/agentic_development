# Parallel sessions specs

Design: [parallel-sessions-design.md](parallel-sessions-design.md).

**Terms used throughout:**

**The scripts and their configuration:**
- "The launcher" is `tools/parallel-sessions/orca-launch`, or its installed copy at `~/.local/bin/orca-launch`.
- "The installer" is `tools/parallel-sessions/orca_install.py`, "the settings check" is `tools/parallel-sessions/orca_settings_check.py`, and "setup" is `tools/parallel-sessions/setup.py`. "The Python scripts" are those three.
- "The config file" is `parallel-sessions/config.toml` under `$XDG_CONFIG_HOME` when that variable is an absolute path, and under `~/.config` otherwise.
- "The install directory" is the config file's `install_dir`, or the platform table's default install directory when the config file doesn't set it.
- "The minimum release age" is the config file's `min_release_age_days`, or 3 days when it doesn't set it.
- "The backup directory" is `parallel-sessions/backups/` under `$XDG_STATE_HOME` when that variable is an absolute path, and under `~/.local/state` otherwise.

**Platforms and Orca's installed files:**
- "A supported platform" is Linux on x86_64 (also reported as `amd64`) or arm64 (also reported as `aarch64`). "The platform table" is the design's table of each supported platform's facts.
- "The current package" is the path in `$ORCA_APPIMAGE` when that variable is set and not empty, and otherwise `orca.AppImage` in the install directory the launcher was written with (PAR-SETUP-010), or in `$HOME/Applications/orca` for the launcher in this repo.
- "A versioned package" is a file `<install dir>/orca-<version>.AppImage`.
- "The install record" is `<install dir>/install-record.json`: a JSON object mapping each installed version to its package's sha512, base64-encoded as release manifests record it.
- "The release" is the GitHub release of `stablyai/orca` with the given tag.
- "The release manifest" is the supported platform's manifest file (such as `latest-linux.yml`) attached to the release. "The package's manifest entry" is the item of its `files` list whose `url` is the platform table's package name.

**Orca's settings and processes:**
- "Orca's settings" are the JSON object in the `payload` of the row whose `domain` is `settings` in the `profile_state_documents` table of the profile database.
- "The profile database" is `profiles/<profile>/profile-state.db` under Orca's user-data directory, for the only directory in `profiles/`.
- "An Orca process" is a running process whose command name is the platform table's Orca process name (`orca-ide` on Linux).
- "A known Orca version" is one whose source was read for the settings check's table of defaults and expected hook scripts: 1.4.269.

**Claude Code settings and Clash:**
- "The Claude settings file" is `~/.claude/settings.json`.
- "An Orca hook entry" is a hook entry in the Claude settings file whose command contains the file name of one of Orca's managed hook scripts for the installed version, immediately after a `/` and not followed by a letter, digit, `_`, `.` or `-` (so neither `openclaude-hook.sh` nor `claude-hook.sh.bak` counts as `claude-hook.sh`).
- "The Claude Code version" is the first version (`x.y.z`, with any prerelease or build suffix) followed by `(Claude Code)` in the output of `claude --version`, run from `PATH`, when that command exits 0.
- "The expected hook events" are the Claude Code events for which the installed known Orca version installs a hook entry, given the Claude Code version, by that version's table, with a prerelease ranked below its release as Orca ranks it (so `2.1.261-beta` is below a floor of `2.1.261`).
- "The Clash entry" is a group in the Claude settings file's `hooks.PreToolUse` whose matcher is `Write|Edit|MultiEdit` and whose only hook's command is `clash check`.
- "An equivalent entry" is a group in `hooks.PreToolUse` whose matcher, split on `|`, includes `Write`, `Edit` and `MultiEdit`, or is `*`, `.*` or empty, and whose hooks include one whose command, trimmed, is `clash check`.
- "Clash's plugin is enabled" means the Claude settings file's `enabledPlugins` has a key whose part before `@` is `clash`, with the value `true`.

**Setup's targets:** "A setup target" is one of:
- the installed launcher at `~/.local/bin/orca-launch`;
- the desktop entry at `~/.local/share/applications/orca.desktop`;
- the Claude settings file.

## All scripts

- [x] **PAR-ALL-001**: When more than one exit status applies to a run of a Python script, it shall exit with the highest that applies: 2 over 1 over 0.
- [x] **PAR-ALL-002**: Each Python script shall carry on checking after a problem it can report, print every problem it found, and only then exit, except where a spec says to stop at once.
- [x] **PAR-ALL-003**: Of the launcher and the Python scripts, only the installer shall make network requests, and it shall make them over HTTPS without sending credentials.

## Platforms

- [x] **PAR-PLAT-001**: The Python scripts shall take every platform-specific value they use (manifest name, package name, default install directory, launcher and menu entry paths, Orca's user-data directory, profile database path, icon path, Orca's process name) from the platform table, held as data in one place.
- [x] **PAR-PLAT-002**: If a Python script is run on a platform that isn't a supported platform, then it shall exit with status 2 and a message naming the operating system and architecture, before reading or writing any file outside this repo.

## Config file

- [x] **PAR-CONF-001**: When a Python script reads a path from the config file that starts with `~/`, or is `~`, it shall expand the `~` to the user's home directory.
- [x] **PAR-CONF-002**: If the config file exists but can't be read, or isn't valid TOML, then each Python script shall exit with status 2 and a message saying so, without falling back to defaults.
- [x] **PAR-CONF-003**: If the config file has a key other than `install_dir` and `min_release_age_days`, then each Python script shall exit with status 2 and a message naming the key.
- [x] **PAR-CONF-004**: If the config file's `install_dir` isn't a string naming an absolute path after PAR-CONF-001's expansion, or its `min_release_age_days` isn't a non-negative integer (a boolean or a float is not), then each Python script shall exit with status 2 and a message naming the key.
- [x] **PAR-CONF-005**: If the config file's `install_dir` starts with `~` followed by anything but `/`, then each Python script shall exit with status 2 and a message naming the key.
- [x] **PAR-CONF-006**: When the config file has more than one problem PAR-CONF-003 to PAR-CONF-005 name, each Python script shall name every one in its message.
- [x] **PAR-CONF-007**: No Python script shall write the config file.

## Launcher

- [x] **PAR-LAUNCH-001**: When the launcher runs, it shall set `DO_NOT_TRACK` and `ORCA_TELEMETRY_DISABLED` to `1` in the environment it passes to the current package, replacing any value either variable already has.
- [x] **PAR-LAUNCH-002**: When the launcher runs and the current package is a regular file that is executable, it shall replace its own process with the current package (`exec`), passing its own arguments through unchanged, so the package's exit status is the launcher's.
- [x] **PAR-LAUNCH-003**: If the current package isn't a regular file that is executable when the launcher runs, then the launcher shall print a message naming the path on stderr and exit with status 1, without starting any other program.
- [x] **PAR-LAUNCH-004**: The launcher shall start with `#!/bin/sh` and use only POSIX shell built-ins until it starts the current package.

## Installer

### Checks before installing

- [x] **PAR-INSTALL-001**: The installer shall take the path of a downloaded package and a release tag as `orca_install.py <package> --tag <tag>`, accepting the usual option forms (`--tag=<tag>`, options in any order).
- [x] **PAR-INSTALL-002**: If the release is a prerelease, or GitHub reports it as not found (which an anonymous request also gets for a draft), then the installer shall exit with status 1 and a message saying which, without writing any file.
- [x] **PAR-INSTALL-003**: If the time since the release's `published_at`, in seconds, is less than the minimum release age times 86,400, and `--allow-young` wasn't passed, then the installer shall exit with status 1 and a message giving the release's age and the minimum in days to one decimal place, without writing any file. A `published_at` in the future counts as an age of 0.
- [x] **PAR-INSTALL-004**: When `--allow-young` is passed, the installer shall skip only the release-age check of PAR-INSTALL-003, and say that it skipped it.
- [x] **PAR-INSTALL-005**: If the downloaded file's sha512 differs from the sha512 in the package's manifest entry, compared as bytes after base64 decoding, then the installer shall exit with status 1 and a message saying the hashes differ, without writing any file.
- [x] **PAR-INSTALL-006**: If the downloaded file's size in bytes differs from the `size` in the package's manifest entry, then the installer shall exit with status 1 and a message saying the sizes differ, without writing any file.
- [x] **PAR-INSTALL-007**: If the release manifest's `version` differs from the tag with any leading `v` removed, then the installer shall exit with status 1 and a message giving both, without writing any file.
- [x] **PAR-INSTALL-008**: If the installer can't complete a check (the network fails, GitHub rate-limits the request, the release has no release manifest, the manifest can't be parsed or lacks its `version`, the package's manifest entry, or that entry's `sha512` or `size`, or the install record exists but isn't a valid JSON object), then it shall exit with status 2 and a message naming the check, without writing any file.
- [x] **PAR-INSTALL-009**: The installer shall run its checks in this order, and stop at the first that fails: PAR-INSTALL-022, PAR-INSTALL-002, PAR-INSTALL-003, PAR-INSTALL-007, PAR-INSTALL-006, PAR-INSTALL-005, PAR-INSTALL-013, PAR-INSTALL-023, PAR-INSTALL-014.
- [x] **PAR-INSTALL-022**: If the downloaded package's path doesn't name a readable regular file, then the installer shall exit with status 2 and a message naming the path, before any network request.
- [x] **PAR-INSTALL-023**: If the install record holds an entry for the version whose sha512 differs from the downloaded file's, then the installer shall exit with status 1 and a message saying the record disagrees, without writing any file.

### Installing

- [x] **PAR-INSTALL-010**: When every check passes and the install directory doesn't exist, the installer shall create it.
- [x] **PAR-INSTALL-011**: When every check passes and `orca-<version>.AppImage` doesn't exist in the install directory, the installer shall write the downloaded file there through a temporary file in the install directory renamed into place, and make it executable.
- [x] **PAR-INSTALL-012**: When every check passes and `orca-<version>.AppImage` already exists in the install directory with the same content as the downloaded file, the installer shall leave it as it is.
- [x] **PAR-INSTALL-013**: If `orca-<version>.AppImage` already exists in the install directory with content different from the downloaded file, then the installer shall exit with status 1 and a message naming the file, without writing any file.
- [x] **PAR-INSTALL-014**: If `<install dir>/orca.AppImage` exists and isn't a symbolic link, then the installer shall exit with status 1 and a message saying so, without writing any file.
- [x] **PAR-INSTALL-015**: When PAR-INSTALL-011 or PAR-INSTALL-012 has applied, the installer shall record the version and its sha512 in the install record, keeping every other entry.
- [x] **PAR-INSTALL-016**: When the installer has recorded the version under PAR-INSTALL-015, it shall make `<install dir>/orca.AppImage` a symbolic link whose target is the relative name of that version's versioned package, by renaming a new link into place.
- [x] **PAR-INSTALL-017**: The installer shall never delete or overwrite a versioned package.
- [x] **PAR-INSTALL-018**: When the installer has repointed `<install dir>/orca.AppImage` under PAR-INSTALL-016, it shall fetch Orca's icon at the release's tag (the platform table's icon path in `stablyai/orca`) and write it to `<install dir>/icon.png` through a temporary file renamed into place.
- [x] **PAR-INSTALL-019**: If fetching Orca's icon fails, or writing it to `<install dir>/icon.png` fails, then the installer shall say so, leave any existing `icon.png` as it is, and continue, without failing the install.
- [x] **PAR-INSTALL-020**: When the installer finishes an install, it shall tell the developer to quit any running Orca, re-run setup, relaunch Orca with the launcher, and run the settings check.
- [x] **PAR-INSTALL-021**: When the installer finishes an install, it shall exit with status 0.

## Settings check

### Outcome

- [x] **PAR-CHECK-001**: The settings check shall create, change or delete no file.
- [x] **PAR-CHECK-002**: When every item the settings check compares matches what's expected, it shall exit with status 0.
- [x] **PAR-CHECK-003**: When the settings check completes and at least one item differs from what's expected, it shall print each difference and exit with status 1.
- [x] **PAR-CHECK-004**: If the settings check can't complete a comparison, then it shall print why and exit with status 2, and shall never exit with status 0 or 1 for a comparison it didn't complete.
- [x] **PAR-CHECK-005**: If an Orca process is running, then the settings check shall make the comparisons that don't need the profile database, print their results, and exit with status 2 and a message saying to quit Orca to check its settings, without opening the profile database.
- [x] **PAR-CHECK-006**: If Orca's user-data directory doesn't exist, then the settings check shall exit with status 2 and a message saying to run Orca once first.
- [x] **PAR-CHECK-009**: If `profiles/` in Orca's user-data directory holds no directory, or more than one, then the settings check shall exit with status 2 and a message naming what it found.
- [x] **PAR-CHECK-007**: If the profile database has no `settings` row in `profile_state_documents`, or has a `profile_state_document_parts` table holding parts for `settings`, then the settings check shall exit with status 2 and a message saying so.
- [x] **PAR-CHECK-008**: The settings check shall open the profile database read-only and as immutable, so that SQLite creates no file beside it.
- [x] **PAR-CHECK-015**: If `profile-state.db-wal` beside the profile database exists and isn't empty, then the settings check shall exit with status 2 and a message saying to start and quit Orca, without opening the profile database.

### Installed files

- [x] **PAR-CHECK-010**: If `<install dir>/orca.AppImage` isn't a symbolic link to a versioned package in the install directory, then the settings check shall report it as a difference.
- [x] **PAR-CHECK-011**: If any versioned package in the install directory has a sha512 different from the one the install record holds for its version, or the install record (or its entry for that version) is missing, then the settings check shall report that package as a difference.
- [x] **PAR-CHECK-012**: The settings check shall take the installed version from the name of the versioned package that `<install dir>/orca.AppImage` links to.
- [x] **PAR-CHECK-013**: If the install record exists but isn't a valid JSON object, then the settings check shall report that it couldn't check the installed files, and exit with status 2.
- [x] **PAR-CHECK-014**: If the installed version can't be taken from `<install dir>/orca.AppImage`, then the settings check shall report that it couldn't check Orca's settings defaults and hook entries, and exit with status 2.

### Orca's settings

- [x] **PAR-CHECK-020**: The settings check shall report Orca's `agentPermissionDefault` as a difference when it is `full-access`.
- [x] **PAR-CHECK-021**: The settings check shall report Orca's `nativeChatPermissionMode` as a difference when it is `full-access`.
- [x] **PAR-CHECK-022**: The settings check shall report Orca's `autoRenameBranchFromWork` as a difference when it isn't `false`.
- [x] **PAR-CHECK-023**: The settings check shall report Orca's `updateDelayDays` as a difference when it is less than the minimum release age.
- [x] **PAR-CHECK-024**: The settings check shall report Orca's `automaticUpdates` as a difference when it is `true`.
- [x] **PAR-CHECK-025**: The settings check shall report Orca's `orchestrationCoordinatorApprovalsEnabled` as a difference when it is `true`.
- [x] **PAR-CHECK-026**: The settings check shall report Orca's `agentStatusHooksEnabled` as a difference when it isn't `true`.
- [x] **PAR-CHECK-027**: The settings check shall report each of Orca's `deleteChatHistoryWithWorkspace`, `alwaysForceDeleteWorktrees`, `alwaysForceDeletePreservedBranches` and `skipDeleteWorktreeConfirm` as a difference when it is `true`.
- [x] **PAR-CHECK-028**: When a setting PAR-CHECK-020 to PAR-CHECK-027 compares is missing from Orca's settings and the installed version is a known Orca version, the settings check shall compare that version's default for it instead.
- [x] **PAR-CHECK-029**: When a setting PAR-CHECK-020 to PAR-CHECK-027 compares is missing from Orca's settings and the installed version isn't a known Orca version, the settings check shall report it as "unset, default unknown", and exit with status 2.
- [x] **PAR-CHECK-032**: When a setting PAR-CHECK-020 to PAR-CHECK-027 compares has a value of a type other than the one Orca stores (such as the string `"false"` for a boolean, or JSON `null`), the settings check shall report it as a difference, showing the value.

### Orca's hook entries

- [x] **PAR-CHECK-030**: When the installed version is a known Orca version and the Claude Code version can be read, the settings check shall report each of the expected hook events for which the Claude settings file has no hook entry, under that event, running the script the version's table names for it.
- [x] **PAR-CHECK-034**: When the installed version is a known Orca version and the Claude Code version can be read, the settings check shall report each Claude Code event other than the expected hook events under which the Claude settings file has an Orca hook entry.
- [x] **PAR-CHECK-035**: If `claude` isn't on `PATH`, `claude --version` exits with a status other than 0, or its output holds no Claude Code version, then the settings check shall report that it couldn't check Orca's hook entries, and exit with status 2.
- [x] **PAR-CHECK-031**: When the installed version isn't a known Orca version, the settings check shall report that it couldn't check Orca's hook entries, and exit with status 2.
- [x] **PAR-CHECK-033**: If the Claude settings file is missing, isn't valid JSON, isn't a JSON object, or has a `hooks` key whose value isn't an object, then the settings check shall report that it couldn't check Orca's hook entries, and exit with status 2.

## Clash's entry

- [x] **PAR-CLASH-001**: When setup runs, `clash` is on `PATH`, the Claude settings file has no equivalent entry, and Clash's plugin isn't enabled, setup shall append the Clash entry to the Claude settings file's `hooks.PreToolUse`.
- [x] **PAR-CLASH-002**: When setup runs and the Claude settings file has an equivalent entry, or Clash's plugin is enabled, setup shall add no Clash entry.
- [x] **PAR-CLASH-003**: When setup runs, `clash` isn't on `PATH`, and the Claude settings file has an equivalent entry, setup shall report the entry as stale, leave it in place, and list it in its summary as making the setup incomplete.
- [x] **PAR-CLASH-004**: When setup runs, `clash` isn't on `PATH`, the Claude settings file has no equivalent entry, and Clash's plugin isn't enabled, setup shall add no Clash entry, print the `mise use -g` command that installs the Clash version the scripts were tested with, and list Clash's entry as skipped in its summary.
- [x] **PAR-CLASH-005**: When setup runs, `clash` isn't on `PATH`, the Claude settings file has no equivalent entry, and Clash's plugin is enabled, setup shall add no Clash entry, report that the plugin's hook can't run, print the `mise use -g` command of PAR-CLASH-004, and list it in its summary as making the setup incomplete.

## Setup

### Showing and applying

- [x] **PAR-SETUP-001**: When setup runs without `--apply`, it shall print, for each setup target it would change, a unified diff of the change (and a line for a change of permissions), and change no file.
- [x] **PAR-SETUP-002**: When setup runs with `--apply`, it shall compute the changes again from the files as they are, print them as PAR-SETUP-001 does, and then make exactly the printed changes, except for a target PAR-SETUP-004 leaves alone.
- [x] **PAR-SETUP-003**: When setup with `--apply` writes a setup target, it shall write it through a temporary file in the directory of the file being written, renamed into place.
- [x] **PAR-SETUP-004**: When setup with `--apply` is about to write a setup target, it shall check that the target's content is unchanged since setup read it, before taking a backup and again just before the rename, and if it changed, leave that target as it is and report that it changed underneath.
- [x] **PAR-SETUP-005**: When setup with `--apply` writes a setup target that already exists, it shall first copy it into the backup directory, under a name made of the target's file name and the run's UTC start time (`YYYYMMDDTHHMMSS.ffffffZ`).
- [x] **PAR-SETUP-016**: Setup shall create the backup directory, and the copies in it, readable and writable only by the user, and with no execute permission on the copies.
- [x] **PAR-SETUP-006**: When the Claude settings file is a symbolic link, setup shall write the file the link points to, with its temporary file beside that file, and leave the link in place.
- [x] **PAR-SETUP-017**: When the installed launcher or the desktop entry is a symbolic link, setup shall replace the link with a regular file, through a temporary file beside the link renamed into place, leaving the file the link pointed to as it is, and its diff shall say the link is replaced.
- [x] **PAR-SETUP-007**: When setup with `--apply` runs and no setup target needs a change, it shall write no file and make no backup.
- [x] **PAR-SETUP-009**: Setup shall treat a setup target as needing a change only when its permissions differ from what setup would write, or its content does; for the Claude settings file, when its parsed JSON does.
- [x] **PAR-SETUP-008**: When setup changes the Claude settings file, it shall keep every key and hook entry it doesn't add, including Orca hook entries, with the same values, and write the file as JSON indented by two spaces, keeping the order of existing keys.
- [x] **PAR-SETUP-015**: When the Claude settings file doesn't exist and setup has a Clash entry to add, setup shall create it.
- [x] **PAR-SETUP-025**: If writing one setup target fails, then setup shall carry on with the remaining targets, report the failure in its summary, and exit with status 2.

### What setup writes

- [x] **PAR-SETUP-010**: Setup shall make `~/.local/bin/orca-launch` a copy of `tools/parallel-sessions/orca-launch`, executable, with the install directory written into it as a quoted absolute path, as the directory where the launcher looks for `orca.AppImage`.
- [x] **PAR-SETUP-011**: Setup shall make `~/.local/share/applications/orca.desktop` hold exactly these keys under `[Desktop Entry]`: `Type=Application`, `Name=Orca`, `Exec` set to the installed launcher's absolute path (without `~` or field codes), `Categories=Development;`, `StartupWMClass=orca`, and `Icon` when PAR-SETUP-013 gives one.
- [x] **PAR-SETUP-013**: When `<install dir>/icon.png` exists, setup shall give the desktop entry an `Icon` with that file's absolute path, and when it doesn't, an entry with no `Icon`.

### Prerequisites and outcome

- [x] **PAR-SETUP-020**: Before printing any change, setup shall check that `git`, `uv` and `claude` are on `PATH`.
- [x] **PAR-SETUP-021**: If `git`, `uv` or `claude` isn't on `PATH`, then setup shall exit with status 2 and a message naming each missing one, changing no file.
- [x] **PAR-SETUP-022**: When setup finishes having made or shown every change, with none skipped, no stale Clash entry, no Clash plugin without `clash`, and no target left alone under PAR-SETUP-004, it shall exit with status 0.
- [x] **PAR-SETUP-023**: When setup finishes having skipped a change (a missing `clash`), found a stale Clash entry or a Clash plugin without `clash` (PAR-CLASH-005), or left a target alone under PAR-SETUP-004, it shall end with a summary naming the setup as incomplete and listing what wasn't done, and exit with status 1.
- [x] **PAR-SETUP-024**: If setup fails in any way other than those PAR-SETUP-023 lists, then it shall exit with status 2.
